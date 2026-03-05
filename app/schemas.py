from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum

# ─── Enums ──────────────────────────────────────────────
class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in-progress"
    completed = "completed"

# ─── Auth Schemas ────────────────────────────────────────
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str

# ─── Task Schemas ────────────────────────────────────────
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    due_date: Optional[datetime] = None

class TaskStatusUpdate(BaseModel):
    status: TaskStatus

class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: TaskStatus
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    owner_id: str

# ─── Activity Log Schemas ────────────────────────────────
class ActivityLogResponse(BaseModel):
    id: str
    task_id: str
    task_title: str
    action: str
    detail: str
    performed_by: str
    created_at: datetime

class PaginatedLogs(BaseModel):
    logs: list[ActivityLogResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
