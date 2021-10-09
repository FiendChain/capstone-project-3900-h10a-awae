from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def displayMessage(request):
    return HttpResponse('What does the fox say?')

def homepage(request):
    return render(request, "homepage.html")

def login(request):
    return render(request, "login.html")

def registration(request):
    return render(request, "registration.html")
