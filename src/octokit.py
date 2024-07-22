import asyncio
from datetime import datetime
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


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
                    if "X-RateLimit-Reset" in response.headers:
                        reset_time = datetime.fromtimestamp(int(response.headers["X-RateLimit-Reset"]))
                        sleep_time = (reset_time - datetime.now()).total_seconds() + 5
                        logging.warning(f"Rate limit exceeded. Sleeping for {sleep_time} seconds.")
                        await asyncio.sleep(sleep_time)
                    else:
                        logging.error("Rate limit exceeded but no 'X-RateLimit-Reset' header found.")
                        response.raise_for_status()
                else:
                    response.raise_for_status()
                    return await response.json()
