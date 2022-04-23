import asyncio
from argparse import ArgumentParser

from django.core.management import BaseCommand

from site_crawler.crawl_lib import Crawler


class Command(BaseCommand):
    help = 'Crawl url'

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument('--max-depth', type=int, default=3)
        parser.add_argument('url')

    def handle(self, url: str, max_depth: int, *args, **options):
        crawler = Crawler(url)
        loop = asyncio.get_event_loop()
        urls = loop.run_until_complete(crawler.get_hrefs_recursively(max_depth=max_depth))
        for url in urls:
            print(url)
