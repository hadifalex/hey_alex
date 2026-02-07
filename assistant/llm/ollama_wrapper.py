
from typing import  List
import requests

class PersistentLLM:
    def __init__(self, model_name="llama3",profile: dict = None):
        self.model_name = model_name
        self.memory: List[str] = []                     # list of {"role":..., "content":...}
        self.url = "http://localhost:11434/api/chat"
        print(f"[LLM] Connected to Ollama model '{self.model_name}'")

        # Preload memory with system/assistant personality if provided
        if profile is not None:
            system_prompt = profile.get("system_prompt", "")
            if system_prompt:
                self.memory.append({"role": "system", "content": system_prompt})
                

    def generate(self, user_text: str, profile: dict, n_memory: int = 20) -> str:
        # context = "\n".join(self.memory[-n_memory:])
        # full_prompt = f"{context}\nUser: {prompt}\nAssistant:"

        history_messages = self.memory[-n_memory:]  # always store the last 20 conversations or so to give a semblance of memory

        payload = {
            "model": self.model_name,
            "messages":[
        {"role": "system", "content": profile.get("system_prompt","")},
        *history_messages,
        {"role": "user", "content": user_text}
        ],
            "stream": False
        }

        r = requests.post(self.url, json=payload)
        r.raise_for_status()

        response = r.json()["message"]["content"].strip()

        # update memory
        self.memory.append({"role": "user", "content": user_text})
        self.memory.append({"role": "assistant", "content": response})

        return response