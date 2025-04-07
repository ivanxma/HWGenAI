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


# OCI-LLM: Used to prompt the LLM
def query_llm_with_prompt(cursor, query, aschema, aemb_model, acitations,allm, amax_token):

    newquery = query.replace('"', "'")

    q1 = """
    SET @options = JSON_OBJECT('schema', JSON_ARRAY('{vectorSchema}'), 
    'embed_model_id', '{emb_model}', 'n_citations', {xncitations}, 
    'model_options',
    JSON_OBJECT('model_id', '{llm}', 'max_tokens', {max_token}))
    """.format(vectorSchema=aschema,emb_model=aemb_model, xncitations=acitations, llm=allm, max_token=amax_token)

    cursor.execute( q1)
    q2 = '''
    set @query="{query}"
    '''.format(query=newquery)
    cursor.execute( q2)

    newprompt = query.replace('"', "'")
    call_string = 'call sys.ML_RAG(@query, @output, @options) '
    rs = cursor.execute( call_string  ) 

    call_string = 'select @output;'
    rs = cursor.execute( call_string  ) 
    data = cursor.fetchall()
    return data[0][0]




# Perform RAG
def answer_user_question(amydb, query, aemb_model, acitations, allm, amax_token):
   response = {}

   with connectMySQL(myconfig)as db:
        cursor = db.cursor()
        llm_response_result = query_llm_with_prompt(cursor, query, amydb, aemb_model, acitations, allm, amax_token)
        response['message'] = query
        response['result'] = llm_response_result

   return response



with st.form('my_form'):
    text = st.text_area('Question : :', 'What is MySQL HeatWave?')
    col1, col2 = st.columns(2)
    with col1 :
      llm = st.selectbox('Choose LLM : ',
         ("mistral-7b-instruct-v1", "llama3-8b-instruct-v1", "llama3-8b-instruct-v1",  "meta.llama-3.2-90b-vision-instruct", "meta.llama-3.3-70b-instruct", "cohere.command-r-08-2024", "cohere.command-r-plus-08-2024" ))
    with col2 :
      mymodel = st.selectbox('Choose embed model : ', ("minilm", "multilingual-e5-small"))
      mydb = st.text_input(label="Database", value=mydb, max_chars=20 )

    col1, col2 = st.columns(2)
    with col1 :
      mycitations = st.number_input('Citation :', 10)
    with col2 :
      mytoken  = st.number_input('Max Token :', 1024)

    submitted = st.form_submit_button('Submit')

    if submitted:
        myans = answer_user_question(mydb, text, mymodel, mycitations, llm, mytoken )
        mydata = json.loads(myans['result'])
        st.divider()
        st.write(mydata['text'])
        st.divider()
        df = pd.DataFrame(mydata['citations'])
        st.write(df)
    
