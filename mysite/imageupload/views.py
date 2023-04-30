import os
from django.conf import settings
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import Image
from django.shortcuts import render
from .forms import ImageUploadForm, RegistroForm
from django.conf import settings
import logging
from botocore.exceptions import ClientError
from pprint import pprint
from googletrans import Translator
from rekognition_objects import (
    RekognitionFace, RekognitionCelebrity, RekognitionLabel,
    RekognitionModerationLabel, RekognitionText, show_bounding_boxes, show_polygons)
from .models import RekognitionImage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from .models import PollyAudio
from django.contrib import messages
from django.shortcuts import redirect

import tempfile
from pydub import AudioSegment
from pydub.playback import play

import threading

from .controllers.usuarioController import UsuarioController

usuarioController = UsuarioController()
datos_usuarios = usuarioController.cargar_usuarios()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def play_audio(audio):
    play(audio)

def rekognition_view(request):
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

            try:
                imagen =Image(image=file_path)
                animal = imagen.detect_animal()
                
                # Aquí se puede incluir cualquier código adicional para procesar los resultados obtenidos

                # Convertir los resultados obtenidos en un diccionario para pasarlo a la plantilla
                audio = PollyAudio()
                response = audio.transcript_text('Hola Mundo')
                
                if 'AudioStream' in response:
                    audio_bytes = response['AudioStream'].read()
                    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                        tmp_file.write(audio_bytes)
                        tmp_file.flush()

                        # Carga el archivo temporal en un objeto AudioSegment de pydub
                        audio = AudioSegment.from_file(tmp_file.name, format='mp3')

                    audio_thread = threading.Thread(target=play_audio, args=(audio,))
                    audio_thread.start()

                    results = {
                        "animal": animal
                    }
                    return render(request, 'imageupload/rekognition_results.html', results)
                else:
                    raise Exception('Error al sintetizar el texto dado.')

            except Exception as e:
                logger.error('Error: No se pudo procesar la imagen. ' + str(e))
        else:
            form = ImageUploadForm()
        return render(request, 'imageupload/menu.html', {'form': form})
    """
    if request.method == 'POST':
        image_file = request.FILES.get('image')
        image_str= "./imageupload/images/" + str(image_file)
        ruta_relativa = image_file.name
        ruta_absoluta = os.path.abspath(ruta_relativa)
        print(ruta_absoluta )
        print("Esto",image_str)
        print("Tipo",type(image_str))
        #rekognition_client = boto3.client('rekognition')

        try:
            #image = {'Bytes': image_file.read()}
            #print(image_file)
            #print(image)
            #image_name = image_file.name
            #rekognition_image = RekognitionImage(image, image_name, rekognition_client)
            #max_labels = 20
            #labels = rekognition_image.detect_labels(max_labels)
            print(os.getcwd())
            imagen =Image(image=image_str)
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
"""

def index(request):
    latest_question_list = [1, 2, 3, 4, 5, 6, 7]
    context = {
        'latest_question_list': latest_question_list,
    }
    return render(request, 'imageupload/index.html', context)

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST, request.FILES)
        if form.is_valid():
            # Aquí se procesa la información del formulario
            nombre = form.cleaned_data['nombre']
            logger.info(nombre)
            foto = form.cleaned_data['foto']
            fileName, fileExtension = os.path.splitext(foto.name)
            # Procesar la foto y guardarla en algún directorio
            if foto:
                filename = nombre.replace(' ', '_').lower() + fileExtension
                logger.info(filename)
                logger.info(foto.name)
                with open(os.path.join(settings.MEDIA_ROOT + '/rostros/', filename), 'wb+') as destination:
                    for chunk in foto.chunks():
                        destination.write(chunk)
                foto_path = os.path.join(settings.MEDIA_URL + 'rostros/', filename)
                usuarioController.agregar_usuario(nombre=nombre, foto_path=foto_path)
                messages.success(request, '¡Registro exitoso!')
                return redirect('imageupload:index')
            # Crear el usuario con los datos y la ruta de la foto
            # Redirigir al usuario a alguna página de confirmación o a la página de inicio de sesión
            else:
                messages.error(request, 'Por favor corrige los errores del formulario.')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = RegistroForm()
    return render(request, 'imageupload/registro.html', {'form': form})

def menu(request):
    form = ImageUploadForm()
    context = {'form': form}
    return render(request, 'imageupload/menu.html', context)


def historial(request):
    return render(request, 'imageupload/historial.html')

def info(request):
    return render(request,'imageupload/info.html')

def webcam_view(request):
    csrf_token =get_token(request)
    return render(request, 'imageupload/webcam.html', {'csrf_token': csrf_token})

class ImageUploadView(CreateView):
    model = Image
    fields = [ 'image']
    success_url = reverse_lazy('imageupload:index')

def image_upload(request):
    if request.method == 'POST':
        print("hola")
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

#TODO
@csrf_exempt
def reconocimiento_facial(request):
    if request.method == 'POST':

        foto = request.FILES.get('foto')
        #Guardar foto y pasar url
        images_dir = os.path.join(settings.MEDIA_ROOT)
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
        
        file_path = os.path.join(settings.MEDIA_ROOT, "cara.jpg")
        with open(file_path, 'wb') as f:
            f.write(foto.read())
        try:
            imagen =Image(image=file_path)
            iguales = imagen.compare_face()
            print(iguales)
        except Exception as e:
                logger.error(str(e))
                error = 'Error: No se pudo procesar la cara'
            #borrar foto del sistema
        os.remove(file_path)
        if iguales :
            return JsonResponse({'valido': True})
        
        return JsonResponse({'valido': False})
    return JsonResponse({'valido': False})
