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


@app.post('/recommendations/')
async def get_recommendations(request : User) -> dict:
    username = request.username

    try:
        user_details, language_topics = await get_repos(username)
        unique_repos = await main(language_topics)

        urls = recommend(user_details,unique_repos)
        return {'recommendations': urls}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail = 'Error generating recommendatoins')
        

async def main():
    uvicorn.run(app, host='0.0.0.0', port=8000)


if __name__ == '__main__':
    asyncio.run(main())