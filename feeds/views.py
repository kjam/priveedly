# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import Http404, JsonResponse
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.shortcuts import render
from django_filters.views import FilterView
from queryset_sequence import QuerySetSequence

from feeds.models import FeedCategory, Feed, FeedEntry
from sites.models import SitePost, RedditPost

from datetime import datetime
import django_filters


class EntryFilter(django_filters.FilterSet):

    class Meta:
        model = FeedEntry
        fields = ['read', 'read_later', 'feed__title', 'published', 'recommended']


class EntryList(FilterView):
    template_name = "entry_list.html"
    paginate_by = 30
    model = FeedEntry
    context_object_name = 'entry_list'
    filterset_class = EntryFilter


class EntryDetailView(DetailView):
    model = FeedEntry
    template_name = "entry_detail.html"


def main_feed(request):
    group_qs = QuerySetSequence(
            FeedEntry.objects.filter(read=False),
            SitePost.objects.filter(read=False),
            RedditPost.objects.filter(read=False)).order_by('published')

    return render(request,
            'entry_list.html', {
                'entry_list': group_qs[:30],
                'total_unread': len(group_qs)})


def read_later_feed(request):
    group_qs = QuerySetSequence(
            FeedEntry.objects.filter(read_later=True),
            SitePost.objects.filter(read_later=True),
            RedditPost.objects.filter(read_later=True)).order_by('published')[:20]
    return render(request,
            'entry_list.html', {'entry_list': group_qs})


def recommended_feed(request):
    group_qs = QuerySetSequence(
            FeedEntry.objects.filter(recommended__gte=0.5, read=False),
            SitePost.objects.filter(recommended__gte=0.5, read=False),
            RedditPost.objects.filter(recommended__gte=0.5, read=False)).order_by('published')[:20]
    return render(request,
            'entry_list.html', {'entry_list': group_qs})

def mark_read(request):
    if request.method == 'POST':
        entry_ids = request.POST.get('id_list').split(',')
        entry_types = request.POST.get('entry_types').split(',')
        for etype, ein in zip(entry_types, entry_ids):
            if etype == 'sites':
                e = SitePost.objects.get(id=ein)
            elif etype == 'feeds':
                e = FeedEntry.objects.get(id=ein)
            elif etype == 'reddit':
                e = RedditPost.objects.get(id=ein)
            e.read = True
            e.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False,
        'error': 'Please send a list of ids'})

def mark_read_later(request):
    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        entry_type = request.POST.get('entry_type')
        if entry_type == 'sites':
            e = SitePost.objects.get(id=entry_id)
        elif entry_type == 'feeds':
            e = FeedEntry.objects.get(id=entry_id)
        elif entry_type == 'reddit':
            e = RedditPost.objects.get(id=entry_id)
        e.read_later = True
        e.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False,
        'error': 'Please send an entry id'})

def unmark_read_later(request):
    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        entry_type = request.POST.get('entry_type')
        if entry_type == 'sites':
            e = SitePost.objects.get(id=entry_id)
        elif entry_type == 'feeds':
            e = FeedEntry.objects.get(id=entry_id)
        elif entry_type == 'reddit':
            e = RedditPost.objects.get(id=entry_id)
        e.read_later = False
        e.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False,
        'error': 'Please send an entry id'})

def mark_interesting(request):
    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        entry_type = request.POST.get('entry_type')
        if entry_type == 'sites':
            e = SitePost.objects.get(id=entry_id)
        elif entry_type == 'feeds':
            e = FeedEntry.objects.get(id=entry_id)
        elif entry_type == 'reddit':
            e = RedditPost.objects.get(id=entry_id)
        e.read_later = False
        e.interesting = True
        e.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False,
        'error': 'Please send an entry id'})
