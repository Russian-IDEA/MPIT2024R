from main.parsing import parse_file
from django.shortcuts import render


def home(request):
    result = parse_file('feeds/yandex_feed.xml')
    table = result['offers']
    # print(result['report'])
    return render(request, 'index.html',
                  {
                      'columns': result['columns'],
                      'table': table[:10],

                  })
