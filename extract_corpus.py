import os
import re
from typing import List

import pandas
from lxml import etree
from lxml.etree import XMLSyntaxError
from redis import Redis
from tqdm import tqdm

from grobid_utils import pdf_to_xml

namespaces = {
    'tei': 'http://www.tei-c.org/ns/1.0'
}

redis = Redis(decode_responses=True)


def extract_structure(xml_text):
    pattern = re.compile(r'<\?xml.*\?>')  # we need to get rid of the xml declaration
    xml = pattern.sub('', xml_text)
    try:
        root = etree.fromstring(xml, base_url="http://www.tei-c.org/ns/1.0/")

        title = root.xpath("//tei:fileDesc/tei:titleStmt/tei:title/text()", namespaces=namespaces)
        abstract = root.xpath("//tei:profileDesc/tei:abstract/text()", namespaces=namespaces)
        body = root.xpath("//tei:body//text()", namespaces=namespaces)

        body = " ".join(body)

        if len(title) > 0:
            title = title[0]
        else:
            title = ""

        if len(abstract) > 0:
            abstract = abstract[0]
        else:
            abstract = ""

        return title.strip(), abstract.strip(), body.strip()
    except XMLSyntaxError:
        return "", "", ""


def extract_corpus_dataframe(input_path, fileter_langs: List[str] = None, filter_article_types: List[int] = None,
                             limit_number=None) -> pandas.DataFrame:
    if ".xlsx" in input_path:
        dataframe = pandas.read_excel(input_path)
    else:
        dataframe = pandas.read_csv(
            '2020_export_Projet_Indexation_Automatique_Notice_accesTI_public_depuis2010_20200204.xlsx')

    if fileter_langs is not None and len(fileter_langs) > 0:
        dataframe = dataframe.loc[dataframe['LANGUE_DOC'].isin(fileter_langs)]

    dataframe = dataframe.dropna(subset=['DESCRIPTEURS'])

    if filter_article_types is not None:
        type_filter_pattern = ""
        for type in filter_article_types:
            str_rep = ""
            if type < 10:
                str_rep += "0"
            str_rep += str(type) + "-"
            type_filter_pattern += str_rep
            type_filter_pattern += "|"
        type_filter_pattern = type_filter_pattern[:-1]
        dataframe = dataframe.loc[dataframe['TYPE_DOC_GR'].str.contains(type_filter_pattern, na=False)]

    if limit_number > -1:
        dataframe = dataframe.head(limit_number)

    titles = []
    abstracts = []
    bodies = []
    keywords = []
    urls = []

    for i, row in tqdm(dataframe.iterrows(), total=len(dataframe)):
        pdf = row['ACCES_TEXTE_INTEGRAL']
        descriptors = row["DESCRIPTEURS"]

        xml = redis.get(pdf)
        if xml is None:
            xml = pdf_to_xml(pdf, "http://localhost:8070/api/processFulltextDocument")
            redis.set(pdf, xml)
        else:
            xml = str(xml)

        structure = extract_structure(xml_text=xml)
        titles.append(structure[0])
        abstracts.append(structure[1])
        bodies.append(structure[2])
        keywords.append(descriptors.strip())
        urls.append(pdf)

    dataframe["title_grobid"] = titles
    dataframe["abstract_grobid"] = abstracts
    dataframe["body_grobid"] = bodies

    return dataframe


dataframe = extract_corpus_dataframe(
    "2020_export_Projet_Indexation_Automatique_Notice_accesTI_public_depuis2010_20200204.xlsx",
    fileter_langs=['eng'], filter_article_types=[1, 2, 4], limit_number=100)
folder1 = "./eng_abstracts/"
folder2 = "./eng_fulltext/"
os.mkdir(folder1)
os.mkdir(folder2)
for index, row in dataframe.iterrows():
    filename = str(row["CLE"]) + ".txt"
    title = row["title_grobid"]
    abstract = row["RESUM"]
    if not isinstance(abstract, str):
        abstract = ""
    text = row["body_grobid"]

    with open(folder1 + filename, "w") as absfile:
        absfile.write(title + "\n")
        absfile.write(abstract + "\n")

    with open(folder2 + filename, "w") as fullfile:
        fullfile.write(title + "\n")
        fullfile.write(abstract + "\n")
        fullfile.write(text)

# dataframe.to_csv("corpus_titres_abstracts_corps_eng_articles-type_1_2_4_100_limit.csv")
