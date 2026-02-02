
from typing import  List
import requests

class PersistentLLM:
    def __init__(self, model_name="llama3"):
        self.model_name = model_name
        self.memory: List[str] = []
        self.url = "http://localhost:11434/api/chat"
        print(f"[LLM] Connected to Ollama model '{self.model_name}'")

    def generate(self, prompt: str, n_memory: int = 20) -> str:
        # context = "\n".join(self.memory[-n_memory:])
        # full_prompt = f"{context}\nUser: {prompt}\nAssistant:"

        payload = {
            "model": self.model_name,
            "messages":[{"role":"user","content":prompt}],
            "stream": False
        }

        r = requests.post(self.url, json=payload)
        r.raise_for_status()

        response = r.json()["message"]["content"].strip()

        # update memory
        self.memory.append(f"User: {prompt}")
        self.memory.append(f"Assistant: {response}")

        return response