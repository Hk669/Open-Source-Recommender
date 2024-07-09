from .search import main
import asyncio
import requests
import logging
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
import uvicorn
from .user_data import get_repos
from src.db import (recommend, 
                    get_topic_based_recommendations, 
                    get_chromadb_collection, 
                    upsert_to_chroma_db)
from src.models import User, GithubUser
load_dotenv()


GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")

logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.get('/github-login')
async def github_login():
    return RedirectResponse(f'https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}', status_code=302)

#TODO: redirect to frontend
@app.get('/github-callback')
async def github_callback(code: str):
    try:
        # Exchange code for access token
        response = requests.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
            },
        )
        response.raise_for_status()
        access_token = response.json().get("access_token")

        # Get user info
        user_response = requests.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_response.raise_for_status()
        user_data = user_response.json()

        github_user = GithubUser(
            username=user_data.get("login"),
            email=user_data.get("email"),
            name=user_data.get("name"),
            avatar_url=user_data.get("avatar_url"),
            bio=user_data.get("bio"),
            location=user_data.get("location"),
            company=user_data.get("company"),
            twitter_username=user_data.get("twitter_username"),
            followers=user_data.get("followers"),
            following=user_data.get("following"),
            public_repos=user_data.get("public_repos"),
            public_gists=user_data.get("public_gists"),
            access_token=access_token,
            created_at=user_data.get("created_at"),
            updated_at=user_data.get("updated_at"),
        )

        await github_user.save()

        print({"access_token": access_token, "user_data": user_data})

        return {"access_token": access_token, "user_data": github_user.model_dump()}
        # return {"authenticated": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error authenticating: {str(e)}")


async def run_server():
    uvicorn.run(app, host='0.0.0.0', port=8000)


if __name__ == '__main__':
    asyncio.run(run_server())