import requests
import pandas as pd
from lxml import etree
import re


def get_body_text(root):
    """Extracts the text from the "body" tag of a etree xml TEI"""

    for child in root.getchildren():
        if 'text' in child.tag:
            for sub_child in child.getchildren():
                if 'body' in sub_child.tag:
                    return ' '.join(sub_child.itertext())


def pdf_to_xml(url):
    """Takes an url of a pdf as an input and returns its parsed xml TEI"""

    r = requests.get(url)  # fetching the pdf
    r = requests.post('http://cloud.science-miner.com/grobid/api/processFulltextDocument',
                      files={'input': r.content})
    return r.text


def extract_entities(xml, lang='fr'):
    """Takes an xml string and returns a json with the entities"""

    pattern = re.compile(r'<\?xml.*\?>')  # we need to get rid of the xml declaration
    xml = pattern.sub('', xml)
    root = etree.fromstring(xml)
    fulltext = get_body_text(root)
    alphanumeric = re.compile("([^\w\s']|_|\n|\t)+")
    fulltext = alphanumeric.sub(' ', fulltext)
    query = '{"text": "' + fulltext + '", "language": {"lang": "' + lang + '"} }'
    r = requests.post('http://cloud.science-miner.com/nerd/service/disambiguate',
                      files={'query': query})
    return r.text


def intersection(set1, set2):
    """Computes the intersection of two sets of concepts
       the sets must be populated with tuples of (uri, label)"""

    inter_concept = set()
    for concept1 in set1:
        for concept2 in set2:
            if concept1[0] == concept2[0]:
                inter_concept.add(concept1)
                break
    return inter_concept

