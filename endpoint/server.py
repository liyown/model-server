from fastapi import FastAPI
from endpoint.face_controller import router as face_detection_router
import uvicorn

app = FastAPI()

app.include_router(face_detection_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

