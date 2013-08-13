from django.conf.urls import *

urlpatterns = patterns("",
    url("^music", include("audiotracks.urls")),
    url("^(?P<username>[\w\._-]+)/music", include("audiotracks.urls")),
)
