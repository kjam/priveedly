# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from base import Entry

class Subreddit(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return u'Subreddit: {}'.format(self.name)

class RedditPost(Entry):
    subreddit = models.ForeignKey(Subreddit,
            on_delete=models.SET_NULL,
            null=True)

    @property
    def entry_type(self):
        return "reddit"

    @property
    def source(self):
        if self.subreddit:
            return self.subreddit.name
        return 'deleted'

class SitePost(Entry):
    site_name = models.CharField(max_length=200)

    @property
    def entry_type(self):
        return "sites"

    @property
    def source(self):
        return self.site_name
