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
n_citations = globalvar.citations
emb_modelid = globalvar.emb_modelid
compartment_id = globalvar.compartment_id
CONFIG_PROFILE = globalvar.CONFIG_PROFILE
headers = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.47"}


# MySQL Connectoin Profile
myconfig = globalvar.myconfig

# Used to connect to MySQL
def connectMySQL(myconfig) :
    cnx = mysql.connector.connect(**myconfig)
    return cnx

# Data Preperation - Chunking
def parse_and_chunk_url_text(source_url):

    formatted_url = source_url.strip()
    chunks = []

    try:
        elements = partition_html(url=formatted_url, headers=headers, skip_headers_and_footers=True)

    except  Exception as error:

        print("Error while attempting to crawl {site} : ".format(site=formatted_url), error)

    else:

        chunks = chunk_by_title(elements)

    finally:

        return chunks


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



# OCI-LLM: Used to prompt the LLM
def query_llm_with_prompt(cursor, prompt, allm):

    newprompt = prompt.replace('"', "'")
    cursor.execute( """
        select sys.ML_GENERATE("{query}", JSON_OBJECT("task", "generation", "model_id", "{myllm}", "max_tokens", 4000) )
    """.format(query=newprompt,myllm=allm))

    data = cursor.fetchall()
    
    return data[0][0]



# Perform RAG
def summarize_url(org, content, myllm):
           
           
    with connectMySQL(myconfig)as db:

        cursor = db.cursor()


        prompt_template = '''
        Text: {documents} \n
        Summarize the Text provided. 
        '''

        prompt = prompt_template.format( documents = content)

        llm_response_result = query_llm_with_prompt(cursor, prompt, myllm)
        response = {}
        response_json = json.loads(llm_response_result)
        response['text'] = response_json['text']


        return response



with st.form('my_form'):
    myurl = st.text_area('Please put in URL : :', 'https://en.wikipedia.org/wiki/MySQL')
    myllm = st.selectbox('Choose LLM : ',
      ("mistral-7b-instruct-v1", "llama3-8b-instruct-v1", "llama3-8b-instruct-v1",  "meta.llama-3.2-90b-vision-instruct", "meta.llama-3.3-70b-instruct", "cohere.command-r-08-2024", "cohere.command-r-plus-08-2024" ))
    submitted = st.form_submit_button('Submit')

    if submitted:
        organized_content = parse_and_chunk_url_text(myurl)
        # clean data
        contents = []
    
        for chunk in organized_content:
    
            text = chunk.text
            text = clean(text, extra_whitespace=True)
            contents.append(text)
    
        myans = summarize_url(mydb, contents, myllm)
        st.divider()
        st.write(myans['text'])
        st.divider()
    
