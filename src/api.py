from .search import main
import asyncio
import requests
import logging
import os
import sys
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from datetime import timedelta, datetime
import uvicorn
from fastapi.responses import JSONResponse
from .user_data import get_repos
from src.db import (recommend, 
                    get_topic_based_recommendations)
from src.models import User, GithubUser, get_user_collection, append_recommendations_to_db

# load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)

# Create a detailed log format
log_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)

# Set the format for handlers
console_handler.setFormatter(log_format)
logger.addHandler(console_handler)


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DELTA = timedelta(days=1)


FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
ALLOWED_ORIGINS = ["*"]


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_jwt(user_id: str):
    payload = {
        "user_id": user_id,
        "exp": datetime.now() + JWT_EXPIRATION_DELTA
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            logger.error("Invalid authentication credentials")
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        logger.error("Invalid authentication credentials")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user_collection = await get_user_collection()
    user = await user_collection.find_one({"_id": user_id})

    if user is None:
        logger.error("User not found")
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.post('/refresh-token')
async def refresh_token(current_user: dict = Depends(get_current_user)):
    new_token = create_jwt(current_user["username"])
    return {"jwt": new_token}

@app.get('/github-login')
async def github_login():
    return RedirectResponse(f'https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}', status_code=302)


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
        jwt_token = create_jwt(str(github_user.username))

        return RedirectResponse(f'{FRONTEND_URL}/auth-callback?authenticated=true&jwt={jwt_token}', status_code=302)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error authenticating: {str(e)}")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user_collection = await get_user_collection()
    user = await user_collection.find_one({"username": user_id})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.get('/verify-token')
async def verify_token(current_user: dict = Depends(get_current_user)):
    return {
        "username": current_user["username"],
        "email": current_user["email"],
        "name": current_user["name"],
        "avatar_url": current_user["avatar_url"]
    }

@app.options("/verify-token")
async def preflight_verify_token():
    return {"message": "Preflight response"}


@app.post('/api/recommendations/')
async def get_recommendations(request: Request, current_user: dict = Depends(get_current_user)) -> dict:
    try:
        body = await request.json()
        username = body.get("username")
        extra_topics = body.get("extra_topics", [])
        languages = body.get("languages", [])

        # TODO: v2
        # try: 
        #     check_daily_limit(username)
        # except ValueError as e:
        #     raise HTTPException(status_code=403, detail=str(e))

        urls = []
        user = User(username=current_user["username"], access_token=current_user["access_token"],extra_topics=extra_topics, languages=languages)

        user_details, language_topics = await get_repos(user)
        if not user_details:
            logger.info("No repos found for user")
            logger.info("Generating topic-based recommendations")
            return await get_topic_based_recommendations(user)
        
        # try:
        #     fetched_repos = await main(language_topics, access_token=user.access_token, extra_topics=extra_topics, extra_languages=languages)
        #     logger.info(f"Fetched {len(fetched_repos)} repositories")
        # except Exception as e:
        #     logger.error(f"Error fetching repositories: {str(e)}")
        #     raise ValueError("Error fetching repositories")
        
        try:
            print('Recommending\n\n')
            urls = await recommend(user_details=user_details, languages_topics=language_topics)
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            print("Error: Generating topic-based recommendations")
            return await get_topic_based_recommendations(user)

        if urls and len(urls) < 5:
            logger.info("Fewer than 10 recommendations found, fetching more repositories based on topics")
            fetched_repos = await main(language_topics, access_token=user.access_token, extra_topics=extra_topics, extra_languages=languages)
            urls = await recommend(user_details=user_details, languages_topics=language_topics)

        seen_full_names = set()
        unique_recommendations = []

        for rec in urls:
            full_name = rec.get("full_name")
            if full_name not in seen_full_names:
                seen_full_names.add(full_name)
                unique_recommendations.append(rec)

        if not unique_recommendations:
            return {'recommendations': [], 'message': 'No recommendations found'}
        
        rec_name = f"Recommendations for {username} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        rec_id = append_recommendations_to_db(username, unique_recommendations, rec_name)
        logger.info(f"Recommendations saved to DB with ID: {rec_id}")


        # update_daily_limit(username) # updates the daily limit of the user.
        return {
            'recommendations': unique_recommendations[::-1],
            'recommendation_id': rec_id
        }
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while generating recommendations")

@app.get('/api/health')
async def health_check(request: Request):
    return JSONResponse({"status": "OK"})


if __name__ == '__main__':
    uvicorn.run("src.api:app", host='0.0.0.0', port=8000, reload=True)