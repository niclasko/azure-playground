import asyncio
import logging
from typing import AsyncIterator, Coroutine, Iterator, List, Tuple

import tqdm
from azure_playground.instructions.instruction import Instruction
from azure_playground.models.llms.openai import (
    Image,
    ImagePart,
    OpenAI,
    OpenAIData,
    OpenAIModel,
    OpenAIResponse,
    Role,
    TextPart,
    VisionMessage,
)
from azure_playground.utils.image_encoder import ImageEncoder
from azure_playground.utils.video_frame_sampler import Frame
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class VideoFrameAnalyzer:
    def __init__(self, instruction: Instruction, model: OpenAI) -> None:
        self.instruction = instruction
        self.model: OpenAI = model

    async def analyze(self, frames: List[Frame]) -> List[BaseModel]:
        logger.info(f"Analyzing {len(frames)} video frames")
        encoded: List[str] = list(ImageEncoder.encode_many(frames))
        calls: List[Coroutine] = list(self._calls(encoded))
        return list(self._sort([response async for response in self._run(calls)]))

    def _calls(self, encoded: List[str]) -> Iterator[Coroutine]:
        instruction: TextPart = TextPart(text=self.instruction.instantiate())
        for index, data in enumerate(encoded):
            image: ImagePart = ImagePart(image_url=Image(url=data))
            payload: OpenAIData = OpenAIData(
                index=index,
                model=OpenAIModel.GPT_4O,
                messages=[VisionMessage(role=Role.USER, content=[instruction, image])],
            )
            yield self.model.completion(payload)

    async def _run(self, calls: List[Coroutine]) -> AsyncIterator[Tuple[int, BaseModel]]:
        for future in tqdm.tqdm(
            asyncio.as_completed(calls), total=len(calls), desc="Analyzing Frames"
        ):
            response: OpenAIResponse = await future
            yield response.index, self.instruction.parse(response.choices[0].message.content)

    def _sort(self, responses: List[Tuple[int, BaseModel]]) -> Iterator[BaseModel]:
        for _, response in sorted(responses, key=lambda x: x[0]):
            yield response
