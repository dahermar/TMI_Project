from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import Image

class ImageUploadView(CreateView):
    model = Image
    fields = ['title', 'image']
    success_url = reverse_lazy('imageupload:index')
