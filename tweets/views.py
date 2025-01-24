# -*- coding: utf-8 -*-
# NOTE: no longer tested or maintained due to change in Twitter/X API

from __future__ import unicode_literals

from django.http import Http404, JsonResponse
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django_filters.views import FilterView

from tweets.models import Tweet

from datetime import datetime
import django_filters


class TweetFilter(django_filters.FilterSet):

    class Meta:
        model = Tweet
        fields = ['read', 'read_later', 'published', 'twitter_list__name']


class TweetList(FilterView):
    template_name = "entry_list.html"
    paginate_by = 30
    model = Tweet
    context_object_name = 'entry_list'
    filterset_class = TweetFilter


class TweetDetailView(DetailView):
    model = Tweet
    template_name = "entry_detail.html"
