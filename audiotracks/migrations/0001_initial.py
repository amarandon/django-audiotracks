# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import audiotracks.models
import audiotracks.thumbs


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('audio_file', models.FileField(upload_to=audiotracks.models.get_audio_upload_path, verbose_name='Audio file')),
                ('image', audiotracks.thumbs.ImageWithThumbsField(null=True, upload_to=audiotracks.models.get_images_upload_path, blank=True)),
                ('title', models.CharField(max_length=200, null=True, verbose_name='Title')),
                ('artist', models.CharField(max_length=200, null=True, verbose_name='Artist', blank=True)),
                ('genre', models.CharField(max_length=200, null=True, verbose_name='Genre', blank=True)),
                ('date', models.CharField(max_length=200, null=True, verbose_name='Date', blank=True)),
                ('description', models.TextField(null=True, verbose_name='Description', blank=True)),
                ('slug', models.SlugField(verbose_name='Slug (last part of the url)')),
                ('user', models.ForeignKey(related_name='tracks', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
                'swappable': 'AUDIOTRACKS_MODEL',
            },
        ),
    ]
