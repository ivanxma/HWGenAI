# It is HW GenAI reference 
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

To run
- change to the folder
- execute
```
streamlit run main.py
```

Reference :
. https://blogs.oracle.com/ai-and-datascience/post/how-to-build-a-rag-solution-using-oci-generative-ai
