import json
import os
import urllib.request

import lxml
from lxml import etree
from main.parsing import parse_file, parse_and_save, parse_offer_attribs_tags_names, validate_change, test_db

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse

from .models import Report, YandexOffer, Current


def home(request):
    # filename = request.GET['filename']
    # table = parse_and_save(f'feeds/{filename}')
    # table = parse_and_save('/Users/user/PycharmProjects/MPITR/feeds/yandex_feed.xml')
    # report = get_info_report(table)
    if not Current.objects.exists():
        return redirect('/upload')
    report = get_info_db()
    return render(request, 'index.html',
                  {
                      'columns': report[0],
                      'table': report[1]
                  })

def upload(request):
    if request.method == 'POST':
        path = request.POST['path']
        files_number = len([name for name in os.listdir('feeds/')])
        filename = f'feeds/file{files_number + 1}.xml'
        urllib.request.urlretrieve(path, filename)
        Current.objects.create(current=filename)
        test_db(filename)
        return redirect('/')
    return render(request, 'upload.html')


def update_value_bd(request):
    if request.method == 'POST':
        body = json.loads(request.body.decode('utf-8'))
        id = int(body['id'])
        column = body['column']
        new_value = body['new_value']

        result = validate_change({"index": id, "column": column, "value": new_value})
        return JsonResponse(result)
    return JsonResponse({"ohno": "we are doomed"})


# def get_info_report(table):
#     res_reports = {}
#     all_element = table["offers"]
#     res_element = []
#     report_all = list(reversed(Report.objects.all().order_by("type")))
#     for i in report_all:
#         if i.index in res_reports.keys():
#             res_reports[i.index][i.column] = [i.type, i.reason]
#         else:
#             res_reports[i.index] = {i.column: [i.type, i.reason]}
#     for i in res_reports.keys():
#         res_element.append(all_element[i])
#     keys_rest_arr = list(res_reports.keys())[:10]
#     res_rest_elem = []
#     res_rest_rep = {}
#     for i in keys_rest_arr:
#         res_rest_elem.append(all_element[i])
#         res_rest_rep[i] = res_reports[i]
#     return [table["columns"], res_rest_elem, res_rest_rep]


def get_info_db(template_file_name="feeds/template.xml"):
    dict_const = ["index", "available", "price", "currencyId", "categoryId", "picture", "name",
                  "vendor", "description", "barcode", "article", "rating", "review_amount", "sale", "newby"]
    # dict_const = {"index": 0, "available": 1, "price": 2, "currencyId": 3, "categoryId": 4, "picture": 5, "name": 6, "vendor": 7,
    #        "description": 8, "barcode": 9, "article": 10, "rating": 11, "review_amount": 12, "sale": 13, "newby": 14}
    res_reports = {}
    report_all = list(reversed(Report.objects.all().order_by("type")))
    for i in report_all:
        if i.index in res_reports.keys():
            res_reports[i.index][i.column] = [i.type, i.reason, i.advice]
        else:
            res_reports[i.index] = {i.column: [i.type, i.reason, i.advice]}
    keys_rest_arr = list(res_reports.keys())[:10]
    res_rest_elem = []
    res_rest_rep = {}
    for i in keys_rest_arr:
        y = YandexOffer.objects.get(pk=i)
        dt = res_reports[i]
        res_elem = [y.index, {"value": y.available}, {"value": y.price}, {"value": y.currencyId}, {"value": y.categoryId}, {"value": y.picture}, {"value": y.name}, {"value": y.vendor},
                              {"value": y.description}, {"value": y.barcode}, {"value": y.article}, {"value": y.rating}, {"value": y.review_amount}, {"value": y.sale}, {"value": y.newby}]
        for j in dt.keys():
            res_elem[j]["type"] = res_reports[i][j][0]
            res_elem[j]["reason"] = res_reports[i][j][1]
            res_elem[j]["advice"] = res_reports[i][j][2]
        res_rest_elem.append(res_elem)
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
    return [columns, res_rest_elem]