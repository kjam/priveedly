# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from base import Entry

class FeedCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return u'Category: {}'.format(self.name)

class Feed(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField()
    is_alive = models.BooleanField(default=True)
    category = models.ForeignKey(FeedCategory, 
            on_delete=models.SET_NULL,
            null=True)
    updated = models.DateTimeField(null=True, default=None)
    last_entry = models.DateTimeField(null=True, default=None)

    def __str__(self):
        return u'Feed: {}'.format(self.title)

    class Meta:
        ordering = ('-last_entry',)

class FeedEntry(Entry):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)

    @property
    def entry_type(self):
        return "feeds"

    @property
    def source(self):
        return self.feed.title
