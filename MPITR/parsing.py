import lxml
from lxml import etree

parser = etree.XMLParser(encoding='utf-8',
                         recover=True)


def parse_xml(root) -> dict:
    offers = {}
    for offer in root.findall(".//offer"):
        offerDict = {
            "available": offer.attrib["available"],
            "price": offer.find("price").text,
            "currencyID": offer.find("currencyId").text,
            "categoryId": offer.find("categoryId").text,
            "picture": offer.find("picture").text,
            "name": offer.find("name").text,
            "vendor": offer.find("vendor").text,
            "description": offer.find("description").text,
            "barcode": offer.find("barcode").text,
        }
        for param in offer.findall("param"):
            offerDict[param.attrib["name"]] = param.text

        offers[offer.attrib["id"]] = offerDict
    return offers


def parse_file(file_name: str = "../feeds/yandex_feed.xml") -> dict:
    tree = lxml.etree.parse(file_name, parser)
    root = tree.getroot()

    offers = parse_xml(root)

    return offers

