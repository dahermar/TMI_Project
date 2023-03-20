from django.urls import path
from .views import webcam_view

from . import views

app_name = 'imageupload'
urlpatterns = [
    path('menu/', views.ImageUploadView.as_view(), name='upload'), ## original de path de upload es ""
    path('index', views.index, name='index'),
    #path('menu/', views.menu, name='menu'),
    path('menu/historial', views.historial, name='historial'),
    path('menu/info', views.info, name='info'),
    path('webcam/', webcam_view, name='webcam'),
]