from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('menu/', views.menu, name='menu'),
    path('menu/historial', views.historial, name='historial'),
    path('menu/info', views.menu, name='info'),
]