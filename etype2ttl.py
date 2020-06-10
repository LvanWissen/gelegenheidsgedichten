import json
from rdflib import Graph, Namespace, OWL, Literal, URIRef, BNode, XSD, RDFS
from rdfalchemy import rdfSubject, rdfSingle, rdfMultiple

skos = Namespace("http://www.w3.org/2004/02/skos/core#")


class Concept(rdfSubject):
    rdf_type = skos.concept

    prefLabel = rdfMultiple(skos.prefLabel)

    skos.broaderTransitive = rdfMultiple(skos.broaderTransitive)
    skos.narrowerTransitive = rdfMultiple(skos.narrowerTransitive)

    relatedMatch = rdfMultiple(skos.relatedMatch)


def main(filepath, destination='data/etypes.ttl'):

    g = rdfSubject.db = Graph()

    with open(filepath) as infile:
        data = json.load(infile)

    for uri in data:

        concept = Concept(URIRef(uri))

        # Labels
        prefLabels = []
        for lang in data[uri]['prefLabel']:
            prefLabels.append(Literal(data[uri]['prefLabel'][lang], lang=lang))
        concept.prefLabel = prefLabels

        # Broader / Narrower
        broaders = []
        for broader in data[uri]['broaderTransitive']:
            broaders.append(URIRef(broader))
        concept.broaderTransitive = broaders

        # Matches
        matches = []
        for match in data[uri]['relatedMatch']:
            matches.append(URIRef(match))
        concept.relatedMatch = matches

    g.bind('skos', skos)
    g.serialize(destination=destination, format='turtle')


if __name__ == "__main__":
    main(filepath='data/eventTypes.json', destination='ttl/etypes.ttl')