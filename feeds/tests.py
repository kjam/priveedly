import unittest
from django.contrib.auth.models import User
from django.test import TestCase, Client
from feeds.models import FeedCategory, Feed, FeedEntry
from datetime import datetime, timezone, timedelta

from feeds.management_commands import get_pub_date, get_title, get_description, get_image, parse_feed
import feedparser

class LogInTest(TestCase):
    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'secret'}
        user = User.objects.create_user(**self.credentials)
        user.save()

    def test_login(self):
        # try to reach home logged out
        response = self.client.get('/', follow=True)
        self.assertEqual(response.status_code, 200)
        last_url, status_code = response.redirect_chain[-1]

        self.assertEqual(last_url, '/accounts/login/?next=/')

        # send login
        response = self.client.post('/accounts/login/?next=/', self.credentials, follow=True)

        # logged in now
        last_url, status_code = response.redirect_chain[-1]
        self.assertEqual(last_url, "/")
        self.assertTrue(response.context['user'].is_active)


class MainPageTesting(TestCase):

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

        #user account
        self.credentials = {
            'username': 'testuser',
            'password': 'secret'}
        User.objects.create_user(**self.credentials)

        # feeds
        feed_cat = FeedCategory(name="testing")
        feed_cat.save()
        feed = Feed(title='test feed', url="https://example.com", category=feed_cat)
        feed.save()
        self.posts = []
        for idx in range(3):
            feed_post = FeedEntry(feed=feed,
                              title="Here is a post #{}".format(idx),
                              url="https://localhost:8000/post-{}".format(idx),
                              published=datetime.utcnow().replace(tzinfo=timezone(timedelta(0))))
            feed_post.save()
            self.posts.append(feed_post)

    def test_main_page(self):
        response = self.client.login(**self.credentials)
        response = self.client.get('/', follow=True)
        self.assertEqual(response.status_code, 200)

        for post in self.posts:
            self.assertIn(post.title, str(response.content))
            self.assertIn(post.url, str(response.content))


    def test_mark_read(self):
        response = self.client.login(**self.credentials)
        id_list = '{},{}'.format(self.posts[0].id, self.posts[1].id)
        entry_types = '{},{}'.format(self.posts[0].entry_type, self.posts[1].entry_type)
        response = self.client.post('/feeds/mark-read/',
                        {'id_list': id_list,
                         'entry_types': entry_types
                        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'success': True}
        )

        self.assertTrue(FeedEntry.objects.get(pk=self.posts[0].id).read)
        self.assertTrue(FeedEntry.objects.get(pk=self.posts[1].id).read)

        response = self.client.get('/')

        self.assertIn(self.posts[2].title, str(response.content))
        self.assertIn(self.posts[2].url, str(response.content))

        self.assertNotIn(self.posts[1].title, str(response.content))
        self.assertNotIn(self.posts[1].url, str(response.content))

        self.assertNotIn(self.posts[0].title, str(response.content))
        self.assertNotIn(self.posts[0].url, str(response.content))


    def test_mark_read_later(self):
        response = self.client.login(**self.credentials)
        response = self.client.post('/feeds/mark-read-later/',
                        {'entry_id': self.posts[1].id,
                         'entry_type': self.posts[1].entry_type
                        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'success': True}
        )

        self.assertTrue(FeedEntry.objects.get(pk=self.posts[1].id).read_later)


        response = self.client.get('/read-later/')

        self.assertIn(self.posts[1].title, str(response.content))
        self.assertIn(self.posts[1].url, str(response.content))

        self.assertNotIn(self.posts[2].title, str(response.content))
        self.assertNotIn(self.posts[2].url, str(response.content))

        self.assertNotIn(self.posts[0].title, str(response.content))
        self.assertNotIn(self.posts[0].url, str(response.content))


        response = self.client.post('/feeds/unmark-read-later/',
                        {'entry_id': self.posts[1].id,
                         'entry_type': self.posts[1].entry_type
                        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'success': True}
        )

        self.assertFalse(FeedEntry.objects.get(pk=self.posts[1].id).read_later)

        response = self.client.get('/read-later/')

        self.assertNotIn(self.posts[1].title, str(response.content))
        self.assertNotIn(self.posts[1].url, str(response.content))

    def test_mark_interesting(self):
        response = self.client.login(**self.credentials)
        response = self.client.post('/feeds/mark-interesting/',
                        {'entry_id': self.posts[1].id,
                         'entry_type': self.posts[1].entry_type
                        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'success': True}
        )

        self.assertTrue(FeedEntry.objects.get(pk=self.posts[1].id).interesting)
        self.assertFalse(FeedEntry.objects.get(pk=self.posts[1].id).read_later)


class ParseFeedTests(TestCase):

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

        #user account
        self.credentials = {
            'username': 'testuser',
            'password': 'secret'}
        User.objects.create_user(**self.credentials)
        self.feed_files = [
            'feeds/tests/iapp.rss',
            'feeds/tests/nomnom.rss',
            'feeds/tests/jvns_ca.xml',
        ]

    def test_feed_parsing_units(self):
        for feed_file in self.feed_files:
            parser = feedparser.parse(feed_file)
            file_contents = open(feed_file, 'r').read()
            for entry in parser.entries:

                # test pub date
                pub_date = get_pub_date(entry)
                self.assertTrue(pub_date.year >= 2023)
                self.assertTrue(isinstance(pub_date, datetime))

                # test get_title
                title = get_title(entry)
                self.assertTrue(isinstance(title, str))
                self.assertTrue(len(title)<=355)
                if hasattr(entry, 'title'):
                    self.assertEqual(title, entry.title)

                # test get_description
                description = get_description(entry)
                self.assertTrue(isinstance(description, str))
                if hasattr(entry, 'content'):
                    self.assertIn(description,
                    ''.join([ce.get('value') for ce in entry.content]))
                elif hasattr(entry, 'description'):
                    self.assertEqual(description, entry.description)

                # test get_image
                image = get_image(description)
                if hasattr(entry, 'content'):
                    if image:
                        self.assertTrue(isinstance(image, str))
                        self.assertIn(image,
                        ''.join([ce.get('value') for ce in entry.content]))
                else:
                    self.assertEqual(image, None)

    def test_feed_reader(self):
        response = self.client.login(**self.credentials)
        initial_response = self.client.get('/')
        self.assertEqual(initial_response.status_code, 200)

        feed = Feed(title='test', url=self.feed_files[1]) # WARNING: this has to be updated
                                                          # for timely parsing (i.e. update RSS feed)
        feed.save()
        parse_feed(feed)

        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)

        self.assertNotEqual(initial_response.content, response.content)
        self.assertTrue(len(response.content) > len(initial_response.content))
