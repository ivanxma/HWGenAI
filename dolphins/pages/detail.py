import streamlit as st
from mydb import *
import globalvar
import json

myconfig = globalvar.myconfig
ml_generate_options = {'max_tokens', 'temperature', 'top_k', 'top_p', 'repeat_penalty', 'frequency_penalty', 'presence_penalty'  }
st.set_page_config(layout='centered')
st.subheader('Detail Page')

itemid = st.session_state['itemid']
modelid = st.session_state['model_id']
mloptions = st.session_state['mloptions']
context = st.session_state['context']
query = st.session_state['query']


result = get_product_detail(itemid)
myrows = result['rows']
print(myrows)
descr = myrows[0][2]
print(context)
newcontext = context.format(descr)


answer = query_llm_with_prompt( myconfig, query, newcontext, modelid, mloptions, ml_generate_options)

myanswer = json.loads(answer)
st.write(myanswer["text"])
st.write(result)


