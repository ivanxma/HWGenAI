import streamlit as st
import pandas as pd
import globalvar

# # NLP pkgs
# import spacy
# from spacy import displacy
# nlp = spacy.load('en')

# Database Functions
from mydb import *

from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')


# Avatar Image using a url
avatar1 ="https://www.w3schools.com/howto/img_avatar1.png"
avatar2 ="https://www.w3schools.com/howto/img_avatar2.png"

# Reading Time
def readingTime(mytext):
	total_words = len([ token for token in mytext.split(" ")])
	estimatedTime = total_words/200.0
	return estimatedTime

def analyze_text(text):
	return nlp(text)

# Layout Templates
review_message_temp = """
	<div style="background-color:#464e5f;padding:10px;border-radius:10px;margin:10px;">
	<h6><TABLE border=1><tr><td>Review Summary</td></tr><tr><td>{}</td></tr></TABLE>
	</div>
	"""
title_temp ="""
	<div style="background-color:#464e5f;padding:10px;border-radius:10px;margin:10px;">
	<h5 style="color:white;text-align:center;">{}</h5>
	<table>
	<td>
	<img src="https://www.w3schools.com/howto/img_avatar.png" alt="Avatar" style="vertical-align: middle;float:left;width: 50px;height: 50px;border-radius: 50%;" >
	</td>
	<td>User:{}</td>
	<td>{}</td>
	</table>
	</div>
	"""
article_temp ="""
	<div style="background-color:#464e5f;padding:10px;border-radius:5px;margin:10px;">
	<h5 style="color:white;text-align:center;">{}</h5>
	<h6>User:{}</h6> 
	<h6>Post Date: {}</h6>
	<img src="https://www.w3schools.com/howto/img_avatar.png" alt="Avatar" style="vertical-align: middle;width: 50px;height: 50px;border-radius: 50%;" >
	<br/>
	<br/>
	<p style="text-align:justify">{}</p>
	</div>
	"""
head_message_temp ="""
	<div style="background-color:#464e5f;padding:10px;border-radius:5px;margin:10px;">
	<h5 style="color:white;text-align:center;">{}</h5>
	<img src="https://www.w3schools.com/howto/img_avatar.png" alt="Avatar" style="vertical-align: middle;float:left;width: 50px;height: 50px;border-radius: 50%;">
	<h6>User: {}</h6> 		
	<h6>Product : {}</h6>		
	<h6>Post Date: {}</h6>		
	</div>
	"""
full_message_temp ="""
	<div style="background-color:silver;overflow-x: auto; padding:10px;border-radius:5px;margin:10px;">
		<p style="text-align:justify;color:black;padding:10px">Review Comment : {}</p>
	</div>
	"""

HTML_WRAPPER = """<div style="overflow-x: auto; border: 1px solid #e6e9ef; border-radius: 0.25rem; padding: 1rem">{}</div>"""


langChoices = {"en": "English", "de": "German", "fr": "French", "hi": "Hindi", "it": "Italian", "pt": "Portugues", "es": "Spanish", "th": "Thai"}

llmChoices = {"mistral-7b-instruct-v1": "mistral-7b-instruct-v1 (In-DB LLM)", "llama3-8b-instruct-v1": "llama3-8b-instruct-v1 (In-DB LLM)", "cohere.command-r-08-2024": "cohere.command-r-08-2024 (OCI LLM)", "cohere.command-r-plus-08-2024": "cohere.command-r-plus-08-2024 (OCI LLM)", "meta.llama-3.1-70b-instruct": "meta.llama-3.1-70b-instruct (OCI LLM)", "meta.llama-3.1-405b-instruct": "meta.llama-3.1-405b-instruct (OCI LLM)"}

def format_lang_func(option):
    return langChoices[option]

def format_llm_func(option):
    return llmChoices[option]

def main():
	"""A Simple CRUD Review App"""
	html_temp = """
		<div style="background-color:{};padding:10px;border-radius:10px">
		<h4 style="color:{};text-align:center;">HeatWave GenAI Demo - Review Summarization</h4>
		</div>
		"""
	st.markdown(html_temp.format('royalblue','white'),unsafe_allow_html=True)
		

	menu = ["Home","Show Reviews","Add Review","Search","Manage Review"]
	choice = st.sidebar.selectbox("Menu",menu)

	if choice == "Home":
		st.subheader("Home")		
		result = view_all_notes()
		for i in result:
			# short_article = str(i[2])[0:int(len(i[2])/2)]
			short_article = str(i[2])[0:50]
			st.write(title_temp.format(i[0],i[1],short_article),unsafe_allow_html=True)

		# st.write(result)
	elif choice == "Show Reviews":
		st.subheader("Reviews")
		all_titlesx = view_all_titles()
		all_titles = [i[0] for i in all_titlesx]
		postlist = st.sidebar.selectbox("Products",all_titles)
		langoption = st.selectbox(
			"Languages",
			options=list(langChoices.keys()), 
			format_func=format_lang_func
		)
		llmoption = st.selectbox(
			"LLM",
			options=list(llmChoices.keys()), 
			format_func=format_llm_func
		)
		st.text("")
		if st.button("GenAI Summarize"):
			review_summary = get_review_summary_by_title(postlist, langoption, llmoption)
			st.markdown(review_message_temp.format(review_summary), unsafe_allow_html=True)
		post_result = get_review_by_title(postlist)
		for i in post_result:
			st.markdown(head_message_temp.format(i[0],i[1],i[2], i[3]),unsafe_allow_html=True)
			st.markdown(full_message_temp.format(i[4]),unsafe_allow_html=True)
			# if st.button("GenAI Summarize"):
				# review_summary = get_review_summary_by_title(postlist)
				# st.markdown(review_message_temp.format(review_summary), unsafe_allow_html=True)
			 	# docx = analyze_text(i[2])
			 	# html = displacy.render(docx,style="ent")
			 	# html = html.replace("\n\n","\n")
			 	# st.write(HTML_WRAPPER.format(html),unsafe_allow_html=True)

			


	elif choice == "Add Review":
		st.subheader("Add Your Review")
		review_asin  = st.text_input('Enter Product ID')
		review_title = st.text_input('Enter Product Description')
		review_user_id = st.text_input("Enter User ID",max_chars=50)
		review_text = st.text_area("Enter Your Message",height=200)
		review_post_date = st.date_input("Post Date")
		if st.button("Add"):
			add_data(review_user_id,review_asin, review_title, review_text,review_post_date)
			st.success("Post::'{}' Saved".format(review_title))


	elif choice == "Search":
		st.subheader("Search Review")
		search_term = st.text_input("Enter Term")
		search_choice = st.radio("Field to Search",("title","user_id"))
		if st.button('Search'):
			if search_choice == "title":
				article_result = get_review_by_title(search_term)
			elif search_choice =="user_id":
				article_result = get_review_by_user_id(search_term)
			
			# Preview Articles
			for i in article_result:
				st.text("Reading Time:{} minutes".format(readingTime(str(i[2]))))
				# st.write(article_temp.format(i[1],i[0],i[3],i[2]),unsafe_allow_html=True)
				st.write(head_message_temp.format(i[0],i[1],i[2], i[3]),unsafe_allow_html=True)
				# st.write(head_message_temp.format(i[1],i[0],i[3]),unsafe_allow_html=True)
				st.write(full_message_temp.format(i[4]),unsafe_allow_html=True)
			

	elif choice == "Manage Review":
		st.subheader("Manage Review")
		result = view_all_notes()
		clean_db = pd.DataFrame(result,columns=["ASIN", "User ID","Product","Review","Rating","Date"])
		st.dataframe(clean_db)
		unique_list = [i[0] for i in view_all_titles()]
		delete_by_title =  st.selectbox("Select Product",unique_list)
		if st.button("Delete"):
			delete_data(delete_by_title)
			st.warning("Deleted: '{}'".format(delete_by_title))

		if st.checkbox("Metrics"):
			new_df = clean_db
			new_df['Length'] = new_df['Review'].str.len() 
			st.dataframe(new_df)
			# st.dataframe(new_df['User ID'].value_counts())
			st.subheader("User Stats")
			fig, ax = plt.subplots()
			new_df['User ID'].value_counts().plot(kind='bar')
			st.pyplot(fig)

			fig, ax = plt.subplots()
			new_df['User ID'].value_counts().plot.pie(autopct="%1.1f%%")
			st.pyplot(fig)

		if st.checkbox("WordCloud"):
			# text = clean_db['Review'].iloc[0]
			st.subheader("Word Cloud")
			text = ', '.join(clean_db['Review'])
			# Create and generate a word cloud image:
			wordcloud = WordCloud().generate(text)

			# Display the generated image:
			plt.imshow(wordcloud, interpolation='bilinear')
			fig, ax = plt.subplots()
			plt.axis("off")
			st.pyplot(fig)

		if st.checkbox("BarH Plot"):
				fig, ax = plt.subplots()
				st.subheader("Length of Review")
				new_df = clean_db
				new_df['Length'] = new_df['Review'].str.len() 
				barh_plot = new_df.plot.barh(x='User ID',y='Length',figsize=(10,10))
				st.write(barh_plot)
				st.pyplot(fig)



if __name__ == '__main__':
	main()
