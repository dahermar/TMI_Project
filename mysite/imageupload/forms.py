from django import forms

class ImageUploadForm(forms.Form):
    imagen = forms.ImageField()

class RegistroForm(forms.Form):
    nombre = forms.CharField(max_length=50)
    foto = forms.ImageField()