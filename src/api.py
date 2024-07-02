from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
from src.user_data import get_repos
from src.search import main
from chroma.db import recommend
import asyncio

app = FastAPI()

class User(BaseModel):
    username:str
    extra_topics: list = []


@app.post('/recommendations/')
async def get_recommendations(user: User) -> dict:
    username = user.username
    extra_topics = user.extra_topics or []

    try:
        print(f'Fetching recommendations for {username}')
        user_details, language_topics = await get_repos(username)
        print(f'--------\n{user_details}')
        print(f'--------\n{language_topics}')
        unique_repos = await main(language_topics, extra_topics)
        print(f'--------\n{unique_repos}')
        # urls = recommend(user_details,unique_repos)
        return {'recommendations': unique_repos}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail = 'Error generating recommendatoins')
        

async def run_server():
    uvicorn.run(app, host='0.0.0.0', port=8000)


if __name__ == '__main__':
    asyncio.run(run_server())