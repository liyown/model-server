import logging

from fastapi import APIRouter, HTTPException

from module.ORM.model import ImageToVideoTaskModel
from services.model_inference.face_recog.model_service import face_task_queue
from utils.snowflake import Snowflake

router = APIRouter()
snowflake = Snowflake(1, 1)
logger = logging.getLogger(__name__)


@router.get("/face_detection")
async def face_detection():
    task_id = face_task_queue.add_task(ImageToVideoTaskModel.parse_obj({
        "image_url": "data/dog.png",
        "audio_url": "http://example.com/audio.mp3",
        "status": 0
    }))
    return {"task_id": task_id}


@router.get("/face_detection/{task_id}")
async def read_item(task_id: int):
    result = face_task_queue.get_result(task_id)
    if result is None:
        return "任务正在处理中"
    return result
