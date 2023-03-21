from django import forms

class ImageUploadForm(forms.Form):
    imagen = forms.ImageField()