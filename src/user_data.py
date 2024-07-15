import os
import aiohttp
import asyncio
from .octokit import Octokit
from datetime import datetime
from aiohttp import ClientSession
from .models import get_user_collection
from dotenv import load_dotenv
load_dotenv()
import logging

logger = logging.getLogger(__name__)


async def get_repos(user):
    """
    Fetches the repositories of the user
    """
    user_details = []
    language_topics = {}
    
    try:
        async with ClientSession() as session:
            if not user.access_token:
                raise ValueError("Access token not found")

            octokit = Octokit(user.access_token, session)

            # To store the unique data of the user 
            languages_map = {} # store the freq of the languages
            topics_map = {}

            url = f'/users/{user.username}/repos'
            repos_data = await octokit.request('GET', url)

            repo_limit = 15
            cnt = 0

            # iterates through every repository of the user data
            for repo in repos_data:
                if cnt >= repo_limit:
                    break
                
                if not repo['fork'] and (repo['description'] or repo['language'] or len(repo['topics'])>0):
                    language_url = repo['languages_url'].replace('https://api.github.com', '')
                    languages_data = await octokit.request('GET', language_url)

                    user_repo = {
                        'project_name' : repo['name'],
                        'description' : repo['description'],
                        "related_language_or_topic": list(languages_data.keys()),
                    }
                    user_details.append(user_repo)

                    for lang in languages_data.keys():
                        languages_map[lang] = languages_map.get(lang, 0) + 1

                    for topic in repo['topics']:
                        topics_map[topic] = topics_map.get(topic, 0) + 1
                    
                    cnt += 1

            # return the top5 languages
            top5_languages = user.languages + sorted(languages_map, key=languages_map.get, reverse=True)[:5] if user.languages else sorted(languages_map, key=languages_map.get, reverse=True)[:5]
            top_topics = user.extra_topics + sorted(topics_map, key=topics_map.get, reverse=True)[:7] if user.extra_topics else sorted(topics_map, key=topics_map.get, reverse=True)[:7]
            language_topics = {"languages" : list(top5_languages), "topics" : list(top_topics)}

    except aiohttp.ClientError as e:
        logger.info(f"Error fetching data: {e}")

    return user_details, language_topics

# if __name__ == '__main__':
#     from .models import User
#     username = 'Hk669'
#     user = User(username=username, access_token=GPAT)

#     loop = asyncio.get_event_loop()
#     user_details, language_topics = loop.run_until_complete(get_repos(user))
#     loop.close()
#     print('-----')
#     print(user_details)
#     print('-----')
#     print(language_topics)
