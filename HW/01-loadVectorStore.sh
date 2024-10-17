SET @dl_tables = '[{"db_name": "vector_store", "tables": [{"table_name": "mygenai", "dialect": {"format": "pdf"}, "file": [{"namespace":"idazzjlcjqzj", "bucket":"HWdatalake", "name": "genai/heatwave-gen-ai-getting-started.en.pdf", "region":"us-ashburn-1"}]}]}]';
SET @options = JSON_OBJECT( 'policy', 'disable_unsupported_columns', 'external_tables', CAST(@dl_tables AS JSON));
call sys.heatwave_load(@dl_tables, @options);

SET @dl_tables = '[{"db_name": "vector_store", "tables": [{"table_name": "mygenai_pdf", "dialect": {"format": "pdf"}, "file": [{"namespace":"idazzjlcjqzj", "bucket":"HWdatalake", "prefix": "genai/", "region":"us-ashburn-1"}]}]}]';
SET @options = JSON_OBJECT( 'policy', 'disable_unsupported_columns', 'external_tables', CAST(@dl_tables AS JSON));

SET @dl_tables = '[{"db_name": "vector_store", "tables": [{"table_name": "mygenai_html", "dialect": {"format": "html"}, "file": [{"namespace":"idazzjlcjqzj", "bucket":"HWdatalake", "prefix": "genai/", "region":"us-ashburn-1"}]}]}]';
SET @options = JSON_OBJECT( 'policy', 'disable_unsupported_columns', 'external_tables', CAST(@dl_tables AS JSON));

SET @dl_tables = '[{"db_name": "vector_store", "tables": [{"table_name": "mygenai_html3", 
	"engine_attribute": { 
		"dialect": {"format": "html", "language" : "en"},
		"file": [{"namespace":"idazzjlcjqzj", "bucket":"HWdatalake", "prefix": "genai/", "region":"us-ashburn-1"}]
	}}]}]';
SET @options = JSON_OBJECT( 'policy', 'disable_unsupported_columns', 'external_tables', CAST(@dl_tables AS JSON));
call sys.heatwave_load(@dl_tables, @options);


select * from performance_schema.error_log where error_code not in ('MY-010914','MY-014051', 'MY-013694');
