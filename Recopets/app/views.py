from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.template import loader


def index(request):
    latest_question_list = [1,2,3,4,5,6,7]
    context = {
        'latest_question_list': latest_question_list,
    }
    return render(request, 'app/index.html', context)

def menu(request):
    context = {
        'a': 'hola',
    }
    return render(request, 'app/menu.html', context)

def historial(request):
    return render(request, 'app/historial.html')

def info(request):
    return render(request,'app/info.html')