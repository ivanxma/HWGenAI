import streamlit as st
from PIL import Image
import base64
import io
import mysql.connector
import globalvar
from mydbtools import *
import json

# MySQL Connectoin Profile
myconfig = globalvar.myconfig


def answer_query_on_image(aquestion, allm, aimage):
           
   with connectMySQL(myconfig) as db:

   	cursor = db.cursor()
   	myquery = """
   	select sys.ML_GENERATE("{question}", JSON_OBJECT("model_id", "{llm}", "image", "{image_base64}"));
   	""".format(question=aquestion, llm=allm, image_base64=aimage)
   	print(myquery)
   	llm_response_result = runSQL(myquery,db)
   	return llm_response_result




    
# Set title
st.title("📷 Image Upload + Base64 App")

# File uploader
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Open image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Convert image to base64
    buffered = io.BytesIO()
    image.save(buffered, format=image.format or "PNG")
    img_bytes = buffered.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode()

    # Display the base64 string (optional)
    with st.expander("📄 Show Base64 String"):
        st.code(img_base64, language='text')

    # Now you can use `img_base64` variable as needed
    ans = answer_query_on_image("Describe the image", "meta.llama-3.2-90b-vision-instruct", img_base64)
    response_json = json.loads(ans[0][0])
    with st.expander("Describe the image"):
        st.text_area("The image", response_json['text'], 400)

else:
    st.info("Please upload an image file.")




