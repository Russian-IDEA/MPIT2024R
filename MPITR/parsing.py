import lxml
from lxml import etree

parser = etree.XMLParser(encoding='utf-8',
                         recover=True)


def parse_tags(root) -> list[str]:
    """Парсит все не param теги. Используем через root.find('.//offer')."""
    tags = list()
    added = set('param')
    for element in root:
        if element.tag not in added:
            tags.append(element.tag)
            added.add(element.tag)

    return tags


def parse_param_names(root) -> list[str]:
    names = list()
    for param in root.findall("param"):
        names.append(param.attrib["name"])
    return names


def parse_offer_attrib(root) -> list[str]:
    names = list()
    for attrib in root.attrib:
        names.append(attrib)

    return names


def parse_xml(root, offer_attribs: list[str], tags: list[str], params_names: list[str]) -> list:
    offers = list()
    for offer in root.findall(".//offer"):
        offer_list = list()

        for attrib in offer_attribs:
            offer_list.append(offer.attrib[attrib])

        for tag in tags:
            offer_list.append(offer.find(tag).text)

        param_dict = dict()
        for param in offer.findall("param"):
            param_dict[param.attrib["name"]] = param.text
        for param_name in params_names:
            offer_list.append(param_dict[param_name])

        offers.append(offer_list)
    return offers


def parse_file(file_name: str = "../feeds/yandex_feed.xml"):
    tree = lxml.etree.parse(file_name, parser)
    root = tree.getroot()

    offer_attribs = parse_offer_attrib(root.find('.//offer'))
    tags = parse_tags(root.find('.//offer'))
    params_names = parse_param_names(root.find('.//offer'))

    offers = parse_xml(root, offer_attribs, tags, params_names)

    return offer_attribs + tags + params_names, offers