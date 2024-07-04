from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from .user_data import get_repos
from chroma.db import recommend, get_topic_based_recommendations
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  #TODO: Update this to the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class User(BaseModel):
    username: str
    extra_topics: list[str] = []
    languages: list[str] = []


@app.post('/recommendations/')
async def get_recommendations(user: User) -> dict:
    try:
        if user.username:
            # Existing logic for users with GitHub repos
            user_details, language_topics = await get_repos(user.username)
            if not user_details:
                print("No repos found for user")
                # Fall back to topic-based recommendations if no repos found
                return get_topic_based_recommendations(user)
            urls = recommend(user_details)
        else:
            raise Exception("No username provided")

        if not urls:
            return {'recommendations': [], 'message': 'No recommendations found'}
        
        return {'recommendations': urls}
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
        

async def run_server():
    uvicorn.run(app, host='0.0.0.0', port=8000)


if __name__ == '__main__':
    asyncio.run(run_server())