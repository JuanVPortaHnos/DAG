from fastapi import APIRouter, HTTPException
from app.models import UserQuestion
from app.services.document_service import load_document, create_chunks
from app.services.embedding_service import generate_embeddings
from app.services.chromadb_service import save_to_chromadb, query_chromadb
from app.services.cohere_service import get_cohere_response
from app.config import API_KEY, DOCUMENT_PATH

router = APIRouter()

# Configuración inicial
document_text = load_document(DOCUMENT_PATH)
chunks = create_chunks(document_text)
chunk_embeddings = generate_embeddings(chunks, API_KEY)
save_to_chromadb(chunks, chunk_embeddings)

@router.post("/ask/")
async def ask_question(user_question: UserQuestion):
    """Endpoint para responder a la pregunta del usuario."""
    try:
        question = user_question.question
        context = query_chromadb(question, API_KEY)
        
        # Consultar el idioma de la pregunta
        message_idioma = f"Cual es el idioma de la siguiente pregunta?: {question}, devuelve como response unicamente el idioma "
        idioma = get_cohere_response(message_idioma, API_KEY, max_tokens=10, temperature=0).strip()

        if "Spanish" in idioma:
            idioma = "Spanish"
            context_translate = context
        else:
            idioma = "English" 
            message_translate = f"Traduce el siguiente contexto: {context} al idioma {idioma}."
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
