""" Site crawler lib """
import aiohttp
import asyncio
import logging
from typing import Iterable, Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup

log = logging.getLogger('crawler.crawl_lib')


class Crawler:
    def __init__(self, url: str):
        self._url = url

    async def _get_site_hrefs(
        self,
        session: aiohttp.ClientSession,
        url: str,
    ) -> Iterable[str]:
        try:
            async with session.get(url) as resp:
                if resp.content_type != 'text/html':
                    return []
                text = await resp.text()
        except aiohttp.ClientError:
            log.exception('Cannot fetch url {}'.format(url))
            return []

        soup = BeautifulSoup(text, features="html.parser")
        return (a['href'] for a in soup.find_all('a', href=True))

    @staticmethod
    def _abs_url(base_url, href) -> Optional[str]:
        """
        Parses href into absolute URL relative to base_url.
        Returns None if url is just a fragment.
        """
        if href.startswith('#'):
            return None
        base_url_parse = urlparse(base_url)
        href_parse = urlparse(href)
        if base_url_parse.path:
            return '{scheme}://{netloc}{path}{params}{query}'.format(
                scheme=href_parse.scheme or base_url_parse.scheme,
                netloc=href_parse.netloc or base_url_parse.netloc,
                path=href_parse.path,
                params=';' + href_parse.params if href_parse.params else '',
                query='?' + href_parse.query if href_parse.query else '',
            )

    async def _load_hrefs(
        self,
        session: aiohttp.ClientSession,
        url: str,
        depth_left: int,
        hrefs: set[str],
        visited: set[str],
    ):
        """
        Loads hrefs from url recursively
        """
        print('Loading hrefs from {} {}'.format(url, depth_left))
        log.debug('Loading hrefs from {}'.format(url))
        current_hrefs = await self._get_site_hrefs(session, url)

        to_visit = []
        for href in current_hrefs:
            hrefs.add(href)
            abs_href = self._abs_url(url, href)
            if abs_href and abs_href not in visited:
                visited.add(abs_href)
                to_visit.append(abs_href)

        # Run next level of recursion
        next_depth_left = depth_left - 1
        if next_depth_left:
            await asyncio.wait([
                asyncio.create_task(self._load_hrefs(
                    session=session,
                    url=url,
                    depth_left=next_depth_left,
                    hrefs=hrefs,
                    visited=visited,
                ))
                for url in to_visit
            ])

    async def get_hrefs_recursively(self, max_depth: int) -> set[str]:
        """ Get all hrefs from crawler URL recursively with max_depth """
        hrefs = set()
        visited = set()
        timeout = aiohttp.ClientTimeout(total=5.0)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            await self._load_hrefs(
                session=session,
                url=self._url,
                depth_left=max_depth,
                hrefs=hrefs,
                visited=visited,
            )
        return visited
