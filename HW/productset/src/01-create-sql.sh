
USER=
PASWWORD=
HOST=
PORT=3306

wget https://github.com/etano/productner/raw/refs/heads/master/Product%20Dataset.csv

iconv -f ISO-8859-1 -t UTF-8 ProductDataset.csv > p.csv

mysql -u$USER -$PASSWORD -h$HOST -P$PORT << EOL
create database if not exists productdb;
create table if not exists productdb.products (product_id int not null primary key, product_name varchar(80) not null, product_description text, price decimal(20,2)) engine=innodb secondary_engine=rapid;
EOL

mysqlsh -u$USER -$PASSWORD -h$HOST -P$PORT << EOL
util.importTable('p.csv', {schema:'productdb', table:'products', skipRows:1, dialect:'csv-unix'})
alter table productdb.products secondary_load;
EOL

mysql -u$USER -$PASSWORD -h$HOST -P$PORT << EOL
call sys.ML_EMBED_TABLE('productdb.products.product_description', 'productdb.products_embedding.vector_embedding', JSON_OBJECT("model_id", "all_minilm_l12_v2")) ;
alter table productdb.products_embedding secondary_engine=rapid;
alter table productdb.products_embedding secondary_load;
EOL


mysql -u$USER -$PASSWORD -h$HOST -P$PORT < sp.sql
call sys.ML_EMBED_TABLE('productdb.products.product_description', 'productdb.products_embedding.vector_embedding', JSON_OBJECT("model_id", "all_minilm_l12_v2")) ;
