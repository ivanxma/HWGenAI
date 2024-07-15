# It is HW GenAI demo 
#

The KB-HW-Vector code uses HeatWave 9.0 on OCI with Vector datatype and Vector functions with OCI Generative AI capability to parse web pages into segments.  
Using OCI embedding model to convert the page into vector which is stored in HeatWave (Table : web_embeddings).  

Pre-requisite :
- install streamlit - https://docs.streamlit.io/get-started/installation
  - example :
```
pip install streamlit
```
- using python 3.9 (or after)

- COHERE_API_KEY is used for rerank GenAI to provide more relevant docs 


Change the global variable (globalvar.py)
- Using the globalvar.example.py as sample
```
cp globalvar.example.py globalvar.py
```
- Update the corresponding VARs with actual env details

## FOLDER : KB-HW-Vector
To run
- change to the folder KB-HW-Vector
- execute
```
streamlit run main.py
```
## FOLDER : langchain

It is about using langchain to run with MySQL using llm.
Use streamlit to run

## FOLDER cohere

It is the demo python script to run with cohere API
Run with python3.9+

Reference :
. https://blogs.oracle.com/ai-and-datascience/post/how-to-build-a-rag-solution-using-oci-generative-ai


