-- https://objectstorage.uk-london-1.oraclecloud.com/p/KhiNmaq2c8tORrjYQxQNFpqTPeAkcimZsKXf4uK4tA4LQCk7IEtR6vL1pcWusrXh/n/idazzjlcjqzj/b/LONDON_BUCKET/o/

create database if not exists mydemo;
drop table if exists mydemo.error_log;
drop table if exists vec_error_log;
create table mydemo.error_log engine=innodb secondary_engine=rapid select * from performance_schema.error_log;
alter table mydemo.error_log secondary_load;

select * from mydemo.errorlog into outfile with parameters '{ "file": [{"par":
"https://the PAR for the bucket/",
"prefix":"errorlog/"}],"dialect": { "format": "csv", "has_header" : true }}';


call sys.VECTOR_STORE_LOAD("https://objectstorage.uk-london-1.oraclecloud.com/p/KhiNmaq2c8tORrjYQxQNFpqTPeAkcimZsKXf4uK4tA4LQCk7IEtR6vL1pcWusrXh/n/idazzjlcjqzj/b/LONDON_BUCKET/o/errorlog/", JSON_OBJECT('schema_name', 'mydemo', 'table_name', 'vec_error_log'));

