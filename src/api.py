from .search import main
import asyncio
import requests
import logging
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
import uvicorn
from .user_data import get_repos
from src.db import (recommend, 
                    get_topic_based_recommendations, 
                    get_chromadb_collection, 
                    upsert_to_chroma_db)
from src.models import User, GithubUser, get_user_collection
load_dotenv()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
ALLOWED_ORIGINS = ["http://localhost:3000"]

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
        print("user", user)
        if not user.access_token:
            raise HTTPException(status_code=401, detail="Access token missing")
        
        if user.access_token:
            # TODO: Fetch repos using topics
            user_details, language_topics = await get_repos(user)
            if not user_details:
                logger.info("No repos found for user")
                logger.info("Generating topic-based recommendations")
                return get_topic_based_recommendations(user)
            
            try:
                urls = recommend(user_details, language_topics)
            except Exception as e:
                logger.error(f"Error generating recommendations: {str(e)}")
                logger.info("Generating topic-based recommendations")
                return get_topic_based_recommendations(user)

            if urls and len(urls) < 10:
                logger.info("Fewer than 5 recommendations found, fetching more repositories based on topics")
                fetched_repos = await main(language_topics, access_token=user.access_token, extra_topics=user.extra_topics, extra_languages=user.languages)
                urls = recommend(user_details, language_topics)
        else:
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

        # return {"access_token": access_token, "user_data": github_user.model_dump()}
        return RedirectResponse(f'{FRONTEND_URL}/auth-callback?authenticated=true&access_token={access_token}', status_code=302)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error authenticating: {str(e)}")

@app.get('/verify-token')
async def verify_token(authorization: str = Header(None)):
    try:
        if authorization is None:
            raise HTTPException(status_code=401, detail="Authorization header missing")

        token = authorization.split(" ")[1]
        user_collection = await get_user_collection()
        user = await user_collection.find_one({"access_token": token})
        if user:
            user['_id'] = str(user['_id'])
            return {"user_data": user}
        else:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error verifying token: {str(e)}")

@app.options("/verify-token")
async def preflight_verify_token():
    return {"message": "Preflight response"}

async def run_server():
    uvicorn.run(app, host='0.0.0.0', port=8000)


if __name__ == '__main__':
    asyncio.run(run_server())