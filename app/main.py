from fastapi import FastAPI
from app.api import endpoints

# Inicializar la aplicación FastAPI
app = FastAPI()

# Incluir las rutas de la API
app.include_router(endpoints.router)
