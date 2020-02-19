from logging import getLogger

from rdflib import Graph, Namespace

from reconciler.dictionary import StringDictionaryLoader
from reconciler.recognizer.IntersStemConceptRecognizer import IntersStemConceptRecognizer

logger = getLogger("Agrovoc")


class Agovoc:
    def __init__(self, graph: Graph, agrovoc_path="claimskg/data/agrovoc-komplett.xml"):
        self.graph = graph
        logger.info("Loading agrovoc into ClaimsKG graph...")
        graph.load(agrovoc_path)

        string_entries = []
        pref_labels = graph.query("""SELECT ?x ?lf WHERE {
            ?x a skos:Concept;
            skosxl:prefLabel ?l.
            ?l skosxl:literalForm ?lf.
        }
        """, initNs=dict(skos=Namespace("http://www.w3.org/2004/02/skos/core#"),
                         skosxl=Namespace("http://www.w3.org/2008/05/skos-xl#")))

        for result in pref_labels:
            string_entries.append((str(result[0]), str(result[1])))

        alt_labels = graph.query("""SELECT ?x ?lf WHERE {
            ?x a skos:Concept;
            skosxl:altLabel ?l.
            ?l skosxl:literalForm ?lf.
        }
        """, initNs=dict(skos=Namespace("http://www.w3.org/2004/02/skos/core#"),
                         skosxl=Namespace("http://www.w3.org/2008/05/skos-xl#")))

        for result in alt_labels:
            string_entries.append((str(result[0]), str(result[1])))
        dictionary_loader = StringDictionaryLoader(string_entries)
        dictionary_loader.load()

        self.concept_recognizer = IntersStemConceptRecognizer(dictionary_loader,
                                                              "claimskg/data/stopwordsfr.txt",
                                                              "claimskg/data/termination_termsen.txt")
        self.concept_recognizer.initialize()

    def find_with_agrovoc(self, keyword):
        matching_annotations = self.concept_recognizer.recognize(keyword)
        return_annotations = set()
        for matching_annotation in matching_annotations:
            delta = matching_annotation.end - matching_annotation.start
            if len(keyword) == delta:
                return_annotations.add((matching_annotation.concept_id, matching_annotation.matched_text))
        return return_annotations
