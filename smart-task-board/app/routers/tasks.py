from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime
from bson import ObjectId
from app.database import get_db
from app.schemas import TaskCreate, TaskStatusUpdate, TaskResponse, TaskStatus
from app.utils.auth import get_current_user
from app.utils.logger import log_activity

router = APIRouter()

# Strict status flow: todo → in-progress → completed
STATUS_FLOW = {
    TaskStatus.todo: TaskStatus.in_progress,
    TaskStatus.in_progress: TaskStatus.completed,
    TaskStatus.completed: None  # terminal state
}

def task_to_response(task: dict) -> TaskResponse:
    return TaskResponse(
        id=str(task["_id"]),
        title=task["title"],
        description=task.get("description"),
        status=task["status"],
        due_date=task.get("due_date"),
        created_at=task["created_at"],
        updated_at=task["updated_at"],
        owner_id=task["owner_id"]
    )

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(data: TaskCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    now = datetime.utcnow()
    task_doc = {
        "title": data.title,
        "description": data.description,
        "status": TaskStatus.todo,
        "due_date": data.due_date,
        "owner_id": str(current_user["_id"]),
        "created_at": now,
        "updated_at": now
    }
    result = await db.tasks.insert_one(task_doc)
    task_doc["_id"] = result.inserted_id

    await log_activity(
        task_id=str(result.inserted_id),
        task_title=data.title,
        action="CREATED",
        detail=f"Task '{data.title}' created with status 'todo'",
        performed_by=current_user["username"]
    )
    return task_to_response(task_doc)

@router.get("/", response_model=list[TaskResponse])
async def get_tasks(current_user: dict = Depends(get_current_user)):
    db = get_db()
    cursor = db.tasks.find({"owner_id": str(current_user["_id"])}).sort("created_at", -1)
    tasks = await cursor.to_list(length=100)
    return [task_to_response(t) for t in tasks]

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    try:
        oid = ObjectId(task_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid task ID")

    task = await db.tasks.find_one({"_id": oid, "owner_id": str(current_user["_id"])})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_to_response(task)

@router.patch("/{task_id}/status", response_model=TaskResponse)
async def update_task_status(
    task_id: str,
    data: TaskStatusUpdate,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    try:
        oid = ObjectId(task_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid task ID")

    task = await db.tasks.find_one({"_id": oid, "owner_id": str(current_user["_id"])})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    current_status = TaskStatus(task["status"])
    new_status = data.status

    # Strict flow validation
    allowed_next = STATUS_FLOW.get(current_status)
    if allowed_next is None:
        raise HTTPException(
            status_code=400,
            detail="Task is already completed. Status cannot be changed."
        )
    if new_status != allowed_next:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status transition: '{current_status}' → '{new_status}'. "
                   f"Only allowed next status is '{allowed_next}'."
        )

    now = datetime.utcnow()
    await db.tasks.update_one(
        {"_id": oid},
        {"$set": {"status": new_status, "updated_at": now}}
    )

    await log_activity(
        task_id=task_id,
        task_title=task["title"],
        action="STATUS_UPDATED",
        detail=f"Status changed from '{current_status}' to '{new_status}'",
        performed_by=current_user["username"]
    )

    task["status"] = new_status
    task["updated_at"] = now
    return task_to_response(task)

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    try:
        oid = ObjectId(task_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid task ID")

    task = await db.tasks.find_one({"_id": oid, "owner_id": str(current_user["_id"])})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await db.tasks.delete_one({"_id": oid})
    await log_activity(
        task_id=task_id,
        task_title=task["title"],
        action="DELETED",
        detail=f"Task '{task['title']}' was deleted",
        performed_by=current_user["username"]
    )
