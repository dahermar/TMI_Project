from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import Image
from django.shortcuts import render
from .forms import ImageUploadForm

def index(request):
    latest_question_list = [1,2,3,4,5,6,7]
    context = {
        'latest_question_list': latest_question_list,
    }
    return render(request, 'imageupload/index.html', context)

def menu(request):
    form = ImageUploadForm()
    context = {'form': form}
    return render(request, 'imageupload/menu.html', context)

def historial(request):
    return render(request, 'imageupload/historial.html')

def info(request):
    return render(request,'imageupload/info.html')

def webcam_view(request):
    return render(request, 'imageupload/webcam.html')

class ImageUploadView(CreateView):
    model = Image
    fields = ['imagen']
    success_url = reverse_lazy('imageupload:index')

    