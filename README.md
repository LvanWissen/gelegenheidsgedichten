# Gelegenheidsgedichten
[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-blue.svg)](https://creativecommons.org/licenses/by/4.0/)

RDF conversion of the Gelegenheidsgedichten [=Occasional Poetry] dataset, once collected by the Koninklijke Bibliotheek (https://www.kb.nl/onderzoeken-vinden/bijzondere-collecties/gelegenheidsgedichten). 

Part of the Golden Agents project (https://www.goldenagents.org/). Work in progress. 

- [Gelegenheidsgedichten](#gelegenheidsgedichten)
  - [Introduction](#introduction)
  - [Data](#data)
    - [Model](#model)
    - [Enrichments](#enrichments)
      - [Dates](#dates)
    - [Statistics](#statistics)
    - [Example data](#example-data)
  - [Contact](#contact)


## Introduction



## Data


### Model

### Enrichments

#### Dates

### Statistics


### Example data

**JSON-LD example**
```jsonld
{
  "id": "723",
  "type": [
    "CreativeWork",
    "ProductModel",
    "Book"
  ],
  "mainEntityOfPage": {
    "id": "723#description",
    "type": [
      "Dataset",
      "WebPage"
    ],
    "dateCreated": "2000-06-22",
    "dateModified": "2008-07-11",
    "description": "Vijftien gedichten.",
    "identifier": "723",
    "isPartOf": "https://data.goldenagents.org/datasets/ggd/"
  },
  "workExample": [
    {
      "type": [
        "CreativeWork",
        "ArchiveComponent",
        "Book",
        "IndividualProduct"
      ],
      "label": "Koninklijke Bibliotheek 852 F 403",
      "holdingArchive": "Koninklijke Bibliotheek",
      "itemLocation": "852 F 403",
      "sameAs": "http://data.bibliotheken.nl/id/nbt/e223556289"
    }
  ],
  "inLanguage": [
    "iso639-3:dut"
  ],
  "publication": {
    "id": "723#publication",
    "type": "PublicationEvent",
    "publishedBy": [
      {
        "id": "http://data.bibliotheken.nl/id/thes/p075565579",
        "type": "Organization",
        "label": "Rieuwertsz, Jan I",
        "name": [
          "Jan I Rieuwertsz"
        ],
        "hasName": [
          {
            "type": "PersonName",
            "id": "c47bf7d4-e5fb-5325-9e1f-bfb7294c00ad",
            "givenName": "Jan",
            "baseSurname": "I",
            "patronym": "Rieuwertsz",
            "literalName": "Jan I Rieuwertsz",
            "label": "Jan I Rieuwertsz"
          }
        ]
      }
    ],
    "description": "t'Amsterdam, by Jan Rieuwertsz. boekverkooper in de Beursstraat in't Martelaarsboek, 1679.",
    "location": {
      "type": "Place",
      "name": "Amsterdam",
      "id": "https://ecartico.org/places/11"
    },
    "startDate": 1679,
    "hasEarliestBeginTimeStamp": "1679-01-01",
    "hasLatestEndTimeStamp": "1679-12-31"
  },
  "author": [
    {
      "type": "Person",
      "label": "Petersom, J. van",
      "name": [
        "J. van Petersom"
      ],
      "hasName": [
        {
          "type": "PersonName",
          "id": "afd90513-3a6e-55c5-80a5-53884321f6f8",
          "initials": "J.",
          "baseSurname": "Petersom",
          "surnamePrefix": "van",
          "literalName": "J. van Petersom",
          "label": "J. van Petersom"
        }
      ],
      "id": "http://data.bibliotheken.nl/id/thes/p069755825"
    }
  ],
  "about": [
    {
      "type": "Event",
      "id": "1679-02-05-1",
      "label": "Overlijden (1679)",
      "eventType": [
        {
          "id": "https://data.goldenagents.org/thesaurus/overlijden",
          "type": "EventType",
          "label": "Overlijden"
        }
      ],
      "hasEarliestBeginTimeStamp": "1679-02-05",
      "hasLatestEndTimeStamp": "1679-02-05",
      "hasActor": [
        {
          "id": "http://data.bibliotheken.nl/id/thes/p068423667",
          "name": "Joost van den Vondel"
        }
      ],
      "hasTimeStamp": "1679-02-05",
      "location": [
        {
          "type": "Place",
          "name": "Amsterdam",
          "id": "https://ecartico.org/places/11"
        }
      ]
    },
    {
      "type": "Person",
      "label": "Vondel, Joost van den",
      "name": [
        "Joost van den Vondel"
      ],
      "hasName": [
        {
          "type": "PersonName",
          "id": "2cd48c43-7fbc-5e5e-9823-3721545189ea",
          "givenName": "Joost",
          "baseSurname": "Vondel",
          "surnamePrefix": "van den",
          "literalName": "Joost van den Vondel",
          "label": "Joost van den Vondel"
        }
      ],
      "gender": "Male",
      "sameAs_saa_begraaf": [
        "https://archief.amsterdam/indexen/deeds/8b589232-7d6f-4f54-9260-99341818bee6?person=99e87e15-ab4e-2bb2-e053-b784100a6a2e"
      ],
      "sameAs_ecartico": [
        "https://www.vondel.humanities.uva.nl/ecartico/persons/9696"
      ],
      "sameAs_wikidata": [
        "http://www.wikidata.org/entity/Q312673"
      ],
      "id": "http://data.bibliotheken.nl/id/thes/p068423667"
    }
  ],
  "name": "J. v. Petersoms Lykvaerzen, ter gedachtenis van den doorluchtigen po\u00ebet Joost van den Vondel, overleden den 5n. en begraven den 8n. van sprokkelmaand des jaars 1679. (Dr.m.)",
  "bibliographicFormat": "4\u00b0",
  "sameAs": "http://data.bibliotheken.nl/id/nbt/p841150109",
  "stcnCollationalFormula": "A{4}",
  "numberOfPages": 8
}
```

**Turtle example (canonized version)**
```ttl
<http://data.bibliotheken.nl/id/nbt/p841150109> a schema:Book,
        schema:CreativeWork,
        schema:ProductModel ;
    kbdef:bibliographicFormat "4°" ;
    kbdef:stcnCollationalFormula "A{4}" ;
    schema:about <http://data.bibliotheken.nl/id/thes/p068423667>,
        <https://data.goldenagents.org/datasets/ggd/1679-02-05-1> ;
    schema:author <http://data.bibliotheken.nl/id/thes/p069755825> ;
    schema:inLanguage "iso639-3:dut" ;
    schema:mainEntityOfPage <https://data.goldenagents.org/datasets/ggd/723#description> ;
    schema:name "J. v. Petersoms Lykvaerzen, ter gedachtenis van den doorluchtigen poëet Joost van den Vondel, overleden den 5n. en begraven den 8n. van sprokkelmaand des jaars 1679. (Dr.m.)" ;
    schema:numberOfPages 8 ;
    schema:publication <https://data.goldenagents.org/datasets/ggd/723#publication> ;
    schema:workExample <http://data.bibliotheken.nl/id/nbt/e223556289> .

<http://data.bibliotheken.nl/id/thes/p068423667> a schema:Person ;
    rdfs:label "Vondel, Joost van den" ;
    schema:birthDate "1587-11-17"^^xsd:date,
        "1587"^^xsd:gYear ;
    schema:deathDate "1679-02-05"^^xsd:date ;
    schema:gender schema:Male ;
    schema:name "Joost van den Vondel" ;
    pnv:hasName <https://data.goldenagents.org/datasets/ggd/personname/2cd48c43-7fbc-5e5e-9823-3721545189ea> .

<https://data.goldenagents.org/datasets/ggd/personname/2cd48c43-7fbc-5e5e-9823-3721545189ea> a pnv:PersonName ;
    rdfs:label "Joost van den Vondel" ;
    pnv:baseSurname "Vondel" ;
    pnv:givenName "Joost" ;
    pnv:literalName "Joost van den Vondel" ;
    pnv:surnamePrefix "van den" .

<https://data.goldenagents.org/datasets/ggd/1679-02-05-1> a sem:Event ;
    rdfs:label "Overlijden (1679)" ;
    sem:eventType <https://data.goldenagents.org/thesaurus/overlijden> ;
    sem:hasActor <http://data.bibliotheken.nl/id/thes/p068423667> ;
    sem:hasEarliestBeginTimeStamp "1679-02-05" ;
    sem:hasLatestEndTimeStamp "1679-02-05" ;
    sem:hasTimeStamp "1679-02-05" ;
    schema:location <https://ecartico.org/places/11> .

<https://data.goldenagents.org/thesaurus/overlijden> a sem:EventType ;
    rdfs:label "Overlijden" .

<https://ecartico.org/places/11> a schema:Place ;
    schema:name "Amsterdam" .

<http://data.bibliotheken.nl/id/thes/p069755825> a schema:Person ;
    rdfs:label "Petersom, J. van" ;
    schema:name "J. van Petersom" ;
    pnv:hasName <https://data.goldenagents.org/datasets/ggd/personname/afd90513-3a6e-55c5-80a5-53884321f6f8> .

<https://data.goldenagents.org/datasets/ggd/personname/afd90513-3a6e-55c5-80a5-53884321f6f8> a pnv:PersonName ;
    rdfs:label "J. van Petersom" ;
    pnv:baseSurname "Petersom" ;
    pnv:initials "J." ;
    pnv:literalName "J. van Petersom" ;
    pnv:surnamePrefix "van" .

<https://data.goldenagents.org/datasets/ggd/723#description> a schema:Dataset,
        schema:WebPage ;
    schema:dateCreated "2000-06-22"^^xsd:date ;
    schema:dateModified "2008-07-11"^^xsd:date ;
    schema:description "Vijftien gedichten." ;
    schema:identifier "723" ;
    schema:isPartOf <https://data.goldenagents.org/datasets/ggd/> .

<https://data.goldenagents.org/datasets/ggd/723#publication> a schema:PublicationEvent ;
    sem:hasEarliestBeginTimeStamp "1679-01-01" ;
    sem:hasLatestEndTimeStamp "1679-12-31" ;
    schema:description "t'Amsterdam, by Jan Rieuwertsz. boekverkooper in de Beursstraat in't Martelaarsboek, 1679." ;
    schema:location <https://ecartico.org/places/11> ;
    schema:publishedBy <http://data.bibliotheken.nl/id/thes/p075565579> ;
    schema:startDate "1679"^^xsd:gYear .

<http://data.bibliotheken.nl/id/thes/p075565579> a schema:Organization ;
    rdfs:label "Rieuwertsz, Jan I" ;
    schema:name "Jan I Rieuwertsz" ;
    pnv:hasName <https://data.goldenagents.org/datasets/ggd/personname/c47bf7d4-e5fb-5325-9e1f-bfb7294c00ad> .

<https://data.goldenagents.org/datasets/ggd/personname/c47bf7d4-e5fb-5325-9e1f-bfb7294c00ad> a pnv:PersonName ;
    rdfs:label "Jan I Rieuwertsz" ;
    pnv:baseSurname "I" ;
    pnv:givenName "Jan" ;
    pnv:literalName "Jan I Rieuwertsz" ;
    pnv:patronym "Rieuwertsz" .

<http://data.bibliotheken.nl/id/nbt/e223556289> a schema:ArchiveComponent,
        schema:Book,
        schema:CreativeWork,
        schema:IndividualProduct ;
    rdfs:label "Koninklijke Bibliotheek 852 F 403" ;
    schema:holdingArchive "Koninklijke Bibliotheek" ;
    schema:itemLocation "852 F 403" .
```


## Contact

l.vanwissen@uva.nl