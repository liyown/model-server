import logging
from fastapi import FastAPI
from pynvml import nvmlInit, nvmlShutdown
from starlette.middleware.cors import CORSMiddleware

from endpoint.face_controller import router as face_detection_router
from endpoint.middle_ground_controller import router as middle_ground_router
import uvicorn

from module.config.env_config import config
from services.model_inference.face_recog.model_service import FaceRecognitionService, face_service

logging.basicConfig(level=config.get_logging_level(), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = FastAPI()

# 设置 CORS 策略
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 允许所有域名访问
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
    expose_headers=["Authorization"]
)

def service_start():
    face_service.start()
    nvmlInit()


def service_stop():
    face_service.stop()
    nvmlShutdown()


app.include_router(face_detection_router, prefix="/api/v1")
app.include_router(middle_ground_router, prefix="/admin")

app.add_event_handler("startup", service_start)
app.add_event_handler("shutdown", service_stop)

# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8080)
