from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import Image
from django.shortcuts import render


def webcam_view(request):
    return render(request, 'imageupload/webcam.html')

class ImageUploadView(CreateView):
    model = Image
    fields = ['title', 'image']
    success_url = reverse_lazy('imageupload:index')

    