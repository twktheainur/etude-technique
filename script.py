import requests
import pandas as pd
from lxml import etree
import re

def get_body_text(root):
    for child in root.getchildren():
        if 'text' in child.tag:
            for subchild in child.getchildren():
                if 'body' in subchild.tag:
                    return ' '.join(subchild.itertext())

file = pd.read_excel('https://github.com/Kipre/etude-technique/blob/master/2020_export_Projet_Indexation_Automatique_Notice_accesTI_public_depuis2010_20200204.xlsx?raw=true')
file = file.loc[file.LANGUE_DOC=="fre"]

for i, pdf in file['ACCES_TEXTE_INTEGRAL'].iteritems():
    r = requests.get(pdf)
    r = requests.post('http://cloud.science-miner.com/grobid/api/processFulltextDocument', 
    	              files={'input': r.content})
    xml = r.text
    pattern = re.compile(r'<\?xml.*\?>')
    xml = pattern.sub('', xml)
    root = etree.fromstring(xml)
    fulltext = get_body_text(root)
    alphanumeric = re.compile("([^\s\w']|_|\n|\t)+")
    fulltext = alphanumeric.sub(' ', fulltext)
    query = '{"text": "' + fulltext + '", "language": {"lang": "fr"} }'
    r = requests.post('http://localhost:8090/service/disambiguate', 
    	              files={'query': query})
    print(r.text)

    if i == 0:
    	break
