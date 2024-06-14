"""
@author : Hrushikesh Dokala
username : Hk669
"""


from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
from src.user_data import get_repos
from src.search import get_projects
from chroma.db import recommend
import asyncio

app = FastAPI()

class User(BaseModel):
    username:str


@app.post('/osrecommender')
async def get_recommendations(request : User) -> dict:
    username = request.username

    try:
        user_details, language_topics = await get_repos(username)
        unique_repos =await get_projects(language_topics)

        urls = recommend(user_details,unique_repos)
        return {'recommendations': urls}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail = 'Error generating recommendatoins')
        

async def main():
    uvicorn.run(app,host='127.0.0.1',port=8000)


if __name__ == '__main__':
    asyncio.run(main())