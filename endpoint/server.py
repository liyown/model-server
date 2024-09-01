import logging
from fastapi import FastAPI
from endpoint import face_controller
from endpoint.face_controller import router as face_detection_router
import uvicorn

from services.model_inference.face_recog.model_service import FaceRecognitionService, face_service

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = FastAPI()

app.include_router(face_detection_router, prefix="/api/v1")


def face_service_start():
    face_service.start()


def face_service_stop():
    face_service.stop()


app.include_router(face_controller.router, prefix="/api/v1")
app.add_event_handler("startup", face_service_start)
app.add_event_handler("shutdown", face_service_stop)

# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8080)
