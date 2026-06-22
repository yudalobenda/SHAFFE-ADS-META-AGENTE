import os

from anthropic import Anthropic

DEFAULT_MODEL = "claude-sonnet-4-6"


class ClaudeClient:
    def __init__(self, api_key: str | None = None, model: str = DEFAULT_MODEL):
        self.client = Anthropic(api_key=api_key or os.environ["ANTHROPIC_API_KEY"])
        self.model = model

    def ask(self, prompt: str, system: str | None = None, max_tokens: int = 1024) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system or "",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
