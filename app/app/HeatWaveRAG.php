<?php

class HeatWaveRAG {
    private $conn;
    private $vectorStore = 'genai_db.livelab_embedding_pdf';
    private $vectorSchema = 'quickstart_db';
    private $llm = "mistral-7b-instruct-v1";
    private $ncitations = 5;

    public function __construct($host, $user, $password, $database, $xllm, $xncitations) {
        $this->conn = new mysqli($host, $user, $password, $database);
        if ($this->conn->connect_error) {
            die("Connection failed: " . $this->conn->connect_error);
        }
        $this->vectorSchema = $database;
	$this->llm = $xllm;
	$this->ncitations = $xncitations;
    }

    public function loadModel() {
    	if (!$this->modelLoaded) {
        	$query = "CALL sys.ML_MODEL_LOAD('" . $this->llm . "', NULL)";
        	$result = $this->conn->query($query);
        	if ($result === false) {
            		throw new Exception("Failed to load model: " . $this->llm . $this->conn->error);
        	}
        	$this->modelLoaded = true;
    	}
    }

    public function runRAG($userQuery, $xncitations) {
        // Set the options
        // $optionsQuery = "SET @options = JSON_OBJECT('vector_store', JSON_ARRAY('{$this->vectorStore}'))";
        $optionsQuery = "SET @options = JSON_OBJECT('schema', JSON_ARRAY('{$this->vectorSchema}'), 'n_citations', {$xncitations}, 'model_options',JSON_OBJECT('model_id', '{$this->llm}'))";
        // throw new Exception("testing " . $optionsQuery);
        $this->conn->query($optionsQuery);
        
        // Set the query
        $escapedQuery = $this->conn->real_escape_string($userQuery);
        $querySetQuery = "SET @query = '$escapedQuery'";
        $this->conn->query($querySetQuery);
        
        // Run the RAG procedure
        $ragQuery = "CALL sys.ML_RAG(@query, @output, @options)";
        $this->conn->query($ragQuery);
        
        // Fetch the result
        $resultQuery = "SELECT JSON_PRETTY(@output) AS result";
        $result = $this->conn->query($resultQuery);
        
        if ($result === false) {
            throw new Exception("Query failed: " . $this->conn->error);
        }
        
        $row = $result->fetch_assoc();
        return json_decode($row['result'], true);
    }

    public function close() {
        $this->conn->close();
    }
}

