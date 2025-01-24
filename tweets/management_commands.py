# NOTE: no longer tested or maintained due to change in Twitter/X API

from tweets.models import Tweet, TwitterList
from django.conf import settings

import logging
import pytz
import tweepy

from datetime import datetime, timedelta

logging.basicConfig(filename='/var/log/priveedly/parse.log', encoding='utf-8', level=logging.INFO)

def parse_all_lists():
    all_lists = TwitterList.objects.all()
    for twlist in all_lists:
        try:
            parse_list(twlist)
        except Exception as e:
            logging.error(e)
            logging.error('error parsing %s' % twlist)
    logging.info('Finished parsing {} lists.'.format(len(all_lists)))

def get_twitter_api():
    auth = tweepy.OAuthHandler(
            settings.TWITTER_CONSUMER_KEY,
            settings.TWITTER_CONSUMER_SECRET)
    auth.set_access_token(
            settings.TWITTER_ACCESS_TOKEN,
            settings.TWITTER_ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth)
    return api

def parse_list(twlist):
    entry_count = 0
    api = get_twitter_api()
    if twlist.since_id != 0:
        tweets = api.list_timeline(
            list_id=twlist.list_id,
            count=400,
            since_id=twlist.since_id)
    else:
        tweets = api.list_timeline(
            list_id=twlist.list_id,
            count=400)

    for tweet in tweets:
        url = 'https://twitter.com/{}/status/{}'.format(
                tweet.user.screen_name,
                tweet.id)
        if not Tweet.objects.filter(url=url):
            e = Tweet(
                    entry_category='TW',
                    twitter_list=twlist,
                    title='@{}: {}...'.format(
                        tweet.user.screen_name,
                        tweet.text[:40]),
                    url=url,
                    description=tweet.text,
                    published=tweet.created_at
                )
            if 'media' in tweet.entities:
                e.image_url = tweet.entities['media'][0]['media_url']

            e.save()
            entry_count += 1
            if not twlist.since_id or tweet.id > twlist.since_id:
                twlist.last_entry = e.published
                twlist.since_id = tweet.id

    twlist.updated = pytz.utc.localize(datetime.utcnow())
    twlist.save()
    logging.info("Parsed Twitter list: {} and found {} new items".format(
            twlist.name,
            entry_count))
