import logging
import boto3
from botocore.exceptions import ClientError
from django.db import models
from rekognition_objects import (
    RekognitionFace, RekognitionCelebrity, RekognitionLabel,
    RekognitionModerationLabel, RekognitionText, show_bounding_boxes, show_polygons)
from pprint import pprint
import os
from django.conf import settings

#aqui el error TODO meter las clases
#from googletrans import Translator
from translate import Translator
import wikipedia
import re

from django.http import StreamingHttpResponse


logger = logging.getLogger(__name__)


class RekognitionImage:

    def __init__(self, image, image_name, rekognition_client):
        self.image = image
        self.image_name = image_name
        self.rekognition_client = rekognition_client

    @classmethod
    def from_file(cls, image_file_name, rekognition_client, image_name=None):
        with open(image_file_name, 'rb') as img_file:
            image = {'Bytes': img_file.read()}
        name = image_file_name if image_name is None else image_name
        return cls(image, name, rekognition_client)

    @classmethod
    def from_bucket(cls, s3_object, rekognition_client):
        image = {'S3Object': {'Bucket': s3_object.bucket_name, 'Name': s3_object.key}}
        return cls(image, s3_object.key, rekognition_client)
    
    #@classmethod
    def detect_labels(self, max_labels):
        try:
            response = self.rekognition_client.detect_labels(
                Image=self.image, MaxLabels=max_labels)
            labels = [RekognitionLabel(label) for label in response['Labels']]
            logger.info("Found %s labels in %s.", len(labels), self.image_name)
        except ClientError:
            logger.info("Couldn't detect labels in %s.", self.image_name)
            raise
        else:
            return labels
    
    #@classmethod
    def detect_faces(self):
        try:
            response = self.rekognition_client.detect_faces(
                Image=self.image, Attributes=['ALL'])
            faces = [RekognitionFace(face) for face in response['FaceDetails']]
            logger.info("Detected %s faces.", len(faces))
        except ClientError:
            logger.exception("Couldn't detect faces in %s.", self.image_name)
            raise
        else:
            return faces
    
    #@classmethod
    def compare_faces(self, target_image, similarity):
        """
        Compares faces in the image with the largest face in the target image.

        :param target_image: The target image to compare against.
        :param similarity: Faces in the image must have a similarity value greater
                           than this value to be included in the results.
        :return: A tuple. The first element is the list of faces that match the
                 reference image. The second element is the list of faces that have
                 a similarity value below the specified threshold.
        """
        try:
            response = self.rekognition_client.compare_faces(
                SourceImage=self.image,
                TargetImage=target_image.image,
                SimilarityThreshold=similarity)
            matches = [RekognitionFace(match['Face']) for match
                       in response['FaceMatches']]
            unmatches = [RekognitionFace(face) for face in response['UnmatchedFaces']]
            logger.info(
                "Found %s matched faces and %s unmatched faces.",
                len(matches), len(unmatches))
        except ClientError:
            logger.exception(
                "Couldn't match faces from %s to %s.", self.image_name,
                target_image.image_name)
            raise
        else:
            return matches, unmatches


class Animal(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class PollyAudio(models.Model):

    polly = boto3.client('polly')
    
    def transcript_text(self, text):
        if self.polly is not None:
            response = self.polly.synthesize_speech(Text=text, OutputFormat='mp3', VoiceId='Lucia', LanguageCode='es-ES')
            return response
        else:
            raise Exception('Cliente de Amazon no inicializado.')


class Image(models.Model):
    
    
    #image_cara = models.ImageField(upload_to='images')
    image= models.CharField(max_length=255)
    #detected_animal = models.ForeignKey(Animal, null=True, blank=True, on_delete=models.SET_NULL)
    translation = models.CharField(max_length=255, null=True, blank=True)
   
    def __init__(self, image):
            self.image = image
    
    def detect_animal(self):
        with open("./imageupload/animals.txt", "r") as archivo:
            animal_list = archivo.readlines()

        # Remove the newline character from each animal name.
        animal_list = [animal.strip() for animal in animal_list]
        # Convert the list to a set to remove duplicates.
        set_animals = set(animal_list)
        #print(set_animals)


        # Initialize the Rekognition client
        rekognition_client = boto3.client('rekognition')
        # Detect labels in the image

        image = RekognitionImage.from_file(self.image, rekognition_client)

        #print("Detcatdo")
        labels = image.detect_labels(20)
        # Look for the detected animal label
        #print(labels)
        #set_animals = set(Animal.objects.all().values_list('name', flat=True))
        #print(set_animals)
        detected_animal = None
        for label in labels:
            print(label.name)
            if label.name in set_animals:
                detected_animal = label.name
                break
        # Translate the animal name if detected
        #print(detected_animal)
        if detected_animal:
            translator = Translator(to_lang="es")
            #translation = translator.translate("CHICKEN", dest='es').text
            translation = translator.translate(detected_animal)   
        else:
            translation = None
        #return detected_animal, translation
        
        try:
            wikipedia.set_lang("es")
            wikiTexto = wikipedia.summary(translation, auto_suggest = False)
            wikiTexto = re.sub('\[[0-9]+\]','',wikiTexto.split('\n')[0])
            
        except:
            wikiTexto = "No se ha encontrado información sobre este animal"
        print(wikiTexto)
        
        return translation, wikiTexto
    
    def detect_face(self):
        # Initialize the Rekognition client
        rekognition_client = boto3.client('rekognition')
        # Detect labels in the image

        imagen = RekognitionImage.from_file(self.image, rekognition_client)
        caras= imagen.detect_faces()
        print(caras)
        print(f"Found {len(caras)} faces.")
        for cara in caras:
            pprint(cara.to_dict())
        return caras

    def compare_face(self):
        # Initialize the Rekognition client
        rekognition_client = boto3.client('rekognition')
        # Detect labels in the image

        #TODO hacer que compare con varias fotos
        imagen = RekognitionImage.from_file(self.image, rekognition_client)
        file_path = os.path.join(settings.MEDIA_ROOT, "cara_original.jpg")
        imagen_original = RekognitionImage.from_file(file_path, rekognition_client)
        caras= imagen.compare_faces(imagen_original,80)
        if len(caras[0])>0:
            print("Cara detectada")
            return True
        else:
            print("Cara no detectada")
            return False


