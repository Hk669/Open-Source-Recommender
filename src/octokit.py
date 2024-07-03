import asyncio
from datetime import datetime
from typing import Optional, List


class Octokit:
    def __init__(self, auth: str, session):
        self.auth = auth
        self.session = session

    async def request(self, 
                      method: str, 
                      url: str, 
                      params: Optional[dict]=None):
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
