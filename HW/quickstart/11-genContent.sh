. ./comm.sh
mysql -t -u$USER -p -h$HOST -P$PORT << EOL
call sys.ML_MODEL_LOAD("mistral-7b-instruct-v1", NULL);

set @query="Write an article on Artificial intelligence in 300 words.";
select @mytext := sys.ML_GENERATE(@query, JSON_OBJECT("task", "generation", "model_id", "mistral-7b-instruct-v1", "language", "en")) ;

select JSON_PRETTY(@mytext), length(@mytext), char_length(@mytext );
EOL
