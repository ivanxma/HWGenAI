<?php
session_start();

require_once 'HeatWaveRAG.php'; // Assuming your RAG class is in this file

// Initialize chat history if it doesn't exist
if (!isset($_SESSION['chat_history'])) {
    $_SESSION['chat_history'] = [];
}

if (isset($_POST['setConfiguration'])) {
    $_SESSION['host'] = $_POST['host'];
    $_SESSION['user'] = $_POST['user'];
    $_SESSION['password'] = $_POST['password'];
    $_SESSION['genai_db'] = $_POST['genai_db'];
    $_SESSION['llm'] = $_POST['llm'];
    $_SESSION['ncitations'] = $_POST['ncitations'];
}

// Handle form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST' && !empty($_POST['user_query'])) {
    $userQuery = $_POST['user_query'];
    $host = $_SESSION['host'];
    $user = $_SESSION['user'];
    $pass = $_SESSION['password'];
    $db = $_SESSION['genai_db'];
    $llm = $_SESSION['llm'];
    $ncitations = $_POST['ncitations'];
    
    try {
        $rag = new HeatWaveRAG($host, $user, $pass, $db, $llm, $ncitations);
        // $rag->loadModel(); // Call this once at the start of your application
        $response = $rag->runRAG($userQuery, $ncitations);
        $rag->close();

        // Add to chat history
	/*
        $_SESSION['chat_history'][] = [
            'query' => $userQuery,
            'response' => $response['text'],
            'citations' => $response['citations'] ?? []
        ];
	 */
	array_unshift($_SESSION['chat_history'], [
            'query' => $userQuery,
            'response' => $response['text'],
            'citations' => $response['citations']] 
   	 );
	// throw new Exception("session chat hsitory: " . $_SESSION['chat_history'][0]['query']);
    } catch (Exception $e) {
        $error = "An error occurred: " . $e->getMessage();
    }
}

// Clear chat history if requested
if (isset($_POST['clear_history'])) {
    $_SESSION['chat_history'] = [];
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HeatWave RAG Chat</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f4f4f4;
        }
        .container {
            max-width: 1024;
            margin: auto;
            background: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
        }

        .configuration {
            font-size: 0.5em;
            margin-top: 20px;
            margin-bottom: 20px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 5px;
            background-color: #fff;
        }

        .question {
            max-width: 1024;
            margin-bottom: 20px;
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 10px;
            background-color: #fff;
        }
        .chat-history {
            margin-top: 20px;
            margin-bottom: 20px;
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 10px;
            background-color: #fff;
        }
        .user-query {
            background-color: #e6f2ff;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        .ai-response {
            background-color: #f0f0f0;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        .citations {
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }
        form {
            display: flex;
            margin-top: 20px;
        }

	.mytext {
            flex-grow: 1;
            width: 100;
            padding: 10px 0px;
            font-size: 14px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }

        input[type="text"] {
            flex-grow: 1;
            padding: 1px 1px;
            font-size: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        input[type="submit"] {
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-left: 10px;
        }
        input[type="submit"]:hover {
            background-color: #45a049;
        }
        .clear-history {
            text-align: right;
            margin-top: 10px;
        }
        .clear-history input[type="submit"] {
            background-color: #f44336;
        }
        .clear-history input[type="submit"]:hover {
            background-color: #d32f2f;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>HeatWave RAG Chat</h1>
        
        <?php if (isset($error)): ?>
            <p style="color: red;"><?php echo $error; ?></p>
        <?php endif; ?>

        <form  method="post" action="">
            <!-- input type="text" name="user_query" placeholder="Ask a question..." required -->
            <label for="user_query">Ask a Question ...</label>
            <textarea id="user_query" name="user_query" rows="5" cols="160"></textarea>
	    <br/>
            n_citations : <input type=number value="3" name="ncitations" placeholder="n_citations" min="0" max=100 required>
            <input type="submit" value="Send">
        </form>


        <div class="chat-history">
            <?php foreach ($_SESSION['chat_history'] as $chat): ?>
                <div class="user-query">
                    <strong>You:</strong> <?php echo htmlspecialchars($chat['query']); ?>
                </div>
                <div class="ai-response">
                    <strong>AI:</strong> <?php echo nl2br(htmlspecialchars($chat['response'])); ?>
                    <?php if (!empty($chat['citations'])): ?>
                        <div class="citations">
                            <strong>Citations:</strong>
                            <ul>
                                <?php foreach ($chat['citations'] as $citation): ?>
                                    <li><?php echo htmlspecialchars($citation['segment']); ?> (Document: <?php echo htmlspecialchars($citation['document_name']); ?>)</li>
                                <?php endforeach; ?>
                            </ul>
                        </div>
                    <?php endif; ?>
                </div>
            <?php endforeach; ?>

            <form method="post" action="">
                <input type="submit" name="clear_history" value="Clear Chat History">
            </form>
        </div>

	<div class="configuration">
        <form name="configuration" method="post" action="">
            Host: <input type="text" name="host" placeholder="DB Host IP" required>
            User: <input type="text" name="user" placeholder="Username" required>
            Password : <input type="password" name="password" placeholder="password" required>
            Schema : <input type="text" name="genai_db" placeholder="DB" required>
            <label for="llm">Choose LLM : </label>
            <select id="llm" name="llm">
              <option value="mistral-7b-instruct-v1">mistral-7b-instruct-v1 (In-DB LLM)</option>
              <option value="llama3-8b-instruct-v1">llama3-8b-instruct-v1 (In-DB LLM)</option>
              <option value="cohere.command-r-plus">cohere.command-r-plus (OCI LLM)</option>
              <option value="cohere.command-r-16k">cohere.command-r-16k (OCI LLM)</option>
              <option value="meta.llama-3-70b-instruct" >meta.llama-3-70b-instruct (OCI LLM)</option>
            </select>
            <input type="submit" name="setConfiguration" value="Configure"/>
	</form>
	</div>
	<div class="listinfo">
<table border=1>
<td> Host :
<?php echo htmlspecialchars($_SESSION['host']);?>
</td>
<td> User :
<?php echo htmlspecialchars($_SESSION['user']);?>
</td>
<td> Vector Schema :
<?php echo htmlspecialchars($_SESSION['genai_db']);?>
</td>
<td> LLM :
<?php echo htmlspecialchars($_SESSION['llm']);?>
</td>
</table>
	</div>

    </div>
</body>
</html>
