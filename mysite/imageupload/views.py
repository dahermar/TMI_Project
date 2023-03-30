import os
from django.conf import settings
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import Image
from django.shortcuts import render
from django.shortcuts import render
from .forms import ImageUploadForm
from django.conf import settings
import logging
import boto3
from botocore.exceptions import ClientError
from pprint import pprint
from googletrans import Translator
from rekognition_objects import (
    RekognitionFace, RekognitionCelebrity, RekognitionLabel,
    RekognitionModerationLabel, RekognitionText, show_bounding_boxes, show_polygons)
from .models import RekognitionImage

logger = logging.getLogger(__name__)

def rekognition_view(request):
    if request.method == 'POST':
        image_file = request.FILES.get('image')
        print(image_file)
        #rekognition_client = boto3.client('rekognition')

        try:
            image = {'Bytes': image_file.read()}
            #print(image_file)
            #print(image)
            #image_name = image_file.name
            #rekognition_image = RekognitionImage(image, image_name, rekognition_client)
            #max_labels = 20
            #labels = rekognition_image.detect_labels(max_labels)
            imagen =Image(image=image)
            animal = imagen.detect_animal()
            #animal = type(image_file)
            
            #animal_es ="jirafa"
            # Aquí se puede incluir cualquier código adicional para procesar los resultados obtenidos

            # Convertir los resultados obtenidos en un diccionario para pasarlo a la plantilla
            results ={"animal": animal}
            return render(request, 'imageupload/rekognition_results.html', results)
        except Exception as e:
            logger.error(str(e))
            error = 'Error: No se pudo procesar la imagen'
           # return render(request, 'rekognition_error.html', {'error': error})

    return render(request, 'imageupload/rekognition_form.html')


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
    return render(request,'imageupload/info.html')

def webcam_view(request):
    return render(request, 'imageupload/webcam.html')

class ImageUploadView(CreateView):
    model = Image
    fields = ['title', 'image']
    success_url = reverse_lazy('imageupload:index')

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