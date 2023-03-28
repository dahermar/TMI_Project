from django.db import models

class Image(models.Model):
    imagen = models.ImageField(upload_to='images/')
