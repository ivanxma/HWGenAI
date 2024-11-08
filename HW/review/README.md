#
# Reference data set : https://amazon-reviews-2023.github.io   where the Subscription_Boxes is used
#

1. load the data to db as JSON
```
mysqlsh <connectstring> --js

mysqlsh JS> util.importJson('Subscription_Boxes.jsonl', {schema:'reviewdb'})
```

2. create schema
```
CREATE TABLE `myreview` (
  `asin` varchar(20) DEFAULT NULL,
  `review_text` text,
  `title` varchar(256) DEFAULT NULL,
  `rating` decimal(5,2) DEFAULT NULL,
  `user_id` varchar(30) DEFAULT NULL,
  `review_timestamp` timestamp NULL DEFAULT NULL,
  `parent_asin` varchar(20) DEFAULT NULL,
  `helpful_vote` decimal(5,2) DEFAULT NULL,
  `verified_purchase` varchar(10) DEFAULT NULL,
  `myid` bigint NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`myid`)
) ENGINE=InnoDB
```

3. Insert data to myreview table with the JSON data
```
MySQL > insert into myreview select doc->>"$.asin", doc->>"$.text", doc->>"$.title", doc->>"$.rating", doc->>"$.user_id", from_unixtime(doc->>"$.timestamp"/1000), doc->>"$.parent_asign", doc->>"$.helpful_vote", doc->>"$.verified_purchase" from Subscription_Boxes;
```

