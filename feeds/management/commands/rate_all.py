from django.core.management.base import BaseCommand

import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import urlparse
from nltk.corpus import stopwords
from nltk import tokenize
import re
import string
import html
import logging
import joblib

from sites.models import RedditPost, SitePost
from feeds.models import FeedEntry
from bs4 import BeautifulSoup

import os
from dotenv import load_dotenv, dotenv_values
load_dotenv()

import nltk
nltk.download('stopwords')
nltk.download('punkt_tab')

logging.basicConfig(filename='/var/log/priveedly/rate.log',
                    encoding='utf-8',
                    level=logging.INFO,
                    datefmt='%Y-%m-%d %H:%M:%S')

CLEAN_HTML = re.compile('<.*?>')
CLEAN_NUMBERS = re.compile('[0-9,\\.$\\%]+')
CLEAN_NUMBERS_AND_ONE_LETTER = re.compile('([a-z]\\d+)|(\\d+[a-z])|(\\d+[a-z]\\d+)')
CLEAN_REPEATED_PUNCTUATION = re.compile('[!\\-\\/:-@-`’–{-~"“”\\[\\]]+')

def tokenize_url(url_str):
    parsed_url = urlparse(url_str)
    return parsed_url.netloc, ' '.join(parsed_url.path.split('/')).replace('-', ' '), parsed_url.query.replace('?', ' ').replace('=', ' ')

def prepare_content(pandas_row):
    netloc, path, query = tokenize_url(pandas_row.url)
    return ' '.join([pandas_row.title, pandas_row.description, pandas_row.site_name, netloc, path, query])

# Update this if you change preprocessing!
def remove_tags_and_lowercase(text):
    # some parts from https://stackoverflow.com/questions/9662346/python-code-to-remove-html-tags-from-a-string
    if BeautifulSoup(text, "html.parser").find():
        try:
            soup = BeautifulSoup(text)
            text = soup.get_text()
        except:
            pass
    cleantext = html.unescape(text).encode('unicode_escape').decode('unicode_escape')
    # you can try this line or other similar things  if you want to be more deliberate about cleaning!
    #cleantext = re.sub(CLEAN_NUMBERS_AND_ONE_LETTER, '', cleantext)
    cleantext = re.sub(CLEAN_NUMBERS, '', cleantext)
    cleantext = re.sub(CLEAN_REPEATED_PUNCTUATION, '', cleantext)
    return cleantext.lower()

# Update this if you change preprocessing!
def tokenize_content(text):
    removal = set(stopwords.words('english')).union(set(string.punctuation))
    return [w for w in tokenize.word_tokenize(remove_tags_and_lowercase(text))
            if w.lower() not in removal]


def get_engine():
    db_str = "postgresql://{}:{}@localhost:5432/{}".format(
        os.environ.get('DB_USERNAME'),
        os.environ.get('DB_PASSWORD'),
        os.environ.get('DB_NAME'))
    return create_engine(db_str)

# Update this if you change preprocessing!
def create_content_df(engine):
    sites_df = pd.read_sql(
        "select id, title, url, description, site_name from sites_sitepost WHERE read is False and interesting is False",
        con=engine)
    sites_df['type'] = 'sites'
    feeds_df = pd.read_sql(
        "select feeds_feedentry.id as id, feeds_feedentry.title as title, feeds_feedentry.url as url, feeds_feedentry.description as description, feeds_feed.title as site_name from feeds_feedentry JOIN feeds_feed ON feeds_feed.id = feed_id WHERE read is False and interesting is False",
        con=engine)
    feeds_df['type'] = 'feeds'
    reddit_df = pd.read_sql(
        "select sites_redditpost.id as id, sites_redditpost.title as title, sites_redditpost.url as url, sites_redditpost.description as description, sites_subreddit.name as site_name from sites_redditpost JOIN sites_subreddit ON sites_redditpost.id = sites_subreddit.id  WHERE read is False and interesting is False",
        con=engine)
    reddit_df['type'] = 'reddit'
    return pd.concat([reddit_df, sites_df, feeds_df])


def update_score(pandas_row):
    if pandas_row.type == 'sites':
        obj = SitePost.objects.get(pk=pandas_row.id)
    elif pandas_row.type == 'feeds':
        obj = FeedEntry.objects.get(pk=pandas_row.id)
    else:
        obj = RedditPost.objects.get(pk=pandas_row.id)
    obj.recommended = pandas_row.y
    obj.save()


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        try:
            # Update this if you change preprocessing!
            engine = get_engine()
            content_df = create_content_df(engine)
            logging.info('about to rate {} items'.format(content_df.shape[0]))
            content_df['full_text'] = content_df.apply(prepare_content, axis=1)
            content_df['cleaned_text'] = content_df['full_text'].map(lambda x: ' '.join(tokenize_content(x)))
            pipeline = joblib.load(os.getenv('PIPELINE_FILE'))
            if hasattr(pipeline, 'predict_proba'):
                proba = pipeline.predict_proba(content_df['cleaned_text'])
                # take only positive class
                y = proba[:, 1]
            else:
                y = pipeline.predict(content_df['cleaned_text'])
            content_df['y'] = y
            content_df.apply(update_score, axis=1)
        except Exception as e:
            logging.exception(e)
            logging.debug('failed to rate incoming content')
