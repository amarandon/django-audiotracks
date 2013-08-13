from django.conf import settings
from django.conf.urls import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'main.views.index', name="home"),
    url("^music", include("audiotracks.urls")),
    url("^(?P<username>[\w\._-]+)/music", include("audiotracks.urls")),
    url(r'^login$', 'django.contrib.auth.views.login', name="login"),
    url(r'^logout$', 'django.contrib.auth.views.logout', name="logout"),
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
            (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', 
                {'document_root': settings.MEDIA_ROOT}),)
    urlpatterns += staticfiles_urlpatterns()
