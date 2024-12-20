import math
import pymorphy3

from django.shortcuts import render, redirect
from django.db.models import sql
from django.db import connection

import urllib
import lxml
from lxml import etree
from cityhash import CityHash64
import os

from .models import Category, Report, YandexOffer
import requests


parser = etree.XMLParser(encoding='utf-8',
                         recover=True)


def parse_bool(value: str):
    if value is None:
        return None

    if value == 'Да':
        return True
    elif value == 'Нет':
        return False
    elif value == 'да':
        return True
    elif value == 'нет':
        return False
    elif value == 'Yes':
        return True
    elif value == 'No':
        return False
    elif value == 'yes':
        return True
    elif value == 'no':
        return False
    elif value == 'true':
        return True
    elif value == 'false':
        return False
    elif value == 'True':
        return True
    elif value == 'False':
        return False

    return None


def parse_offer_attribs_tags_names(root):
    attribs = []
    for attrib in root.findall(".//attribute"):
        name = attrib.find("name").text
        localized_name = attrib.find("localizedname").text
        elem_type = attrib.attrib["type"]
        compulsory = bool(attrib.attrib["compulsory"])
        negative = parse_bool(attrib.attrib.get("negative"))
        attribs.append({"name": name, "localizedname": localized_name, "type": elem_type, "compulsory": compulsory, "negative": negative})

    tags = []
    for tag in root.findall(".//tag"):
        name = tag.find("name").text
        localized_name = tag.find("localizedname").text
        elem_type = tag.attrib["type"]
        compulsory = bool(tag.attrib["compulsory"])
        negative = parse_bool(tag.attrib.get("negative"))
        tags.append({"name": name, "localizedname": localized_name, "type": elem_type, "compulsory": compulsory, "negative": negative})

    params = []
    for param in root.findall(".//param"):
        name = param.find("name").text
        localized_name = param.find("localizedname").text
        elem_type = param.attrib["type"]
        compulsory = bool(param.attrib["compulsory"])
        negative = parse_bool(param.attrib.get("negative"))
        params.append({"name": name, "localizedname": localized_name, "type": elem_type, "compulsory": compulsory, "negative": negative})


    all_props = attribs + tags + params
    for i in range(len(all_props)):
        all_props[i]["column_index"] = i

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
            report.append({"index": i, "column": element_type["column_index"], "type": "technical", "reason": "Элемент должен быть указан", "advice": ""})
        return

    if value == "" and element_type["compulsory"]:
        report.append({"index": i, "column": element_type["column_index"], "type": "technical", "reason": "Элемент должен иметь значение", "advice": ""})
        return

    type = get_type(element_type)
    if type == bool:
        if element_type["compulsory"] and (value == "" or value is None):
            report.append({"index": i, "column": element_type["column_index"], "type": "technical", "reason": "Элемент должен иметь значение", "advice": ""})

        if value is None:
            offer_list.append(None)
            return

        value = parse_bool(value)

        if value is None:
            report.append({"index": i, "column": element_type["column_index"], "type": "technical", "reason": "Неверный двоичный тип", "advice": ""})
        offer_list.append(value)
        return

    try:
        value = type(value)

        if type == int or type == float:
            if not element_type["negative"] and value < 0:
                value = None
                report.append({"index": i, "column": element_type["column_index"], "type": "technical", "reason": "Значение должно быть неотрицательным", "advice": ""})
    except (ValueError, TypeError):
        value = None
        report.append({"index": i, "column": element_type["column_index"], "type": "technical", "reason": "Неверный тип данных", "advice": ""})

    offer_list.append(value)


def insert_element_by_type(i: int, offer_list: list, report: list, element_type: dict, element):
    if element is None:
        offer_list.append(None)
        if element_type["compulsory"]:
            report.append({"index": i, "column": element_type["column_index"], "type": "technical",
                           "reason": "Элемент должен быть указан", "advice": ""})
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
    ids = set()

    offer_elements = root.findall(".//offer")
    for i in range(len(offer_elements)):
        offer = offer_elements[i]

        id = offer.attrib.get("id")
        if id in ids:
            report.append({"index": id, "column": "index", "type": "technical", "reason": "Одинаковый индекс", "advice": ""})
            continue
        ids.add(id)

        offer_list = list()

        for attrib in offer_attribs:
            insert_value_by_type(id, offer_list, report, attrib, offer.attrib.get(attrib["name"]))

        for tag in tags:
            insert_element_by_type(id, offer_list, report, tag, offer.find(tag["name"]))

        param_dict = dict()
        for param in offer.findall("param"):
            param_dict[param.attrib["name"]] = param.text
        for param in params:
            insert_value_by_type(id, offer_list, report, param, param_dict.get(param["name"]))

        offer_hash = hash_offer_without_id(offer_list)
        if offer_hash in hashs:
            report.append({"index": id, "column": 99, "type": "technical", "reason": "Одинаковые значения полей", "advice": ""})
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
        columns.append(attrib["localizedname"])
    for tag in tags:
        columns.append(tag["localizedname"])
    for param in params:
        columns.append(param["localizedname"])
    columns.append("hash")

    props = []
    for attrib in offer_attribs:
        props.append(attrib)
    for tag in tags:
        props.append(tag)
    for param in params:
        props.append(param)

    return {"columns": columns, "offers": offers_data["offers"], "report": offers_data["report"], "props": props}


def parse_and_save(file_name: str = "feeds/yandex_feed.xml", template_file_name: str = "feeds/template.xml"):
    result = parse_file(file_name, template_file_name)
    print('saving xml')
    save_yandex_table(result["offers"])
    print('xml saved')
    print('checking price')
    check_price(result)
    print('price checked')
    save_report(result["report"])

    return result


def test_db(filename):
    result = parse_file(filename)
    print('saving xml')
    save_yandex_table(result["offers"])
    print('xml saved')

    print('checking price')
    check_price(result)
    print('price checked')

    print('price checked, saving reports')
    save_report(result["report"])


def check_price(offers_data: dict):
    morph = pymorphy3.MorphAnalyzer()

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
            report.append({"index": ind, "column": 7, "type": "logical", "reason": "В названии должно быть существительное", "advice": "Название"})
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
        res_category.append([i, c, M_category[i][0], math.sqrt(abs(D_category[i] - (float(M_category[i][0]) ** 2))), M_category[i][1]])

    for c in res_offers:
        max_price = res_category[c[2]][2] + 4 * res_category[c[2]][3]
        min_price = res_category[c[2]][2] - 4 * res_category[c[2]][3]

        if float(c[1]) > float(max_price):
            report.append({"index": c[3], "column": 2, "type": "logical", "reason": "Цена слишком высокая", "advice": round(res_category[c[2]][2], 2)})
        elif float(c[1]) < float(min_price):
            report.append({"index": c[3], "column": 2, "type": "logical", "reason": "Цена слишком низкая", "advice": round(res_category[c[2]][2], 2)})

    saveCategoryMetric(res_category)


def validate_change(change: dict):
    """change {"index": 0, "column": w, "value": "шииш"}"""
    rep = Report.objects.get(index=change["index"], column=change["column"])

    template = lxml.etree.parse("feeds/template.xml").getroot()
    parsed_template = parse_offer_attribs_tags_names(template)
    offer_attribs = parsed_template["attribs"]
    tags = parsed_template["tags"]
    params = parsed_template["params"]

    columns = []
    for attrib in offer_attribs:
        columns.append(attrib)
    for tag in tags:
        columns.append(tag)
    for param in params:
        columns.append(param)

    tech_report = validate_technical(change, columns)
    if not tech_report["valid"]:
        return tech_report
    change["value"] = tech_report["value"]

    delete_report({"index": change["index"], "column": change["column"]})
    change_value(change["index"], change["column"], tech_report["value"], columns)

    logical_report = validate_logical(change, columns, rep)
    if not logical_report["valid"]:
        add_report(logical_report["report"])
        return logical_report

    return {"valid": True}


def validate_technical(change: dict, columns: list[dict]):
    prop = columns[change["column"]]
    type = get_type(prop)
    compulsory = parse_bool(prop["compulsory"])
    negative = parse_bool(prop["negative"])

    if compulsory and (change["value"] is None or change["value"] == ""):
        report = {"index": change["index"], "column": change["column"], "type": "technical",
                  "reason": "Элемент должен иметь значение", "advice": ""}
        # add_report(report)
        return {"valid": False, "report": report}

    if type == bool:
        result = parse_bool(change["value"])
        if result is not None:
            change_value(change["index"], change["column"], result, columns)
            return {"valid": True, "value": result}

        report = {"index": change["index"], "column": change["column"], "type": "technical",
                  "reason": "Неверный двоичный тип", "advice": ""}
        # add_report(report)
        return {"valid": False, "report": report}

    try:
        value = type(change["value"])

        if type == int or type == float:
            if not negative and value < 0:
                report = {"index": change["index"], "column": change["column"], "type": "technical",
                          "reason": "Значение должно быть неотрицательным", "advice": ""}
                # add_report(report)
                return {"valid": False, "report": report}
    except (ValueError, TypeError):
        report = {"index": change["index"], "column": change["column"], "type": "technical",
                  "reason": "Неверный тип данных", "advice": ""}
        # add_report(report)
        return {"valid": False, "report": report}

    return {"valid": True, "value": value}


def validate_logical(change: dict, columns: list[dict], old_rep):
    morph = pymorphy3.MorphAnalyzer()

    name = change["value"]
    if change["column"] != 6:
        offer = YandexOffer.objects.get(index=change["index"])
        name = offer.name

    category = None
    for word in name.split():
        result = morph.parse(word)[0]
        if 'NOUN' in result.tag:
            category = result.normal_form
            break

    if change["column"] == 6 and category is None:
            report = {"index": change["index"], "column": 6, "type": "logical",
                      "reason": "В названии должно быть существительное", "advice": ""}
            add_report(report)
            return {"valid": False, "report": report}

    if change["column"] == 2:
        if category is None:
            # keep previous report
            old_rep.save()
            report = {"index": change["index"], "column": 2, "type": "logical",
                      "reason": "Сначала должно быть указано имя", "advice": ""}
            return report

        cat = Category.objects.get(name=category)
        value = change["value"]

        mat_exp = cat.mat_exp
        sigm = cat.sigm

        min_price = abs(mat_exp - 4 * sigm)
        max_price = abs(mat_exp + 4 * sigm)

        if value > max_price:
            report = {"index": change["index"], "column": 2, "type": "logical", "reason": "Цена слишком высокая", "advice": mat_exp}
            add_report(report)
            return {"valid": False, "report": report}
        if min_price > value:
            report = {"index": change["index"], "column": 2, "type": "logical", "reason": "Цена слишком низкая", "advice": mat_exp}
            add_report(report)
            return {"valid": False, "report": report}

    return {"valid": True}


def change_value(index: int, column: int, value, columns: list):
    inst = YandexOffer.objects.get(index=index)
    setattr(inst, columns[column]["name"], value)
    inst.save()


def delete_report(report: dict):
    inst = Report.objects.filter(index=report["index"], column=report["column"])[0]
    inst.delete()


def add_report(report: dict):
    db_rep = Report(index=report["index"], column=report["column"], type=report["type"], reason=report["reason"], advice=report["advice"])
    Report.save(db_rep)


def saveCategoryMetric(arr):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM categorymetric")

    print('creating categories')
    categories = list()
    for i in arr:
        obj = Category(id_category=int(i[0]), name=str(i[1]), mat_exp=float(i[2]), sigm=float(i[3]), count=int(i[4]))
        categories.append(obj)
    print('adding categories')
    Category.objects.bulk_create(categories, 1000)


def save_report(report: list):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM report")

    print('creating reports')
    reports = list()
    for r in report:
        db_report = Report(index=r["index"], column=r["column"], type=r["type"], reason=r["reason"], advice=r["advice"])
        reports.append(db_report)
    print('adding reports')
    Report.objects.bulk_create(reports, 1000)


def save_yandex_table(table: list):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM main_yandexoffer")

    print('creating offers')
    offers = list()
    for offer in table:

        db_offer = YandexOffer(index=offer[0], available=offer[1], price=offer[2], currencyId=offer[3],
                               categoryId=offer[4], picture=offer[5], name=offer[6],
                               vendor=offer[7], description=offer[8], barcode=offer[9],
                               article=offer[10], rating=offer[11], review_amount=offer[12],
                               sale=offer[13], newby=offer[14])
        offers.append(db_offer)

    print('adding offers')
    YandexOffer.objects.bulk_create(offers, 1000)

