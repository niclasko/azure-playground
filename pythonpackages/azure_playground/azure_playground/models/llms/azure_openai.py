from typing import Any, Dict

from azure_playground.models.llms.openai import OpenAI


class AzureOpenAI(OpenAI):
    def __init__(self, endpoint: str, api_key: str, cache: bool = True) -> None:
        super().__init__(endpoint=endpoint, api_key=api_key, cache=cache)

    def _headers(self) -> Dict[str, Any]:
        return {
            "Content-Type": "application/json",
            "api-key": self.api_key,
        }
