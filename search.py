import asyncio
from datetime import datetime
from aiohttp import ClientSession

class Octokit:
    def __init__(self, auth, session):
        self.auth = auth
        self.session = session


    async def request(self, method, url, params=None):
        headers = {
            'Authorization': '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 ' + self.auth,
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

async def search_repositories(octokit, params):
    response = await octokit.request('GET', '/search/repositories', params)
    unique_repos = {}

    while len(response['items']) > 0 and params['page'] <= 10:
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
async def main(language_topics):
    unique_repos = {}

    async with ClientSession() as session:
        octokit = Octokit('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', session)

        languages = language_topics['languages']
        topics = language_topics['topics']

        tasks = []

        for language in languages:
            base_params = {
                'q': f'stars:>=2000 forks:>=500 language:{language} pushed:>=2023-01-01',
                'sort': 'stars',
                'order': 'desc',
                'per_page': 100,
                'page': 1,
            }

            help_wanted_params = base_params.copy()
            help_wanted_params['q'] += ' help-wanted-issues:>=1'
            tasks.append(asyncio.create_task(search_repositories(octokit, help_wanted_params)))

            good_first_issues_params = base_params.copy()
            good_first_issues_params['q'] += ' good-first-issues:>=1'
            tasks.append(asyncio.create_task(search_repositories(octokit, good_first_issues_params)))

        for topic in topics:
            base_params = {
                'q': f'stars:>=2000 forks:>=500 topic:{topic} pushed:>=2023-01-01',
                'sort': 'stars',
                'order': 'desc',
                'per_page': 100,
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

    return unique_repos

# Define the get_projects function
async def get_projects(language_topics):
    return await main(language_topics)


# Usage example
language_topics = {
    'languages': ['python', 'javascript'],
    'topics': ['machine-learning', 'web-development']
}

# Call the get_projects function to retrieve the repositories
result = asyncio.run(get_projects(language_topics))

# Print the retrieved repositories
for repo_id, repo_info in result.items():
    print(f"Repository ID: {repo_id}")
    print(f"Full Name: {repo_info['full_name']}")
    print(f"Description: {repo_info['description']}")
    print("---------------------------")