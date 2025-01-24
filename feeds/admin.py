# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from feeds.models import FeedCategory, Feed, FeedEntry

class FeedAdmin(admin.ModelAdmin):
    list_filter = ['is_alive']

admin.site.register(FeedCategory)
admin.site.register(Feed, FeedAdmin)
admin.site.register(FeedEntry)
