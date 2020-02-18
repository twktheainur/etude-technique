import requests
import pandas as pd
from lxml import etree
import re

def get_body_text(root):
    for child in root.getchildren():
        print(child.tag)
        if 'text' in child.tag:
            for subchild in child.getchildren():
                print(subchild.tag)
                if 'body' in subchild.tag:
                    return ' '.join(subchild.itertext())

file = pd.read_excel('https://github.com/Kipre/etude-technique/blob/master/2020_export_Projet_Indexation_Automatique_Notice_accesTI_public_depuis2010_20200204.xlsx?raw=true')

for i, pdf in file['ACCES_TEXTE_INTEGRAL'].iteritems():
    r = requests.get(pdf)
    r = requests.post('http://cloud.science-miner.com/grobid/api/processFulltextDocument', files={'input': r.content})
    xml = r.text
    pattern = re.compile(r'<\?xml.*\?>')
    xml = pattern.sub('', xml)
    root = etree.fromstring(xml)
    fulltext = get_body_text(root)
    