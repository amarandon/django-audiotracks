import os
from os.path import dirname, abspath
import shutil

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.test.client import Client
try:
    import mutagen
except ImportError:
    import mutagenx as mutagen  # Py3

from audiotracks.models import get_track_model
Track = get_track_model()

TEST_DATA_DIR = os.path.join(dirname(abspath(__file__)), 'testing', 'data')


@override_settings(ROOT_URLCONF='audiotracks.testing.urls')
class TestViews(TestCase):

    def setUp(self):
        User.objects.create_user("bob", "bob@example.com", "secret")
        User.objects.create_user("alice", "alice@example.com", "secret")
        self.client = Client()
        self.client.login(username='bob', password='secret')

    def tearDown(self):
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)

    def get_upload_file(self, name, ext):
        filename = name + "." + ext
        filepath = os.path.join(TEST_DATA_DIR, filename)
        filehandle = open(filepath, 'rb')
        return filename, filehandle

    def do_upload(self, filename="audio_file", ext="ogg"):
        filename, filehandle = self.get_upload_file(filename, ext)
        resp = self.client.post('/music/upload', {
            'name': filename,
            'audio_file': filehandle
        }, follow=True)
        return resp

    def do_upload_as_user(self, username, ext='ogg'):
        self.client.logout()
        self.client.login(username=username, password='secret')
        self.do_upload(ext=ext)
        upload_path = os.path.join(settings.MEDIA_ROOT, "audiotracks",
                                   "audio_files", username,
                                   "audio_file.%s" % ext)
        self.assert_(os.path.exists(upload_path),
                     "Upload path should contain username")

    def verify_upload(self):
        track = Track.objects.get(genre="Test Data")
        self.assertEquals(track.title, "django-audiotracks test file")
        self.assertEquals(track.slug, "django-audiotracks-test-file")
        return track

    def do_edit(self, track, **params):
        default_params = {
            'title': 'New Title',
            'genre': 'New Genre',
        }
        default_params.update(params)
        return self.client.post('/music/edit/%s' % track.id,
                                default_params)

    def test_upload_ogg(self):
        "OGG file upload"
        self.do_upload(ext='ogg')
        track = self.verify_upload()
        self.assertEquals(track.mimetype, "audio/ogg")
        self.assertEquals(track.filetype, "Ogg Vorbis")

    def test_upload_flac(self):
        "Flac file upload"
        self.do_upload(ext='flac')
        track = self.verify_upload()
        self.assertEquals(track.mimetype, "audio/flac")

    def test_upload_mp3(self):
        "MP3 file upload"
        self.do_upload(ext='mp3')
        track = self.verify_upload()
        self.assertEquals(track.mimetype, "audio/mpeg")

    def test_upload_wav(self):
        "WAV file upload"
        self.do_upload(ext='wav')
        # WAV file metadata not currently supported
        track = Track.objects.get(id=1)
        assert 'wav' in track.audio_file.name
        self.assertEquals(track.slug, "audio_file")
        self.assertEquals(track.mimetype, "audio/x-wav")

    def test_upload_file_with_long_name(self):
        """
        Check that the slug isn't over 50 characters.

        SQLite ignores the VARCHAR size limit, so when testing against it, we
        don't notice that the backend doesn't properly shorten slugs to 50
        characters. Here we check it explicitely with an assertion.
        """
        self.do_upload(
            'Steinregen Dubsystem ls. Zongosound - Outernational Fire Dub',
            'mp3')
        # WAV file metadata not currently supported
        track = Track.objects.get(id=1)
        self.assertEquals(track.slug,
                          "steinregen-dubsystem-ls-zongosound-outernational-f")

    def test_edit_does_not_have_required_audio_file(self):
        self.do_upload()
        track = Track.objects.get(genre="Test Data")
        response = self.client.get("/music/edit/%s" % track.pk)
        self.assertContains(
            response,
            '<input id="id_audio_file" name="audio_file" type="file">',
            html=True)

    def test_edit_track_attributes(self, ext='ogg'):
        """
        Edit track attributes and verify that they get saved into the audiofile
        itself
        """
        self.do_upload(ext=ext)
        track = Track.objects.get(genre="Test Data")
        self.do_edit(track, slug='new-title')
        track = Track.objects.get(genre="New Genre")
        self.assertEquals(track.title, 'New Title')
        audio_file_path = os.path.join(settings.MEDIA_ROOT, "audiotracks",
                                       "audio_files", "bob",
                                       "audio_file.%s" % ext)
        metadata = mutagen.File(audio_file_path, easy=True)
        self.assertEquals(metadata['title'], ['New Title'])
        self.assertEquals(metadata['genre'], ['New Genre'])

    def test_edit_mp3(self):
        "Edit MP3 track"
        self.test_edit_track_attributes('mp3')

    def test_edit_flac(self):
        "Edit FLAC track"
        self.test_edit_track_attributes('flac')

    def test_edit_wav(self):
        "Edit WAV track"
        ext = 'wav'
        self.do_upload(ext=ext)
        track = Track.objects.get(slug="audio_file")
        self.do_edit(track, slug='new-title')
        track = Track.objects.get(genre="New Genre")
        self.assertEquals(track.title, 'New Title')

    def test_replace_track_file(self):
        "Update audio file for a track"

        # Upload mp3
        self.do_upload(ext='mp3')

        # Update track with ogg file
        track_id = Track.objects.get(genre="Test Data").id
        filename, filehandle = self.get_upload_file('audio_file', 'ogg')
        self.client.post('/music/edit/%s' % track_id, {
            'name': filename,
            'audio_file': filehandle,
            'title': "New Title",
            'genre': "New Genre",
            'slug': "new-slug",
        })

        # Check that the file has been replaced
        track = Track.objects.get(id=track_id)
        self.assert_(track.audio_file.path.endswith('.ogg'))

    def test_delete_image(self):
        "Attach and remove track image"
        self.do_upload(ext='ogg')
        track = Track.objects.get(genre="Test Data")
        self.do_edit(track, slug='new-title',
                     image=open(os.path.join(TEST_DATA_DIR, 'image.jpg'),
                                'rb'))
        track = Track.objects.get(title="New Title")
        self.assert_(track.image.url.endswith('image.jpg'),
                     "Image should have been added")
        self.do_edit(track, slug='new-title', delete_image='1', image=None)
        track = Track.objects.get(title="New Title")
        self.assertFalse(track.image, "Image should have been deleted")

    def test_confirm_delete_track(self):
        "Confirm delete track"
        self.do_upload(ext='ogg')
        track = Track.objects.get(genre="Test Data")
        resp = self.client.get('/music/confirm_delete/%s' % track.id)
        assert 'Are you sure' in str(resp.content)

    def test_delete_track(self):
        "Delete track"
        self.do_upload(ext='ogg')
        track = Track.objects.get(genre="Test Data")
        self.client.post('/music/delete', {
            'track_id': track.id,
            'came_from': '/somewhere'
        })
        self.assertEquals(Track.objects.count(), 0)

    def test_latest(self):
        # Create 7 tracks
        for n in range(1, 8):
            self.do_upload(ext='ogg')
            track = Track.objects.get(title="django-audiotracks test file")
            track.title = "Track %s" % n
            track.save()

        # Get latest tracks
        resp = self.client.get('/bob/music/1')
        assert 'Track 7' in str(resp.content)
        assert 'Track 5' in str(resp.content)
        assert 'Track 4' not in str(resp.content)

        # Get oldest tracks
        resp = self.client.get('/bob/music/3')
        assert 'Track 1' in str(resp.content)
        assert 'Track 2' not in str(resp.content)

    def test_user_latest(self):
        # Create 4 tracks for each user
        for name in ('bob', 'alice'):
            self.client.login(username=name, password='secret')
            for n in range(1, 5):
                self.do_upload(ext='ogg')
                track = Track.objects.get(title="django-audiotracks test file")
                track.title = "%s Track %s" % (name.capitalize(), n)
                track.save()

        # Get latest tracks from bob
        self.client.login(username='bob', password='secret')
        resp = self.client.get('/bob/music/tracks/1')
        assert 'Bob Track 4' in str(resp.content)
        assert 'Bob Track 2' in str(resp.content)
        assert 'Bob Track 1' not in str(resp.content)

        # Get oldest tracks from alice while being logged out
        self.client.logout()
        resp = self.client.get('/alice/music/tracks/2')
        assert 'Alice Track 1' in str(resp.content)
        assert 'Alice Track 2' not in str(resp.content)

    def test_get_track(self):
        "Get track"
        self.do_upload_as_user('bob')
        self.do_upload_as_user('alice')
        bob_track, alice_track = Track.objects.all()
        self.assertEquals(bob_track.user.username, 'bob')
        self.assertEquals(alice_track.user.username, 'alice')
        self.assertEquals(bob_track.slug, alice_track.slug)
        self.client.get('/bob/music/track/' + bob_track.slug)

    def test_missing_track(self):
        response = self.client.get('/bob/music/track/non-existing')
        self.assertEqual(response.status_code, 404)

    def test_prevent_duplicate_slug(self):
        "Prevent duplicate slug for the same user"
        # Upload a track
        self.do_upload(ext='ogg')

        # Upload another one as another user
        self.do_upload_as_user('alice')
        bob_track, alice_track = Track.objects.all()
        self.assertEquals(bob_track.slug, alice_track.slug,
                          "We should be able to create 2 tracks as 2 "
                          "different users with the same slug.")

        # We should be allowed to set the same slug for 2 tracks belonging to 2
        # different users
        self.do_edit(alice_track, slug='django-audiotracks-test-file')
        _, alice_track = Track.objects.all()
        self.assertEquals(alice_track.slug, 'django-audiotracks-test-file')

        # We should not be able to set the same slug for 2 tracks belonging to
        # the same user
        self.do_upload_as_user('alice')
        _, existing_alice_track, new_alice_track = Track.objects.all()
        self.do_edit(new_alice_track, slug='django-audiotracks-test-file')
        _, existing_alice_track, new_alice_track = Track.objects.all()
        self.assertEquals(new_alice_track.slug,
                          'django-audiotracks-test-file-2')

    def test_m3u(self):
        "m3u playlists"
        for ext in ('ogg', 'mp3'):
            self.do_upload_as_user('bob', ext)
        for ext in ('flac', 'wav'):
            self.do_upload_as_user('alice', ext)

        response = self.client.get('/bob/music/m3u')
        self.assertTrue("playlist-bob.m3u" in response['Content-Disposition'])
        self.assertContains(
            response,
            "http://testserver/audiotracks/audio_files/bob/audio_file.ogg")
        self.assertNotContains(
            response,
            "http://testserver/audiotracks/audio_files/alice/audio_file.flac")

        response = self.client.get('/music/m3u')
        self.assertTrue(
            "playlist-testserver.m3u" in response['Content-Disposition'])
        self.assertContains(
            response,
            "http://testserver/audiotracks/audio_files/bob/audio_file.ogg")
        self.assertContains(
            response,
            "http://testserver/audiotracks/audio_files/alice/audio_file.flac")

    def test_global_feed(self):
        self.do_upload(ext='mp3')
        track = Track.objects.get(genre="Test Data")
        self.do_edit(track, title='The Title', slug='new-title',
                     image=open(os.path.join(TEST_DATA_DIR, 'image.jpg'),
                                'rb'))
        response = self.client.get('/music/feed')
        self.assertContains(response, '"http://www.w3.org/2005/Atom"')
        self.assertContains(response, 'audio_file.mp3')
        self.assertContains(response, 'The Title')

    def test_user_feed(self):
        self.client.login(username='bob', password='secret')
        self.do_upload(ext='ogg')
        self.client.login(username='alice', password='secret')
        self.do_upload(ext='mp3')
        response = self.client.get('/alice/music/feed')
        self.assertContains(response, 'mp3')
        self.assertNotContains(response, 'ogg')
