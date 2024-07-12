import os
import pandas as pd
import streamlit as st

from unstructured.partition.html import partition_html
from unstructured.chunking.title import chunk_by_title
from unstructured.cleaners.core import clean

import oci
import cohere
import mysql.connector

import globalvar

# Constants
org = globalvar.org
compartment_id = globalvar.compartment_id
CONFIG_PROFILE = globalvar.CONFIG_PROFILE
config = oci.config.from_file('~/.oci/config', CONFIG_PROFILE)

# Service endpoint
endpoint = globalvar.endpoint

generative_ai_inference_client = oci.generative_ai_inference.GenerativeAiInferenceClient(config=config, service_endpoint=endpoint, retry_strategy=oci.retry.NoneRetryStrategy(), timeout=(10,240))

cohere_client = cohere.Client(globalvar.COHERE_API_KEY)

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
def search_data(cursor, query_vec, list_dict_docs, org):

    myvectorStr = ','.join(str(item) for item in query_vec)
    myvectorStr = '[' + myvectorStr + ']'

    relevant_docs = []
    mydata = ( myvectorStr )
    cursor.execute( """
        select *
        from {org}.web_embeddings a
        order by vector_distance(vec, string_to_vector(%s)) desc
        LIMIT 10
    """.format(org=org), [myvectorStr])



    for row in cursor:
        id = row[0]
        text = row[1]
        url = row[3]
        temp_dict = {id:text}
        list_dict_docs.append(temp_dict)
        doc = Document(id, text, url)
        #print(doc)
        relevant_docs.append(doc)


    return relevant_docs

# OCI-LLM: Used to generate embeddings for question(s)
def generate_embeddings_for_question(question_list):

    embed_text_detail = oci.generative_ai_inference.models.EmbedTextDetails()
    embed_text_detail.inputs = question_list
    embed_text_detail.input_type = embed_text_detail.INPUT_TYPE_SEARCH_QUERY
    embed_text_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id="cohere.embed-multilingual-v3.0")
    embed_text_detail.compartment_id = compartment_id
    embed_text_response = generative_ai_inference_client.embed_text(embed_text_detail)
    return embed_text_response

# OCI-LLM: Used to prompt the LLM
def query_llm_with_prompt(prompt):

    cohere_generate_text_request = oci.generative_ai_inference.models.CohereLlmInferenceRequest()
    cohere_generate_text_request.prompt = prompt
    cohere_generate_text_request.is_stream = False
    cohere_generate_text_request.max_tokens = 1000
    cohere_generate_text_request.temperature = 0.75
    cohere_generate_text_request.top_k = 5
    cohere_generate_text_request.top_p = 0

    generate_text_detail = oci.generative_ai_inference.models.GenerateTextDetails()
    generate_text_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id="cohere.command")
    generate_text_detail.compartment_id = compartment_id
    generate_text_detail.inference_request = cohere_generate_text_request

    generate_text_response = generative_ai_inference_client.generate_text(generate_text_detail)

    llm_response_result = generate_text_response.data.inference_response.generated_texts[0].text

    return llm_response_result

# Perform RAG
def answer_user_question(org, query):
           
    question_list = []
    question_list.append(query)
           
    embed_text_response = generate_embeddings_for_question(question_list)

    question_vector = embed_text_response.data.embeddings[0]
        
    with connectMySQL(myconfig)as db:

        cursor = db.cursor()
        list_dict_docs = []
        #query vector db to search relevant records
        similar_docs = search_data(cursor, question_vector, list_dict_docs, org=org)

        rerank_docs = []
        for docs in similar_docs:
            content = str(docs.doc_id) + ": " + docs.doc_text
            rerank_docs.append(content)

        #use cohere reranker to fetch top documents.
        rerank_results = cohere_client.rerank(query=query, documents=rerank_docs, top_n=5, model='rerank-multilingual-v3.0', return_documents=True)

        #prepare documents for the prompt
        context_documents = []
        relevant_doc_ids = []
        similar_docs_subset=[]

        myresult = rerank_results.results

        for rerank_result in myresult:
           my1 = rerank_result
           doc_data = rerank_result.document.text
           context_documents.append(doc_data)
           relevant_doc_ids.append(doc_data.split(":")[0])


        for docs in similar_docs:
            current_id = str(docs.doc_id)
            if current_id in relevant_doc_ids:
                similar_docs_subset.append(docs)


        context_document = "\n".join(context_documents)
        prompt_template = '''
        Text: {documents} \n
        Question: {question} \n
        Answer the question based on the text provided and also return the relevant document numbers where you found the answer. If the text doesn't contain the answer, reply that the answer is not available.
        '''

        prompt = prompt_template.format(question = query, documents = context_document)

        llm_response_result = query_llm_with_prompt(prompt)
        response = {}
        response['message'] = query
        response['text'] = llm_response_result
        response['documents'] = [{'id': doc.doc_id, 'snippet': doc.doc_text, 'url': doc.url } for doc in similar_docs_subset]

        return response



with st.form('my_form'):
    text = st.text_area('Question : :', 'What is MySQL HeatWave?')
    submitted = st.form_submit_button('Submit')

    if submitted:
        myans = answer_user_question(org, text)
        # print(myans)
        st.divider()
        st.write(myans['text'])
        st.divider()
        df = pd.DataFrame(myans['documents'])
        #st.write(myans['documents'])
        st.write(df)
    
