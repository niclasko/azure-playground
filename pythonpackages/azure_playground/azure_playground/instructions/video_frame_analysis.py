from enum import Enum
from typing import Optional, Type

from azure_playground.instructions.instruction import SCHEMA_PLACEHOLDER, Instruction
from pydantic import BaseModel, ConfigDict, Field


class VideoFrameAnalysisResult(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "people_count": 7,
                "looking_at_camera_count": 3,
                "smiling_count": 2,
                "scene_description": "A group of people standing in front of a whiteboard in a conference room.",
            }
        }
    )

    people_count: int = Field(..., description="The total number of people in the frame.")
    looking_at_camera_count: int = Field(
        ..., description="The number of people looking at the camera."
    )
    smiling_count: int = Field(..., description="The number of people smiling.")
    scene_description: str = Field(
        ..., description="A general description of the scene and the people in the frame."
    )


class VideoFrameAnalysis(Instruction):
    text: str = f"""
        You are an expert at analyzing video frames.  You should answer the following questions about the video frame provided to you:
        
        - How many people are in the frame? **Only count people who are clearly visible and not partially cut off.**
        - How many people are looking at the camera? **Only count people who are looking directly at the camera.**
        - How many people are smiling? **Only count people who are clearly smiling.**

        You should also provide a general description of the scene and the people in the frame.

        Provide your answers in the following JSON format:
        {SCHEMA_PLACEHOLDER}
    """
    response_schema: Type[BaseModel] = VideoFrameAnalysisResult
