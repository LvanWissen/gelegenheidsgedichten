from rdflib import Graph, ConjunctiveGraph, Namespace, OWL, XSD

bio = Namespace("http://purl.org/vocab/bio/0.1/")
schema = Namespace("https://schema.org/")
sem = Namespace("http://semanticweb.cs.vu.nl/2009/11/sem/")
pnv = Namespace("https://w3id.org/pnv#")

kbdef = Namespace("http://data.bibliotheken.nl/def#")


def canonize(g):
    """
    Canonizes URIs in an RDF graph by resolving OWL sameAs triples.

    This function processes an RDF graph and replaces non-canonical URIs with canonical ones based on OWL sameAs relationships.
    It prefers URIs from "data.bibliotheken.nl" when available. The function also resolves indirect mappings to ensure that
    all non-canonical URIs are mapped directly to their canonical counterparts.

    Args:
        g (rdflib.Graph): The input RDF graph containing triples with OWL sameAs relationships.

    Returns:
        tuple: A tuple containing:
            - new_graph (rdflib.Graph): The new RDF graph with canonical URIs.
            - mapping (dict): A dictionary mapping non-canonical URIs to their canonical counterparts.
    """

    mapping = {}
    for s, p, o in g.triples((None, OWL.sameAs, None)):

        # We prefer the canonical URI to be a data.bibliotheken.nl URI. If both are, we sort them and take the first.
        if "data.bibliotheken.nl" in s and "data.bibliotheken.nl" in o:
            canonical_uri, non_canonical_uri = sorted([s, o])
        elif "data.bibliotheken.nl" in o:
            canonical_uri = o
            non_canonical_uri = s
        # If the canonical URI is not a data.bibliotheken.nl URI, we take the first one we encounter.
        else:
            canonical_uri = s
            non_canonical_uri = o

        mapping[non_canonical_uri] = canonical_uri

    # Resolve indirect mappings
    for k in list(mapping.keys()):
        while mapping[k] in mapping:
            mapping[k] = mapping[mapping[k]]

    new_graph = Graph(identifier="https://data.goldenagents.org/datasets/ggd/")
    for s, p, o in g:
        s = mapping.get(s, s)
        o = mapping.get(o, o)

        if s != o:
            new_graph.add((s, p, o))

    return new_graph, mapping


if __name__ == "__main__":

    # Load the graph
    g = ConjunctiveGraph()
    g.parse("rdf/ggd.jsonld", format="json-ld")
    g.parse("rdf/ggd_linkset.jsonld", format="json-ld")
    g.parse("rdf/ggd_dates.jsonld", format="json-ld")

    # Replace URIs with canonical URIs until no more OWL sameAs triples are present
    while sum(1 for _ in g.triples((None, OWL.sameAs, None))) > 0:
        print(sum(1 for _ in g.triples((None, OWL.sameAs, None))))
        g, mapping = canonize(g)

        print(mapping)

    # Bind namespaces
    g.bind("schema", schema)
    g.bind("kbdef", kbdef)
    g.bind("owl", OWL)
    g.bind("xsd", XSD)
    g.bind("sem", sem)
    g.bind("bio", bio)
    g.bind("pnv", pnv)

    # Serialize!
    jsonld_data = g.serialize("rdf/ggd_canonized.trig", format="trig")
