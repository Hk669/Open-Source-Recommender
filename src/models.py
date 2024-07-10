from pydantic import BaseModel
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging

logger = logging.getLogger(__name__)

MONGODB_URL = os.getenv("MONGODB_URL")
if not MONGODB_URL:
    raise ValueError("MONGODB_URL environment variable is not set")

client = AsyncIOMotorClient(MONGODB_URL)
db = client['github']

async def get_user_collection():
    return db['users']


class User(BaseModel):
    username: str
    access_token: str
    extra_topics: List[str] = []
    languages: List[str] = []


class GithubUser(BaseModel):
    username: str
    email: Optional[str] = None
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    company: Optional[str] = None
    twitter_username: Optional[str] = None
    followers: int
    following: int
    public_repos: int
    public_gists: int
    access_token: str
    created_at: str
    updated_at: str

    async def save(self):
        try:
            user_collection = await get_user_collection()
        except Exception as e:
            logger.error(f"Failed to fetch users from DB: {str(e)}")
            raise ValueError("Failed to fetch users from DB")
        
        user_in_db = await user_collection.find_one({"username": self.username})
        try:
            if user_in_db:
                await user_collection.update_one(
                    {"username": self.username},
                    {"$set": self.model_dump()}
                )
            else:
                await user_collection.insert_one(self.model_dump())
        except Exception as e:
            logger.error(f"Failed to save user to DB: {str(e)}")
            raise ValueError("Failed to save user to DB")
        
