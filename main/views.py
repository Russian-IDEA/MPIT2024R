from main.parsing import parse_file, parse_and_save
from django.shortcuts import render
from .models import Report


def home(request):
    filename = request.GET['filename']
    table = parse_and_save(f'feeds/{filename}')
    report = get_info_report(table)
    return render(request, 'index.html',
                  {
                      'columns': report[0],
                      'table': report[1],
                      'report': report[2]
                  })


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