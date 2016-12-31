import os

from django.utils.translation import ugettext
from django.contrib.auth.decorators import login_required
from django.contrib.sites.requests import RequestSite
from django.conf import settings
from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import urlresolvers
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth.models import User

try:
    import mutagen
except ImportError:
    import mutagenx as mutagen  # Py3

from audiotracks.models import get_track_model
from audiotracks.forms import TrackUploadForm, TrackEditForm

METADATA_FIELDS = ('title', 'artist', 'genre', 'description', 'date')


def paginate(tracks, page_number):
    per_page = getattr(settings, 'AUDIOTRACKS_PER_PAGE', 10)
    paginator = Paginator(tracks, per_page)

    if page_number is None:
        page = paginator.page(1)
    else:
        try:
            page = paginator.page(int(page_number))
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            page = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of
            # results.
            page = paginator.page(paginator.num_pages)
    return page, page.object_list


def index(request, username=None, page_number=None):
    tracks = get_track_model().objects
    if username:
        tracks = tracks.filter(user__username=username)
    tracks = tracks.order_by('-created_at').all()
    page, tracks = paginate(tracks, page_number)
    base_path = urlresolvers.reverse(
        'audiotracks',
        args=[username] if username is not None else [])
    return render(request, "audiotracks/latest.html", {
        'username': username, 'tracks': tracks, 'page': page,
        'base_path': base_path,
    })


def user_index(request, username, page_number=None):
    user = get_object_or_404(User, username=username)
    tracks = user.tracks.order_by('-created_at').all()
    page, tracks = paginate(tracks, page_number)
    base_path = urlresolvers.reverse('user_index', args=[username])
    return render(request, "audiotracks/user_index.html", {
        'username': username, 'tracks': tracks, 'page': page,
        'base_path': base_path,
    })


def track_detail(request, track_slug, username=None):
    params = {'slug': track_slug}
    params['user__username'] = username
    track = get_object_or_404(get_track_model(), **params)
    return render(request, "audiotracks/detail.html", {
        'username': username, 'track': track
    })


def set_temporary_file_upload_handler(request):
    # Disable in memory upload before accessing POST
    # because we need a file from which to read metadata
    request.upload_handlers = [TemporaryFileUploadHandler()]


@login_required
@csrf_exempt  # request.POST is accessed by CsrfViewMiddleware
def upload_track(request):
    set_temporary_file_upload_handler(request)
    if request.method == "POST":
        form = TrackUploadForm(request.POST, request.FILES)
        if form.is_valid():
            audio_file = request.FILES['audio_file']
            audio_file_path = audio_file.temporary_file_path()
            metadata = mutagen.File(audio_file_path, easy=True)
            track = form.save(commit=False)
            track.user = request.user
            for field in METADATA_FIELDS:
                if metadata and metadata.get(field):
                    setattr(track, field, metadata.get(field)[0])
            track.save(force_insert=True)

            return HttpResponseRedirect(urlresolvers.reverse('edit_track',
                                                             args=[track.id]))
    else:
        form = TrackUploadForm()
    return render(request, "audiotracks/new.html", {'form': form})


def update_audiofile_metadata(track):
    filepath = track.audio_file.path
    metadata = mutagen.File(filepath, easy=True)
    if metadata:
        for field in METADATA_FIELDS:
            try:
                metadata[field] = getattr(track, field)
            except mutagen.easyid3.EasyID3KeyError:
                pass
        metadata.save()


@login_required
def edit_track(request, track_id):
    username = request.user.username
    track = request.user.tracks.get(id=track_id)
    if request.method == "POST":
        form = TrackEditForm(request.POST, request.FILES, instance=track)
        if form.is_valid():
            track = form.save()
            update_audiofile_metadata(track)
            if 'delete_image' in request.POST:
                track.image = None
                track.save()
            messages.add_message(request, messages.INFO,
                                 ugettext('Your changes have been saved.'))
            redirect_url = urlresolvers.reverse('user_index', args=[username])
            return HttpResponseRedirect(redirect_url)
    else:
        form = TrackEditForm(instance=track, )
    track_url_args = ['']
    track_url_args.insert(0, username)
    track_detail_url = urlresolvers.reverse('track_detail',
                                            args=track_url_args)
    track_url_prefix = request.build_absolute_uri(track_detail_url)
    track_filename = os.path.basename(track.audio_file.name)
    return render(request, "audiotracks/edit.html", {
        'form': form,
        'track': track,
        'track_url_prefix': track_url_prefix,
        'track_filename': track_filename,
    })


@login_required
def confirm_delete_track(request, track_id):
    track = get_object_or_404(request.user.tracks, id=track_id)
    default_origin_url = urlresolvers.reverse('user_index',
                                              args=[request.user.username])
    return render(request, "audiotracks/confirm_delete.html", {
        'track': track,
        'came_from': request.GET.get('came_from', default_origin_url)
    })


@login_required
def delete_track(request):
    track_id = request.POST.get('track_id')
    track = get_object_or_404(request.user.tracks, id=track_id)
    track.delete()
    messages.add_message(request, messages.INFO,
                         ugettext('"%s" has been deleted.') % track.title)
    return HttpResponseRedirect(request.POST.get('came_from', '/'))


class JavaScriptView(TemplateView):

    def render_to_response(self, context, **response_kwargs):
        response_kwargs['content_type'] = "application/javascript"
        return super(JavaScriptView, self).render_to_response(
            context, **response_kwargs)


player_script = JavaScriptView.as_view(template_name="audiotracks/player.js")


def m3u(request, username=None):
    tracks = get_track_model().objects
    if username:
        tracks = tracks.filter(user__username=username)
    tracks = tracks.order_by('-created_at').all()
    response = HttpResponse(content_type="audio/x-mpequrl")
    site = RequestSite(request)
    filename = "playlist-%s.m3u" % (site.name if username is None
                                    else username)
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    for track in tracks:
        url = 'http://%s/%s' % (site.domain, track.audio_file.url.strip("/"))
        response.write(url + "\n")
    return response
