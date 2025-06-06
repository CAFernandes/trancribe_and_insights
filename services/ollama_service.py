# Serviço para interagir com o servidor Ollama para geração de insights
import requests
import json
from config import OLLAMA_BASE_URL

def is_ollama_available():
    """
    Verifica se o serviço Ollama está disponível.
    Retorna True se disponível, False caso contrário.
    """
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException:
        return False

def get_available_ollama_models():
    """
    Obtém a lista de modelos disponíveis no Ollama.
    Retorna: (lista_modelos, conectado, quantidade_modelos)
    """
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
        response.raise_for_status()
        models_data = response.json()
        model_names = [model['name'] for model in models_data.get('models', [])]
        return model_names, True, len(model_names)
    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar com Ollama: {e}")
        return [], False, 0

def generate_ollama_insights(text, prompt_template, model_name):
    """
    Gera insights usando o modelo Ollama especificado.

    Args:
        text: Texto para análise
        prompt_template: Template do prompt (deve conter {{text}})
        model_name: Nome do modelo Ollama

    Returns:
        (resposta, erro) - Tupla com resposta ou None, e mensagem de erro ou None
    """
    ollama_models, ollama_connected, _ = get_available_ollama_models()
    if not ollama_connected:
        return None, "Ollama não está acessível."
    if model_name not in ollama_models:
        return None, f"Modelo Ollama '{model_name}' não encontrado."

    prompt = prompt_template.replace("{{text}}", text)
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={"model": model_name, "prompt": prompt, "stream": False}
        )
        response.raise_for_status()
        response_data = response.json()
        return response_data.get("response", "").strip(), None
    except requests.exceptions.RequestException as e:
        return None, f"Erro ao gerar insights com Ollama: {e}"
    except json.JSONDecodeError:
        return None, "Erro ao decodificar a resposta do Ollama (não JSON)."
