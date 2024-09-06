from pathlib import Path
import logging
import os
from pathlib import Path
from typing import Literal

import GPUtil
from fastapi import HTTPException, Depends, Request, APIRouter
from jose import jwt, JWTError
from pydantic import BaseModel
from pynvml import nvmlDeviceGetHandleByIndex, nvmlDeviceGetMemoryInfo
from starlette.responses import HTMLResponse, FileResponse, JSONResponse

from module.JWT.jwt import create_access_token
from module.JWT.resource_access_token import create_unique_resource_token
from module.ORM.table_config import Authorizations, ImageToVideoTask, VideoAndAudioToVideoTask
from module.config.env_config import config

router = APIRouter()
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent


# 定义请求体的模型
class LoginRequest(BaseModel):
    username: str
    password: str


class AddTokenRequest(BaseModel):
    remark: str


@router.get('/')
async def index():
    file_path = BASE_DIR / './web_fronted/dist/index.html'
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Index file not found")
    return HTMLResponse(
        content=open(file_path, 'r', encoding='utf-8').read(),
        media_type='text/html',
        headers={'Cache-Control': 'no-cache'}
    )


@router.get('/assets/{file_path:path}')
async def assets(file_path: str):
    full_path = BASE_DIR / f'./web_fronted/dist/assets/{file_path}'
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Asset not found")
    return FileResponse(full_path)


@router.post("/login")
async def index(login_request: LoginRequest):
    # 验证用户名和密码
    if login_request.username == config.get("admin") and login_request.password == config.get("password"):
        token = create_access_token({"sub": login_request.username})
        response = JSONResponse(content={"userName": "admin", "role": "ADMIN"})
        response.headers["Authorization"] = token
        return response
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")


SECRET_KEY = config.get("login_secret_key")
ALGORITHM = "HS256"


# 验证 cookie 中的 token
async def verify_token_in_cookie(request: Request):
    login_token = request.headers.get("Authorization")
    if not login_token:
        raise HTTPException(status_code=401, detail="Missing token in cookies")

    try:
        # 解码并验证JWT令牌
        payload = jwt.decode(login_token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # 返回解码后的信息，可以在其他地方使用
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# 定义路由
@router.post("/token")
async def token(add_token_request: AddTokenRequest, payload: dict = Depends(verify_token_in_cookie)):
    # 如果验证通过，可以继续处理请求
    if payload.get("sub") != config.get("admin"):
        raise HTTPException(status_code=401, detail="Invalid token")
    source_access_token = create_unique_resource_token()
    Authorizations.create(api_key=source_access_token, remark=add_token_request.remark)
    # 这里可以根据解码后的信息进行进一步的处理，如检查权限等
    return {"code": 200, "message": "Token created successfully",
            "data": {"api_key": source_access_token, "remark": add_token_request.remark}}


# 获取全部token 返回一个list
@router.get("/tokens")
async def tokens(payload: dict = Depends(verify_token_in_cookie)):
    if payload.get("sub") != config.get("admin"):
        raise HTTPException(status_code=401, detail="Invalid token")
    tokens = Authorizations.select()
    return {"code": 200, "message": "Success",
            "data": [{"api_key": token.api_key, "remark": token.remark, "key": token.id} for token in tokens]}


@router.delete("/token/{api_key}")
async def delete_token(api_key: str, payload: dict = Depends(verify_token_in_cookie)):
    if payload.get("sub") != config.get("admin"):
        raise HTTPException(status_code=401, detail="Invalid token")
    token = Authorizations.get(Authorizations.api_key == api_key)
    token.delete_instance()
    return {"code": 200, "message": "Token deleted successfully"}


class TaskTypeRequest(BaseModel):
    task_type: Literal["image_to_video", "video_with_audio_to_video"]


# 查看当前未完成的任务数
@router.post("/task_count")
async def task_count(task_type: TaskTypeRequest, payload: dict = Depends(verify_token_in_cookie)):
    if payload.get("sub") != config.get("admin"):
        raise HTTPException(status_code=401, detail="Invalid token")

    if task_type.task_type == "image_to_video":
        task_counts = ImageToVideoTask.select().where(
            (ImageToVideoTask.status == 0) | (ImageToVideoTask.status == 1)
        ).count()
    elif task_type.task_type == "video_with_audio_to_video":
        task_counts = VideoAndAudioToVideoTask.select().where(
            (VideoAndAudioToVideoTask.status == 0) | (VideoAndAudioToVideoTask.status == 1)
        ).count()
    else:
        raise HTTPException(status_code=400, detail="Invalid task type")

    return {"code": 200, "message": "Success", "data": {"task_count": task_counts}}


@router.get("/gpu_status")
async def get_gpu_status():
    gpus = GPUtil.getGPUs()
    gpu_status = []

    for gpu in gpus:
        handle = nvmlDeviceGetHandleByIndex(gpu.id)
        mem_info = nvmlDeviceGetMemoryInfo(handle)

        gpu_info = {
            "id": gpu.id,
            "name": gpu.name,
            "load": gpu.load * 100,  # GPU使用率
            "memory_total": mem_info.total / (1024 ** 2),  # 总内存(MB)
            "memory_used": mem_info.used / (1024 ** 2),  # 已使用内存(MB)
            "memory_free": mem_info.free / (1024 ** 2),  # 可用内存(MB)
            "temperature": gpu.temperature,  # GPU温度
            "uuid": gpu.uuid
        }
        gpu_status.append(gpu_info)

    return {"gpu_status": gpu_status}




@router.post("/test")
async def test():
    print("payload")
