from django.shortcuts import render
from django.http import HttpResponse

def order(request):
    return HttpResponse('Returning info about your order')

def photos(request):
    return HttpResponse('Returning all photos')
