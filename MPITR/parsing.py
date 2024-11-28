import lxml
from lxml import etree

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