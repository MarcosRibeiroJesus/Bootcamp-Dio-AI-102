import os
import requests
import logging
import time
from typing import List


class Translator:
    def __init__(self, endpoint: str, api_key: str, deployment: str, max_chars_per_chunk: int = 3000):
        self.endpoint = endpoint.rstrip("/") if endpoint else None
        self.api_key = api_key
        self.deployment = deployment
        self.max_chars = max_chars_per_chunk

    def _build_url(self) -> str:
        # Azure OpenAI chat completions endpoint pattern
        # e.g. https://<resource-name>.openai.azure.com/openai/deployments/<deployment>/chat/completions?api-version=2023-10-01-preview
        return f"{self.endpoint}/openai/deployments/{self.deployment}/chat/completions?api-version=2023-10-01-preview"

    def _call_api(self, messages: List[dict]) -> str:
        url = self._build_url()
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key,
        }
        payload = {
            "messages": messages,
            "max_tokens": 1500,
            "temperature": 0.3,
            "top_p": 0.95,
        }

        # simple retry logic
        last_exc = None
        for attempt in range(4):
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=60)
                resp.raise_for_status()
                data = resp.json()
                # expect choices[0].message.content
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                logging.warning("Azure OpenAI request failed (attempt %s): %s", attempt + 1, str(e))
                last_exc = e
                time.sleep(2 ** attempt)
        raise last_exc

    def _chunk_text(self, text: str) -> List[str]:
        text = text.strip()
        if len(text) <= self.max_chars:
            return [text]
        parts = []
        start = 0
        while start < len(text):
            end = min(start + self.max_chars, len(text))
            # try to break at newline or space
            if end < len(text):
                last_nl = text.rfind("\n", start, end)
                if last_nl > start:
                    end = last_nl
                else:
                    last_space = text.rfind(" ", start, end)
                    if last_space > start:
                        end = last_space
            parts.append(text[start:end].strip())
            start = end
        return parts

    def translate_text(self, text: str, target_lang: str) -> str:
        """Translate potentially long text by chunking and joining results."""
        if not text:
            return ""
        chunks = self._chunk_text(text)
        translations = []
        for i, chunk in enumerate(chunks):
            system = {
                "role": "system",
                "content": [
                    {"type": "text", "text": "You are a professional translator. Return only the translated text in markdown format."}
                ],
            }
            user = {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Translate the following text to {target_lang}:\n\n{chunk}"}
                ],
            }
            content = self._call_api([system, user])
            translations.append(content)
        return "\n\n".join(translations)
