from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import os
import uuid
import logging
import asyncio
from dotenv import load_dotenv
from datetime import datetime, timedelta
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
    followers: Optional[int] = None
    following: Optional[int] = None
    public_repos: Optional[int] = None
    public_gists: Optional[int] = None
    access_token: Optional[str] = None
    created_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updated_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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

async def append_user_to_db(username):
    try:
        user = GithubUser(username=username, name=username, email=username+"@gitmtach.in")
        await user.save()

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
    

async def get_user_previous_recommendations(username: str) -> list:
    try:
        # Example query; adjust as per your database schema
        user_recommendations = await db.user_recommendations.find_one({"username": username})
        if not user_recommendations:
            return []

        # Assuming the recommendations are stored in 'recommendation_refs'
        return user_recommendations.get("recommendation_refs", [])
    except Exception as e:
        logger.error(f"Database query error: {str(e)}")
        raise


async def get_user_recommendation_by_id(recommendation_id):
    try:
        recommendations_collection = db['recommendations']
        recommendation_data = await recommendations_collection.find_one({"recommendation_id": recommendation_id})
        
        if not recommendation_data:
            return None

        return {
            "recommendation_id": recommendation_id,
            "recommendations": recommendation_data["recommendations"]
        }

    except Exception as e:
        logger.error(f"Failed to get recommendation from DB: {str(e)}")
        raise ValueError("Failed to get recommendation from DB")

def process_recommendations(urls: List[Dict[str, Any]],
                            languages_topics) -> List[Dict[str, Any]]:
    """
    Process the list of URLs to ensure uniqueness and format them correctly.
    
    Args:
        urls: List of URL recommendations.
        
    Returns:
        Processed list of unique recommendations.
    """
    seen_full_names = set()
    unique_recommendations = []

    for rec in urls:
        full_name = rec.get("full_name")
        if full_name and full_name not in seen_full_names:
            seen_full_names.add(full_name)
            unique_recommendations.append(rec)

    def match_score(rec):
        # Calculate the score based on language and topic match
        score = 0
        rec_language = rec.get('language', '')
        rec_topics = rec.get('topics', [])
        
        # Extract user languages and topics
        user_languages = languages_topics.get("languages", [])
        user_topics = languages_topics.get("topics", [])

        # Add 2 to the score for a language match
        if rec_language in user_languages:
            score += 2
        
        # Add 1 to the score for each matching topic
        score += sum(1 for topic in rec_topics if topic in user_topics)
        
        return score

    # Sort the recommendations based on match score in descending order
    unique_recommendations.sort(key=match_score, reverse=True)

    return unique_recommendations


# TODO: v2
async def update_daily_limit(username: str) -> bool:
    try:
        user_recommendations_coll = db['user_recommendations']
        now = datetime.now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Fetch the user's recommendations
        user_recommendations = await user_recommendations_coll.find_one({"username": username})
        
        # Initialize if no record exists
        if not user_recommendations:
            # Initialize user recommendations with a daily limit
            await user_recommendations_coll.insert_one({
                "username": username,
                "recommendation_refs": [],
                "last_updated": start_of_day,
                "daily_limit": 2
            })
            return True  # Initial limit set

        last_updated = user_recommendations.get("last_updated", start_of_day)
        daily_limit = user_recommendations.get("daily_limit", 2)

        # Check if the limit needs to be reset
        if now - last_updated >= timedelta(days=1):
            # Reset daily limit and update the timestamp
            await user_recommendations_coll.update_one(
                {"username": username},
                {"$set": {"daily_limit": 2, "last_updated": start_of_day}}
            )
            return True  # Limit reset

        # If the limit is zero or less, return False
        if daily_limit <= 0:
            return False

        # Decrease the limit if it's still valid
        await user_recommendations_coll.update_one(
            {"username": username},
            {"$inc": {"daily_limit": -1}}
        )

        return True
    except Exception as e:
        logger.error(f"Failed to update daily limit: {str(e)}")
        return False

async def check_and_update_daily_limit(username: str) -> bool:
    return await update_daily_limit(username)
    
async def main():
    recommendations = await get_user_previous_recommendations("Hk669")
    print(recommendations)

if __name__ == "__main__":
    # asyncio.run(main())
    # Example list of URL recommendations
    urls = [
        {
            "full_name": "pandas-dev/pandas",
            "language": "Python",
            "topics": ["data-analysis", "data-science"]
        },
        {
            "full_name": "tensorflow/tensorflow",
            "language": "C++",
            "topics": ["machine-learning", "deep-learning"]
        },
        {
            "full_name": "vuejs/vue",
            "language": "JavaScript",
            "topics": ["vue", "front-end", "javascript", "framework"]
        },
        {
            "full_name": "d3/d3",
            "language": "JavaScript",
            "topics": ["visualization", "d3", "data-visualization"]
        },
        {
            "full_name": "django/django",
            "language": "Python",
            "topics": ["web", "framework", "django"]
        },
        {
            "full_name": "numpy/numpy",
            "language": "Python",
            "topics": ["math", "array", "numpy"]
        },
        {
            "full_name": "scikit-learn/scikit-learn",
            "language": "Python",
            "topics": ["machine-learning", "data-science", "scikit-learn"]
        },
        {
            "full_name": "nodejs/node",
            "language": "JavaScript",
            "topics": ["nodejs", "javascript", "server"]
        },
        {
            "full_name": "rails/rails",
            "language": "Ruby",
            "topics": ["rails", "web", "ruby"]
        },
        {
            "full_name": "spring-projects/spring-framework",
            "language": "Java",
            "topics": ["spring", "framework", "java"]
        }
    ]

    # User's preferred languages and topics
    languages_topics = {
        "languages": ["Python", "JavaScript"],
        "topics": ["machine-learning", "data-science", "web", "visualization"]
    }

    # Process and sort the recommendations
    sorted_recommendations = process_recommendations(urls, languages_topics)

    # Display the sorted recommendations
    for rec in sorted_recommendations:
        print(f"Repo: {rec['full_name']}, Language: {rec['language']}, Topics: {rec['topics']}")
