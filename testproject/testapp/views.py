from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def displayMessage(request):
    return HttpResponse('What does the fox say?')