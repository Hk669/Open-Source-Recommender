import os
import asyncio
from datetime import datetime
from aiohttp import ClientSession
from typing import Optional, List
from dotenv import load_dotenv
load_dotenv()

GPAT = os.getenv('GPAT')


class Octokit:
    def __init__(self, auth: str, session):
        self.auth = auth
        self.session = session


    async def request(self, method: str, url: str, params: Optional[dict]=None):
        headers = {
            'Authorization': 'BEARER ' + self.auth,
            'Accept': 'application/vnd.github+json',
        }

        url = 'https://api.github.com' + url

        while True:
            async with self.session.request(method, url, headers=headers, params=params) as response:
                if response.status == 403:
                    reset_time = datetime.fromtimestamp(int(response.headers["X-RateLimit-Reset"]))
                    sleep_time = (reset_time - datetime.now()).total_seconds() + 5
                    await asyncio.sleep(sleep_time)
                else:
                    response.raise_for_status()
                    return await response.json()


async def search_repositories(octokit: Octokit, params: Optional[dict]):
    response = await octokit.request('GET', '/search/repositories', params)
    unique_repos = {}

    while len(response['items']) > 0 and params['page'] <= 3:
        for item in response['items']:
            if item['id'] not in unique_repos:
                unique_repos[item['id']] = {
                    "full_name": item['full_name'],
                    "description": item['description']
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
            print(f"Searching for {language} repositories")
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
            print(f"Searching for {topic} repositories")
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
    
    print(f"Found {len(unique_repos)} unique repositories")
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


    for repo_id, repo_info in result.items():
        print(f"Repository ID: {repo_id}")
        print(f"Full Name: {repo_info['full_name']}")
        print(f"Description: {repo_info['description']}")
        print("---------------------------")
