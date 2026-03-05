import motor.motor_asyncio
from decouple import config
from fastapi import HTTPException, status
from pymongo.errors import PyMongoError

MONGODB_URL = config("MONGODB_URL", default="mongodb://localhost:27017")
DB_NAME = config("DB_NAME", default="smart_task_board")

client = None
db = None


async def connect_db():
    global client, db
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
    try:
        await client.admin.command("ping")
    except PyMongoError as exc:
        client = None
        db = None
        raise RuntimeError(
            "Could not connect to MongoDB. Check MONGODB_URL and network access."
        ) from exc

    db = client[DB_NAME]
    print(f"Connected to MongoDB: {DB_NAME}")


async def close_db():
    global client
    if client:
        client.close()
        print("MongoDB connection closed")


def get_db():
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not available. Please try again shortly.",
        )
    return db
