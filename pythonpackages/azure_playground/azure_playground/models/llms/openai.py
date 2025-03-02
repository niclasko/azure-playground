from enum import Enum
from typing import Any, Dict, List, Optional, Union

from azure_playground.models.llms.llm import LLM, LLMData, LLMResponse
from pydantic import BaseModel

ENDPOINT_URL: str = "https://api.openai.com/v1/chat/completions"


class OpenAIModel(Enum):
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4_TURBO = "gpt-4-turbo"


class Role(Enum):
    USER = "user"
    SYSTEM = "system"


class TextPart(BaseModel):
    type: str = "text"
    text: str


class Detail(Enum):
    LOW = "low"
    HIGH = "high"


class Image(BaseModel):
    url: str
    detail: Detail = Detail.LOW

    def model_dump(self) -> Dict[str, Any]:
        return {"url": self.url, "detail": self.detail.value}


class ImagePart(BaseModel):
    type: str = "image_url"
    image_url: Image

    def model_dump(self) -> Dict[str, Any]:
        return {"type": self.type, "image_url": self.image_url.model_dump()}


class Message(BaseModel):
    role: Role = Role.USER
    content: str

    def model_dump(self) -> Dict[str, Any]:
        return {"role": self.role.value, "content": self.content}


class VisionMessage(BaseModel):
    role: Role = Role.USER
    content: List[Union[TextPart, ImagePart]]

    def model_dump(self) -> Dict[str, Any]:
        return {"role": self.role.value, "content": [part.model_dump() for part in self.content]}


class OpenAIData(LLMData):
    model: OpenAIModel = OpenAIModel.GPT_4O
    messages: List[Union[Message, VisionMessage]]
    temperature: float = 0.0

    def model_dump(self) -> Dict[str, Any]:
        return {
            "model": self.model.value,
            "messages": [message.model_dump() for message in self.messages],
            "temperature": self.temperature,
        }


class OpenAIMessage(BaseModel):
    content: str


class OpenAIChoice(BaseModel):
    message: OpenAIMessage


class OpenAIResponse(LLMResponse):
    choices: List[OpenAIChoice]


class OpenAI(LLM):
    def __init__(
        self, endpoint: str, api_key: str, organization_id: Optional[str] = None, cache: bool = True
    ) -> None:
        super().__init__(cache=cache)
        self.endpoint: str = endpoint
        self.api_key: str = api_key
        self.organization_id: Optional[str] = organization_id

    async def completion(self, data: OpenAIData) -> OpenAIResponse:
        headers: Dict[str, Any] = self._headers()
        result: Dict[str, Any] = await self._post(
            url=self.endpoint, headers=headers, payload=data.model_dump()
        )
        return OpenAIResponse(index=data.index, **result)

    def _headers(self) -> Dict[str, Any]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "Openai-Organization": self.organization_id or "",
        }
