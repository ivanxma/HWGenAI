import os
import pandas as pd
import streamlit as st
import json

from unstructured.partition.html import partition_html
from unstructured.chunking.title import chunk_by_title
from unstructured.cleaners.core import clean

import oci
import cohere
import mysql.connector

import globalvar

# Constants
mydb = globalvar.mydb
llm = globalvar.llm
n_citations = globalvar.citations
emb_modelid = globalvar.emb_modelid
compartment_id = globalvar.compartment_id
CONFIG_PROFILE = globalvar.CONFIG_PROFILE


# MySQL Connectoin Profile
myconfig = globalvar.myconfig

# Used to connect to MySQL
def connectMySQL(myconfig) :
    cnx = mysql.connector.connect(**myconfig)
    return cnx


# Used to format response and return references
class Document():

      doc_id: int
      doc_text: str
      url: str

      def __init__(self, id, text, url) -> None:

            self.doc_id = id
            self.doc_text = text
            self.url = url

      def __str__(self):
            return f"doc_id:{self.doc_id},doc_text:{self.doc_text},url:{self.url}"

# Find relevant records from DB using vector_distance function
def search_data(cursor, query_vec, list_dict_docs, amydb):

    myvectorStr = ','.join(str(item) for item in query_vec)
    myvectorStr = '[' + myvectorStr + ']'

    relevant_docs = []
    mydata = ( myvectorStr )
    cursor.execute( """
        select *
        from {mydb}.web_embeddings a
        order by vector_distance(vec, string_to_vector(%s)) desc
        LIMIT {citations}
    """.format(mydb=amydb,citations=n_citations), [myvectorStr])



    for row in cursor:
        id = row[0]
        text = row[1]
        url = row[2]
        temp_dict = {id:text}
        list_dict_docs.append(temp_dict)
        doc = Document(id, text, url)
        relevant_docs.append(doc)


    return relevant_docs

# OCI-LLM: Used to generate embeddings for question(s)
def generate_embeddings_for_question(cursor, question_list):

    cursor.execute( """
        select sys.ML_EMBED_ROW("%s", JSON_OBJECT("model_id", "{emb_modelid}") )
    """.format(emb_modelid=emb_modelid), question_list)

    data = cursor.fetchall()
    
    return data[0][0]

# OCI-LLM: Used to prompt the LLM
def query_llm_with_prompt(cursor, prompt, allm):

    newprompt = prompt.replace('"', "'")
    cursor.execute( """
        select sys.ML_GENERATE("{query}", JSON_OBJECT("task", "generation", "model_id", "{myllm}") )
    """.format(query=newprompt,myllm=allm))

    data = cursor.fetchall()
    
    return data[0][0]



# Perform RAG
def answer_user_question(amydb, query, allm):
           
    question_list = []
    question_list.append(query)
           
    with connectMySQL(myconfig)as db:

        cursor = db.cursor()
        question_vector =  generate_embeddings_for_question(cursor, question_list)
        list_dict_docs = []
        #query vector db to search relevant records
        similar_docs = search_data(cursor, question_vector, list_dict_docs, amydb)

        #prepare documents for the prompt
        context_documents = []
        relevant_doc_ids = []
        similar_docs_subset=[]

        for docs in similar_docs:
           content = str(docs.doc_id) + ": " + docs.doc_text
           context_documents.append(docs.doc_text)
           relevant_doc_ids.append(docs.doc_id)


        for docs in similar_docs:
            current_id = str(docs.doc_id)
            if current_id in relevant_doc_ids:
                similar_docs_subset.append(docs)


        context_document = "\n".join(context_documents)
        prompt_template = '''
        Text: {documents} \n
        Question: {question} \n
        Answer the question in simple format based on the Text provided. If the Text does not provide the answer, reply that the answer is not available.
        '''

        prompt = prompt_template.format(question = query, documents = context_document)

        llm_response_result = query_llm_with_prompt(cursor, prompt, allm)
        response = {}
        response['message'] = query
        response_json = json.loads(llm_response_result)
        response['text'] = response_json['text']
        response['documents'] = [{'id': doc.doc_id, 'snippet': doc.doc_text, 'url': doc.url } for doc in similar_docs]


        return response



with st.form('my_form'):
    col1, col2 = st.columns(2)
    with col1 :
      text = st.text_area('Question : :', 'What is MySQL HeatWave?')
    with col2 :
      llm = st.selectbox('Choose LLM : ',
         ("mistral-7b-instruct-v1",  "llama3-8b-instruct-v1",  "meta.llama-3.2-90b-vision-instruct", "meta.llama-3.3-70b-instruct", "cohere.command-r-08-2024", "cohere.command-r-plus-08-2024" ))
      mydb = st.text_input(label="Database", value=mydb, max_chars=20 )
    
    submitted = st.form_submit_button('Submit')

    if submitted:
        myans = answer_user_question(mydb, text, llm)
        # print(myans)
        st.divider()
        st.write(myans['text'])
        st.divider()
        df = pd.DataFrame(myans['documents'])
        #st.write(myans['documents'])
        st.write(df)
    
