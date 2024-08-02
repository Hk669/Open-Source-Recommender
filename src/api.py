from .search import main
import asyncio
import requests
import logging
import os
import sys
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Header, Depends, Request, Query
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
from src.models import (User, 
                        GithubUser, 
                        get_user_collection, 
                        append_recommendations_to_db, get_user_previous_recommendations, 
                        get_user_recommendation_by_id, check_and_update_daily_limit,
                        process_recommendations, append_user_to_db)

# load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# console_handler = logging.StreamHandler(sys.stdout)
# console_handler.setLevel(logging.DEBUG)

# # Create a detailed log format
# log_format = logging.Formatter(
#     '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
# )

# # Set the format for handlers
# console_handler.setFormatter(log_format)
# logger.addHandler(console_handler)


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DELTA = timedelta(days=1)


FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://gitmatch.in"],
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

        # limit_updated = await check_and_update_daily_limit(username)
        
        # if not limit_updated:
        #     logger.warning(f"Daily limit exceeded for user: {username}")
        #     return {
        #         "success": False,
        #         "message": "Reached your daily limit",
        #         "recommendations": []
        #     }

        urls = []
        user = User(username=current_user["username"], access_token=current_user["access_token"],extra_topics=extra_topics, languages=languages)

        user_details, languages_topics = await get_repos(user)
        if not user_details:
            logger.info("No repos found for user, generating topic-based recommendations")
            urls = await get_topic_based_recommendations(user)
        else:
            try:
                if extra_topics or languages:
                    languages_topics = {'languages': languages, 'topics': extra_topics}
                logger.info('Generating recommendations based on user details')
                urls = await recommend(user_details=user_details, languages_topics=languages_topics)
            except Exception as e:
                logger.error(f"Error generating recommendations: {str(e)}")
                urls = []

        if not urls:
            logger.info("No recommendations found")
            return {'recommendations': [], 'message': 'No recommendations found, please mention more topics or languages'}
        
        unique_recommendations = process_recommendations(urls, languages_topics)

        if not unique_recommendations:
            logger.info(f"No recommendations found for user: {username}")
            return {'recommendations': [], 'message': 'No recommendations found'}
        
        rec_name = f"Recommendations for {username} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        rec_id = append_recommendations_to_db(username, unique_recommendations, rec_name)
        logger.info(f"Recommendations saved to DB with ID: {rec_id}")


        # update_daily_limit(username) # updates the daily limit of the user.
        return {
            'recommendations': unique_recommendations[:20],
            'recommendation_id': rec_id
        }
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while generating recommendations")


@app.get('/api/user-recommendations')
async def get_user_recommendations(username: str = Query(...), current_user: dict = Depends(get_current_user)):
    try:
        if username != current_user["username"]:
            raise HTTPException(status_code=403, detail="Unauthorized access")

        user_recommendations = await get_user_previous_recommendations(username)
        if not user_recommendations:
            raise HTTPException(status_code=404, detail="No recommendations found for user")
        return user_recommendations
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching user recommendations")


@app.get("/api/recommendation/{recommendation_id}")
async def get_recommendation_by_id(recommendation_id: str):
    try:
        recommendation = await get_user_recommendation_by_id(recommendation_id)
        if not recommendation:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        return recommendation
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/recommendations_without_github')
async def get_recommendations_without_github(request: Request):
    try:
        body = await request.json()
        username = body.get("username")
        extra_topics = body.get("extra_topics", [])
        languages = body.get("languages", [])

        assert username, "Username is required"
        assert extra_topics or languages, "Extra topics or languages are required"

        username = username + generate_secure_random_string()
        languages_topics = {"languages": languages, "topics": extra_topics} # this should be topics and not extra_topics
        urls = await recommend(languages_topics=languages_topics)

        if not urls:
            logger.info("No recommendations found")
            return {'recommendations': [], 'message': 'No recommendations found, please mention more topics or languages'}
        
        unique_recommendations = process_recommendations(urls, languages_topics) #for ranking the recommendations based on the languages_topics

        if not unique_recommendations:
            logger.info(f"No recommendations found for user: {username}")
            return {'recommendations': [], 'message': 'No recommendations found'}
        
        await append_user_to_db(username)
        rec_name = f"Recommendations for {username} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        rec_id = append_recommendations_to_db(username, unique_recommendations, rec_name)
        logger.info(f"Recommendations saved to DB with ID: {rec_id}")

        return {
            'recommendations': unique_recommendations[:20],
            'recommendation_id': rec_id
        }
    
    except Exception as e:
        logger.info(f"There is an error: {e}")
        raise HTTPException(status_code=500, detail="There is an error, Couldn't fetch the recommendations")

@app.get('/api/health')
async def health_check(request: Request):
    return JSONResponse({"status": "OK"})

def generate_secure_random_string(length=7):
    """Generate a secure random string."""
    import string
    import secrets

    char_set = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(char_set) for _ in range(length))


if __name__ == '__main__':
    uvicorn.run("src.api:app", host='0.0.0.0', port=8000, reload=True)