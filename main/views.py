import csv

from django.shortcuts import render

def home(request):
    dictionary =
    return render(request, 'index.html', {'table': table})
