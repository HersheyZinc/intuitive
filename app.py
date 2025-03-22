import os
import openai
import faiss
import numpy as np

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
if openai.api_key is None:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")

# Sample corpus of documents
documents = [
    "Change management is a structured approach to transition individuals, teams, and organizations from a current state to a desired future state.",
    "The Prosci ADKAR model focuses on individual change with steps like Awareness, Desire, Knowledge, Ability, and Reinforcement.",
    "Kotter's 8-Step Change Model outlines a process for leading large-scale organizational change with steps from creating urgency to anchoring change in culture.",
    "Lewin's Change Management Model simplifies change into three stages: Unfreeze, Change, and Refreeze.",
    "The McKinsey 7-S Framework examines seven key factors in an organization: Strategy, Structure, Systems, Shared Values, Style, Staff, and Skills."
]

# Function to get an embedding for a text using OpenAI's Embedding API
def get_embedding(text: str) -> np.ndarray:
    response = openai.Embedding.create(
        input=[text],
        model="text-embedding-ada-002"
    )
    embedding = np.array(response['data'][0]['embedding'], dtype=np.float32)
    return embedding

# Build embeddings for our documents
print("Computing document embeddings...")
doc_embeddings = np.array([get_embedding(doc) for doc in documents])
dimension = doc_embeddings.shape[1]

# Build a FAISS index for similarity search
index = faiss.IndexFlatL2(dimension)
index.add(doc_embeddings)
print(f"Indexed {index.ntotal} documents.")

# Function to retrieve top k documents for a given query
def retrieve_documents(query: str, k: int = 3):
    query_embedding = get_embedding(query)
    query_embedding = np.expand_dims(query_embedding, axis=0)
    distances, indices = index.search(query_embedding, k)
    retrieved_docs = [documents[idx] for idx in indices[0]]
    return retrieved_docs

# Function to generate an answer with ChatGPT using retrieved context
def generate_answer(query: str, retrieved_docs: list):
    # Construct a prompt that includes the retrieved documents as context
    context = "\n\n".join(retrieved_docs)
    prompt = (
        "You are a helpful assistant. Use the following context to answer the question below.\n\n"
        "Context:\n"
        f"{context}\n\n"
        "Question:\n"
        f"{query}\n\n"
        "Answer:"
    )
    
    # Call the ChatGPT API (using gpt-3.5-turbo model)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a knowledgeable change management expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=300
    )
    
    answer = response.choices[0].message.content.strip()
    return answer

# Example usage
if __name__ == "__main__":
    user_query = "What are some effective models for implementing change management in an organization?"
    
    print("\nRetrieving relevant documents...")
    retrieved = retrieve_documents(user_query, k=3)
    for i, doc in enumerate(retrieved, 1):
        print(f"Document {i}: {doc}")
    
    print("\nGenerating answer with ChatGPT...\n")
    answer = generate_answer(user_query, retrieved)
    print("Answer:\n", answer)
