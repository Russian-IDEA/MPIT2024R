from MPITR.parsing import parse_file
from django.shortcuts import render

def home(request):
    dictionary = parse_file('feeds/yandex_feed.xml')
    columns = list(dictionary[list(dictionary.keys())[0]].keys())
    return render(request, 'index.html',
                  {'columns': columns, 'table': dictionary})
