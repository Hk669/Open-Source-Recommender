import os
import asyncio
from datetime import datetime
from aiohttp import ClientSession
from typing import Optional, List
from dotenv import load_dotenv
from src.db import get_chromadb_collection, upsert_to_chroma_db
from .octokit import Octokit
from .models import get_user_collection
import logging

load_dotenv()

logger = logging.getLogger(__name__)

logging.basicConfig(filename='repository_search.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

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
                
                topics = item.get('topics', [])
                topics_str = ", ".join(topics) if topics else ""

                unique_repos[item['id']] = {
                    "full_name": item.get('full_name'),
                    "description": item.get('description'),
                    "related_language_or_topic": related,
                    "stargazers_count": item.get('stargazers_count'),
                    "forks_count": item.get('forks_count'),
                    "open_issues_count": item.get('open_issues_count'),
                    "avatar_url": item.get('owner', {}).get('avatar_url'),
                    "language": item.get('language'),
                    "updated_at": item.get('updated_at'),
                    "topics": topics_str
                }

        params['page'] += 1
        response = await octokit.request('GET', '/search/repositories', params)
        logging.info(f"Page: {params['page'] - 1}, Repositories: {response['items']}")

    logging.info(f"Unique Repositories: {unique_repos}")
    return unique_repos

# Define the main function
async def main(language_topics,
               access_token: str,
               extra_topics: List = None,
               extra_languages: List = None,
               ):
    unique_repos = {}

    async with ClientSession() as session:
        if access_token:
            octokit = Octokit(access_token, session)
        else:
                # octokit = Octokit(GPAT, session)
            raise ValueError("Access token not found")
        # octokit = Octokit(GPAT, session)

        languages = language_topics["languages"] if language_topics["languages"] else []
        languages = extra_languages + languages if extra_languages else languages
        topics = extra_topics + languages if extra_topics else languages

        tasks = []
        print("Fetching repositories using main....")
        for language in languages[:5]:
            logger.info(f"Searching for {language} repositories")
            base_params = {
                'q': f'stars:>=2000 forks:>=500 language:{language} pushed:>=2024-03-01',
                'sort': 'stars',
                'order': 'desc',
                'per_page': 7,
                'page': 1,
            }

            help_wanted_params = base_params.copy()
            help_wanted_params['q'] += ' help-wanted-issues:>2'
            tasks.append(asyncio.create_task(search_repositories(octokit, help_wanted_params)))

            good_first_issues_params = base_params.copy()
            good_first_issues_params['q'] += ' good-first-issues:>2'
            tasks.append(asyncio.create_task(search_repositories(octokit, good_first_issues_params)))

        for topic in topics[:7]:
            logger.info(f"Searching for {topic} repositories")
            base_params = {
                'q': f'stars:>=2000 forks:>=500 topic:{topic} pushed:>2024-01-01',
                'sort': 'stars',
                'order': 'desc',
                'per_page': 7,
                'page': 1,
            }

            help_wanted_params = base_params.copy()
            help_wanted_params['q'] += ' help-wanted-issues:>1'
            tasks.append(asyncio.create_task(search_repositories(octokit, help_wanted_params)))

            good_first_issues_params = base_params.copy()
            good_first_issues_params['q'] += ' good-first-issues:>1'
            tasks.append(asyncio.create_task(search_repositories(octokit, good_first_issues_params)))

        results = await asyncio.gather(*tasks)
        for result in results:
            unique_repos.update(result)
        print(f"Unique Repositories: {unique_repos}")
    
    logger.info(f"Found {len(unique_repos)} unique repositories\n--------")

    chroma_db = get_chromadb_collection()
    try:
        print("Upserting data to ChromaDB....")
        upsert_to_chroma_db(chroma_db, unique_repos)
    except Exception as e:
        raise Exception(f"Error upserting data to ChromaDB: {e}")
    
    return unique_repos


if __name__ == '__main__':
    language_topics = {'languages': ['Python'], 
                       'topics': ['llm-agent', 'agentic-agi', 'agentic']}
    
    import time

    start = time.time()
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(main(language_topics, access_token=GPAT))
    loop.close()
    end = time.time()
    print(f"Time taken: {end - start:.2f} seconds")

