import cohere
import faiss
import numpy as np
import globalvar

# Initialize the Cohere client
cohere_client = cohere.Client(globalvar.COHERE_API_KEY)

# Example documents
documents = [
    "Paris is the capital of France.",
    "Berlin is the capital of Germany.",
    "Madrid is the capital of Spain."
]

# Function to get embeddings using Cohere
def get_embeddings(docs):
    response = cohere_client.embed(
        texts=docs,
        model='large'  # or any other model available in Cohere
    )
    return np.array(response.embeddings, dtype='float32')

# Get embeddings for the documents
embeddings = get_embeddings(documents)
print(embeddings)
# Create and populate the FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# Save the document texts with their corresponding vectors
doc_store = {i: doc for i, doc in enumerate(documents)}
print(doc_store)
# Retrieve function
def retrieve(query, index, doc_store, top_k=2):
    query_embedding = get_embeddings([query])[0].reshape(1, -1)

    # Search for the most similar documents
    distances, indices = index.search(query_embedding, top_k)

    # Retrieve the actual documents
    retrieved_docs = [doc_store[i] for i in indices[0]]
    return retrieved_docs

# Generate response function using Cohere
def generate_response(query, retrieved_docs, cohere_client):
    # Concatenate the query and retrieved documents
    context = " ".join(retrieved_docs)
    input_text = f"Context: {context}\nQuery: {query}\nAnswer:"

    # Generate the response
    response = cohere_client.generate(
        model='command-light',  # or any other model available in Cohere
        prompt=input_text,
	temperature=0.1,
        max_tokens=50  # Adjust max tokens as needed
    )
    return response.generations[0].text.strip()

# Query and get response
query = "What is the capital of France?"
retrieved_docs = retrieve(query, index, doc_store)
response = generate_response(query, retrieved_docs, cohere_client)
print("**********************")
print("Query : ", query)
print("Retrieved Documents:", retrieved_docs)
print("Generated Response:", response)
