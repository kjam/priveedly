# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.html import strip_tags

class Entry(models.Model):

    class EntryCategory(models.TextChoices):
        RSS = 'RS', 'RSS Feed'
        TW = 'TW', 'Twitter'
        LS = 'LS', 'Lobste.rs'
        RD = 'RD', 'Reddit'
        HN = 'HN', 'Hacker News'

    title = models.CharField(max_length=355)
    url = models.URLField(max_length=400)
    description = models.TextField()
    image_url = models.URLField(null=True, blank=True, default='')
    published = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    to_delete = models.BooleanField(default=False)
    read_later = models.BooleanField(default=False)
    interesting = models.BooleanField(default=False)
    recommended = models.FloatField(default=0)
    entry_category = models.CharField(
        max_length=2,
        choices=EntryCategory.choices,
    )

    @property
    def safe_text(self):
        return strip_tags(self.description)

    class Meta:
        ordering = ('published',)
        abstract = True

    def __str__(self):
        return u'{} Entry: {}'.format(self.entry_category, self.title)
