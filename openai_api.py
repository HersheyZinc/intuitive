from dotenv import load_dotenv
from openai import OpenAI
import numpy as np
import faiss
load_dotenv(override=True)
CLIENT = OpenAI()


def openai_query(messages, model="gpt-4o-mini", temperature=0, max_tokens=4096):

    response = CLIENT.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    reply = response.choices[0].message.content

    return reply


def openai_query_stream(messages, model="gpt-4o-mini", temperature=0, max_tokens=4096):

    response = CLIENT.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        stream=True,  # Enable streaming
    )

    for chunk in response:
        content = chunk.choices[0].delta.content
        if not content:
            continue
        yield content


def get_top_k_documents(query_embedding, document_embeddings, k=5):

    # Convert embeddings to numpy arrays
    query_embedding = np.array(query_embedding).astype('float32')
    document_embeddings = np.array(document_embeddings).astype('float32')

    # Create a FAISS index
    index = faiss.IndexFlatL2(document_embeddings.shape[1])
    index.add(document_embeddings)

    # Search for the top k nearest neighbors
    _, indices = index.search(query_embedding.reshape(1, -1), k)
    
    return indices.flatten().tolist()


def rag_query(messages, document_embeddings, k=5, model="gpt-4o-mini", temperature=0, max_tokens=4096):
    # Get the last message as the usr query
    query = messages[-1]["content"]

    # get the query embeddings
    query_embedding = CLIENT.embeddings.create(input=query, model="text-embedding-ada-002")['data'][0]['embedding']
    
    # Use faiss similarity function to get the top k relevant documents
    top_k_indices = get_top_k_documents(query_embedding, document_embeddings, k)
    
    # Append each document to the chat history
    for idx in top_k_indices:
        document_content = document_embeddings[idx] 
        messages.append({"role": "system", "content": document_content})
    
    # Call the OpenAI API
    reply = openai_query(messages, model=model, temperature=temperature, max_tokens=max_tokens)
    
    return reply
