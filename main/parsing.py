import math
import pymorphy2
from django.shortcuts import render

import lxml
from lxml import etree
from cityhash import CityHash64

from .models import Category, Report, YandexOffer


parser = etree.XMLParser(encoding='utf-8',
                         recover=True)


def parse_offer_attribs_tags_names(root):
    attribs = []
    for attrib in root.findall(".//attribute"):
        name = attrib.text
        elem_type = attrib.attrib["type"]
        compulsory = bool(attrib.attrib["compulsory"])
        attribs.append({"name": name, "type": elem_type, "compulsory": compulsory})

    tags = []
    for tag in root.findall(".//tag"):
        name = tag.text
        elem_type = tag.attrib["type"]
        compulsory = bool(tag.attrib["compulsory"])
        tags.append({"name": name, "type": elem_type, "compulsory": compulsory})

    params = []
    for param in root.findall(".//param"):
        name = param.text
        elem_type = param.attrib["type"]
        compulsory = bool(param.attrib["compulsory"])
        params.append({"name": name, "type": elem_type, "compulsory": compulsory})

    return {"attribs": attribs, "tags": tags, "params": params}


def get_type(element: dict):
    if element["type"] == "int":
        return int
    elif element["type"] == "str":
        return str
    elif element["type"] == "bool":
        return bool
    elif element["type"] == "float":
        return float


def insert_value_by_type(i: int, offer_list: list, report: list, element_type: dict, value: str):
    if value is None:
        offer_list.append(None)
        if element_type["compulsory"]:
            report.append({"index": i, "column": element_type["name"], "type": "technical",
                           "reason": "compulsory element required"})
        return

    if value == "" and element_type["compulsory"]:
        report.append(
            {"index": i, "column": element_type["name"], "type": "technical", "reason": "compulsory element is empty"})
        return

    if get_type(element_type) == bool:
        if value == 'Да':
            offer_list.append(True)
        elif value == 'Нет':
            offer_list.append(False)
        elif value == 'да':
            offer_list.append(True)
        elif value == 'нет':
            offer_list.append(False)
        elif value == 'Yes':
            offer_list.append(True)
        elif value == 'No':
            offer_list.append(False)
        elif value == 'yes':
            offer_list.append(True)
        elif value == 'no':
            offer_list.append(False)
        elif value == 'true':
            offer_list.append(True)
        elif value == 'false':
            offer_list.append(False)
        elif value == 'True':
            offer_list.append(True)
        elif value == 'False':
            offer_list.append(False)
        return

    try:
        value = get_type(element_type)(value)
    except (ValueError, TypeError):
        value = None
        report.append({"index": i, "column": element_type["name"], "type": "technical", "reason": "invalid type"})

    offer_list.append(value)


def insert_element_by_type(i: int, offer_list: list, report: list, element_type: dict, element):
    if element is None:
        offer_list.append(None)
        if element_type["compulsory"]:
            report.append({"index": i, "column": element_type["name"], "type": "technical",
                           "reason": "compulsory element required"})
        return

    value = element.text
    insert_value_by_type(i, offer_list, report, element_type, value)


def hash_offer_without_id(offer_list: list) -> int:
    data = ""
    for i in range(1, len(offer_list)):
        value = offer_list[i]
        if value is not None:
            data += str(value)

    return CityHash64(data)


def parse_xml(root, offer_attribs, tags, params) -> dict:
    report = list()
    offers = list()
    hashs = set()

    offer_elements = root.findall(".//offer")
    for i in range(len(offer_elements)):
        offer = offer_elements[i]

        offer_list = list()

        for attrib in offer_attribs:
            insert_value_by_type(i, offer_list, report, attrib, offer.attrib.get(attrib["name"]))

        for tag in tags:
            insert_element_by_type(i, offer_list, report, tag, offer.find(tag["name"]))

        param_dict = dict()
        for param in offer.findall("param"):
            param_dict[param.attrib["name"]] = param.text
        for param in params:
            insert_value_by_type(i, offer_list, report, param, param_dict.get(param["name"]))

        offer_hash = hash_offer_without_id(offer_list)
        if offer_hash in hashs:
            report.append({"index": i, "column": "hash", "type": "technical", "reason": "equal hash"})
        else:
            hashs.add(offer_hash)
        offer_list.append(offer_hash)

        offers.append(offer_list)
    return {"offers": offers, "report": report}


def parse_file(file_name: str = "feeds/yandex_feed.xml", template_file_name: str = "feeds/template.xml"):
    print('launch')
    template = lxml.etree.parse(template_file_name).getroot()
    parsed_template = parse_offer_attribs_tags_names(template)
    offer_attribs = parsed_template["attribs"]
    tags = parsed_template["tags"]
    params = parsed_template["params"]

    tree = lxml.etree.parse(file_name, parser)
    root = tree.getroot()
    print('start parsing')
    offers_data = parse_xml(root, offer_attribs, tags, params)
    print('parsed')

    # generate columns
    columns = []
    for attrib in offer_attribs:
        columns.append(attrib["name"])
    for tag in tags:
        columns.append(tag["name"])
    for param in params:
        columns.append(param["name"])
    columns.append("hash")

    return {"columns": columns, "offers": offers_data["offers"], "report": offers_data["report"]}


def parse_and_save(file_name: str = "feeds/yandex_feed.xml", template_file_name: str = "feeds/template.xml"):
    result = parse_file(file_name, template_file_name)
    save_yandex_table(result["offers"])

def test_db(request):
    result = parse_file()
    save_yandex_table(result["offers"])

    # print('checking price')
    # check_price(result)
    #
    # print('price checked, saving reports')
    # save_report(result["report"])
    return render(request, 'index.html',
                  {'columns': [], 'table': []})


def check_price(offers_data: dict):
    morph = pymorphy2.MorphAnalyzer()

    category = []
    M_category = []
    D_category = []
    res_offers = []

    offers_cols = offers_data["columns"]
    offers_arr = offers_data["offers"]
    report = offers_data["report"]

    for ind, i in enumerate(offers_arr):
        if i[6] is None or i[2] is None:
            continue
        text = i[6]
        words = text.split()
        res_noun = ""
        for word in words:
            a = morph.parse(word)[0]
            if str(a.tag)[:4] == "NOUN":
                res_noun = a.normal_form
                break
        if res_noun == "":
            noun = words[0]
            report.append({"index": ind, "column": offers_cols[7], "type": "logical", "reason": "noun required in name"})
        else:
            noun = res_noun
        c_r = len(category)
        if noun not in category:
            category.append(noun)
            M_category.append([float(i[2]), 1])
            D_category.append(float(i[2]) ** 2)
        else:
            c_r = category.index(noun)
            M_category[category.index(noun)][1] += 1
            M_category[category.index(noun)][0] = M_category[category.index(noun)][0] / \
                                                  M_category[category.index(noun)][1] * (
                                                              M_category[category.index(noun)][1] - 1) + float(i[2]) / \
                                                  M_category[category.index(noun)][1]
            D_category[category.index(noun)] = D_category[category.index(noun)] / M_category[category.index(noun)][
                1] * (M_category[category.index(noun)][1] - 1) + (float(i[2]) ** 2) / M_category[category.index(noun)][
                                                   1]
        res_offers.append([text, i[2], c_r, ind + 1])

    res_category = []
    for i, c in enumerate(category):
        res_category.append([i, c, M_category[i][0], math.sqrt(D_category[i] - (float(M_category[i][0]) ** 2)), M_category[i][1]])

    for c in res_offers:
        max_price = res_category[c[2]][2] + 4 * res_category[c[2]][3]
        min_price = res_category[c[2]][2] - 4 * res_category[c[2]][3]

        if float(c[1]) > float(max_price) or float(c[1]) < float(min_price):
            report.append({"index": c[3], "column": "price", "type": "logical", "reason": "price too high/low"})

    saveCategoryMetric(res_category)


def saveCategoryMetric(arr):
    for i in arr:
        obj = Category(id_category=int(i[0]), name=str(i[1]), mat_exp=float(i[2]), sigm=float(i[3]), count=int(i[4]))
        obj.save()


def save_report(report: list):
    for r in report:
        db_report = Report(index=r["index"], column=r["column"], type=r["type"], reason=r["reason"])
        db_report.save()


def save_yandex_table(table: list):
    YandexOffer.objects.all().delete()
    for offer in table:
        db_offer = YandexOffer(index=offer[0], available=offer[1], price=offer[2], currencyId=offer[3],
                               categoryId=offer[4], picture=offer[5], name=offer[6],
                               vendor=offer[7], description=offer[8], barcode=offer[9],
                               article=offer[10], rating=offer[11], review_amount=offer[12],
                               sale=offer[13], newby=offer[14])
        db_offer.save()