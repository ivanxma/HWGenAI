import os
import pandas as pd
import streamlit as st

import oci
import mysql.connector

import globalvar
from mydb import *

# Constants
mydb = globalvar.mydb
myconfig = globalvar.myconfig


ml_generate_options = {'max_tokens', 'temperature', 'top_k', 'top_p', 'repeat_penalty', 'frequency_penalty', 'presence_penalty'  }

llms_data = get_generation_llms()
print (llms_data)

llm_map = {
  "mistral-7b-instruct-v1": "mistral-7b-instruct-v1(in-DB LLM)",
  "llama3-8b-instruct-v1": "llama3-8b-instruct-v1 (in-DB LLM)",
  "meta.llama-3.2-90b-vision-instruct": "meta.llama-3.2-90b-vision-instruct (OCI LLM)",
  "meta.llama-3.3-70b-instruct": "meta.llama-3.3-70b-instruct (OCI LLM)",
  "cohere.command-r-08-2024": "cohere.command-r-08-2024 (OCI LLM)",
  "cohere.command-r-plus-08-2024" : "cohere.command-r-plus-08-2024 (OCI LLM)"
}

myoptions = {}
myoptions["temperature"] = 0
myoptions["max_tokens"] = 4000
if "mloptions" in st.session_state :
   mloptions = st.session_state['mloptions']
else :     
   mloptions = myoptions

st.session_state['mloptions'] = mloptions

# Functions to interact with DB

def start_app():
    st.empty()

    menu = ["Home"]
    choice = st.sidebar.selectbox("Menu",menu)

    myllm = st.selectbox('Choose LLM : ',
      ("mistral-7b-instruct-v1", "llama3-8b-instruct-v1",  "meta.llama-3.2-90b-vision-instruct", "meta.llama-3.3-70b-instruct", "cohere.command-r-08-2024", "cohere.command-r-plus-08-2024" ), format_func=llm_map.get)

    myprompt = st.text_input('Instruction:', 'Rephrase the context with nice and attractive wordings and response Only with Output format with [New Description(Category)].')
    mytemplate = st.text_area('Context:', 'Description : {}')

    if choice == "Home":
        st.subheader("Product list")
        result = get_product_list()
        clean_db = pd.DataFrame(result['rows'], columns=result['colnames'])
        event = st.dataframe( clean_db, on_select='rerun', selection_mode='single-row')
        if len(event.selection['rows']):
          selected_row = event.selection['rows'][0]

          print(selected_row)
          itemid=clean_db.iloc[selected_row]['itemid']

          st.session_state['itemid'] = itemid
          st.session_state['model_id'] = myllm
          st.session_state['model_id'] = myllm
          st.session_state['context'] = mytemplate
          st.session_state['query'] = myprompt

          st.page_link('pages/detail.py', label=f'Goto {itemid} Page', icon='🗺️')
        # st.dataframe(clean_db)

        container1 = st.container(border=True)
        col0, col1,col2,col3,col4 = container1.columns(5)
        col0.text("Options")
        option = col1.selectbox("options ", tuple(ml_generate_options), label_visibility='collapsed')
        option_value = col2.number_input("Value", 0, label_visibility='collapsed')
        add_button = col3.button('add', use_container_width=True)
        reset_button = col4.button('reset', use_container_width=True)
        
        if add_button:
            myvalue = {option: option_value}
            mloptions.update(myvalue)
            st.session_state['mloptions'] = mloptions
            col0.write(mloptions)
              
        if reset_button:
            mloptions = myoptions
            st.session_state['mloptions'] = mloptions
            col0.empty()
            col0.write(mloptions)


def main():
    # You can put your main app content here
    # st.write("You are logged in!")
    start_app()


# Main Function
print("name: ", __name__)
start_app()

    
