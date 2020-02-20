from logging import getLogger

from rdflib import Graph, Namespace
import zipfile

from reconciler.dictionary import StringDictionaryLoader
from reconciler.recognizer.IntersStemConceptRecognizer import IntersStemConceptRecognizer

logger = getLogger("Agrovoc")


class Agrovoc:
    def __init__(self, graph: Graph, agrovoc_zip_path="data/agrovoc.zip"):
        self.graph = graph
        logger.info("Unzipping agrovoc...")
        with zipfile.ZipFile(agrovoc_zip_path, 'r') as zip_ref:
            rdf = zip_ref.read(zip_ref.namelist()[0])
        logger.info("Loading agrovoc into ClaimsKG graph...")

        #graph.parse(rdf)


g = Graph()
a = Agrovoc(g)
    #     string_entries = []
    #     pref_labels = graph.query("""SELECT ?x ?lf WHERE {
    #         ?x a skos:Concept;
    #         skosxl:prefLabel ?l.
    #         ?l skosxl:literalForm ?lf.
    #     }
    #     """, initNs=dict(skos=Namespace("http://www.w3.org/2004/02/skos/core#"),
    #                      skosxl=Namespace("http://www.w3.org/2008/05/skos-xl#")))

    #     for result in pref_labels:
    #         string_entries.append((str(result[0]), str(result[1])))

    #     alt_labels = graph.query("""SELECT ?x ?lf WHERE {
    #         ?x a skos:Concept;
    #         skosxl:altLabel ?l.
    #         ?l skosxl:literalForm ?lf.
    #     }
    #     """, initNs=dict(skos=Namespace("http://www.w3.org/2004/02/skos/core#"),
    #                      skosxl=Namespace("http://www.w3.org/2008/05/skos-xl#")))

    #     for result in alt_labels:
    #         string_entries.append((str(result[0]), str(result[1])))
    #     dictionary_loader = StringDictionaryLoader(string_entries)
    #     dictionary_loader.load()

    #     self.concept_recognizer = IntersStemConceptRecognizer(dictionary_loader,
    #                                                           "data/stopwordsfr.txt",
    #                                                           "data/termination_termsfr.txt")
    #     self.concept_recognizer.initialize()

    # def find_with_agrovoc(self, keyword):
    #     matching_annotations = self.concept_recognizer.recognize(keyword)
    #     return_annotations = set()
    #     for matching_annotation in matching_annotations:
    #         delta = matching_annotation.end - matching_annotation.start
    #         if len(keyword) == delta:
    #             return_annotations.add((matching_annotation.concept_id, matching_annotation.matched_text))
    #     return return_annotations
