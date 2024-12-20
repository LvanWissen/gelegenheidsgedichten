from rdflib import Graph, Dataset, ConjunctiveGraph, Namespace, OWL, XSD, SDO

bio = Namespace("http://purl.org/vocab/bio/0.1/")
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

    mapping = dict()
    sdo_sameAs_statements = []
    for s, p, o in g.triples((None, OWL.sameAs, None)):

        print(f"Processing {s} owl:sameAs {o}")

        # We prefer the canonical URI to be a data.bibliotheken.nl URI. If both are, we sort them and take the first.
        if "data.bibliotheken.nl" in s and "data.bibliotheken.nl" in o:
            canonical_uri, non_canonical_uri = sorted([s, o])
            sdo_sameAs_statements.append((canonical_uri, SDO.sameAs, non_canonical_uri))
        elif "data.bibliotheken.nl" in s:
            canonical_uri = s
            non_canonical_uri = o
        elif "data.bibliotheken.nl" in o:
            canonical_uri = o
            non_canonical_uri = s

        # If the canonical URI is not a data.bibliotheken.nl URI, we take the first one we encounter.
        else:
            canonical_uri, non_canonical_uri = sorted([s, o], reverse=True)

        mapping[non_canonical_uri] = mapping.get(canonical_uri, canonical_uri)

        # For external links (Ecartico, Wikidata, VIAF, Stadsarchief): move these to a schema:sameAs statement
        if (
            "ecartico.org" in non_canonical_uri
            or "wikidata.org" in non_canonical_uri
            or "viaf.org" in non_canonical_uri
            or "archief.amsterdam" in non_canonical_uri
        ):
            sdo_sameAs_statements.append((canonical_uri, SDO.sameAs, non_canonical_uri))
            print(f"Moving {non_canonical_uri} to schema:sameAs")

    # Create a new graph with the canonical URIs
    new_graph = Graph(identifier="https://data.goldenagents.org/datasets/ggd/")
    for s, p, o in g:
        s = mapping.get(s, s)
        o = mapping.get(o, o)

        if s != o:
            new_graph.add((s, p, o))

    for s, p, o in sdo_sameAs_statements:
        s = mapping.get(s, s)
        new_graph.add((s, p, o))

    return new_graph, mapping


if __name__ == "__main__":

    # Load the graphs
    g = ConjunctiveGraph()
    g.parse("rdf/ggd.jsonld", format="json-ld")
    g.parse("rdf/ggd_linkset.jsonld", format="json-ld")
    g.parse("rdf/ggd_dates.jsonld", format="json-ld")

    # Replace URIs with canonical URIs until no more OWL sameAs triples are present
    while sum(1 for _ in g.triples((None, OWL.sameAs, None))) > 0:
        print(sum(1 for _ in g.triples((None, OWL.sameAs, None))))
        g, mapping = canonize(g)

        print(mapping)

    ds = Dataset()
    g_ggd = ds.graph(identifier="https://data.goldenagents.org/datasets/ggd/")

    # Turn conjunctive graph into a regular graph
    for s, p, o in g:
        g_ggd.add((s, p, o))

    # Add some labels AND the religion info from SAA data
    g_external = ds.graph(
        identifier="https://data.goldenagents.org/datasets/ggd/external/"
    )
    g_external.parse("rdf/ggd_external.jsonld", format="json-ld")

    # Bind namespaces
    ds.bind("schema", SDO)
    ds.bind("kbdef", kbdef)
    ds.bind("owl", OWL)
    ds.bind("xsd", XSD)
    ds.bind("sem", sem)
    ds.bind("bio", bio)
    ds.bind("pnv", pnv)

    # Serialize! (two named graphs in the end)
    ds.serialize("rdf/ggd_canonized.trig", format="trig")
