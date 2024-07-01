import os
import aiohttp
import asyncio
from src.search import Octokit
from datetime import datetime
from aiohttp import ClientSession
from dotenv import load_dotenv
load_dotenv()

GPAT = os.getenv('GPAT')

async def get_repos(username: str):
    user_details = []
    language_topics = {}
    
    try:
        async with ClientSession() as session:
            octokit = Octokit(GPAT, session)

        # To store the unique data of the user 
            languages_set = set()
            topics_set = set()

            url = f'/users/{username}/repos'
            repos_data = await octokit.request('GET', url)

            # iterates through every repository of the user data
            for repo in repos_data:
                if not repo['fork'] and (repo['description'] or repo['language'] or len(repo['topics'])>0):
                    language_url = repo['languages_url'].replace('https://api.github.com', '')
                    languages_data = await octokit.request('GET', language_url)

                    user_repo = {
                        'project_name' : repo['name'],
                        'description' : repo['description'],
                    }
                    user_details.append(user_repo)

                    languages_set.update(languages_data.keys())
                    topics_set.update(repo['topics'])

            language_topics = {"languages" : list(languages_set), "topics" : list(topics_set)}

    except aiohttp.ClientError as e:
        print(f"Error fetching data: {e}")

    return user_details, language_topics

if __name__ == '__main__':
    username = 'Hk669'
    loop = asyncio.get_event_loop()
    user_details, language_topics = loop.run_until_complete(get_repos(username))
    loop.close()
    print('-----')
    print(user_details)
    print('-----')
    print(language_topics)
