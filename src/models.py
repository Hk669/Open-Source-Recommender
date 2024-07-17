from pydantic import BaseModel
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorClient
import os
import uuid
import logging
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

MONGODB_URL = os.getenv("MONGODB_URL")
if not MONGODB_URL:
    raise ValueError("MONGODB_URL environment variable is not set")

client = AsyncIOMotorClient(MONGODB_URL)
db = client['github']

async def get_user_collection():
    return db['users']

async def get_recommendations_collection():
    return db['recommendations']


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
        

class RepositoryRecommendation(BaseModel):
    full_name: str
    description: Optional[str]
    related_language_or_topic: str
    stargazers_count: int
    forks_count: int
    open_issues_count: int
    avatar_url: Optional[str]
    language: str
    updated_at: str
    topics: str


def append_recommendations_to_db(username, recommendations, recommendation_name):
    try:
        user_recommenations_coll = db['user_recommendations']
        recommendations_collection = db['recommendations']

    except Exception as e:
        logger.error(f"Failed to fetch recommendations from DB: {str(e)}")
        raise ValueError("Failed to fetch recommendations from DB")
    
    recommendation_id = str(uuid.uuid4())
    try:
        recommendations_collection.insert_one({
            "recommendation_id": recommendation_id,
            "recommendations": recommendations
        })

    except Exception as e:
        logger.error(f"Failed to save recommendations to DB: {str(e)}")
        raise ValueError("Failed to save recommendations to DB")

    try:
        user_recommenations_coll.update_one(
            {"username": username},
            {"$push": {
                "recommendation_refs": {
                    "recommendation_id": recommendation_id,
                    "recommendation_name": recommendation_name
                }
            }},
            upsert=True
        )

        return recommendation_id
    except Exception as e:
        logger.error(f"Failed to save user recommendations to DB: {str(e)}")
        raise ValueError("Failed to save user recommendations to DB")
    

def get_recommendation_by_id(recommendation_id):
    try:
        recommendations_collection = db['recommendations']
        recommendation_data = recommendations_collection.find_one({"recommendation_id": recommendation_id})
        
        if not recommendation_data:
            return None

        return {
            "recommendation_id": recommendation_id,
            "recommendations": recommendation_data["recommendations"]
        }

    except Exception as e:
        logger.error(f"Failed to get recommendation from DB: {str(e)}")
        raise ValueError("Failed to get recommendation from DB")


# TODO: v2
# def update_daily_limit_to_all_users():
#     try:
#         user_collection = db['users']
#         user_collection.update_many({}, {"$set": {"daily_limit": 2}})
#     except Exception as e:
#         logger.error(f"Failed to update daily limit: {str(e)}")
#         raise ValueError("Failed to update daily limit")


# def check_and_update_daily_limit(username: str):
#     user_collection = db['users']
#     result = user_collection.find_one_and_update(
#         {"username": username, "daily_limit": {"$gt": 0}},
#         {"$inc": {"daily_limit": -1}},
#         return_document=True
#     )
    
#     if not result:
#         logger.warning(f"Daily limit exceeded for user: {username}")
#         raise ValueError("Daily limit exceeded")
    
#     return result