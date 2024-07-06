from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from .user_data import get_repos
from src.db import recommend, get_topic_based_recommendations, get_chromadb_collection, upsert_to_chroma_db
from .search import main
import asyncio
import logging

logger = logging.getLogger(__name__)

app = FastAPI()

origins = [
    "http://localhost:3000",  # React development server
    # Add other origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class User(BaseModel):
    username: str
    extra_topics: list[str] = []
    languages: list[str] = []


@app.post('/api/recommendations/')
async def get_recommendations(user: User) -> dict:
    try:
        urls = []

        if user.username:
            user_details, language_topics = await get_repos(user.username)
            if not user_details:
                logger.info("No repos found for user")
                logger.info("Generating topic-based recommendations")
                return get_topic_based_recommendations(user)
            
            try:
                urls = recommend(user_details)
            except Exception as e:
                logger.error(f"Error generating recommendations: {str(e)}")
                logger.info("Generating topic-based recommendations")
                return get_topic_based_recommendations(user)

            if not urls or len(urls) < 5:
                logger.info("Fewer than 5 recommendations found, fetching more repositories based on topics")
                fetched_repos = await main(language_topics, user.extra_topics, user.languages)
                collection = get_chromadb_collection()
                upsert_to_chroma_db(collection, fetched_repos)
                urls = recommend(user_details)
        else:
            try:
                logger.info("Generating topic-based recommendations")
                return get_topic_based_recommendations(user)
            except Exception as e:
                logger.error(f"Error generating recommendations: {str(e)}")
                return HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

        if not urls:
            return {'recommendations': [], 'message': 'No recommendations found'}
        
        return {'recommendations': urls}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
        

async def run_server():
    uvicorn.run(app, host='0.0.0.0', port=8000)


if __name__ == '__main__':
    asyncio.run(run_server())