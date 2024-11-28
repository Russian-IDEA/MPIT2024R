import math
import pymorphy2
import lxml
from django.shortcuts import render
from lxml import etree
from .models import Category

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


def parse_xml(root, offer_attribs, tags, params) -> list:
    offers = list()
    for offer in root.findall(".//offer"):
        offer_list = list()

        for attrib in offer_attribs:
            attrib_value = offer.attrib.get(attrib["name"])
            offer_list.append(attrib_value)

        for tag in tags:
            tag_element = offer.find(tag["name"])
            if tag_element is None:
                offer_list.append(None)
                continue

            offer_list.append(tag_element.text)

        param_dict = dict()
        for param in offer.findall("param"):
            param_dict[param.attrib["name"]] = param.text
        for param in params:
            value = param_dict.get(param["name"])
            offer_list.append(value)

        offers.append(offer_list)
    return offers


def parse_file(file_name: str = "../feeds/yandex_feed.xml", template_file_name: str = "feeds/template.xml"):
    template = lxml.etree.parse(template_file_name).getroot()
    parsed_template = parse_offer_attribs_tags_names(template)
    offer_attribs = parsed_template["attribs"]
    tags = parsed_template["tags"]
    params = parsed_template["params"]

    tree = lxml.etree.parse(file_name, parser)
    root = tree.getroot()
    offers = parse_xml(root, offer_attribs, tags, params)

    # generate columns
    columns = []
    for attrib in offer_attribs:
        columns.append(attrib["name"])
    for tag in tags:
        columns.append(tag["name"])
    for param in params:
        columns.append(param["name"])

    return columns, offers


def check_price(request):
    morph = pymorphy2.MorphAnalyzer()
    error_arr = []

    category = []
    M_category = []
    D_category = []
    res_offers = []

    offers_arr = parse_file("feeds/yandex_feed.xml")[1]
    # offers_arr = parse_file("/Users/user/PycharmProjects/NLTC/feeds/test.xml")[1]
    # offers_arr = parse_file("/Users/user/PycharmProjects/NLTC/feeds/san_yandex_feed.xml")[1]

    for ind, i in enumerate(offers_arr):
        if i[7] is None or i[3] is None:
            continue
        text = i[7]
        words = text.split()
        res_noun = ""
        for word in words:
            a = morph.parse(word)[0]
            if str(a.tag)[:4] == "NOUN":
                res_noun = a.normal_form
                break
        if res_noun == "":
            print("pricol")
            noun = words[0]
            error_arr.append([ind + 1, "name", 0, "В имени товара не найдено существительное"])
        else:
            noun = res_noun
        c_r = len(category)
        if noun not in category:
            category.append(noun)
            M_category.append([float(i[3]), 1])
            D_category.append(float(i[3]) ** 2)
        else:
            c_r = category.index(noun)
            M_category[category.index(noun)][1] += 1
            M_category[category.index(noun)][0] = M_category[category.index(noun)][0] / \
                                                  M_category[category.index(noun)][1] * (
                                                              M_category[category.index(noun)][1] - 1) + float(i[3]) / \
                                                  M_category[category.index(noun)][1]
            D_category[category.index(noun)] = D_category[category.index(noun)] / M_category[category.index(noun)][
                1] * (M_category[category.index(noun)][1] - 1) + (float(i[3]) ** 2) / M_category[category.index(noun)][
                                                   1]
        res_offers.append([text, i[3], c_r, ind + 1])

    res_category = []
    for i, c in enumerate(category):
        res_category.append([i, c, M_category[i][0], math.sqrt(D_category[i] - (float(M_category[i][0]) ** 2)), M_category[i][1]])
        # print(c + " | M | " + str(M_category[i][0]) + " | D | " + str(
        #     math.sqrt(D_category[i] - (float(M_category[i][0]) ** 2))))

    for c in res_offers:
        max_price = res_category[c[2]][2] + 4 * res_category[c[2]][3]
        min_price = res_category[c[2]][2] - 4 * res_category[c[2]][3]
        # print(str(c[0]) + " " + str(c[1]) + " max price:" + str(max_price))
        if float(c[1]) > float(max_price) or float(c[1]) < float(min_price):
            error_arr.append([c[3], "price", 0, "Цена товара слишком сильно отклоняется от средней"])

    saveCategoryMetric(res_category)
    # saveError(error_arr)
    return render(request, 'index.html',
                  {'columns': [], 'table': []})


def saveCategoryMetric(arr):
    for i in arr:
        obj = Category(id_category=int(i[0]), name=str(i[1]), mat_exp=float(i[2]), sigm=float(i[3]), count=int(i[4]))
        obj.save()
