from django.urls import path

from . import views

app_name = 'imageupload'
urlpatterns = [
    path('', views.ImageUploadView.as_view(), name='upload'),
]