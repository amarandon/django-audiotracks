#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import mimetypes

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site

from audiotracks.models import get_track_model
Track = get_track_model()

ITEMS_PER_FEED = getattr(settings, 'AUDIOTRACKS_PODCAST_LIMIT', 10)


class AllTracks(Feed):

    def link(self):
        return self.request.build_absolute_uri("/")

    def title(self):
        return _("%s Podcast") % self._get_site_name()

    def description(self):
        return _("All audio tracks posted on %s") % self._get_site_name()

    def get_object(self, request):
        self.request = request

    def items(self, user):
        return Track.objects.order_by('-created_at')[:ITEMS_PER_FEED]

    def item_title(self, item):
        return _('"%(title)s" posted by %(username)s') % {
            'title': item.title,
            'username': item.user.username
        }

    def item_description(self, item):
        if item.image:
            return '<img src="%s" alt="%s"/><p>%s</p>' % (
                self.request.build_absolute_uri(item.image.url_200x200),
                _('Image for "%s"') % item.title,
                item.description
            )
        else:
            return item.description

    def item_pub_date(self, item):
        return item.created_at

    def item_enclosure_url(self, item):
        return self.request.build_absolute_uri(item.audio_file.url)

    def item_enclosure_length(self, item):
        return item.audio_file.size

    def item_enclosure_mime_type(self, item):
        return mimetypes.guess_type(item.audio_file.path)[0]

    def _get_site_name(self):
        return Site.objects.get_current().name


class UserTracks(AllTracks):

    def get_object(self, request, username):
        self.request = request
        return get_object_or_404(User, username=username)

    def link(self, user):
        return self.request.build_absolute_uri("/%s/" % user.username)

    def title(self, user):
        return _("Podcast by %(username)s on %(site_name)s") % {
            'username': user.username,
            'site_name': self._get_site_name()
        }

    def description(self, user):
        return _("Audio tracks posted on %(site_name)s by %(username)s" % {
            'site_name': self._get_site_name(),
            'username': user.username
        })

    def items(self, user):
        query = Track.objects.filter(user=user).order_by("-created_at")
        return query[:ITEMS_PER_FEED]


all_tracks = AllTracks()
user_tracks = UserTracks()


def choose_feed(request, *args, **kwargs):
    """
    Pick up the user feed or the global feed depending on whether or not the
    URL contains a username parameter
    """
    feed = user_tracks if 'username' in kwargs else all_tracks
    return feed.__call__(request, *args, **kwargs)
