from typing import Optional

from pydantic import BaseModel


class ImageToVideoTaskModel(BaseModel):
    task_id: Optional[int] = None
    image_key: str
    audio_key: str
    callback_url: Optional[str] = None
    result_id: Optional[int] = None
    status: int


class ImageToVideoResultModel(BaseModel):
    result_id: Optional[int] = None
    video_key: str


class VideoAndAudioToVideoTaskModel(BaseModel):
    task_id: Optional[int] = None
    video_key: str
    audio_key: str
    improve_video: Optional[bool] = False
    callback_url: Optional[str] = None
    result_id: Optional[int] = None
    status: int


class VideoAndAudioToVideoResultModel(BaseModel):
    result_id: Optional[int] = None
    video_key: str
    failed_reason: Optional[str] = None
