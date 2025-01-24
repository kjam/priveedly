from sites.models import Subreddit, RedditPost, SitePost
from django.conf import settings

import logging
import praw
import pytz
import random
import requests

from hackernews import HackerNews
from datetime import datetime, timedelta, timezone

logging.basicConfig(filename='/var/log/priveedly/parse.log',
                    encoding='utf-8',
                    level=logging.INFO,
                    datefmt='%Y-%m-%d %H:%M:%S')

def parse_all_subreddits():
    all_subreddits = Subreddit.objects.all()
    for subreddit in all_subreddits:
        try:
            parse_reddit(subreddit)
        except Exception as e:
            logging.error(e)
            logging.error('Error parsing subreddit {}'.format(subreddit))
    logging.info('Finished parsing {} subreddits.'.format(
        len(all_subreddits)))


def get_lobster_posts(url="https://lobste.rs/hottest.json"):
    return [r for r in requests.get(url).json()]

def parse_lobsters():
    entry_count = 0
    posts = get_lobsters_posts()
    filter_date = datetime.now().replace(tzinfo=timezone.utc) - timedelta(days=120)
    for post in posts:
        if not SitePost.objects.filter(published__gte=filter_date, url=post.get('url')):
            e = SitePost(
                    entry_category='LS',
                    site_name='lobsters',
                    title=post.get('title')[:354],
                    url=post.get('url'),
                    description=post.get('description') + ' Tags: {}'.format(
                        ' '.join(post.get('tags'))),
                    published=post.get('created_at'),
                )
            e.save()
            entry_count += 1
    logging.info("Parsed lobsters and found {} new items".format(entry_count))


def get_text(hn_item):
    if hasattr(hn_item, 'text'):
        return hn_item.text
    return ''


def parse_hackernews():
    entry_count = 0
    hn = HackerNews()
    stories = [hn.item(x) for x in hn.top_stories()]
    filter_date = datetime.now().replace(tzinfo=timezone.utc) - timedelta(days=120)

    for post in stories:
        if not hasattr(post, 'url'):
            continue
        if not SitePost.objects.filter(published__gte=filter_date, url=post.url):
            text = post.title[:354]
            if hasattr(post, 'text'):
                text = post.text
            elif hasattr(post, 'kids'):
                sample_size = (lambda y: len(y) if len(y) < 4 else 4)(post.kids)
                text = '\n '.join(
                        [get_text(hn.item(x)) for x in
                            random.sample(post.kids, sample_size)])
            e = SitePost(
                    entry_category='HN',
                    site_name='hackernews',
                    title=post.title,
                    url=post.url,
                    description=text,
                    published=pytz.utc.localize(post.time)
                )
            e.save()
            entry_count += 1
    logging.info("Parsed hackernews and found {} new items".format(entry_count))


def get_praw():
    return praw.Reddit(
            client_id=settings.REDDIT_CLIENT_ID,
            client_secret=settings.REDDIT_CLIENT_SECRET,
            password=settings.REDDIT_PASSWORD,
            user_agent=settings.REDDIT_USER_AGENT,
            username=settings.REDDIT_USERNAME)

def parse_reddit(subreddit):
    entry_count = 0
    api = get_praw()
    posts = api.subreddit(subreddit.name).new(limit=500)
    filter_date = datetime.now().replace(tzinfo=timezone.utc) - timedelta(days=120)

    for post in posts:
        if not RedditPost.objects.filter(published__gte=filter_date, url=post.url):
            pub_date = pytz.utc.localize(datetime.utcfromtimestamp(post.created_utc))
            if pub_date <= filter_date:
                continue
            text = post.selftext
            if not text:
                sample_size = (lambda y: len(y) if
                        len(y) < 4 else 4)(list(post.comments))
                text = '\n '.join(
                        [comment.body for comment in
                            random.sample(list(post.comments), sample_size)])

            e = RedditPost(
                    entry_category='RD',
                    subreddit=subreddit,
                    title=post.title[:354],
                    url=post.url,
                    description=text,
                    published=pub_date
                )
            e.save()
            entry_count += 1

    subreddit.updated = pytz.utc.localize(datetime.utcnow())
    subreddit.save()
    logging.info("Parsed subreddit: {} and found {} new items".format(
            subreddit.name,
            entry_count))
