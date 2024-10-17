. ./comm.sh
mysql -u$USER -p -h$HOST -P$PORT << EOL

select mysql_task_management_ensure_schema();

create database if not exists quickstart;

drop table if exists quickstart.quickstart_embeddings;

call sys.VECTOR_STORE_LOAD('oci://HWdatalake@idazzjlcjqzj/genai/heatwave-gen-ai-getting-started.en.pdf', '{"schema_name": "quickstart", "table_name": "quickstart_embeddings"}');


EOL
