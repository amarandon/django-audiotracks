==================
django-audiotracks
==================

A Django_ app to publish audio tracks.

.. image:: https://pypip.in/v/django-audiotracks/badge.png
        :target: https://pypi.python.org/pypi/django-audiotracks

.. image:: https://pypip.in/d/django-audiotracks/badge.png
        :target: https://pypi.python.org/pypi/django-audiotracks

.. image:: https://travis-ci.org/amarandon/django-audiotracks.png?branch=master
    :target: https://travis-ci.org/amarandon/django-audiotracks

.. image:: https://coveralls.io/repos/amarandon/django-audiotracks/badge.png?branch=master
    :target: https://coveralls.io/r/amarandon/django-audiotracks

Introduction
~~~~~~~~~~~~

django-audiotracks is a simple Django_ app that allows your users to publish
audio tracks in various formats (Ogg Vorbis, Flac, MP3, WAV). It ships with a
default ``Track`` model, a set of views, default templates, podcast feeds and
sensible default URL configuration.  It uses mutagen_ to extract metadata from
audio files.  PIL is required to process images that can be attached to tracks.  

Default templates include the audio player from MediaElement.js_. I've added
some custom code for listing pages so that when a track ends playing, the next
one starts playing automatically.


Installation
~~~~~~~~~~~~


Using PyPi
__________

You can install django-audiotracks from PyPI using pip::

    $ pip install django-audiotracks


From GitHub
___________

Clone the repository with::

    $ git clone git://github.com/amarandon/django-audiotracks.git

Then install the ``audiotracks`` package in your Python path. A ``setup.py`` script is provided. You
can use it with a command such as::

    $ cd django-audiotracks
    $ python setup.py install

Or if you wish to modify the code::

    $ python setup.py develop

Run the example project
~~~~~~~~~~~~~~~~~~~~~~~

If you get django-audiotracks from GitHub, an example project styled with
Twitter Bootstrap is provided with the source code. You can run it like this::

    $ cd <django-audiotracks_source_dir>/example_project/
    $ python manage.py syncdb      # Create initial user at this stage
    $ python manage.py runserver

Log in and start uploading tracks.


Add ``audiotracks`` to your app
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Edit ``settings.py`` and add ``audiotracks`` to your list of
``INSTALLED_APPS``. Then synchronize your database with::

    $ python manage.py syncdb

Edit your ROOT_URLCONF_ and add a piece of code similar to::

    urlpatterns += patterns('',
        # Here we mount the app under /music. Feel free to use something else
        url("^music", include("audiotracks.urls")),
        # Some URLs require a Django username
        url("^(?P<username>[\w\._-]+)/music", include("audiotracks.urls")),
    )

Visit the URL ``/music/upload`` to upload your first track.

Views
~~~~~

Upload
______


* View function: ``upload_track``
* Default URL: <app_mount_point>/upload

This view allows authenticated users to upload a new audio file.  Metadata is
extracted from the file and used to prefill track attributes. Users get
redirected to the edit view.

Edit
____

* View function: ``edit_track``
* Default URL: <app_mount_point>/edit/<id>

Allow users to edit track attributes such as title, artist name, etc., upload an
image to attach to the track or change the audio file. Modified metadata
is stored back into the audio file itself if the format supports it (eg. it won't
work with a WAV file).

Display
_______

* View function: ``track_detail``
* URL: <app_mount_point_containing_username>/track/<slug>

Display track. The URL pattern must capture a ``username`` argument, it will be
used in the query to select the track. For example, if the app is mounted using
the pattern ``"^(?P<username>[\w\._-]+)/music"``, a URL such as
/bob/music/track/love-forever will look for the track which slug is love-forever
and has been uploaded by bob. A user who is logged in and owns the track can see
links to the edit page for this track. 

Delete
______

* View function: ``confirm_delete`` 
* Default URL: <app_mount_point>/confirm_delete/<id>

This is a confirmation page before deletion. Link to this page if you want to
provide a link to delete a track.

* View function: ``delete_track`` 
* Default URL: <app_mount_point>/delete (takes id as POST a param)

This view takes a track id as a POST parameter and delete the corresponding track.

User tracks listing
___________________

* View function: ``user_index``
* Default URL: <app_mount_point_containing_username>/

If the app is mounted with a pattern containing a username such as
``"^(?P<username>[\w\._-]+)/music"``, a URL such as /bob/music will display a
list of tracks uploaded by bob.

Latest tracks listing
_____________________

* View function: ``latest_tracks``
* Default URL: <app_mount_point>/

Show latest tracks by all users.


Podcast feeds
_____________

* View function ``feeds.choose_feed``
* Default URL: <app_mount_point>/feed and <app_mount_point_containing_username>/feed

Choose user feed or global feed depending on whether or not URL contains a
``username`` parameter


M3U playlists
_____________

* View function ``views.m3u``
* Default URLs: <app_mount_point>/m3u and <app_mount_point_containing_username>/m3u

Serve an M3U_ playlist file.

Configuration
~~~~~~~~~~~~~

AUDIOTRACKS_MODEL
_________________

Default: ``audiotracks.Track`` (string)

If the default ``Track`` model doesn't satisfy your needs, you can define your
own track model that inherits from ``audiotracks.models.AbstractTrack``. For
instance if you wish to add tagging you might define a model like this::

   class MyTrack(AbstractTrack):
       tags = TagField(_("Tags"))

Use the ``AUDIOTRACKS_MODEL`` setting to tell django-audiotracks about your
model, using the convention ``<app_name>.<model_class_name>``. So if your model
is called ``MyTrack`` and is located withing the app ``myapp``, use this
setting::

    AUDIOTRACKS_MODEL = 'myapp.MyTrack'


AUDIOTRACKS_PODCAST_LIMIT
_________________________

Default: ``10`` (integer)

Use this setting to specify how many tracks podcast feeds should contain.


AUDIOTRACKS_PER_PAGE
____________________

Default: ``10`` (integer)

Use this setting to specify how many tracks to display per listing page.


.. _`Django`: http://djangoproject.com
.. _`mutagen`: http://code.google.com/p/mutagen/
.. _`ROOT_URLCONF`: http://docs.djangoproject.com/en/dev/ref/settings/#std:setting-ROOT_URLCONF
.. _M3U: https://en.wikipedia.org/wiki/M3U
.. _MediaElement.js: http://mediaelementjs.com/
