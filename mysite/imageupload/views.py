import os
import sys
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
from contextlib import closing
from tempfile import gettempdir

import threading
import random

import playsound

from .controllers.usuarioController import UsuarioController
from django.contrib.auth import logout
from django.views.decorators.cache import never_cache

usuarioController = UsuarioController()
datos_usuarios = usuarioController.cargar_usuarios()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def play_audio(audio):
    play(audio)

@never_cache
def rekognition_view(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)

        if form.is_valid():
            # obtener la imagen del formulario
            image = form.cleaned_data['imagen']

            images_dir = os.path.join(settings.MEDIA_ROOT)

            if not os.path.exists(images_dir):
                os.makedirs(images_dir)

            
            file_path = os.path.join(settings.MEDIA_ROOT, image.name)
            with open(file_path, 'wb') as f:
                f.write(image.read())

            # guardar la imagen en la ubicación deseada
            return rekognition_animal(request, image.name)
        else:
            form = ImageUploadForm()
        return render(request, 'imageupload/menu.html', {'form': form})


def rekognition_historial(request, foto):
    return rekognition_animal(request, foto, False)


def rekognition_animal(request, image_name, guardarHistorial=True):
    
    file_path = os.path.join(settings.MEDIA_ROOT, image_name)
    
    
    try:
        imagen =Image(image=file_path)
        animal, wikiTexto, wikiUrl = imagen.detect_animal()
        
        if wikiUrl != "":
            wikiUrl = "Para mas información consultar: <a href=\"" + wikiUrl + "\" target=\"_blank\">" + wikiUrl + "</a>" 
        results = {
            "animal": animal,
            "wikiTexto": wikiTexto,
            "imagen": "/static/images/" + image_name,
            "wikiUrl": wikiUrl
        }
        
        usuario_id = request.session['id']

        if guardarHistorial:
            usuarioController.agregar_registro(usuario_id=usuario_id, nombre=animal, foto_path=image_name)
        
        # Aquí se puede incluir cualquier código adicional para procesar los resultados obtenidos

        # Convertir los resultados obtenidos en un diccionario para pasarlo a la plantilla
        
        try:
            audio = PollyAudio()
            response = audio.transcript_text(wikiTexto)
            
            #audio_id = request.session['audio_id']
            #request.session['audio_id'] = audio_id + 1

            audioName = "audio" + str(random.randint(0, 999999999)) + ".mp3"

            if 'AudioStream' in response:
                with closing(response["AudioStream"]) as stream:
                    output = os.path.join(gettempdir(), audioName)
                    with open(output, "wb") as file:
                        file.write(stream.read())
                
                if sys.platform == "win32":
                    playsound.playsound(output, False)
                else:
                    audioSeg = AudioSegment.from_file(output, format='mp3')
                    audioThread = threading.Thread(target=play_audio, args=(audioSeg,))
                    audioThread.start()
                
                print("RUTA ABSOLUTA:", request.build_absolute_uri())

                return render(request, 'imageupload/rekognition_results.html', results)
            else:
                raise Exception('Error al sintetizar el texto dado.')
        except Exception as e:
            print('Error al sintetizar el texto dado.')
            print(e)
            return render(request, 'imageupload/rekognition_results.html', results)
        
    except Exception as e:
        logger.error('Error: ' + str(e))

    

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
                foto_path = 'rostros/' + filename
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

@never_cache
def menu(request):
    form = ImageUploadForm()
    nombre = request.session['nombre']
    context = {
        'form': form,
        "nombre": nombre
    }
    return render(request, 'imageupload/menu.html', context)

@never_cache
def historial(request):
    usuario_id = request.session['id']
    registros = usuarioController.get_registros_por_id(usuario_id=usuario_id)

    context = {
        "registros":registros
    }
    return render(request, 'imageupload/historial.html', context)

def info(request):
    return render(request,'imageupload/info.html')

@never_cache
def logout_view(request):
    logout(request)
    return redirect('imageupload:index')

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
            iguales, usuario = imagen.compare_face()
            print(iguales)
        except Exception as e:
                iguales = False
                logger.error(str(e))
                error = 'Error: No se pudo procesar la cara'
            #borrar foto del sistema
        os.remove(file_path)
        if iguales :
            request.session['id'] = usuario["id"]  
            request.session['nombre'] = usuario["nombre"]  
            request.session['foto'] = usuario["foto"]
            """
            if 'audio_id' not in request.session.keys():
                request.session['audio_id'] = 0 
            """
            return JsonResponse({'valido': True})
        
        return JsonResponse({'valido': False})
    return JsonResponse({'valido': False})
