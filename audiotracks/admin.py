from django.contrib import admin
from audiotracks.models import Track


class TrackAdmin(admin.ModelAdmin):
    pass

admin.site.register(Track, TrackAdmin)
