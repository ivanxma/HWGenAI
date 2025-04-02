import streamlit as st
def main():
    st.header("HeatWave Vector Store with OCI GenAI")   
    st.divider()
    st.write("This is a DEMO using HeatWave 9.2.2 on OCI")
    st.write("The \"Create KB from URL\" page is to fetch URL content and creats embedding vector into MySQL Vector Store")
    st.write("The \"Search KB \" page is to use the GenAI to generate answer from the KB vector store in MySQL")
    st.write("The \"Summarize \" page is to fetch URL content and summarize")
    st.divider()

            
if __name__ == '__main__':
      main()
