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


def to_agrovoc(concepts, agrovoc):
    """Transforms a list of strings (entities) to a set of concepts (tuples of (uri, label))
       requires an instance of an Agrovoc to make the queries"""

    result = set()
    for concept in concepts:
        result = result.union(agrovoc.find_with_agrovoc(concept))
    return result        


class GrobidCallback:

    def __init__(self, agrovoc, message=""):
        self.average_accuracy = 0
        self.average_precision = 0
        self.average_recovery = 0
        self.average_nb_entities = 0
        self.message = message
        self.examples = 0
        self.memory = []
        self.text = ""
        self.agrovoc = agrovoc

    def update(self, descriptors, entities):
        """ 
        Updates the statistics.
      
        Parameters: 
        descriptors (set): set of the descriptor concepts (uri, label)
        entities (list): list of all the identified entities and categories by entity-fishing
      
        Returns: 
        str: Update message 
        """
        set2 = to_agrovoc(entities, self.agrovoc)
        self.text += ' '.join([word.replace(' ', '_') for _, word in set2])
        recovery = len(set2) / len(entities) if len(entities) > 0 else 0
        res = intersection(descriptors, set2)
        accuracy = len(res) / len(descriptors) if len(descriptors) > 0 else 0
        precision = len(res) / len(set2) if len(set2) > 0 else 0
        self.memory.append([accuracy, precision, recovery])
        self.average_accuracy = (self.average_accuracy * self.examples + accuracy) / (self.examples + 1)
        self.average_nb_entities = (self.average_nb_entities * self.examples + len(entities)) / (self.examples + 1)
        self.average_precision = (self.average_precision * self.examples + precision) / (self.examples + 1)
        self.average_recovery = (self.average_recovery * self.examples + recovery) / (self.examples + 1)
        self.examples += 1
        return "{} : {} , {} , {}".format(self.message, accuracy, precision, recovery)