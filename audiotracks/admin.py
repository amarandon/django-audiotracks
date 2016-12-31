from django.contrib import admin
from audiotracks.models import get_track_model


class TrackAdmin(admin.ModelAdmin):
    pass


admin.site.register(get_track_model(), TrackAdmin)
