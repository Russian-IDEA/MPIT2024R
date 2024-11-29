import os
import urllib.request

import lxml
from lxml import etree
from main.parsing import parse_file, parse_and_save, parse_offer_attribs_tags_names
from django.shortcuts import render
from .models import Report, YandexOffer


def home(request):
    # filename = request.GET['filename']
    # table = parse_and_save(f'feeds/yandex_feed.xml')
    # report = get_info_report(table)
    report = get_info_db()
    return render(request, 'index.html',
                  {
                      'columns': report[0],
                      'table': report[1],
                      'report': report[2]
                  })

def upload(request):
    if request.method == 'POST':
        path = request.POST['path']
        files_number = len([name for name in os.listdir('feeds/') if os.path.isfile(name)])
        urllib.request.urlretrieve(path, f'feeds/file{files_number + 1}.xml')
    return render(request, 'upload.html')


def get_info_report(table):
    res_reports = {}
    all_element = table["offers"]
    res_element = []
    report_all = list(reversed(Report.objects.all().order_by("type")))
    for i in report_all:
        if i.index in res_reports.keys():
            res_reports[i.index][i.column] = [i.type, i.reason]
        else:
            res_reports[i.index] = {i.column: [i.type, i.reason]}
    for i in res_reports.keys():
        res_element.append(all_element[i])
    keys_rest_arr = list(res_reports.keys())[:10]
    res_rest_elem = []
    res_rest_rep = {}
    for i in keys_rest_arr:
        res_rest_elem.append(all_element[i])
        res_rest_rep[i] = res_reports[i]
    return [table["columns"], res_rest_elem, res_rest_rep]


def get_info_db(template_file_name='feeds/template.xml'):
    res_reports = {}
    report_all = list(reversed(Report.objects.all().order_by("type")))
    for i in report_all:
        if i.index in res_reports.keys():
            res_reports[i.index][i.column] = [i.type, i.reason]
        else:
            res_reports[i.index] = {i.column: [i.type, i.reason]}
    keys_rest_arr = list(res_reports.keys())[:10]
    res_rest_elem = []
    res_rest_rep = {}
    for i in keys_rest_arr:
        y = YandexOffer.objects.get(pk=i)
        res_rest_elem.append([y.index, y.available, y.price, y.currencyId, y.categoryId, y.picture, y.name, y.vendor,
                              y.description, y.barcode, y.article, y.rating, y.review_amount, y.sale, y.newby])
        res_rest_rep[i] = res_reports[i]

    template = lxml.etree.parse(template_file_name).getroot()
    parsed_template = parse_offer_attribs_tags_names(template)
    offer_attribs = parsed_template["attribs"]
    tags = parsed_template["tags"]
    params = parsed_template["params"]

    # generate columns
    columns = []
    for attrib in offer_attribs:
        columns.append(attrib["localizedname"])
    for tag in tags:
        columns.append(tag["localizedname"])
    for param in params:
        columns.append(param["localizedname"])
    return [columns, res_rest_elem, res_rest_rep]