from datetime import datetime
from app.database import get_db

async def log_activity(task_id: str, task_title: str, action: str, detail: str, performed_by: str):
    db = get_db()
    await db.activity_logs.insert_one({
        "task_id": task_id,
        "task_title": task_title,
        "action": action,
        "detail": detail,
        "performed_by": performed_by,
        "created_at": datetime.utcnow()
    })
