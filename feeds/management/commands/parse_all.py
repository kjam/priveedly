from django.core.management.base import BaseCommand
from feeds.management_commands import parse_all_feeds
from sites.management_commands import parse_lobsters, parse_hackernews, parse_all_subreddits

from datetime import datetime
import logging


logging.basicConfig(filename='/var/log/priveedly/parse.log',
                    encoding='utf-8',
                    level=logging.INFO,
                    datefmt='%Y-%m-%d %H:%M:%S')

class Command(BaseCommand):


    def handle(self, *args, **kwargs):
        start = datetime.now()
        try:
            parse_all_feeds()
        except Exception as e:
            logging.error('feed error {}'.format(e))
        try:
            parse_all_subreddits()
        except Exception as e:
            logging.error('reddit error {}'.format(e))
        try:
            parse_hackernews()
        except Exception as e:
            logging.error('hackernews error {}'.format(e))
        try:
            parse_lobsters()
        except Exception as e:
            logging.error('lobsters error {}'.format(e))
        logging.info('finished parsing in {}'.format(datetime.now() - start))
