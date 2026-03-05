from fastapi import APIRouter, Depends, Query
from app.database import get_db
from app.schemas import PaginatedLogs, ActivityLogResponse
from app.utils.auth import get_current_user
import math

router = APIRouter()

@router.get("/", response_model=PaginatedLogs)
async def get_activity_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    owner_id = str(current_user["_id"])

    # Get all task IDs owned by user
    user_task_ids = await db.tasks.distinct("_id", {"owner_id": owner_id})
    user_task_id_strs = [str(tid) for tid in user_task_ids]

    # Also include logs from deleted tasks by username
    query = {
        "$or": [
            {"task_id": {"$in": user_task_id_strs}},
            {"performed_by": current_user["username"]}
        ]
    }

    total = await db.activity_logs.count_documents(query)
    total_pages = math.ceil(total / per_page)
    skip = (page - 1) * per_page

    cursor = db.activity_logs.find(query).sort("created_at", -1).skip(skip).limit(per_page)
    logs = await cursor.to_list(length=per_page)

    return PaginatedLogs(
        logs=[
            ActivityLogResponse(
                id=str(log["_id"]),
                task_id=log["task_id"],
                task_title=log["task_title"],
                action=log["action"],
                detail=log["detail"],
                performed_by=log["performed_by"],
                created_at=log["created_at"]
            ) for log in logs
        ],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )
