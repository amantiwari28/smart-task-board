import motor.motor_asyncio
from decouple import config

MONGODB_URL = config("MONGODB_URL", default="mongodb://localhost:27017")
DB_NAME = config("DB_NAME", default="smart_task_board")

client = None
db = None

async def connect_db():
    global client, db
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    print(f"✅ Connected to MongoDB: {DB_NAME}")

async def close_db():
    global client
    if client:
        client.close()
        print("🔌 MongoDB connection closed")

def get_db():
    return db
