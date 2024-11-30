from MPITR.celery import app
from main.parsing import test_db
import urllib.request
from main.models import Report, YandexOffer, Current


@app.task
def parsing_file(path, filename):
    # parse_and_save(filename, template_file_name)
    urllib.request.urlretrieve(path, filename)
    test_db(filename)
    cur = Current.objects.all()[0]
    cur.loaded = True
    cur.save()
