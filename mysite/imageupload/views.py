from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import Image
from django.shortcuts import render
from .forms import ImageUploadForm
from django.shortcuts import redirect
from django.views.generic import View
from django.conf import settings
import os


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

def image_upload(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # obtener la imagen del formulario
            image = form.cleaned_data['image']
            # guardar la imagen en la ubicación deseada
            file_path = os.path.join(settings.MEDIA_ROOT, 'images', image.name)
            with open(file_path, 'wb') as f:
                f.write(image.read())
            # redirigir al usuario a una página de éxito
            #return HttpResponseRedirect(reverse('imageupload:success'))
            return render(request, 'imageupload/info.html', {'image_path': image_path})

    else:
        form = ImageUploadForm()
    return render(request, 'imageupload/menu.html', {'form': form})

class ImageUploadView(View):
    #model = Image
    #fields = ['imagen']
    #success_url = reverse_lazy('imageupload:index')
    form_class = ImageUploadForm
    template_name = 'imageupload/image_form.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']
            # Crear la ruta completa al directorio images
            images_dir = os.path.join(settings.MEDIA_ROOT, 'images')
            if not os.path.exists(images_dir):
                os.makedirs(images_dir)
            # Guardar la imagen en el directorio images
            image_path = os.path.join(images_dir, image.name)
            with open(image_path, 'wb') as f:
                f.write(image.read())
            return render(request, 'imageupload/info.html', {'image_path': image_path})
        else:
            return render(request, self.template_name, {'form': form})
    