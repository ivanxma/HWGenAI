. ./comm.sh
mysql -t -u$USER -p -h$HOST -P$PORT << EOL

set @chat_options='{"tables": [{"table_name": "quickstart_embeddings", "schema_name": "quickstart"}], "model_options": {"model_id": "mistral-7b-instruct-v1"}}';
call sys.HEATWAVE_CHAT("What is HeatWave AutoML?");

select JSON_PRETTY(@chat_options);

call sys.HEATWAVE_CHAT("How to set it up?");
select JSON_PRETTY(@chat_options);

EOL
