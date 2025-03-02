import json
from typing import Any


class LLMOutputDecoder:
    @classmethod
    def decode(cls, output: str) -> Any:
        return cls._to_json(output) or output

    @classmethod
    def _to_json(cls, output: str) -> Any:
        prepared: str = output.replace("```json\n", "").replace("```", "")
        try:
            return json.loads(prepared)
        except json.JSONDecodeError:
            return None
