DROP PROCEDURE IF EXISTS SUMMARIZE_TRANSLATE;
CREATE PROCEDURE SUMMARIZE_TRANSLATE(
  IN mytitle VARCHAR(200),
  IN mylanguage VARCHAR(64)
) 
BEGIN
  set group_concat_max_len=327680;
  SELECT group_concat(review_text) into @all_reviews FROM myreview group by title having title = mytitle limit 1;

  select JSON_EXTRACT(sys.ML_GENERATE(@all_reviews, JSON_OBJECT('task', 'summarization', 'max_tokens', 800, 'model_id', 'llama3-8b-instruct-v1', 'language', mylanguage)), "$.text")  summary;
END
$$;

