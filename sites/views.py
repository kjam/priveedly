# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import Http404, JsonResponse
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django_filters.views import FilterView

from sites.models import SitePost, RedditPost

from datetime import datetime
import django_filters


class SitesFilter(django_filters.FilterSet):

    class Meta:
        model = SitePost
        fields = ['read', 'read_later', 'published', 'site_name', 'recommended']

class RedditFilter(django_filters.FilterSet):

    class Meta:
        model = RedditPost
        fields = ['read', 'read_later', 'published', 'subreddit__name', 'recommended']


class SiteList(FilterView):
    template_name = "entry_list.html"
    paginate_by = 30
    model = SitePost
    context_object_name = 'entry_list'
    filterset_class = SitesFilter

class SiteDetailView(DetailView):
    model = SitePost
    template_name = "entry_detail.html"

class RedditList(FilterView):
    template_name = "entry_list.html"
    paginate_by = 30
    model = RedditPost
    context_object_name = 'entry_list'
    filterset_class = RedditFilter


class RedditDetailView(DetailView):
    model = RedditPost
    template_name = "entry_detail.html"
