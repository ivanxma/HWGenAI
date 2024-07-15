import os
from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_cohere import CohereEmbeddings
from langchain_cohere import ChatCohere
from langchain.chains import create_sql_query_chain
from langchain_community.utilities import SQLDatabase
import mysql.connector
#from json2table import convert
import pandas as pd
import globalvar

import streamlit as st

os.environ['COHERE_API_KEY'] = globalvar.COHERE_API_KEY

def getSQL(query) :
    if (query.find("```sql") != -1) :
        myquery = query.split("```sql")[1].split("```")[0]
    else :
        myquery = query
    return myquery


def connectMySQL(myconfig) : 
    cnx = mysql.connector.connect(**myconfig)
    return cnx

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
    


st.title('🦜🔗 SQL Query Chain App')

#cohere_api_key = st.sidebar.text_input('Cohere API Key', type='password')


def generate_response(input_text, db):
    # llm = ChatCohere(model="command", temperature=0)
    # db_chain = SQLDatabaseChain.from_llm(llm=llm, db=db, verbose=True)
    # st.info(db_chain.invoke(input_text))
    st.divider()
    theSQL = chain.invoke({"question": input_text})
    st.info(theSQL)
    return theSQL


examples = [
    {
        "input": "List all employees.", 
        "query": "SELECT * FROM employees.employees;"},
    {
        "input": "Find all managers'.",
        "query": "SELECT * FROM employees where Name = 'AC/DC');",
    },
    {
        "input": "List all tracks in the 'Rock' genre.",
        "query": "SELECT * FROM Track WHERE GenreId = (SELECT GenreId FROM Genre WHERE Name = 'Rock');",
    },
    {
        "input": "Find the total duration of all tracks.",
        "query": "SELECT SUM(Milliseconds) FROM Track;",
    },
    {
        "input": "List all customers from Canada.",
        "query": "SELECT * FROM Customer WHERE Country = 'Canada';",
    },
    {
        "input": "How many tracks are there in the album with ID 5?",
        "query": "SELECT COUNT(*) FROM Track WHERE AlbumId = 5;",
    },
    {
        "input": "Find the total number of invoices.",
        "query": "SELECT COUNT(*) FROM Invoice;",
    },
    {
        "input": "List all tracks that are longer than 5 minutes.",
        "query": "SELECT * FROM Track WHERE Milliseconds > 300000;",
    },
    {
        "input": "Who are the top 5 customers by total purchase?",
        "query": "SELECT CustomerId, SUM(Total) AS TotalPurchase FROM Invoice GROUP BY CustomerId ORDER BY TotalPurchase DESC LIMIT 5;",
    },
    {
        "input": "Which albums are from the year 2000?",
        "query": "SELECT * FROM Album WHERE strftime('%Y', ReleaseDate) = '2000';",
    },
    {
        "input": "How many employees are there",
        "query": 'SELECT COUNT(*) FROM "Employee"',
    },
]


from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate

example_prompt = PromptTemplate.from_template("User input: {input}\nSQL query: {query}")
prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix="You are a MySQL expert. Given an input question, create a syntactically correct MySQL query to run. Unless otherwise specificed, do not return more than {top_k} rows.\n\nHere is the relevant table info: {table_info}\n\nBelow are a number of examples of questions and their corresponding SQL queries.",
    suffix="User input: {input}\nSQL query: ",
    input_variables=["input", "top_k", "table_info"],
)

llm = ChatCohere(model="command-r", temperature=0.0)

example_selector = SemanticSimilarityExampleSelector.from_examples(
    examples,
    CohereEmbeddings(),
    FAISS,
    k=5,
    input_keys=["input"],
)

db_user=globalvar.myconfig['user']
db_password=globalvar.myconfig['password']
db_host=globalvar.myconfig['host']
db_port=globalvar.myconfig['port']
db_name='employees'

db = SQLDatabase.from_uri(f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}", 
    include_tables= ["employees", "departments",   "salaries", "titles",  "dept_emp", "dept_manager"],
    sample_rows_in_table_info=2, view_support=False)

chain = create_sql_query_chain(llm, db, prompt)
# chain.get_prompts()[0].pretty_print()



myconfig = {
    "user":"myroot",
    "password":"MySQL8.0",
    "host":"127.0.0.1",
    "port":3340,
    "database": "employees"
}

cnx = connectMySQL(myconfig)

with st.form('my_form'):
    text = st.text_area('Your question : :', 'How many employees are there?')
    submitted = st.form_submit_button('Submit')
    #if submitted and cohere_api_key.startswith('sk-'):
        #generate_response(text)
    if submitted:
        theSQL = generate_response(text, db)
        theSQL = getSQL(theSQL)
        mydata = runSQL(theSQL,cnx)
        df = pd.DataFrame(mydata)
        #myhtml=convert(json.loads(mydata))
        st.write(df)

cnx.close()
	

