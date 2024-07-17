import os
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


async def main(language_topics,
               access_token: str,
               ):
    unique_repos = {}

    async with ClientSession() as session:
        if access_token:
            octokit = Octokit(access_token, session)
        else:
            raise ValueError("Access token not found")

        languages = language_topics["languages"]
        topics = language_topics["topics"]
        

        tasks = []
        print("Fetching repositories using main....")
        
        for language in languages:
            try:
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
            except Exception as e:
                logger.info(f"Error searching for {language} repositories: {e}")
                continue
        

        for topic in topics:
            try:
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
            except Exception as e:
                logger.info(f"Error searching for {topic} repositories: {e}")
                continue

        results = await asyncio.gather(*tasks)
        for result in results:
            unique_repos.update(result)
        print(f"Unique Repositories: {len(unique_repos)}")
    
    logger.info(f"Found {len(unique_repos)} unique repositories\n--------")

    chroma_db = get_chromadb_collection()
    try:
        print("Upserting data to ChromaDB....")
        upsert_to_chroma_db(chroma_db, unique_repos)
    except Exception as e:
        raise Exception(f"Error upserting data to ChromaDB: {e}")
    
    return unique_repos


if __name__ == "__main__":
    load_dotenv()
    access_token = os.getenv("GITHUB_ACCESS_TOKEN")
    # mention almost all the languages and topics

    language_topics = {
        "languages": [
            "python", "java", "javascript", "c++", "c#", "ruby", "php", "go", 
            "swift", "typescript", "jupyter-notebook", "assembly", "bash", 
            "c", "clojure", "cobol", "coffeescript", "crystal", "d", "dart", 
            "elixir", "elm", "erlang", "f#", "fortran", "groovy", "haskell", 
            "haxe", "julia", "kotlin", "lisp", "lua", "matlab", "nim", "objective-c", 
            "ocaml", "pascal", "perl", "powershell", "r", "racket", "rust", 
            "scala", "scheme", "shell", "smalltalk", "solidity", "sql", "tcl", 
            "vb.net", "vhdl", "visual-basic", "wolfram", "zig"
        ],
        "topics": ['ai', 'llms', 'ai-agents', 'agentic-ai', 'openai', 'artificial-intelligence', 'gpt', 
                   'ai-assistant', 'machine-learning', 'transformers', 'chatbot', 'nlp', 'reinforcement-learning',
                   'docker', 'kubernetes', 'devops', 'cloud', 'aws', 'azure', 'gcp', 'serverless', 'terraform',
                   'web', 'web-development', 'web-design', 'ui', 'html', 'css', 'javascript', 'react', 'angular',
                   'nodejs', 'nextjs', 'express', 'flask', 'django', 'rails', 'laravel', 'spring', 'spring-boot', 'strapi',
                   'graphql', 'rest', 'api', 'microservices', 'server', 'server-side', 'client', 'client-side',
                   'frontend', 'backend', 'fullstack', 'dev', 'developer', 'development', 'software', 'engineering',
                   'devops', 'web3', 'blockchain', 'crypto', 'cryptocurrency', 'bitcoin', 'ethereum', 'solidity',
                   'security', 'cybersecurity', 'hacking', 'pentesting', 'privacy', 'encryption', 'cryptography',
                   'network', 'networking', 'iot', 'internet-of-things', 'cloud', 'cloud-computing', 'cloud-native']
    }

    start_time = datetime.now()
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(main(language_topics, access_token=access_token))
    print(f"Time taken: {datetime.now() - start_time}")

