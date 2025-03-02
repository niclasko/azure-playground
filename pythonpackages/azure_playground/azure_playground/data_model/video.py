from pathlib import Path
from typing import List

from azure_playground.data_model.frame import Frame
from pydantic import BaseModel


class Video(BaseModel):
    name: str
    path: Path
    frames: List[Frame]
