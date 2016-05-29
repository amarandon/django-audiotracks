from django.conf.urls import url

from audiotracks import feeds
from audiotracks import views


urlpatterns = [
    url(r"^$", views.index, name="audiotracks"),
    url(r"^(?P<page_number>\d+)/?$", views.index, name="audiotracks"),
    url(r"^track/(?P<track_slug>.*)$", views.track_detail,
        name="track_detail"),
    url(r"^upload", views.upload_track, name="upload_track"),
    url(r"^edit/(?P<track_id>.+)", views.edit_track, name="edit_track"),
    url(r"^confirm_delete/(?P<track_id>\d+)$",
        views.confirm_delete_track, name="confirm_delete_track"),
    url(r"^delete$", views.delete_track, name="delete_track"),
    url(r"^tracks$", views.user_index, name="user_index"),
    url(r"^tracks/(?P<page_number>\d)/?$", views.user_index,
        name="user_index"),
    url(r"^feed/?$", feeds.choose_feed, name="tracks_feed"),
    url(r"^player.js$", views.player_script, name="player_script"),
    url(r"^m3u/?$", views.m3u, name="m3u"),
]
