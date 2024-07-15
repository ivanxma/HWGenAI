import cohere 
import globalvar

co = cohere.Client(
  api_key=globalvar.COHERE_API_KEY
) 

stream = co.chat_stream( 
  model='command-r-plus',
  message='Please tell me more about the Oracle Cloud Infrastructure versus AWS',
  temperature=0.3,
  chat_history=[{"role": "User", "message": "Can you give me a global market overview of the solar panels?"}],
  prompt_truncation='AUTO',
  connectors=[{"id":"web-search"}]
) 

for event in stream:
  if event.event_type == "text-generation":
    print(event.text, end='')
