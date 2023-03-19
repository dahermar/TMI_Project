from django.urls import path
from .views import webcam_view

from . import views

app_name = 'imageupload'
urlpatterns = [
    path('', views.ImageUploadView.as_view(), name='upload'),
    path('webcam/', webcam_view, name='webcam'),
]