import json
from enum import Enum
from json import JSONDecodeError
from typing import Any, Dict, Optional, Type, cast

from azure_playground.utils.llm_output_decoder import LLMOutputDecoder
from pydantic import BaseModel, ValidationError

SCHEMA_PLACEHOLDER: str = "{schema}"


class Status(Enum):
    SUCCESS = "success"
    FAILURE = "failure"


class Response(BaseModel):
    status: Status = Status.SUCCESS
    message: str = "Success"


class Instruction(BaseModel):
    text: str
    response_schema: Optional[Type[BaseModel]] = None

    def instantiate(self, **kwargs: Any) -> str:
        if self.response_schema is None:
            return self.text
        schema: Dict[str, Any] = self.response_schema.model_json_schema()
        return self.text.format(schema=json.dumps(schema.get("example", schema)), **kwargs)

    def parse(self, response: str) -> BaseModel:
        if self.response_schema is None:
            return BaseModel()
        try:
            decoded: Dict[str, Any] = cast(Dict[str, Any], LLMOutputDecoder.decode(response))
            return self.response_schema.model_validate(decoded)
        except (ValidationError, JSONDecodeError) as e:
            return Response(status=Status.FAILURE, message=str(e))
