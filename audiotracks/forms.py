from django import forms

from audiotracks.models import get_track_model


class TrackUploadForm(forms.ModelForm):
    class Meta:
        model = get_track_model()
        fields = ('audio_file',)


class TrackEditForm(forms.ModelForm):

    class Meta:
        model = get_track_model()
        exclude = ('user', 'created_at', 'updated_at')
        widgets = {'audio_file': forms.FileInput, 'image': forms.FileInput}

    def clean_slug(self):
        new_slug = self.cleaned_data['slug']
        if new_slug != self.instance._original_slug:
            params = {'slug': new_slug}
            params['user'] = self.instance.user
            if get_track_model().objects.filter(**params).count():
                raise forms.ValidationError("This URL is already taken.")

        return new_slug
