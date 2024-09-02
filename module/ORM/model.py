from typing import Optional

from pydantic import BaseModel


class ImageToVideoTaskModel(BaseModel):
    task_id: Optional[int] = None
    image_url: str
    audio_url: str
    result_id: Optional[int] = None
    status: int


class ImageToVideoResultModel(BaseModel):
    result_id: Optional[int] = None
    video_url: str


