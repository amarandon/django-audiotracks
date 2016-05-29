from django.conf import settings
from django.conf.urls import url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from main import views
from django.contrib.auth import views as auth_views
from django.views.static import serve

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^$', views.index, name="home"),
    url("^music/", include("audiotracks.urls")),
    url("^(?P<username>[\w\._-]+)/music/", include("audiotracks.urls")),
    url(r'^login$', auth_views.login, name="login"),
    url(r'^logout$', auth_views.logout, name="logout"),
    url(r'^admin/', include(admin.site.urls)),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^site_media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT
        })
    ]
    urlpatterns += staticfiles_urlpatterns()
