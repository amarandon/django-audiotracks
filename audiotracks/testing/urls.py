from django.conf.urls import url, include


urlpatterns = [
    url("^music/", include("audiotracks.urls")),
    url("^(?P<username>[\w\._-]+)/music/", include("audiotracks.urls")),
]
