# -*- coding: utf-8 -*-
# NOTE: no longer tested or maintained due to change in Twitter/X API

from __future__ import unicode_literals

from django.db import models
from base import Entry

class TwitterList(models.Model):
    name = models.CharField(max_length=100)
    list_id = models.BigIntegerField()
    since_id = models.BigIntegerField(null=True, default=None)

    def __str__(self):
        return u'Twitter List: {}'.format(self.name)

class Tweet(Entry):
    username = models.CharField(max_length=200)
    twitter_list = models.ForeignKey(TwitterList,
            on_delete=models.SET_NULL,
            null=True)

    @property
    def entry_type(self):
        return "tweets"

    @property
    def source(self):
        return self.twitter_list.name
