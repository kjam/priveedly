from feeds.models import Feed, FeedEntry

import feedparser
import logging
import pytz

from datetime import datetime, timedelta, timezone
from dateutil import parser as date_parser
from django.utils.timezone import is_aware
from lxml.html import fromstring


logging.basicConfig(filename='/var/log/priveedly/parse.log',
                    encoding='utf-8',
                    level=logging.INFO,
                    datefmt='%Y-%m-%d %H:%M:%S')

def test_feeds_for_zombies():
    all_feeds = Feed.objects.filter(is_alive=True)
    zombies = 0
    utcnow = pytz.utc.localize(datetime.utcnow())
    for feed in all_feeds:
        if feed.last_entry < utcnow - timedelta(days=90):
            feed.is_alive = False
            feed.save()
            zombies += 1
    logging.info('Found {} zombies.'.format(zombies))


def parse_all_feeds():
    all_feeds = Feed.objects.filter(is_alive=True)
    for feed in all_feeds:
        try:
            parse_feed(feed)
        except Exception as e:
            logging.error(e)
            logging.error('Problem parsing %s' % feed)
    logging.info('Finished parsing {} feeds.'.format(len(all_feeds)))

def get_pub_date(entry):
    if hasattr(entry, 'published'):
        pub_date = date_parser.parse(entry.published)
    elif hasattr(entry, 'updated'):
        pub_date = date_parser.parse(entry.updated)
    else:
        pub_date = pytz.utc.localize(datetime.utcnow())

    if not is_aware(pub_date):
        pub_date = pytz.utc.localize(pub_date)

    return pub_date

def get_title(entry):
    if hasattr(entry, 'title'):
        return entry.title[:354]
    return 'no title'

def get_description(entry):
    # this prefers HTML and longer content over shorter !!
    if hasattr(entry, 'content'):
        if len(entry.content) == 1:
            return entry.content[0]['value']
        else:
            for ec in entry.content:
                if 'html' in ec['type']:
                    return ec['value']
            return ec['value']            # default if no html
    elif hasattr(entry, 'description'):
        return entry.description
    return 'no description'

def get_image(description):
    doc = fromstring(description)
    for pattern in ['//img/@src', '//img/@src']:
        images = doc.xpath(pattern)
        if len(images):
            return images[0]

def parse_feed(feed):
    entry_count = 0
    entries = feedparser.parse(feed.url)
    for entry in entries.entries:
        pub_date = get_pub_date(entry)

        # this speeds up queries once you have many entries
        filter_date = datetime.now().replace(tzinfo=timezone.utc) - timedelta(days=120)
        if not FeedEntry.objects.filter(published__gte=filter_date, url=entry.link) and pub_date >= filter_date:
            title = get_title(entry)
            desc = get_description(entry)

            e = FeedEntry(
                    feed=feed,
                    title=title,
                    url=entry.link,
                    description=desc,
                    entry_category='RS',
                    published=pub_date,
                )

            img = get_image(desc)
            if img:
                e.image_url = img

            e.save()
            entry_count += 1
            if not feed.last_entry or e.published > feed.last_entry:
                feed.last_entry = e.published

    feed.updated = pytz.utc.localize(datetime.utcnow())
    feed.save()
    logging.info("Parsed feed: {} and found {} new items".format(
            feed.title,
            entry_count))
