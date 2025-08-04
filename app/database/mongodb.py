from pymongo import MongoClient
from app.config import settings

def get_mongo_client():
    return MongoClient(
        settings.MONGODB_URL,
        username=settings.MONGODB_USER,
        password=settings.MONGODB_PASSWORD,
        authSource=settings.MONGODB_AUTH_SOURCE
    )
   
client = get_mongo_client()
db = client[settings.MONGODB_DB]

def get_incidents_collection():
    return db["incidents"]

def get_events_collection():
    return db["events"]

def get_messages_collection():
    return db["messages"]