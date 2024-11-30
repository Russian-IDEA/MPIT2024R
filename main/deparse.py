import lxml
from lxml import etree

from .models import YandexOffer

from .parsing import parse_offer_attribs_tags_names


def yandex_offer_to_xml(template_file_name: str = "/Users/user/PycharmProjects/MPITR/feeds/templates.xml", output_file_name: str = "feeds/output.xml"):
    template = lxml.etree.parse(template_file_name).getroot()
    parsed_template = parse_offer_attribs_tags_names(template)

    # todo parse from file
    offer_attribs = ["available"]
    tags = ["price", "currencyId", "categoryId", "picture", "name", "vendor", "description", "barcode"]
    params = {"article": "Артикуль", "rating": "Рейтинг", "review_amount": "Количество оценок", "sale": "Скидка", "newby": "Новинка"}

    page = etree.Element('yml_catalog')

    doc = etree.ElementTree(page)

    shop = etree.SubElement(page, 'shop')
    offers = etree.SubElement(shop, 'offers')

    data = YandexOffer.objects.all()
    for db_entry in data:
        offer = etree.SubElement(offers, 'offer')

        offer.attrib["id"] = str(getattr(db_entry, "index"))
        for attrib in offer_attribs:
            offer.attrib[attrib] = str(getattr(db_entry, attrib))

        for tag in tags:
            value = getattr(db_entry, tag)
            value_element = etree.SubElement(offer, tag)

            if value is not None:
                value_element.text = str(value)

        for param in params:
            value = getattr(db_entry, param)
            value_element = etree.SubElement(offer, 'param')
            value_element.attrib["name"] = params[param]

            if value is not None:
                value_element.text = str(value)

    doc.write(output_file_name, xml_declaration=True, encoding='utf-8', pretty_print=True)