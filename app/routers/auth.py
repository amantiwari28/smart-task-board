from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from pymongo.errors import PyMongoError

from app.database import get_db
from app.schemas import UserRegister, UserLogin, TokenResponse
from app.utils.auth import hash_password, verify_password, create_access_token

router = APIRouter()

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister):
    db = get_db()
    try:
        if await db.users.find_one({"email": data.email}):
            raise HTTPException(status_code=400, detail="Email already registered")

        if await db.users.find_one({"username": data.username}):
            raise HTTPException(status_code=400, detail="Username already taken")

        user_doc = {
            "username": data.username,
            "email": data.email,
            "password": hash_password(data.password),
            "created_at": datetime.utcnow()
        }
        result = await db.users.insert_one(user_doc)
        token = create_access_token({"sub": str(result.inserted_id)})
        return TokenResponse(access_token=token, username=data.username)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail="Password hashing failed") from exc
    except PyMongoError as exc:
        raise HTTPException(
            status_code=503,
            detail="Database is unavailable. Please try again shortly.",
        ) from exc

@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin):
    db = get_db()
    try:
        user = await db.users.find_one({"email": data.email})

        if not user or not verify_password(data.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = create_access_token({"sub": str(user["_id"])})
        return TokenResponse(access_token=token, username=user["username"])
    except ValueError as exc:
        raise HTTPException(status_code=500, detail="Password verification failed") from exc
    except PyMongoError as exc:
        raise HTTPException(
            status_code=503,
            detail="Database is unavailable. Please try again shortly.",
        ) from exc
