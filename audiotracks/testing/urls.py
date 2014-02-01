from django.conf.urls import patterns, url, include


urlpatterns = patterns(
    "",
    url("^music", include("audiotracks.urls")),
    url("^(?P<username>[\w\._-]+)/music", include("audiotracks.urls")),
)
