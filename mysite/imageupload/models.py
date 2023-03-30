import logging
import boto3
from botocore.exceptions import ClientError
from django.db import models
from rekognition_objects import (
    RekognitionFace, RekognitionCelebrity, RekognitionLabel,
    RekognitionModerationLabel, RekognitionText, show_bounding_boxes, show_polygons)
from googletrans import Translator

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


class Animal(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Image(models.Model):
    

    image = models.ImageField(upload_to='images')
    #detected_animal = models.ForeignKey(Animal, null=True, blank=True, on_delete=models.SET_NULL)
    translation = models.CharField(max_length=255, null=True, blank=True)
   
    def __init__(self, image):
            self.image = image
    
    def detect_animal(self):
        # Initialize the Rekognition client
        rekognition_client = boto3.client('rekognition')
        # Detect labels in the image
        image = RekognitionImage(image=self.image.read(), image_name=self.image.name, rekognition_client=rekognition_client)
        labels = image.detect_labels(20)
        # Look for the detected animal label
        set_animals = set(Animal.objects.all().values_list('name', flat=True))
        detected_animal = None
        for label in labels:
            if label.name in set_animals:
                detected_animal = label.name
                break
        # Translate the animal name if detected
        if detected_animal:
            translator = Translator()
            translation = translator.translate(detected_animal, dest='es').text
        else:
            translation = None
        #return detected_animal, translation
        return translation

    def save(self, *args, **kwargs):
        # Detect the animal and save the detection results before saving the image
        detected_animal, translation = self.detect_animal()
        self.detected_animal = Animal.objects.filter(name=detected_animal).first() if detected_animal else None
        self.translation = translation
        super
