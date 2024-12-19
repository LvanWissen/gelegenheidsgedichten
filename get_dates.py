import json
from collections import defaultdict

import requests
import pandas as pd

from pyld import jsonld
from rdflib import Graph, Literal, BNode, URIRef, RDF, PROV, SDO, XSD

cache = dict()

GGD_OTR_LEEFTIJDEN = "data/ggd_otr_leeftijden.csv"

df_ggd_otr = pd.read_csv(GGD_OTR_LEEFTIJDEN)

CONTEXT = {
    "birthDate_year": {
        "@id": "https://schema.org/birthDate",
        "@type": "http://www.w3.org/2001/XMLSchema#gYear",
    },
    "birthDate_date": {
        "@id": "https://schema.org/birthDate",
        "@type": "http://www.w3.org/2001/XMLSchema#date",
    },
    "deathDate_year": {
        "@id": "https://schema.org/deathDate",
        "@type": "http://www.w3.org/2001/XMLSchema#gYear",
    },
    "deathDate_date": {
        "@id": "https://schema.org/deathDate",
        "@type": "http://www.w3.org/2001/XMLSchema#date",
    },
    "wasDerivedFrom": {
        "@id": "http://www.w3.org/ns/prov#wasDerivedFrom",
        "@type": "@id",
    },
    "Statement": "http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement",
    "subject": {
        "@id": "http://www.w3.org/1999/02/22-rdf-syntax-ns#subject",
        "@type": "@id",
    },
    "predicate": {
        "@id": "http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate",
        "@type": "@id",
    },
    "object": {"@id": "http://www.w3.org/1999/02/22-rdf-syntax-ns#object"},
}


def query_endpoint(q: str, endpoint: str, source: str = ""):
    """
    Executes a SPARQL query against a specified endpoint and returns the results.
    Args:
        q (str): The SPARQL query string.
        endpoint (str): The URL of the SPARQL endpoint.
        source (str, optional): An optional source identifier to include in the results. Defaults to "".
    Returns:
        list: A list of dictionaries containing the query results.
    """

    # Prevent multiple queries for the same query string
    if q in cache:
        return cache[q]

    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
    }
    params = {"query": q}
    r = requests.get(endpoint, headers=headers, params=params)
    data = r.json()
    # time.sleep(0.1)

    results = []
    for r in data["results"]["bindings"]:

        if source:
            entry = {"source": source}
        else:
            entry = {}

        for k, v in r.items():
            entry[k] = v["value"]

        results.append(entry)

    cache[q] = results

    return results


def get_dates_from_nta(uri, endpoint="http://data.bibliotheken.nl/sparql"):
    """
    Get birth and death dates from the NTA dataset.

    Args:
        uri (str): The URI of the person.
        endpoint (str, optional): The SPARQL endpoint. Defaults to "http://data.bibliotheken.nl/sparql".

    Returns:
        list: A list of dictionaries containing the birth and death dates.
    """

    q = """
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX schema: <http://schema.org/>

    SELECT * WHERE {
        <URI> a schema:Person .
        
        OPTIONAL { 
            <URI> schema:birthDate ?birthDate_year .
            FILTER(DATATYPE(?birthDate_year) = xsd:gYear)
        }

        OPTIONAL {
            <URI> schema:birthDate ?birthDate_date .
            FILTER(DATATYPE(?birthDate_date) = xsd:date)
        }

        OPTIONAL {
            <URI> schema:deathDate ?deathDate_year .
            FILTER(DATATYPE(?deathDate) = xsd:gYear)
        }

        OPTIONAL {
            <URI> schema:deathDate ?deathDate_date .
            FILTER(DATATYPE(?deathDate) = xsd:date)
        }

    }
    """.replace(
        "<URI>", f"<{uri}>"
    )

    results = query_endpoint(
        q, endpoint, "http://data.bibliotheken.nl/id/dataset/persons"
    )
    print(uri, results)

    return results


def get_dates_from_ecartico(
    uri,
    endpoint="https://api.lod.uba.uva.nl/datasets/CREATE/ECARTICO/services/ECARTICO/sparql",
):
    """
    Get birth and death dates from Ecartico

    Args:
        uri (str): The URI of the person.
        endpoint (str, optional): The SPARQL endpoint. Defaults to "https://api.lod.uba.uva.nl/datasets/CREATE/ECARTICO/services/ECARTICO/sparql".

    Returns:
        list: A list of dictionaries containing the birth and death dates.
    """

    # The old data is still in the endpoint
    uri = uri.replace(
        "https://www.vondel.humanities.uva.nl/ecartico/", "https://ecartico.org/"
    )

    q = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX schema: <https://schema.org/>
    
    SELECT * WHERE {
        <URI> a schema:Person .
        
        OPTIONAL { 
            <URI> (schema:birthDate)|(schema:birthDate/xsd:value) ?birthDate_year .
            FILTER(!ISURI(?birthDate_year))
            FILTER(DATATYPE(?birthDate_year) = xsd:gYear)
        }

        OPTIONAL {
            <URI> (schema:birthDate)|(schema:birthDate/xsd:value) ?birthDate_date .
            FILTER(!ISURI(?birthDate_date))
            FILTER(DATATYPE(?birthDate_date) = xsd:date)
        }

        OPTIONAL {
            <URI> (schema:deathDate)|(schema:deathDate/xsd:value) ?deathDate_year .
            FILTER(!ISURI(?deathDate_year))
            FILTER(DATATYPE(?deathDate_year) = xsd:gYear)
        }

        OPTIONAL {
            <URI> (schema:deathDate)|(schema:deathDate/xsd:value) ?deathDate_date .
            FILTER(!ISURI(?deathDate_date))
            FILTER(DATATYPE(?deathDate_date) = xsd:date)
        }
    }
    """.replace(
        "<URI>", f"<{uri}>"
    )

    results = query_endpoint(q, endpoint, "https://ecartico.org/")
    print(results)

    return results


def get_dates_from_wikidata(uri, endpoint="https://query.wikidata.org/sparql"):
    """
    Get birth and death dates from Wikidata

    Args:
        uri (str): The URI of the person.
        endpoint (str, optional): The SPARQL endpoint. Defaults to "https://query.wikidata.org/sparql".

    Returns:
        list: A list of dictionaries containing the birth and death dates.
    """

    q = """
    PREFIX schema: <http://schema.org/>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX wikibase: <http://wikiba.se/ontology#>
    PREFIX psv: <http://www.wikidata.org/prop/statement/value/>

    SELECT * WHERE {
        <URI> wdt:P31 wd:Q5 ;
        
        OPTIONAL { 
            <URI> p:P569/psv:P569 ?birthDate .
            ?birthDate wikibase:timeValue ?birthDate_value ; 
                       wikibase:timePrecision ?precision .

            BIND(YEAR(?birthDate_value) AS ?birthDate_year)

            FILTER(?precision = 9)
        }

        OPTIONAL { 
            <URI> p:P569/psv:P569 ?birthDate .
            ?birthDate wikibase:timeValue ?birthDate_value ; 
                       wikibase:timePrecision ?precision .

            BIND(SUBSTR(STR(?birthDate_value), 1, 10) AS ?birthDate_date)

            FILTER(?precision = 11)
        }

        OPTIONAL { 
            <URI> p:P570/psv:P570 ?deathDate .
            ?deathDate wikibase:timeValue ?deathDate_value ; 
                       wikibase:timePrecision ?precision .

            BIND(YEAR(?deathDate_value) AS ?deathDate_year)

            FILTER(?precision = 9)
        }

        OPTIONAL { 
            <URI> p:P570/psv:P570 ?deathDate .
            ?deathDate wikibase:timeValue ?deathDate_value ; 
                       wikibase:timePrecision ?precision .

            BIND(SUBSTR(STR(?deathDate_value), 1, 10) AS ?deathDate_date)

            FILTER(?precision = 11)
        }
    }
    """.replace(
        "<URI>", f"<{uri}>"
    )

    results = query_endpoint(q, endpoint, "https://www.wikidata.org/")

    print(uri, results)

    return results


def get_dates_from_saa(uri):
    """
    Extracts age, birth date, and estimated birth year for a given person URI from a table.

    Args:
        uri (str): The URI of the person to extract dates for.

    Returns:
        list: A list containing a dictionary with the following keys:
            - "source" (str): The URI of the person.
            - "age" (int or None): The age of the person, if available.
            - "birthDate_year" (int or None): The estimated birth year of the person, if available.
            - "birthDate_date" (datetime or None): The birth date of the person, if available.
        If no data is found, returns an empty list.
    """

    frame = df_ggd_otr[df_ggd_otr["person"] == uri]

    age, birth_date, estimated_birth_year = None, None, None
    for row in frame.itertuples():

        if pd.notna(row.Age):
            age = row.Age

        if pd.notna(row.Birth_date):
            birth_date = row.Birth_date

        if pd.notna(row.Estimated_birth_year):
            estimated_birth_year = int(row.Estimated_birth_year)

    if age or birth_date or estimated_birth_year:
        print(uri, age, birth_date, estimated_birth_year)

        return [
            {
                "source": uri,
                "age": age,
                "birthDate_year": estimated_birth_year,
                "birthDate_date": birth_date,
            }
        ]
    else:
        return []


def main(persons):

    person2name = dict()
    person2dates = defaultdict(list)

    for r in persons:

        uri = r["uri"]
        name = r["name"]

        person2name[uri] = name

        # List possible sources for birth and death dates
        if "data.bibliotheken.nl" in uri:
            person2dates[uri] += get_dates_from_nta(uri)

        if r.get("ecartico"):
            person2dates[uri] += get_dates_from_ecartico(r["ecartico"])

        if r.get("wikidata"):
            person2dates[uri] += get_dates_from_wikidata(r["wikidata"])

        if r.get("saa"):
            person2dates[uri] += get_dates_from_saa(r["saa"])

    # Make a new dataset
    g = Graph(identifier="https://data.goldenagents.org/datasets/ggd/dates/")
    for uri, dates in person2dates.items():
        name = person2name[uri]
        uri = URIRef(uri)

        for d in dates:
            if d.get("birthDate_year") or d.get("birthDate_date"):

                if d.get("birthDate_year"):
                    date = Literal(d["birthDate_year"], datatype=XSD.gYear)
                else:
                    date = Literal(d["birthDate_date"], datatype=XSD.date)

                g.add((uri, SDO.birthDate, date))

                # statement
                statement_uri = BNode()
                g.add((statement_uri, RDF.type, RDF.Statement))
                g.add((statement_uri, RDF.subject, uri))
                g.add((statement_uri, RDF.predicate, SDO.birthDate))
                g.add((statement_uri, RDF.object, date))
                g.add((statement_uri, PROV.wasDerivedFrom, URIRef(d["source"])))

            if d.get("deathDate_year") or d.get("deathDate_date"):

                if d.get("deathDate_year"):
                    date = Literal(d["deathDate_year"], datatype=XSD.gYear)
                else:
                    date = Literal(d["deathDate_date"], datatype=XSD.date)

                g.add((uri, SDO.deathDate, date))

                # statement
                statement_uri = BNode()
                g.add((statement_uri, RDF.type, RDF.Statement))
                g.add((statement_uri, RDF.subject, uri))
                g.add((statement_uri, RDF.predicate, SDO.deathDate))
                g.add((statement_uri, RDF.object, date))
                g.add((statement_uri, PROV.wasDerivedFrom, URIRef(d["source"])))

    # Serialize the graph first
    g.serialize("rdf/ggd_dates.jsonld", format="json-ld")

    # Then compact it
    with open("rdf/ggd_dates.jsonld") as f:

        doc = json.load(f)
        compacted = jsonld.compact(doc, CONTEXT)

    with open("rdf/ggd_dates.jsonld", "w") as f:
        json.dump(compacted, f, indent=4)


if __name__ == "__main__":

    # Temporary endpoint
    ENDPOINT = "https://api.druid.datalegend.net/datasets/LvanWissen/Test/sparql"
    Q = """
        PREFIX schema: <https://schema.org/>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>

        SELECT * WHERE {
            ?uri a schema:Person ;
                 schema:name ?name .

            OPTIONAL {
                ?uri owl:sameAs ?ecartico .
                FILTER(CONTAINS(STR(?ecartico), "ecartico"))
            }

            OPTIONAL {
                ?uri owl:sameAs ?wikidata .
                FILTER(CONTAINS(STR(?wikidata), "wikidata"))
            }

            OPTIONAL {
                ?uri owl:sameAs ?saa .
                FILTER(CONTAINS(STR(?saa), "archief.amsterdam") || CONTAINS(STR(?saa), "jaikwil"))
            }
        }
    """

    results = query_endpoint(Q, ENDPOINT)

    main(results)
