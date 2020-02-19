import requests
import pandas as pd
from lxml import etree
import re

def get_body_text(root):
    '''Extraxts the text from the "body" tag of a etree xml TEI'''
    
    for child in root.getchildren():
        if 'text' in child.tag:
            for subchild in child.getchildren():
                if 'body' in subchild.tag:
                    return ' '.join(subchild.itertext())

def pdf_to_xml(url):
    '''Takes an url of a pdf as an input and returns its parsed xml TEI'''
    
    r = requests.get(url)                  # fetching the pdf
    r = requests.post('http://cloud.science-miner.com/grobid/api/processFulltextDocument', 
                      files={'input': r.content})
    return r.text

def extract_entities(xml):
    '''Takes an xml string and returns a json with the entities'''
    
    pattern = re.compile(r'<\?xml.*\?>')   # we need to get rid of the xml declaration
    xml = pattern.sub('', xml)
    root = etree.fromstring(xml)
    fulltext = get_body_text(root)
    alphanumeric = re.compile("([^\w\s']|_|\n|\t)+")
    fulltext = alphanumeric.sub(' ', fulltext)
    query = '{"text": "' + fulltext + '", "language": {"lang": "fr"} }'
    r = requests.post('http://localhost:8090/service/disambiguate', 
                      files={'query': query})
    return r.text


