from pydantic import BaseModel

# Modelo de datos para la solicitud
class UserQuestion(BaseModel):
    user_name: str
    question: str
