from MPITR.parsing import parse_file
from django.shortcuts import render

def home(request):
    table = parse_file('feeds/yandex_feed.xml')
    return render(request, 'index.html',
                  {'columns': table[0], 'table': table[1][:10]})
