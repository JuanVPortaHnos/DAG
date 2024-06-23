from langchain_cohere import CohereEmbeddings
import os

def generate_embeddings(chunks, api_key):
    """Genera embeddings para los chunks utilizando Cohere."""
    os.environ["COHERE_API_KEY"] = api_key
    embeddings = CohereEmbeddings(model="embed-english-light-v3.0")
    chunk_embeddings = [embeddings.embed_documents([chunk]) for chunk in chunks]
    return chunk_embeddings

def ensure_flat_embedding(embedding):
    """Asegura que los embeddings sean listas planas de floats."""
    if isinstance(embedding[0], list):
        return [float(item) for sublist in embedding for item in sublist]
    else:
        return [float(item) for item in embedding]
