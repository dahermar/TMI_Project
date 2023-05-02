# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Purpose

Shows how to use the AWS SDK for Python (Boto3) with Amazon Rekognition to
recognize people, objects, and text in images.

The usage demo in this file uses images in the .media folder. If you run this code
without cloning the GitHub repository, you must first download the image files from
    https://github.com/awsdocs/aws-doc-sdk-examples/tree/master/python/example_code/rekognition/.media
"""

# snippet-start:[python.example_code.rekognition.image_detection_imports]
import logging
from pprint import pprint
import boto3
from botocore.exceptions import ClientError
import requests
from googletrans import Translator


from rekognition_objects import (
    RekognitionFace, RekognitionCelebrity, RekognitionLabel,
    RekognitionModerationLabel, RekognitionText, show_bounding_boxes, show_polygons)

logger = logging.getLogger(__name__)

# snippet-end:[python.example_code.rekognition.image_detection_imports]


# snippet-start:[python.example_code.rekognition.RekognitionImage]
class RekognitionImage:
    """
    Encapsulates an Amazon Rekognition image. This class is a thin wrapper
    around parts of the Boto3 Amazon Rekognition API.
    """
    def __init__(self, image, image_name, rekognition_client):
        """
        Initializes the image object.

        :param image: Data that defines the image, either the image bytes or
                      an Amazon S3 bucket and object key.
        :param image_name: The name of the image.
        :param rekognition_client: A Boto3 Rekognition client.
        """
        self.image = image
        self.image_name = image_name
        self.rekognition_client = rekognition_client
# snippet-end:[python.example_code.rekognition.RekognitionImage]

# snippet-start:[python.example_code.rekognition.RekognitionImage.from_file]
    @classmethod
    def from_file(cls, image_file_name, rekognition_client, image_name=None):
        """
        Creates a RekognitionImage object from a local file.

        :param image_file_name: The file name of the image. The file is opened and its
                                bytes are read.
        :param rekognition_client: A Boto3 Rekognition client.
        :param image_name: The name of the image. If this is not specified, the
                           file name is used as the image name.
        :return: The RekognitionImage object, initialized with image bytes from the
                 file.
        """
        with open(image_file_name, 'rb') as img_file:
            image = {'Bytes': img_file.read()}
        name = image_file_name if image_name is None else image_name
        return cls(image, name, rekognition_client)
# snippet-end:[python.example_code.rekognition.RekognitionImage.from_file]

# snippet-start:[python.example_code.rekognition.RekognitionImage.from_bucket]
    @classmethod
    def from_bucket(cls, s3_object, rekognition_client):
        """
        Creates a RekognitionImage object from an Amazon S3 object.

        :param s3_object: An Amazon S3 object that identifies the image. The image
                          is not retrieved until needed for a later call.
        :param rekognition_client: A Boto3 Rekognition client.
        :return: The RekognitionImage object, initialized with Amazon S3 object data.
        """
        image = {'S3Object': {'Bucket': s3_object.bucket_name, 'Name': s3_object.key}}
        return cls(image, s3_object.key, rekognition_client)
# snippet-end:[python.example_code.rekognition.RekognitionImage.from_bucket]

# snippet-start:[python.example_code.rekognition.DetectFaces]
    def detect_faces(self):
        """
        Detects faces in the image.

        :return: The list of faces found in the image.
        """
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
# snippet-end:[python.example_code.rekognition.DetectFaces]

# snippet-start:[python.example_code.rekognition.CompareFaces]
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
# snippet-end:[python.example_code.rekognition.CompareFaces]
    
# snippet-start:[python.example_code.rekognition.DetectLabels]
    def detect_labels(self, max_labels):
        """
        Detects labels in the image. Labels are objects and people.

        :param max_labels: The maximum number of labels to return.
        :return: The list of labels detected in the image.
        """
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
# snippet-end:[python.example_code.rekognition.DetectLabels]

# snippet-start:[python.example_code.rekognition.DetectModerationLabels]
    def detect_moderation_labels(self):
        """
        Detects moderation labels in the image. Moderation labels identify content
        that may be inappropriate for some audiences.

        :return: The list of moderation labels found in the image.
        """
        try:
            response = self.rekognition_client.detect_moderation_labels(
                Image=self.image)
            labels = [RekognitionModerationLabel(label)
                      for label in response['ModerationLabels']]
            logger.info(
                "Found %s moderation labels in %s.", len(labels), self.image_name)
        except ClientError:
            logger.exception(
                "Couldn't detect moderation labels in %s.", self.image_name)
            raise
        else:
            return labels
# snippet-end:[python.example_code.rekognition.DetectModerationLabels]

# snippet-start:[python.example_code.rekognition.DetectText]
    def detect_text(self):
        """
        Detects text in the image.

        :return The list of text elements found in the image.
        """
        try:
            response = self.rekognition_client.detect_text(Image=self.image)
            texts = [RekognitionText(text) for text in response['TextDetections']]
            logger.info("Found %s texts in %s.", len(texts), self.image_name)
        except ClientError:
            logger.exception("Couldn't detect text in %s.", self.image_name)
            raise
        else:
            return texts
# snippet-end:[python.example_code.rekognition.DetectText]



# snippet-start:[python.example_code.rekognition.Usage_ImageDetection]
def usage_demo():
    
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    rekognition_client = boto3.client('rekognition')
   
    image_animal= "./.media/rinoceronte.jpg"

    '''swimwear_object = boto3.resource('s3').Object(
        'console-sample-images-pdx', 'yoga_swimwear.jpg')'''
    # book_file_name = '.media/pexels-christina-morillo-1181671.jpg'

    '''street_scene_image = RekognitionImage.from_file(
        street_scene_file_name, rekognition_client)
    '''
    animal_scene_image = RekognitionImage.from_file(
        image_animal, rekognition_client)
    

    print(f"Detecting labels in {animal_scene_image.image_name}...")
    labels = animal_scene_image.detect_labels(20)
    print(f"Found {len(labels)} labels.")
    for label in labels:
        pprint(label.to_dict())
    names = []
    box_sets = []
    colors = ['aqua', 'red', 'white', 'blue', 'yellow', 'green']
    detected_animal = None
    for label in labels:
        print(label.name)
        if label.name in set_animals:
           detected_animal = label.name
           break


        if label.instances:
            names.append(label.name)
            box_sets.append([inst['BoundingBox'] for inst in label.instances])
    print(f"Showing bounding boxes for {names} in {colors[:len(names)]}.")
    show_bounding_boxes(
        animal_scene_image.image['Bytes'], box_sets, colors[:len(names)])
    if detected_animal != None:
        translation= translator.translate(detected_animal, dest='es').text
        print("Animal detectado ingles: ", detected_animal)
        print("Animal detectado español: ", translation)
    else:
        print("Animal no detectado")
    input("Press Enter to continue.")


# snippet-end:[python.example_code.rekognition.Usage_ImageDetection]


if __name__ == '__main__':
    # Read the list of animals from the file.
    with open("animals.txt", "r") as archivo:
        animal_list = archivo.readlines()

    # Remove the newline character from each animal name.
    animal_list = [animal.strip() for animal in animal_list]
    # Convert the list to a set to remove duplicates.
    set_animals = set(animal_list)
    #print(set_animals)

    translator=Translator()


    usage_demo()
