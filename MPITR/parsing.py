import lxml
from lxml import etree

parser = etree.XMLParser(encoding='utf-8',
                         recover=True)

def parse_tags(root) -> list[str]:
    tags = list()
    added = set('param')
    for element in root:
        if element.tag not in added:
            tags.append(element.tag)
            added.add(element.tag)

    return tags

def parse_params_amount(offer) -> int:
    return len(offer.findall('param'))


def parse_xml(root, tags: list[str], params_amount: int) -> dict:
    offers = {}
    for offer in root.findall(".//offer"):
        offerDict = list()
        for tag in tags:
            offerDict.append(offer.find(tag).text)

        # params = offer.findall("param")
        # for param in offer.findall("param"):
        #     offerDict.append(param.text)

        offers[offer.attrib["id"]] = offerDict
    return offers


def parse_file(file_name: str = "../feeds/yandex_feed.xml") -> dict:
    tree = lxml.etree.parse(file_name, parser)
    root = tree.getroot()

    tags = parse_tags(root.find('.//offer'))
    params_amount = parse_params_amount(root.find('.//offer'))
    offers = parse_xml(root, tags, params_amount)

    return offers

