import os
import mimetypes

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ImproperlyConfigured
try:
    from django.apps import apps as django_apps
except ImportError:
    django_apps = None


from .thumbs import ImageWithThumbsField


def slugify_uniquely(value, obj, slugfield="slug"):
    suffix = 1
    potential = base = slugify(value)
    filter_params = {}
    filter_params['user'] = obj.user
    while True:
        if suffix > 1:
            potential = "-".join([base, str(suffix)])
        filter_params[slugfield] = potential
        obj_count = obj.__class__.objects.filter(**filter_params).count()
        if not obj_count:
            return potential[:50]
        # we hit a conflicting slug, so bump the suffix & try again
        suffix += 1


def get_upload_path(dirname, obj, filename):
    return os.path.join("audiotracks", dirname, obj.user.username, filename)


def get_images_upload_path(obj, filename):
    return get_upload_path("images", obj, filename)


def get_audio_upload_path(obj, filename):
    return get_upload_path("audio_files", obj, filename)


class AbstractTrack(models.Model):

    class Meta:
        abstract = True

    user = models.ForeignKey(User,
                             related_name="tracks",
                             blank=True,
                             null=True
                             )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    audio_file = models.FileField(
        _("Audio file"), upload_to=get_audio_upload_path)
    image = ImageWithThumbsField(
        _("Image"), upload_to=get_images_upload_path, null=True,
        blank=True, sizes=((48, 48), (200, 200)))
    title = models.CharField(_("Title"), max_length=200, null=True)
    artist = models.CharField(
        _("Artist"), max_length=200, null=True, blank=True)
    genre = models.CharField(
        _("Genre"), max_length=200, null=True, blank=True)
    date = models.CharField(_("Date"), max_length=200, null=True, blank=True)
    description = models.TextField(_("Description"), null=True, blank=True)
    slug = models.SlugField(verbose_name=_("Slug (last part of the url)"))
    _original_slug = None  # Used to detect slug change

    def __init__(self, *args, **kwargs):
        super(AbstractTrack, self).__init__(*args, **kwargs)
        self._original_slug = self.slug

    def __unicode__(self):
        return "Track '%s' uploaded by '%s'" % (self.title, self.user.username)

    def save(self, **kwargs):
        if not self.slug:
            # Automatically set initial slug
            slug_source = getattr(self, 'title') or \
                os.path.splitext(os.path.basename(self.audio_file.name))[0]
            self.slug = slugify_uniquely(slug_source, self)
        super(AbstractTrack, self).save(**kwargs)

    @property
    def mimetype(self):
        if not hasattr(self, '_mimetype'):
            self._mimetype = mimetypes.guess_type(self.audio_file.path)[0]
        return self._mimetype

    @property
    def filetype(self):
        if '/' in self.mimetype:
            type_names = {'mpeg': 'MP3', 'ogg': 'Ogg Vorbis'}
            filetype = self.mimetype.split('/')[1]
            return type_names.get(filetype, filetype)
        else:
            return self.mimetype

    @models.permalink
    def get_absolute_url(self):
        return ('audiotracks.views.track_detail',
                [self.user.username, self.slug])


class Track(AbstractTrack):

    class Meta(AbstractTrack.Meta):
        swappable = 'AUDIOTRACKS_MODEL'


def get_track_model():
    if not hasattr(get_track_model, 'result'):
        if hasattr(settings, 'AUDIOTRACKS_MODEL'):
            if django_apps:
                try:
                    get_track_model.result = django_apps.get_model(
                        settings.AUDIOTRACKS_MODEL)
                except ValueError:
                    raise ImproperlyConfigured(
                        "AUDIOTRACKS_MODEL must be of the form " +
                        "'app_label.model_name'")
                except LookupError:
                    raise ImproperlyConfigured(
                        "AUDIOTRACKS_MODEL refers to model " +
                        "'%s' that has not been installed" %
                        settings.AUTH_USER_MODEL)
            else:
                app_name, model_name = settings.AUDIOTRACKS_MODEL.split('.')
                get_track_model.result = models.get_model(app_name, model_name)
        else:
            get_track_model.result = Track
    return get_track_model.result
