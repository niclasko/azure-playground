import base64
from pathlib import Path
from typing import Iterator, List, Set

import requests
from azure_playground.data_model.frame import Frame

SUPPORTED_IMAGE_FORMATS: Set[str] = {".png", ".jpg", ".jpeg", ".gif", ".bmp"}


class ImageEncoder:
    @classmethod
    def encode_many(cls, frames: List[Frame]) -> Iterator[str]:
        for frame in frames:
            if frame.image.suffix in SUPPORTED_IMAGE_FORMATS:
                yield cls.encode(str(frame.image))

    @classmethod
    def encode(cls, url: str) -> str:
        type: str = cls.file_type(url)
        encoded: str = cls._encode(url)
        return f"data:{type};base64,{encoded}"

    @classmethod
    def file_type(cls, url: str) -> str:
        if url.endswith(".png"):
            return "image/png"
        elif url.endswith(".jpg") or url.endswith(".jpeg"):
            return "image/jpeg"
        elif url.endswith(".gif"):
            return "image/gif"
        elif url.endswith(".bmp"):
            return "image/bmp"
        else:
            return "image/jpeg"

    @classmethod
    def _encode(cls, url: str) -> str:
        content: bytes = cls.read(url)
        return base64.b64encode(content).decode("utf-8")

    @classmethod
    def read(cls, url: str) -> bytes:
        if url.startswith("http"):
            response = requests.get(url)
            return response.content
        else:
            file: Path = Path(url)
            return file.read_bytes()
