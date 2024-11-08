import streamlit as st
import pandas as pd
import globalvar
import json

# # NLP pkgs
# import spacy
# from spacy import displacy
# nlp = spacy.load('en')

# Database Functions
from mydb import *


def format_lang_func(option):
    return langChoices[option]

def main():
	"""A Simple CRUD Review App"""
	html_temp = """
		<div style="background-color:{};padding:10px;border-radius:10px">
		<h4 style="color:{};text-align:center;">HeatWave GenAI Demo - Vector Simularity Search</h4>
		</div>
		"""
	st.markdown(html_temp.format('royalblue','white'),unsafe_allow_html=True)
		

	menu = ["Home","Search"]
	choice = st.sidebar.selectbox("Menu",menu)

	if choice == "Home":
		st.subheader("Home")		
		result = view_all_products()
		clean_db = pd.DataFrame(result,columns=["ID", "Product","Description","Price"])
		st.dataframe(clean_db)
	elif choice == "Search":
		st.subheader("Search Products")
		question = st.text_input('Enter Question')
		if st.button("GenAI Simularity Search"):
			mylist = get_similar_products(question)
			st.dataframe(pd.DataFrame( mylist, columns=["ID", "Product","Description","Price"]))



if __name__ == '__main__':
	main()
