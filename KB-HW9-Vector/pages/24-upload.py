import os
import pandas as pd
import streamlit as st
import json
from streamlit_file_browser import st_file_browser

from unstructured.partition.html import partition_html
from unstructured.chunking.title import chunk_by_title
from unstructured.cleaners.core import clean

from oci.config import from_file
from oci.object_storage import ObjectStorageClient
from oci.exceptions import ServiceError

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


# OCI-LLM: Used to prompt the LLM
def query_llm_with_prompt(cursor, prompt, allm):

    newprompt = prompt.replace('"', "'")
    cursor.execute( """
        select sys.ML_GENERATE("{query}", JSON_OBJECT("task", "generation", "model_id", "{myllm}", "max_tokens", 4000) )
    """.format(query=newprompt,myllm=allm))

    data = cursor.fetchall()
    
    return data[0][0]



           
def vector_store_load(cursor, abucket,anamespace,afolder,aobjectnames, aschema, atable, adesc) :

    call_string = '''
      call sys.VECTOR_STORE_LOAD(
      'oci://{bucket}@{namespace}/{folder}/{objectnames}',  '
      '''.format(bucket=abucket,namespace=anamespace,folder=afolder,objectnames=aobjectnames ) + '{' + '''
      "schema_name": "{schema}", "table_name": "{table}", "description": "{desc}"
      '''.format(schema=aschema, table=atable, desc=adesc) + "}')"


    print(call_string)
           
    cursor.execute( 'create database if not exists {dbname}'.format(dbname=aschema))

    datasets = []
    for rs in cursor.execute( call_string, multi=True  ) :
      data = cursor.fetchall()
      datasets.append(data)

    return datasets


def upload_to_oci_object_storage(aprofile, afile, bucket_name, object_name):
    # Load the configuration from the default location (~/.oci/config)
    config = from_file(profile_name=aprofile)

    # Define namespace and bucket name
    mynamespace = config['namespace']  # Tenancy ID is used as the namespace

    # Create an ObjectStorageClient instance
    client = ObjectStorageClient(config)

    try:
        with afile as file:
            # Upload the file
            response = client.put_object(anamespace, bucket_name, object_name, file)
            print(response)
            # print(f"Upload successful. ETag: {response.etag}")
            return True
    except ServiceError as e:
        print(f"Service error: {e}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


with st.form('my_form'):
    col1, col2, col3 = st.columns(3)
    with col1 :
      myschema = st.text_input('Vector Store Schema :', 'mydb')
    with col2 :
      mytable = st.text_input('Vector Store table :', 'mytable')
    with col3 :
      mymodel = st.selectbox('Choose embed model : ', ("minilm", "multilingual-e5-small"))

    
    col1, col2,col3 = st.columns(3)
    with col1 :
      mybucket = st.text_input('Object Storage Bucket :', 'myhw')
    with col2 :
      myfolder = st.text_input('Folder:', 'mypdf')
    with col3 :
      myprofile = st.text_input('OCI config profile:', 'london-mysqleu')

    uploaded_files = st.file_uploader(
        "Choose a (CSV,PDF,HTML,DOC,PPT) file", accept_multiple_files=True
    )
    submitted = st.form_submit_button('Submit')

    if submitted:
        # Load the configuration from the default location (~/.oci/config)
        config = from_file(profile_name=myprofile)

        # Define namespace and bucket name
        mynamespace = config['namespace']  # Tenancy ID is used as the namespace
        for uploaded_file in uploaded_files:
            print(uploaded_file.name)
            object_name = myfolder + '/' + uploaded_file.name
            if upload_to_oci_object_storage(myprofile, uploaded_file, mybucket, object_name) :
               print('uploaded successful')

        with connectMySQL(myconfig)as db:
          cursor = db.cursor()
          myans = vector_store_load(cursor, mybucket, mynamespace, myfolder, '*', myschema, mytable, "uploaded for testing")
          st.write(myans)
    
