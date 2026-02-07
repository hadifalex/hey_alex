import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def ask_llm(prompt: str)->str:

    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
        }

    r = requests.post(OLLAMA_URL, json=payload,timeout=120)
    data = r.json()

    return data.get("response","").strip()
