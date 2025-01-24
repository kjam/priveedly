
from django.urls import include, re_path
from django.contrib import admin

from feeds.views import EntryList, EntryDetailView, main_feed, read_later_feed, recommended_feed, mark_read, mark_read_later, mark_interesting, unmark_read_later
from sites.views import SiteList, SiteDetailView, RedditList, RedditDetailView

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^accounts/', include("django.contrib.auth.urls")),
    re_path(r'^$', main_feed),
    re_path(r'^read-later/$', read_later_feed),
    re_path(r'^recommended/$', recommended_feed),
    re_path(r'^feeds/$', EntryList.as_view()),
    re_path(r'^feeds/(?P<pk>\d+)/$', EntryDetailView.as_view()),
    re_path(r'^sites/$', SiteList.as_view()),
    re_path(r'^sites/(?P<pk>\d+)/$', SiteDetailView.as_view()),
    re_path(r'^reddit/$', RedditList.as_view()),
    re_path(r'^reddit/(?P<pk>\d+)/$', RedditDetailView.as_view()),
    re_path(r'^feeds/mark-read/', mark_read),
    re_path(r'^feeds/mark-interesting/', mark_interesting),
    re_path(r'^feeds/mark-read-later/', mark_read_later),
    re_path(r'^feeds/unmark-read-later/', unmark_read_later),
]
