import logging
from typing import Optional

from fastapi import HTTPException, Depends, Request, APIRouter
from pydantic import BaseModel

from module.ORM.model import ImageToVideoTaskModel, VideoAndAudioToVideoTaskModel
from module.ORM.table_config import Authorizations
from services.model_inference.wav2lip.model_service import video_with_audio_task_queue
from utils.snowflake import Snowflake

router = APIRouter()
snowflake = Snowflake(1, 1)
logger = logging.getLogger(__name__)


async def verify_token_in_cookie(request: Request):
    login_token = request.headers.get("access_token")
    if not login_token:
        raise HTTPException(status_code=401, detail="Missing token in headers")
    try:
        # 去数据库查询是否存在该 token
        token = Authorizations.get(Authorizations.api_key == login_token)
        if token is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Authorizations.DoesNotExist:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        # 可以记录异常信息到日志
        raise HTTPException(status_code=500, detail="Internal Server Error")


class VideoWithAudioRequest(BaseModel):
    video_key: str
    audio_key: str
    callback_url: Optional[str] = None


@router.post("/video_with_audio")
async def face_detection(request_body: VideoWithAudioRequest, payload: dict = Depends(verify_token_in_cookie)):
    task_data = {
        "video_key": request_body.video_key,
        "audio_key": request_body.audio_key,
        "callback_url": request_body.callback_url,
        "status": 0
    }
    task_id = video_with_audio_task_queue.add_task(VideoAndAudioToVideoTaskModel.parse_obj(task_data))

    if task_id is None:
        raise HTTPException(status_code=400, detail="任务队列已满")
    return {"task_id": task_id}


@router.get("/video_with_audio/{task_id}")
async def read_item(task_id: int, payload: dict = Depends(verify_token_in_cookie)):
    result = video_with_audio_task_queue.get_result(task_id)
    if result is None:
        return "任务正在处理中"
    return result
