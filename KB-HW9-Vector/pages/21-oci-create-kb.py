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
mydb = globalvar.mydb
compartment_id = globalvar.compartment_id
CONFIG_PROFILE = "DEFAULT"

config = oci.config.from_file('~/.oci/config', CONFIG_PROFILE)

# Service endpoint
endpoint = globalvar.endpoint

headers = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.47"}
myconfig = globalvar.myconfig

# Functions to interact with DB

def connectMySQL(myconfig):
    cnx = mysql.connector.connect(**myconfig)
    return cnx
    

def create_table(cursor, amydb):
    try:

        cursor.execute("""
            create table if not exists {db}.web_embeddings (
                id bigint unsigned auto_increment,
                content varchar(4000),
                source_url varchar(4000),
		vec vector(2048) null,
                primary key (id)
            )""".format(db=amydb))

        cursor.execute("""
            drop table if exists {db}.web_embeddings_trx 
            """.format(db=amydb))

        cursor.execute("""
            create table if not exists {db}.web_embeddings_trx (
                id bigint unsigned,
                content varchar(4000),
                primary key (id)
            )""".format(db=amydb))

    except Exception as error :
        print("Error while creating table for {db}".format(db=amydb), error)

def insert_data(cursor, chunk, source_url, amydb):
    try:  
        mydata = ( chunk, source_url)
        result = cursor.execute("INSERT INTO {db}.web_embeddings (content, source_url) VALUES (%s, %s)".format(db=amydb), mydata)
        # connection.commit()

    except Exception as error:
        print("Error while inserting in DB : ", error)

def get_last_id(cursor, amydb ):
    last_id = 0 
    try:  
        result = cursor.execute("SELECT max(id) from {db}.web_embeddings".format(db=amydb))
        data = cursor.fetchall()
        if (data is None) :
          last_id = 0
        else :
          last_id = data[0][0]

    except Exception as error:
        print("Error getting lastid  : ", error)

    return last_id

def call_embed_sp(cursor, amydb, aid):
    try:  

        result = cursor.execute("insert into {db}.web_embeddings_trx(id, content) SELECT id, content from {db}.web_embeddings where id > {last_id}".format(db=amydb, last_id=aid))
        result = cursor.execute("""
           call sys.ML_EMBED_TABLE("{db}.web_embeddings_trx.content", "{db}.web_embeddings_trx.vec", JSON_OBJECT("model_id", "multilingual-e5-small"))
        """.format(db=amydb))
        result = cursor.execute("update {db}.web_embeddings a, {db}.web_embeddings_trx b set a.vec = b.vec where a.id = b.id".format(db=amydb))

        # connection.commit()

    except Exception as error:
        print("Error calling embedding SPs: ", error)

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

def create_knowledge_base_from_client_content(amydb, contents, myurl):

    connection = connectMySQL(myconfig)
    cursor = connection.cursor()
    create_table(cursor=cursor, amydb = amydb)
    print("creating embeddings for {db}".format(db=amydb))
    len_of_contents = len(contents)

    start = 0

    last_id = get_last_id(cursor, amydb)
    if (last_id is None) :
       last_id = 0

    while start < len_of_contents:

        content_subsets = contents[start:start+96]
        inputs = []

        for subset in content_subsets:
            if subset:
                inputs.append(subset)

        for i in range(len(inputs)):
            insert_data(cursor,  inputs[i], myurl, amydb)

        start = start + 96
        

    connection.commit()

    call_embed_sp(cursor, amydb, last_id)

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
        mydata = create_knowledge_base_from_client_content(mydb, contents, myurl)
        st.divider()
        # st.write(mydata)
        cnx = connectMySQL(myconfig)
        try :
            result = runSQL("SELECT source_url, count(*) from {db}.web_embeddings group by source_url".format(db=mydb), cnx)
            df = pd.DataFrame(result)
            st.write(df)
 
        except mysql.connector.Error as error :
            st.info("executing SQL error : {}".format(error))
        cnx.close()
	
    
