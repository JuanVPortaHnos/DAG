from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from docx import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_cohere import CohereEmbeddings
import chromadb
import uuid
import os
import cohere


# Inicializar la aplicación FastAPI
app = FastAPI()

# Modelo de datos para la solicitud
class UserQuestion(BaseModel):
    user_name: str
    question: str

# Configuraciones y preparación de recursos globales
API_KEY = "blrNVdjNdW9dbxfbU0F6D6kvyuJ4MmAZ7FgojsWd"
DOCUMENT_PATH = "data/documento.docx"

# Función para cargar y procesar el documento
def load_document(file_path: str) -> str:
    doc = Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

# Función para crear chunks de texto
def create_chunks(text: str):
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n"],
        chunk_size=400,
        chunk_overlap=50,
        length_function=len
    )
    return text_splitter.split_text(text)

# Función para generar embeddings
def generate_embeddings(chunks, api_key):
    os.environ["COHERE_API_KEY"] = api_key
    embeddings = CohereEmbeddings(model="embed-english-light-v3.0")
    chunk_embeddings = [embeddings.embed_documents([chunk]) for chunk in chunks]
    return chunk_embeddings

# Función para asegurar que los embeddings sean listas planas de floats
def ensure_flat_embedding(embedding):
    if isinstance(embedding[0], list):
        return [float(item) for sublist in embedding for item in sublist]
    else:
        return [float(item) for item in embedding]

# Función para guardar en ChromaDB
def save_to_chromadb(chunks, embeddings):
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

# Función para consultar ChromaDB
def query_chromadb(question, api_key):
    embeddings = CohereEmbeddings(model="embed-english-light-v3.0")
    question_embedding = embeddings.embed_query(question)
    chroma_client = chromadb.Client()
    collection = chroma_client.get_or_create_collection(name="my_collection")
    context_response = collection.query(query_embeddings=[question_embedding], n_results=1)['documents'][0]
    return context_response[0] if context_response else "No se encontró contexto relevante."

# Función para obtener respuesta del modelo Cohere
def get_cohere_response(prompt, api_key, max_tokens=50, temperature=0):
    co = cohere.Client(api_key=api_key)
    response = co.generate(
        model="command",
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature
    )
    return response.generations[0].text

# Configuración inicial
document_text = load_document(DOCUMENT_PATH)
chunks = create_chunks(document_text)
chunk_embeddings = generate_embeddings(chunks, API_KEY)
save_to_chromadb(chunks, chunk_embeddings)

# Punto final de la API
@app.post("/ask/")
async def ask_question(user_question: UserQuestion):
    try:
        question = user_question.question
        context = query_chromadb(question, API_KEY)
        
        # Consultar el idioma de la pregunta
        message_idioma = f"cual es el idioma de la siguiente pregunta?: {question}, devuelve como response unicamente el idioma "
        idioma = get_cohere_response(message_idioma, API_KEY, max_tokens=10, temperature=0).strip()

        if "Spanish" in idioma:
            idioma = "Spanish"
            context_translate = context
        else:
            idioma = "English" 
            message_translate = f"traduce el siguiente contexto: {context} al idioma {idioma}."
            context_translate = get_cohere_response(message_translate, API_KEY)
        
        # Generar la respuesta final
        prompt = f"Pregunta: {question}\nContexto: {context_translate}\nResponde a la pregunta en una sola oración corta, sin saltos de linea, en el idioma {idioma}, utilizando emojis que resuman el contenido y respondiendo en tercera persona."
        answer = get_cohere_response(prompt, API_KEY)
        
        return {
            "user_name": user_question.user_name,
            "question": question,
            "context": context_translate,
            "answer": answer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

