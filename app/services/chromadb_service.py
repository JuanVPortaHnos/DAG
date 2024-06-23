import chromadb
import uuid
from langchain_cohere import CohereEmbeddings
from app.services.embedding_service import ensure_flat_embedding

def save_to_chromadb(chunks, embeddings):
    """Guarda los chunks y sus embeddings en ChromaDB."""
    chroma_client = chromadb.Client()
    metadata_options = {
        "hnsw:space": "ip"
    }
    collection = chroma_client.get_or_create_collection(
        name="my_collection", metadata=metadata_options
    )
    for i, chunk in enumerate(chunks):
        uuid_name = str(uuid.uuid1())
        embedding = ensure_flat_embedding(embeddings[i])
        collection.add(ids=[uuid_name], documents=[chunk], embeddings=[embedding])

def query_chromadb(question, api_key):
    """Consulta ChromaDB para encontrar el contexto relevante a la pregunta."""
    embeddings = CohereEmbeddings(model="embed-english-light-v3.0")
    question_embedding = embeddings.embed_query(question)
    chroma_client = chromadb.Client()
    collection = chroma_client.get_or_create_collection(name="my_collection")
    context_response = collection.query(query_embeddings=[question_embedding], n_results=1)['documents'][0]
    return context_response[0] if context_response else "No se encontró contexto relevante."