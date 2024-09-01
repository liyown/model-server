from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/face_detection")
async def face_detection():
    return {"message": "Face detected"}


@router.get("/face_detection/{task_id}")
async def read_item(task_id: int):
    return {"task_id": task_id}
