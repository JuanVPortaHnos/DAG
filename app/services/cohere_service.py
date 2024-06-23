import cohere

def get_cohere_response(prompt, api_key, max_tokens=50, temperature=0):
    """Obtiene una respuesta del modelo de Cohere basado en el prompt proporcionado."""
    co = cohere.Client(api_key=api_key)
    response = co.generate(
        model="command",
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature
    )
    return response.generations[0].text