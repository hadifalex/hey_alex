from typing import List

import requests


class PersistentLLM:
    """Thin wrapper around a local Ollama server that remembers the conversation."""

    def __init__(self, model_name="llama3", profile: dict = None,
                 keep_alive="30m", timeout=180, max_memory=40):
        """
        :param model_name: the Ollama model to use (must already be pulled)
        :param profile: the personality profile (used for the system prompt)
        :param keep_alive: how long Ollama keeps the model loaded in RAM while idle.
                           Ollama's default is 5 minutes; after that the next question
                           has to wait for the model to load again (slow on a Pi).
        :param timeout: seconds to wait for an answer before giving up
        :param max_memory: maximum number of messages kept in memory (2 per exchange)
        """
        self.model_name = model_name
        self.url = "http://localhost:11434/api/chat"
        self.generate_url = "http://localhost:11434/api/generate"
        self.keep_alive = keep_alive
        self.timeout = timeout
        self.max_memory = max_memory
        self.system_prompt = (profile or {}).get("system_prompt", "")

        # conversation history: a list of {"role": "user"/"assistant", "content": ...}
        # (the system prompt is NOT stored here; it is added fresh on every request)
        self.memory: List[dict] = []

        print(f"[LLM] Connected to Ollama model '{self.model_name}'")

    def warm_up(self):
        """Load the model into memory now, so the first real question is fast."""
        try:
            requests.post(
                self.generate_url,
                json={"model": self.model_name, "keep_alive": self.keep_alive},
                timeout=(5, self.timeout),
            )
        except requests.exceptions.RequestException as e:
            print(f"[LLM] Warm-up failed: {e}")

    def generate(self, user_text: str, profile: dict = None, n_memory: int = 20) -> str:
        """
        Ask the model for a reply.

        :param n_memory: how many of the most recent messages to send as context
                         (20 messages = about 10 back-and-forth exchanges).
                         n_memory=0 makes it a one-shot question: no history is sent
                         and nothing is saved to memory.
        """
        system_prompt = (profile or {}).get("system_prompt", self.system_prompt)
        one_shot = n_memory <= 0
        history = [] if one_shot else self.memory[-n_memory:]

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                *history,
                {"role": "user", "content": user_text},
            ],
            "stream": False,
            "keep_alive": self.keep_alive,
        }

        try:
            r = requests.post(self.url, json=payload, timeout=(5, self.timeout))
            r.raise_for_status()
            response = r.json()["message"]["content"].strip()

        except requests.exceptions.ConnectionError:
            print("[LLM] Can't reach Ollama at localhost:11434. Is it running?")
            return "Hmm, my brain isn't answering right now."
        except requests.exceptions.Timeout:
            print(f"[LLM] No answer after {self.timeout}s.")
            return "Sorry, I took too long thinking about that one."
        except requests.exceptions.HTTPError as e:
            print(f"[LLM] Ollama returned an error: {e}")
            print(f"[LLM] Is the model installed? Try: ollama pull {self.model_name}")
            return "Hmm, something went wrong in my head."
        except (KeyError, ValueError) as e:
            print(f"[LLM] Unexpected reply from Ollama: {e}")
            return "Hmm, something went wrong in my head."

        # update memory (only for normal questions, and only when it worked)
        if not one_shot:
            self.memory.append({"role": "user", "content": user_text})
            self.memory.append({"role": "assistant", "content": response})
            self.memory = self.memory[-self.max_memory:]

        return response