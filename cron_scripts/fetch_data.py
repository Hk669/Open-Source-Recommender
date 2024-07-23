import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from datetime import datetime
from aiohttp import ClientSession
from typing import Optional, List
from dotenv import load_dotenv
from src.search import search_repositories
from src.octokit import Octokit
from src.db import get_chromadb_collection, upsert_to_chroma_db
import logging

logger = logging.getLogger(__name__)

logging.basicConfig(filename='cron_scripts_new.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

async def process_query(octokit, params):
    try:
        result = await search_repositories(octokit, params)
        await asyncio.sleep(2)  # Rate limiting
        return result
    except Exception as e:
        logger.info(f"Error searching with params {params}: {e}")
        return {}

async def main(language_topics, access_token: str):
    unique_repos = {}

    async with ClientSession() as session:
        if access_token:
            octokit = Octokit(access_token, session)
        else:
            raise ValueError("Access token not found")

        languages = language_topics["languages"]
        topics = language_topics["topics"]

        logger.info("Fetching repositories using main....")

        # Process languages sequentially
        for language in languages:
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
            unique_repos.update(await process_query(octokit, help_wanted_params))

            good_first_issues_params = base_params.copy()
            good_first_issues_params['q'] += ' good-first-issues:>2'
            unique_repos.update(await process_query(octokit, good_first_issues_params))

        # Process topics sequentially
        for topic in topics:
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
            unique_repos.update(await process_query(octokit, help_wanted_params))

            good_first_issues_params = base_params.copy()
            good_first_issues_params['q'] += ' good-first-issues:>1'
            unique_repos.update(await process_query(octokit, good_first_issues_params))

    logger.info(f"Found {len(unique_repos)} unique repositories\n--------")

    chroma_db = get_chromadb_collection()
    try:
        logger.info("Upserting data to ChromaDB....")
        upsert_to_chroma_db(chroma_db, unique_repos)
    except Exception as e:
        raise Exception(f"Error upserting data to ChromaDB: {e}")
    
    return unique_repos

if __name__ == "__main__":
    access_token = os.getenv("GPAT")
    language_topics = {
        "languages": [
            "python", "java", "javascript", "c++", "c#", "ruby", "php", "go", 
            "swift", "typescript", "jupyter-notebook", "bash", 
            "c", "dart", 
            "elixir", "kotlin", "perl", "powershell", "r", "rust", 
            "scala", "shell"
        ],
        "topics": ['ai', 'llms', 'ai-agents', 'agentic-ai', 'openai', 'artificial-intelligence', 'gpt', 
                   'ai-assistant', 'machine-learning', 'transformers', 'chatbot', 'nlp', 'reinforcement-learning',
                   'docker', 'kubernetes', 'devops', 'cloud', 'aws', 'azure', 'gcp', 'serverless', 'terraform',
                   'web', 'web-development', 'web-design', 'ui', 'html', 'css', 'react', 'angular',
                   'nodejs', 'nextjs', 'express', 'flask', 'django', 'rails', 'laravel', 'spring', 'spring-boot',
                   'graphql', 'rest', 'api', 'microservices',
                   'frontend', 'backend', 'fullstack', 'software',
                   'devops', 'web3', 'blockchain', 'crypto', 'bitcoin', 'ethereum',
                   'security', 'hacking', 'pentesting', 'privacy', 'encryption',
                   'network', 'networking', 'internet-of-things', 'cloud', 'cloud-native', 'aws', 'azure', 'gcp']
    }

    start_time = datetime.now()
    result = asyncio.run(main(language_topics, access_token=access_token))
    print(f"Time taken: {datetime.now() - start_time}")