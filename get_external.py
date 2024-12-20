import json
from rdflib import Graph, Literal, URIRef, RDF, RDFS, SDO, Namespace
from SPARQLWrapper import SPARQLWrapper, JSON
from pyld import jsonld

import pandas as pd

ENDPOINT = "http://graphdb.localhost/repositories/GA_ALL"  # My local GA-dump. You can also use data.goldenagents.org.

RPP = Namespace("https://data.goldenagents.org/ontology/rpp/")
SEM = Namespace("http://semanticweb.cs.vu.nl/2009/11/sem/")

CONTEXT = {
    "@context": {
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "rpp": "https://data.goldenagents.org/ontology/rpp/",
        "schema": "https://schema.org/",
        "comment": "rdfs:comment",
        "label": "rdfs:label",
        "religion": "rpp:hasReligion",
        "documentType": "schema:subjectOf",
        "churchReligion": "rpp:churchReligion",
        "place": "rpp:hasPlace",
        "date": {
            "@id": "http://semanticweb.cs.vu.nl/2009/11/sem/hasTimeStamp",
            "@type": "http://www.w3.org/2001/XMLSchema#date",
        },
    }
}


def get_label(uri, g):

    q = """
    PREFIX sem: <http://semanticweb.cs.vu.nl/2009/11/sem/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rpp: <https://data.goldenagents.org/ontology/rpp/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?label ?eventTypeLabel ?date ?churchLabel ?churchReligion ?religion {
    
    <URIHIER> rdfs:label ?label .
    
    ?record rpp:mentionsPerson <URIHIER> ;
            rpp:mentionsEvent ?event .
    
    ?event a ?eventType ;
           sem:hasTimeStamp ?date .
    
    ?eventType rdfs:label ?eventTypeLabel .

    ?event rpp:registers ?actualEvent .
    
    OPTIONAL { 
        ?actualEvent rpp:hasPlace ?church . 
        ?church rpp:hasReligion/rdfs:label ?churchReligion ;
                rdfs:label ?churchLabel .
        }

    OPTIONAL {
        ?actualEvent rpp:hasReligion/rdfs:label ?religion .
        }
 
    }
    """.replace(
        "URIHIER", uri
    )

    sparql = SPARQLWrapper(ENDPOINT)
    sparql.setQuery(q)
    sparql.setReturnFormat(JSON)
    sparql.addParameter("infer", "false")
    results = sparql.query().convert()

    if results["results"]["bindings"]:
        label, eventTypeLabel, date = (
            results["results"]["bindings"][0]["label"]["value"],
            results["results"]["bindings"][0]["eventTypeLabel"]["value"],
            results["results"]["bindings"][0]["date"]["value"],
        )

        if "religion" in results["results"]["bindings"][0]:
            religion = results["results"]["bindings"][0]["religion"]["value"]
        else:
            religion = None

        churchReligions = []
        for result in results["results"]["bindings"]:
            if "churchLabel" in result:
                churchLabel = result["churchLabel"]["value"]
                churchReligion = result["churchReligion"]["value"]
                churchReligions.append(churchReligion)
            else:
                churchLabel = None

        print(f"Label: {label}")
        print(f"Religion: {religion}")
        print(f"Church: {churchLabel}")
        print(f"Church religion: {churchReligions}")

        comment = f"Date: {date}. "

        if religion:
            comment += f" Religion: {religion}"
        if churchLabel:
            comment += f" Church: {churchLabel}"
        if churchReligions:
            comment += f" Church religions: {', '.join(churchReligions)}"

        g.add((URIRef(uri), RDF.type, SDO.Person))
        g.add((URIRef(uri), RDFS.label, Literal(label)))
        g.add((URIRef(uri), RDFS.comment, Literal(comment)))
        g.add((URIRef(uri), SEM.hasTimeStamp, Literal(date)))
        g.add(
            (URIRef(uri), SDO.subjectOf, Literal(eventTypeLabel))
        )  # To group on external link type

        if religion:
            g.add(
                (URIRef(uri), RPP.hasReligion, Literal(religion))
            )  # To group on religion

        if churchLabel:
            g.add((URIRef(uri), RPP.hasPlace, Literal(churchLabel)))

        if churchReligions:
            for churchReligion in churchReligions:
                g.add((URIRef(uri), RPP.churchReligion, Literal(churchReligion)))

    return g


if __name__ == "__main__":

    df = pd.read_csv("data/external_uri_saa.csv")

    g = Graph(identifier="https://data.goldenagents.org/datasets/ggd/external/")

    for n, uri in enumerate(df["uri"], 1):
        g = get_label(uri, g)

        print(f"Processed {n} URIs")

    # Serialize the graph first
    g.serialize("rdf/ggd_external.jsonld", format="json-ld")

    # Then compact it
    with open("rdf/ggd_external.jsonld") as f:

        doc = json.load(f)
        compacted = jsonld.compact(doc, CONTEXT)

    with open("rdf/ggd_external.jsonld", "w") as f:
        json.dump(compacted, f, indent=4)
