import logging

from fastapi import APIRouter, HTTPException
from services.model_inference.face_recog.model_service import face_task_queue, get_result
from utils.snowflake import Snowflake

router = APIRouter()
snowflake = Snowflake(1, 1)
logger = logging.getLogger(__name__)


@router.get("/face_detection")
async def face_detection():
    snowflake_id = snowflake.generate()
    logger.info(f"生成任务ID: {snowflake_id}")
    face_task_queue.put({"task_id": snowflake_id, "ctx": {"image_path": "data/dog.png"}})
    return {"task_id": snowflake_id}


@router.get("/face_detection/{task_id}")
async def read_item(task_id: int):
    result = get_result(task_id)
    if result is None:
        return "任务正在处理中"
    return result
