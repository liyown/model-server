import logging
from fastapi import FastAPI, Request
from pynvml import nvmlInit, nvmlShutdown
from starlette.middleware.cors import CORSMiddleware

from endpoint.middle_ground_controller import router as middle_ground_router
from endpoint.video_with_audio_controller import router as video_with_audio_router
from module.config.env_config import config
from services.model_inference.wav2lip.model_service import video_with_audio_task_service
from endpoint.gradio import gradio_app 
from gradio.routes import mount_gradio_app

logging.basicConfig(level=config.get_logging_level(), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = FastAPI()


mount_gradio_app(app, gradio_app, "/gradio")


# 设置 CORS 策略
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://120.132.118.114:1221"],  # 允许所有域名访问
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
    expose_headers=["Authorization"]
)


def service_start():
    video_with_audio_task_service.start()
    nvmlInit()


def service_stop():
    video_with_audio_task_service.stop()
    nvmlShutdown()

app.include_router(middle_ground_router, prefix="/admin")
app.include_router(video_with_audio_router, prefix="/api/v1")

app.add_event_handler("startup", service_start)
app.add_event_handler("shutdown", service_stop)

# 创建一个 logger 实例
logger = logging.getLogger("uvicorn.access")

# 定义需要过滤的路径列表
EXCLUDE_PATHS = ["/admin/api/gpu_status", "/admin/api/gpu_status","/admin/api/task_count"]


@app.middleware("http")
async def filter_logging_middleware(request: Request, call_next):
    if request.url.path in EXCLUDE_PATHS:
        # 禁用日志
        uvicorn_logger = logging.getLogger("uvicorn.access")
        uvicorn_logger.disabled = True
    else:
        uvicorn_logger = logging.getLogger("uvicorn.access")
        uvicorn_logger.disabled = False

    response = await call_next(request)
    return response
