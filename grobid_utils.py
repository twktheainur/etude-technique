import requests
import pandas as pd
from lxml import etree
import json
import re


def get_body_text(root):
    """Extracts the text from the "body" tag of a etree xml TEI"""

    for child in root.getchildren():
        if 'text' in child.tag:
            for sub_child in child.getchildren():
                if 'body' in sub_child.tag:
                    return ' '.join(sub_child.itertext())


def get_abstract_text(root):
    """Extracts the text from the "abstract" tag of a etree xml TEI"""

    for child in root.getchildren():
        if 'teiHeader' in child.tag:
            for sub_child in child.getchildren():
                if 'profileDesc' in sub_child.tag:
                    for sub_sub_child in sub_child.getchildren():
                        if 'abstract' in sub_sub_child.tag:
                            return ' '.join(sub_sub_child.itertext())


def pdf_to_xml(url):
    """Takes an url of a pdf as an input and returns its parsed xml TEI"""

    r = requests.get(url)  # fetching the pdf
    r = requests.post('http://cloud.science-miner.com/grobid/api/processFulltextDocument',
                      files={'input': r.content})
    return r.text


def extract_entities(xml, lang='fr', mode='fulltext'):
    """Takes an xml string and returns a json with the entities"""

    pattern = re.compile(r'<\?xml.*\?>')  # we need to get rid of the xml declaration
    xml = pattern.sub('', xml)
    root = etree.fromstring(xml)
    if mode == 'fulltext': 
        fulltext = get_body_text(root)
    elif mode == 'abstract':
        fulltext = get_abstract_text(root)
    else:
        raise Exception('Unknown mode ' + mode)
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


def to_agrovoc(concepts, agrovoc):
    """Transforms a list of strings (entities) to a set of concepts (tuples of (uri, label))
       requires an instance of an Agrovoc to make the queries"""

    result = set()
    for concept in concepts:
        result = result.union(agrovoc.find_with_agrovoc(concept))
    return result


def fetch_entities(text_json):
    """Extracts the entities and categories from a json string to a list"""

    text = json.loads(text_json)
    entities = [part["rawName"].strip() for part in text["entities"]]
    categories = [part["category"].strip() for part in text["global_categories"]]
    return entities + categories        
