use productdb;
drop function get_similar_products;
delimiter $$
create function get_similar_products( question varchar(1024) ) returns JSON
begin
	-- set @vstore=JSON_ARRAY("productdb.products");
	SELECT sys.ML_EMBED_ROW(question, JSON_OBJECT("model_id", 'all_minilm_l12_v2')) INTO @input_embedding;
	set @output = (select JSON_ARRAYAGG(
		JSON_OBJECT( "product_id", product_id,
			"product_name", product_name,
			"distance", distance))
		from (
			select products.product_id, product_name, product_description,vector_distance(@input_embedding, vector_embedding, 'COSINE') distance 
			from productdb.products, productdb.products_embedding 
			where products.product_id = products_embedding.product_id
			order by distance asc
			limit 5) x);
	return @output;
end
$$
delimiter ;
drop function get_similar_product_list;
delimiter $$
create procedure  get_similar_product_list( IN question varchar(1024) )
begin
	-- set @vstore=JSON_ARRAY("productdb.products");
	SELECT sys.ML_EMBED_ROW(question, JSON_OBJECT("model_id", 'all_minilm_l12_v2')) INTO @input_embedding;
	
	select products.product_id, product_name, product_description,vector_distance(@input_embedding, vector_embedding, 'COSINE') distance 
	from productdb.products, productdb.products_embedding 
	where products.product_id = products_embedding.product_id
	order by distance asc
	limit 5;
end
$$
delimiter ;
