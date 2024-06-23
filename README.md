Pasos para Ejecutar el Servidor Localmente
Primero, clona este repositorio en tu máquina local:
git clone git@github.com:JuanVPortaHnos/DAG.git
cd DAG

Configurar el Entorno Virtual
Se recomienda usar un entorno virtual para manejar las dependencias del proyecto. Puedes crear y activar uno con los siguientes comandos:

python -m venv Environment
.\Environment\Scripts\activate

Instalar dependencias:
Instala todas las dependencias del proyecto utilizando el archivo requirements.txt:
pip install -r requirements.txt

Ejecutar el servidor localmente:
Navega al directorio donde está main.py y ejecuta:
uvicorn main:app --reload

Usando Postman
1. Abre Postman y crea una nueva solicitud.
2. Configura la solicitud como POST.
3. Establece la URL a http://127.0.0.1:8000/ask/.
4. En la sección "Body", selecciona "raw" y elige "JSON" en el menú desplegable.
5. Introduce el JSON:
{
    "user_name": "Juan Vaca",
    "question": "What is the name of the magical flower?"
}
6. Haz clic en "Send".
