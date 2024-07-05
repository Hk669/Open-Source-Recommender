import os
import asyncio
from datetime import datetime
from aiohttp import ClientSession
from typing import Optional, List
from dotenv import load_dotenv
from src.db import get_or_create_chromadb_collection, upsert_to_chroma_db
from .octokit import Octokit
import logging

load_dotenv()

logger = logging.getLogger(__name__)

GPAT = os.getenv('GPAT')

async def search_repositories(octokit: Octokit, 
                              params: Optional[dict]):
    unique_repos = {}
    try:
        response = await octokit.request('GET', '/search/repositories', params)
    except Exception as e:
        raise Exception(f"Error fetching data: {e}")
    
    while len(response['items']) > 0 and params['page'] <= 3:
        for item in response['items']:
            if item['id'] not in unique_repos:
                language = params["q"].split('language:')[1].split(' ')[0] if 'language:' in params["q"] else ""
                topic = params["q"].split('topic:')[1].split(' ')[0] if 'topic:' in params["q"] else ""

                if language:
                    related = language
                elif topic:
                    related = topic
                else:
                    related = "Others"

                unique_repos[item['id']] = {
                    "full_name": item['full_name'],
                    "description": item['description'],
                    "related_language_or_topic": related,
                }

        params['page'] += 1
        response = await octokit.request('GET', '/search/repositories', params)

    return unique_repos

# Define the main function
async def main(language_topics, 
               extra_topics: List = None,
               extra_languages: List = None):
    unique_repos = {}

    async with ClientSession() as session:
        octokit = Octokit(GPAT, session)

        languages = extra_languages + language_topics['languages'] if extra_languages else language_topics['languages']
        topics = extra_topics + language_topics['topics'] if extra_topics else language_topics['topics']

        tasks = []

        for language in languages[:5]:
            logger.info(f"Searching for {language} repositories")
            base_params = {
                'q': f'stars:>=2000 forks:>=500 language:{language} pushed:>=2024-01-01',
                'sort': 'stars',
                'order': 'desc',
                'per_page': 7,
                'page': 1,
            }

            help_wanted_params = base_params.copy()
            help_wanted_params['q'] += ' help-wanted-issues:>=1'
            tasks.append(asyncio.create_task(search_repositories(octokit, help_wanted_params)))

            good_first_issues_params = base_params.copy()
            good_first_issues_params['q'] += ' good-first-issues:>=1'
            tasks.append(asyncio.create_task(search_repositories(octokit, good_first_issues_params)))

        for topic in topics[:7]:
            logger.info(f"Searching for {topic} repositories")
            base_params = {
                'q': f'stars:>=2000 forks:>=500 topic:{topic} pushed:>=2024-01-01',
                'sort': 'stars',
                'order': 'desc',
                'per_page': 7,
                'page': 1,
            }

            help_wanted_params = base_params.copy()
            help_wanted_params['q'] += ' help-wanted-issues:>=1'
            tasks.append(asyncio.create_task(search_repositories(octokit, help_wanted_params)))

            good_first_issues_params = base_params.copy()
            good_first_issues_params['q'] += ' good-first-issues:>=1'
            tasks.append(asyncio.create_task(search_repositories(octokit, good_first_issues_params)))

        results = await asyncio.gather(*tasks)
        for result in results:
            unique_repos.update(result)
    
    logger.info(f"Found {len(unique_repos)} unique repositories\n--------")

    chroma_db = get_or_create_chromadb_collection()
    try:
        upsert_to_chroma_db(chroma_db, unique_repos)
    except Exception as e:
        raise Exception(f"Error upserting data to ChromaDB: {e}")
    
    return unique_repos


if __name__ == '__main__':
    language_topics = {'languages': ['Jupyter Notebook', 'Python', 'C++', 'go'], 
                       'topics': ['openai', 'llm-agent', 'agentic-agi', 'agentic']}
    
    import time

    start = time.time()
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(main(language_topics))
    loop.close()
    end = time.time()
    print(f"Time taken: {end - start:.2f} seconds")

    print('------')
    print(result)
