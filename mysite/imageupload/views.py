import os
from django.conf import settings
from django.shortcuts import render
from .forms import ImageUploadForm


def index(request):
    latest_question_list = [1, 2, 3, 4, 5, 6, 7]
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
    return render(request, 'imageupload/info.html')


def webcam_view(request):
    return render(request, 'imageupload/webcam.html')


def image_upload(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # obtener la imagen del formulario
            image = form.cleaned_data['imagen']
            # guardar la imagen en la ubicación deseada
            
            images_dir = os.path.join(settings.MEDIA_ROOT)

            if not os.path.exists(images_dir):
                os.makedirs(images_dir)
                
            file_path = os.path.join(settings.MEDIA_ROOT, image.name)
            with open(file_path, 'wb') as f:
                f.write(image.read())
            # redirigir al usuario a una página de éxito
            return render(request, 'imageupload/info.html', {'image_path': file_path})
    else:
        form = ImageUploadForm()
    return render(request, 'imageupload/menu.html', {'form': form})