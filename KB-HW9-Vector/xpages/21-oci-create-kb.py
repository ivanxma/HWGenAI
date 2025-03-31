import os
import pandas as pd
import streamlit as st

from unstructured.partition.html import partition_html
from unstructured.chunking.title import chunk_by_title
from unstructured.cleaners.core import clean

import oci
import mysql.connector

import globalvar

# Constants
org = globalvar.org
compartment_id = globalvar.compartment_id
CONFIG_PROFILE = "DEFAULT"

config = oci.config.from_file('~/.oci/config', CONFIG_PROFILE)

# Service endpoint
endpoint = globalvar.endpoint

generative_ai_inference_client = oci.generative_ai_inference.GenerativeAiInferenceClient(config=config, service_endpoint=endpoint, retry_strategy=oci.retry.NoneRetryStrategy(), timeout=(10,240))

headers = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.47"}

myconfig = globalvar.myconfig

# Functions to interact with DB

def connectMySQL(myconfig):
    cnx = mysql.connector.connect(**myconfig)
    return cnx
    


def create_table(cursor, org):
    
    
#    try:
#     
#        cursor.execute("""
#            drop table if exists {test}.web_embeddings;
#        """.format(test = org))
#
#    except Exception as error:
#        print("Error dropping table for {org} : ".format(org=org), error)
#   

    try:

        cursor.execute("""

            create table if not exists {org}.web_embeddings (
                id bigint unsigned auto_increment,
                content varchar(4000),
                vec vector(1024),
                source_url varchar(4000),
                primary key (id)
            )""".format(org=org))

    except:

        print("Error while creating table for {org}".format(org=org))


def insert_data(cursor, chunk, vec, source_url, org):

    try:  
        myvec2 = "; ".join(str(x) for x in vec)
        myvec = myvec2[:1024]
        myvectorStr = ','.join(str(item) for item in vec)
        myvectorStr = '[' + myvectorStr + ']'

        mydata = ( chunk, myvectorStr, source_url)
        result = cursor.execute("INSERT INTO {org}.web_embeddings (content, vec, source_url) VALUES (%s,string_to_vector(%s), %s)".format(org=org), mydata)

        # connection.commit()

    except Exception as error:

        print("Error while inserting in DB : ", error)

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

def runSQL(theSQL, cnx) :
    cursor = cnx.cursor()
    try :
        cursor.execute(theSQL)
        data = cursor.fetchall()
        return data
    
    except mysql.connector.Error as error:
        print("executing SQL failure : {}".format(error))
        st.info("executing SQL error : {}".format(error))
    finally:
            if cnx.is_connected():
                cursor.close()
        

# Data Preperation - Embedding

def create_knowledge_base_from_client_content(org, contents, myurl):

    connection = connectMySQL(myconfig)
    cursor = connection.cursor()
    create_table(cursor=cursor, org = org)
    print("creating embeddings for {org}".format(org=org))
    len_of_contents = len(contents)

    start = 0
    cursor_index = 0

    while start < len_of_contents:

        embed_text_detail = oci.generative_ai_inference.models.EmbedTextDetails()
        content_subsets = contents[start:start+96]
        inputs = []

        for subset in content_subsets:
            if subset:
                inputs.append(subset)

        embed_text_detail.inputs = inputs
        embed_text_detail.truncate = embed_text_detail.TRUNCATE_END
        embed_text_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id="cohere.embed-multilingual-v3.0")
        embed_text_detail.compartment_id = compartment_id
        embed_text_detail.input_type = embed_text_detail.INPUT_TYPE_SEARCH_DOCUMENT

        try:

            embed_text_response = generative_ai_inference_client.embed_text(embed_text_detail)

        except Exception as e:

            print("Error while creating embeddings ", e)
            embeddings = []
            return(f"Error while creating embedding {e}")

        else:

            embeddings = embed_text_response.data.embeddings

        for i in range(len(inputs)):
            insert_data(cursor,  inputs[i], list(embeddings[i]), myurl, org)

        start = start + 96

    connection.commit()
    cursor.close()
    connection.close()
    return(f"len of contents is {len_of_contents}")


# Main Function
print("name: ", __name__)

with st.form('my_form'):
    myurl = st.text_area('Please put in URL : :', 'https://en.wikipedia.org/wiki/MySQL')
    submitted = st.form_submit_button('Submit')

    if submitted:
        organized_content = parse_and_chunk_url_text(myurl)
        # clean data
        contents = []
    
        for chunk in organized_content:
    
            text = chunk.text
            text = clean(text, extra_whitespace=True)
            contents.append(text)
    
        # prepare knowledge base
        mydata = create_knowledge_base_from_client_content(org, contents, myurl)
        st.divider()
        # st.write(mydata)
        cnx = connectMySQL(myconfig)
        try :
            result = runSQL(f"SELECT source_url, count(*) from {org}.web_embeddings group by source_url", cnx)
            df = pd.DataFrame(result)
            st.write(df)
 
        except mysql.connector.Error as error :
            st.info("executing SQL error : {}".format(error))
        cnx.close()
	
    
