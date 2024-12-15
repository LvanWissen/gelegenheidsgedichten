import re
import json
from datetime import datetime
from collections import defaultdict
from itertools import count
import calendar

from typing import List, Dict
import uuid

GGDFILE = "data/Gelegenheidsgedichten_Golden Agents_KB.dmp"

KEYS = {
    "AAR": "event",
    "ABS": "description",
    "AN_GA": "item_saa_annotation",
    "AN_CBG": "item_cbg_annotation",
    "AN_KB": "item_kb_annotation",
    "AN_MMW": "item_mmw_annotation",
    "AN_MNL": "item_mnl_annotation",
    "AUT": "author",
    "BYZ": "comments",
    "COL": "collate",
    "DAT": "date",
    "EXE": "archive",
    "EXF": "exf",
    "EX_CBG": "item_cbg",
    "EX_GA": "item_saa",
    "EX_KB": "item_kb",
    "EX_MMW": "item_mmw",
    "EX_MNL": "item_mnl",
    "FMT": "format",
    "GED": "ged",
    "GEN": "society",
    "ILL": "illustrator",
    "IMP": "impressum",
    "INV": "created",
    "MEL": "melody",
    "MFN": "mfn",
    "MOT": "motif",
    "MUT": "modified",
    "PAG": "pages",
    "PLT": "place",
    "PSN": "person",
    "REC": "id",
    "REG": "registered",
    "STR": "steurid",
    "TAA": "language",
    "TIT": "title",
    "VWN": "signature",
    "WAT": "remarks",
}

k2archive = {
    "item_cbg": "Centraal Bureau voor Genealogie",
    "item_saa": "Stadsarchief Amsterdam",
    "item_kb": "Koninklijke Bibliotheek",
    "item_mmw": "Museum Meermanno",
    "item_mnl": "Bibliotheek van de Maatschappij der Nederlandse Letterkunde",
}

languages = {
    "Duits": "iso639-3:ger",
    "Engels": "iso639-3:eng",
    "Frans": "iso639-3:fre",
    "Fries": "iso639-3:stq",
    "Grieks": "iso639-3:gre",
    "Hebreeuws": "iso639-3:heb",
    "Italiaans": "iso639-3:ita",
    "Latijn": "iso639-3:lat",
    "Nederlands": "iso639-3:dut",
    "Spaans": "iso639-3:spa",
    "latijn": "iso639-3:lat",
}

# Thesaurus, anyone?
eventtype2uri = {
    "10-jarig huwelijk": "https://data.goldenagents.org/thesaurus/10-jarighuwelijk",
    "12,5-jarig huwelijk": "https://data.goldenagents.org/thesaurus/12en5-jarighuwelijk",
    "16-jarig huwelijk": "https://data.goldenagents.org/thesaurus/16-jarighuwelijk",
    "25-jarig huwelijk": "https://data.goldenagents.org/thesaurus/25-jarighuwelijk",
    "3-jarig huwelijk": "https://data.goldenagents.org/thesaurus/3-jarighuwelijk",
    "40-jarig huwelijk": "https://data.goldenagents.org/thesaurus/40-jarighuwelijk",
    "50-jarig huwelijk": "https://data.goldenagents.org/thesaurus/50-jarighuwelijk",
    "7-jarig huwelijk": "https://data.goldenagents.org/thesaurus/7-jarighuwelijk",
    "Aanvang studie": "https://data.goldenagents.org/thesaurus/aanvangstudie",
    "Afscheid": "https://data.goldenagents.org/thesaurus/afscheid",
    "Afwijzing beroep": "https://data.goldenagents.org/thesaurus/afwijzingberoep",
    "Ambtsaanvaarding": "https://data.goldenagents.org/thesaurus/ambtsaanvaarding",
    "Ambtsaftreden": "https://data.goldenagents.org/thesaurus/ambtsaftreden",
    "Geboorte": "https://data.goldenagents.org/thesaurus/geboorte",
    "Genezing": "https://data.goldenagents.org/thesaurus/genezing",
    "Huwelijk": "https://data.goldenagents.org/thesaurus/huwelijk",
    "Jubileum": "https://data.goldenagents.org/thesaurus/jubileum",
    "Kloosterintrede": "https://data.goldenagents.org/thesaurus/kloosterintrede",
    "Meesterproef": "https://data.goldenagents.org/thesaurus/meesterproef",
    "Overlijden": "https://data.goldenagents.org/thesaurus/overlijden",
    "Prijs": "https://data.goldenagents.org/thesaurus/prijs",
    "Promotie": "https://data.goldenagents.org/thesaurus/promotie",
    "Proponentsexamen": "https://data.goldenagents.org/thesaurus/proponentsexamen",
    "Verjaardag": "https://data.goldenagents.org/thesaurus/verjaardag",
    "Welkom": "https://data.goldenagents.org/thesaurus/welkom",
}

CONTEXT = {
    "@base": "https://data.goldenagents.org/datasets/ggd/",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "Dataset": "https://schema.org/Dataset",
    "WebPage": "https://schema.org/WebPage",
    "ArchiveComponent": "https://schema.org/ArchiveComponent",
    "IndividualProduct": "https://schema.org/IndividualProduct",
    "Book": "https://schema.org/Book",
    "CreativeWork": "https://schema.org/CreativeWork",
    "ProductModel": "https://schema.org/ProductModel",
    "MusicComposition": "https://schema.org/MusicComposition",
    "Person": "https://schema.org/Person",
    "Organization": "https://schema.org/Organization",
    "Place": "https://schema.org/Place",
    "Role": "https://schema.org/Role",
    "Event": "http://semanticweb.cs.vu.nl/2009/11/sem/Event",
    "PublicationEvent": "https://schema.org/PublicationEvent",
    "PersonName": "https://w3id.org/pnv#PersonName",
    "name": "https://schema.org/name",
    "description": "https://schema.org/description",
    "author": "https://schema.org/author",
    "publication": "https://schema.org/publication",
    "EventType": "http://semanticweb.cs.vu.nl/2009/11/sem/EventType",
    "eventType": "http://semanticweb.cs.vu.nl/2009/11/sem/eventType",
    "hasActor": "http://semanticweb.cs.vu.nl/2009/11/sem/hasActor",
    "hasPlace": "http://semanticweb.cs.vu.nl/2009/11/sem/hasPlace",
    "hasTime": "http://semanticweb.cs.vu.nl/2009/11/sem/hasTime",
    "hasEarliestBeginTimeStamp": "http://semanticweb.cs.vu.nl/2009/11/sem/hasEarliestBeginTimeStamp",
    "hasLatestBeginTimeStamp": "http://semanticweb.cs.vu.nl/2009/11/sem/hasLatestBeginTimeStamp",
    "hasEarliestEndTimeStamp": "http://semanticweb.cs.vu.nl/2009/11/sem/hasEarliestEndTimeStamp",
    "hasLatestEndTimeStamp": "http://semanticweb.cs.vu.nl/2009/11/sem/hasLatestEndTimeStamp",
    "hasBeginTimeStamp": "http://semanticweb.cs.vu.nl/2009/11/sem/hasBeginTimeStamp",
    "hasEndTimeStamp": "http://semanticweb.cs.vu.nl/2009/11/sem/hasEndTimeStamp",
    "hasTimeStamp": "http://semanticweb.cs.vu.nl/2009/11/sem/hasTimeStamp",
    "type": "@type",
    "id": "@id",
    "label": "http://www.w3.org/2000/01/rdf-schema#label",
    "comment": "http://www.w3.org/2000/01/rdf-schema#comment",
    "bibliographicFormat": "http://data.bibliotheken.nl/def#bibliographicFormat",
    "stcnCollationalFormula": "http://data.bibliotheken.nl/def#stcnCollationalFormula",
    "about": "https://schema.org/about",
    "inLanguage": "https://schema.org/inLanguage",
    "mainEntityOfPage": "https://schema.org/mainEntityOfPage",
    "numberOfPages": "https://schema.org/numberOfPages",
    "workExample": "https://schema.org/workExample",
    "itemLocation": "https://schema.org/itemLocation",
    "holdingArchive": "https://schema.org/holdingArchive",
    "locationCreated": "https://schema.org/location",
    "publishedBy": "https://schema.org/publishedBy",
    "startDate": {"@id": "https://schema.org/startDate", "@type": "xsd:gYear"},
    "hasName": {
        "@id": "https://w3id.org/pnv#hasName",
        "@context": {"@base": "https://data.goldenagents.org/datasets/ggd/personname/"},
        "@type": "@id",
    },
    "givenName": "https://w3id.org/pnv#givenName",
    "patronym": "https://w3id.org/pnv#patronym",
    "initials": "https://w3id.org/pnv#initials",
    "baseSurname": "https://w3id.org/pnv#baseSurname",
    "surnamePrefix": "https://w3id.org/pnv#surnamePrefix",
    "literalName": "https://w3id.org/pnv#literalName",
    "identifier": "https://schema.org/identifier",
    "isPartOf": {"@id": "https://schema.org/isPartOf", "@type": "@id"},
    "dateCreated": {"@id": "https://schema.org/dateCreated", "@type": "xsd:date"},
    "dateModified": {"@id": "https://schema.org/dateModified", "@type": "xsd:date"},
    "location": {"@id": "https://schema.org/location", "@type": "@id"},
    "sameAs": {"@id": "http://www.w3.org/2002/07/owl#sameAs", "@type": "@id"},
    "gender": {
        "@id": "https://schema.org/gender",
        "@type": "@id",
        "@context": {
            "@base": "https://schema.org/",
        },
    },
    "lyricsOf": {"@reverse": "https://schema.org/lyrics"},
    "arrangementOf": {"@reverse": "https://schema.org/musicArrangement"},
    # And now these custom types to keep _some_ semantics in the outgoing links
    "sameAs_saa_doop": {
        "@id": "http://www.w3.org/2002/07/owl#sameAs",
        "@type": "@id",
    },
    "sameAs_saa_otr": {
        "@id": "http://www.w3.org/2002/07/owl#sameAs",
        "@type": "@id",
    },
    "sameAs_saa_begraaf": {
        "@id": "http://www.w3.org/2002/07/owl#sameAs",
        "@type": "@id",
    },
    "sameAs_saa_na": {
        "@id": "http://www.w3.org/2002/07/owl#sameAs",
        "@type": "@id",
    },
    "sameAs_ecartico": {
        "@id": "http://www.w3.org/2002/07/owl#sameAs",
        "@type": "@id",
    },
    "sameAs_wikidata": {
        "@id": "http://www.w3.org/2002/07/owl#sameAs",
        "@type": "@id",
    },
    "sameAs_rkd": {
        "@id": "http://www.w3.org/2002/07/owl#sameAs",
        "@type": "@id",
    },
    "sameAs_other": {
        "@id": "http://www.w3.org/2002/07/owl#sameAs",
        "@type": "@id",
    },
}

CONTEXT_LINKS = {
    "type": "@type",
    "id": "@id",
    "label": "http://www.w3.org/2000/01/rdf-schema#label",
    "sameAs": {"@id": "http://www.w3.org/2002/07/owl#sameAs", "@type": "@id"},
}

## Mappings

personCounter = count(1)
recordCounter = defaultdict(lambda: count(1))
indexMapping = defaultdict(dict)  # some kind of hash dict for bnodes

## STCN
with open("data/ggd2stcn.json") as infile:
    GGD2STCN = json.load(infile)

with open("data/id2printer.json") as infile:
    ID2PRINTER = json.load(infile)

## Author/Person to URI (NTA or VIAF)
with open("data/id2author.json") as infile:
    ID2AUTHOR = json.load(infile)

with open("data/id2person.json") as infile:
    ID2PERSON = json.load(infile)

## Ecartico
with open("data/id2ecartico.json") as infile:
    ID2ECARTICO = json.load(infile)

## Gender based on given name
with open("data/id2gender.json") as infile:
    ID2GENDER = json.load(infile)

# SAA DTB
with open("data/id2doop.json") as infile:
    ID2DOOP = json.load(infile)

with open("data/id2otr.json") as infile:
    ID2OTR = json.load(infile)

with open("data/id2begraaf.json") as infile:
    ID2BEGRAAF = json.load(infile)

## SAA NA
with open("data/id2na_hv.json") as infile:
    ID2NA_HV = json.load(infile)

with open("data/id2na_boedel.json") as infile:
    ID2NA_BOEDEL = json.load(infile)

with open("data/id2na_testament.json") as infile:
    ID2NA_TESTAMENT = json.load(infile)

## RKD
with open("data/id2rkd.json") as infile:
    ID2RKD = json.load(infile)

## Wikidata
with open("data/id2wikidata.json") as infile:
    ID2WIKIDATA = json.load(infile)

## Liederenbank
with open("data/id2melodie.json") as infile:
    ID2MELODIE = json.load(infile)

## KB
with open("data/shelfmark2item.json") as infile:
    SHELFMARK2ITEM = json.load(infile)

## Everything into one big thesaurus
ID2THESAURUS = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
for ggdid in ID2PERSON:
    for name in ID2PERSON[ggdid]:
        ID2THESAURUS[ggdid]["person"][name] += ID2PERSON[ggdid][name]
for ggdid in ID2AUTHOR:
    for name in ID2AUTHOR[ggdid]:
        ID2THESAURUS[ggdid]["author"][name] += ID2AUTHOR[ggdid][name]
for ggdid in ID2PRINTER:
    for name in ID2PRINTER[ggdid]:
        ID2THESAURUS[ggdid]["printer"][name] += ID2PRINTER[ggdid][name]

## We link places to Ecartico
with open("data/place2ecartico.json") as infile:
    PLACE2ECARTICO = json.load(infile)

## And we have parsed the impressum info into place and year
with open("data/impressum_place_year.json") as infile:
    IMPRESSUMDATA = json.load(infile)


def unique(*args, ns=None):
    """
    Get a unique identifier (BNode or URIRef) for an entity based on an ordered
    list of values. Specify the namespace (ns) attribute to return a URIRef.

    Args:
        *args: Variable length argument list of values.
        ns: If given, return a URIRef on this namespace. Otherwise, return a BNode.

    Returns:
        A BNode or URIRef.
    """

    identifier = "".join(str(i) for i in args)  # order matters

    if not identifier:
        unique_id = str(uuid.uuid4())
    else:
        unique_id = str(uuid.uuid5(uuid.NAMESPACE_X500, identifier))

    if ns:
        return unique_id, ns + unique_id
    else:
        return unique_id, "_:" + unique_id


def parsePersonName(nameString: str, identifier_uri=None, ns=None):
    """
    Parse a name string into a unique PersonName object.

    Args:
        nameString (str): The name string to be parsed.
        identifier_uri (str, optional): The unique identifier or URI for the person. Defaults to None.
        ns (str, optional): The namespace for the unique identifier. Defaults to None.

    Returns:
        tuple: A tuple containing the parsed PersonName objects and the labels.
    """

    pns = []
    labels = []

    if "(" in nameString:
        nameString = re.sub(r" ?\(.*\) ?", "", nameString)

    if "," in nameString:
        last, first = nameString.split(",", 1)
        nameString = " ".join([first, last]).strip()

    for full_name in nameString.split(" / "):

        if ns:
            identifier, identifier_uri = unique(nameString, ns=ns)

        # Some static lists
        dets = ["van", "de", "den", "des", "der", "ten", "l'", "d'"]
        prefixes = ["Mr."]
        suffixes = ["Jr.", "Sr."]
        patronymfix = ("sz", "sz.", "szoon", "dr.", "dr", "sdochter")

        # Correcting syntax errors
        # full_name = full_name.replace('.', '. ')
        full_name = full_name.replace("'", "' ")
        full_name = full_name.replace("  ", " ")

        # Tokenise
        tokens = full_name.split(" ")
        tokens = [i.lower() for i in tokens]
        tokens = [i.title() if i not in dets else i for i in tokens]
        full_name = " ".join(
            tokens
        )  # ALL CAPS to normal name format (e.g. Mr. Jan van Tatenhove)
        full_name = full_name.replace(
            "' ", "'"
        )  # clunk back the apostrophe to the name

        # -fixes
        infix = " ".join(i for i in tokens if i in dets).strip()
        prefix = " ".join(i for i in tokens if i in prefixes).strip()
        suffix = " ".join(i for i in tokens if i in suffixes).strip()

        name_removed_fix = " ".join(
            i for i in tokens if i not in prefixes and i not in suffixes
        )

        if infix and infix in name_removed_fix:
            name = name_removed_fix.split(infix)
            first_name = name[0].strip()
            family_name = name[1].strip()

        else:
            name = name_removed_fix.split(" ", 1)
            if len(name) == 1:
                first_name = ""
                family_name = name[0]
            else:
                first_name = name[0]
                family_name = name[1]

        family_name_split = family_name.split(" ")
        first_name_split = first_name.split(" ")

        # build first name, family name, patronym and ignore -fixes
        first_name = " ".join(
            i for i in first_name_split if not i.endswith(patronymfix)
        ).strip()
        family_name = " ".join(
            i for i in family_name_split if not i.endswith(patronymfix)
        ).strip()
        patronym = " ".join(
            i for i in first_name_split + family_name_split if i.endswith(patronymfix)
        ).strip()

        full_name = " ".join(
            tokens
        ).strip()  # ALL CAPS to normal name format (e.g. Mr. Jan van Tatenhove)

        if first_name.endswith("."):
            initials = first_name
            givenName = None
        elif first_name != "":
            givenName = first_name
            initials = None
        else:
            givenName, initials = None, None

        pn = {"type": "PersonName"}

        if identifier:
            pn["id"] = identifier

        if givenName:
            pn["givenName"] = givenName

        if initials:
            pn["initials"] = initials

        if family_name:
            pn["baseSurname"] = family_name

        if patronym:
            pn["patronym"] = patronym

        if infix:
            pn["surnamePrefix"] = infix

        if prefix:
            pn["prefix"] = prefix

        if suffix:
            pn["disambiguatingDescription"] = suffix

        if full_name:
            pn["literalName"] = full_name.strip()
        else:
            pn["literalName"] = "Unknown"

        pn["label"] = pn["literalName"]

        pns.append(pn)
        labels.append(pn["literalName"])

    return pns, labels


def getRecords(filepath: str) -> List[Dict]:
    """
    Reads in the GGD Dump and converts it into a list of dicts.

    Args:
        filepath (str): Path to the GGD Dump file.

    Returns:
        List[Dict]: List of dictionaries (records) from the GGD data.
    """

    NONSPLIT = ("title", "impressum", "collate", "description", "comments", "pages")
    SPLIT = ("language", "item_cbg", "item_saa", "item_kb", "item_mmw", "item_mnl")

    records = []

    with open(filepath, encoding="utf-8-sig") as infile:
        data = infile.read()

        for r in data.split("\n$\n"):
            d = dict()

            for i in r.split("\n"):
                key, value = i.split(" ", 1)

                # Split into list
                if "; " in value and KEYS[key] not in NONSPLIT:
                    value = value.split("; ")

                # Force list with some properties
                elif KEYS[key] in SPLIT:
                    value = [value]

                d[KEYS[key]] = value

            records.append(d)

    return records


def getPersons(persons, getRole=False, recordID=None, indexMapping=indexMapping):
    """
    Parse information for a person/author.

    This function processes a list of persons, extracting and organizing various attributes such as roles,
    thesaurus entries, gender, and other related information. It also handles the creation of unique identifiers
    and mappings for each person.

    Args:
        persons (str or list): A single person as a string or a list of persons.
        getRole (bool, optional): Flag to determine if roles should be extracted from the person string. Defaults to False.
        recordID (str, optional): The record ID used to fetch additional information from various mappings. Defaults to None.
        indexMapping (dict, optional): A dictionary used to map persons to their unique identifiers. Defaults to indexMapping.

    Returns:
        list: A list of dictionaries, each containing detailed information about a person, including:
            - id (str): The unique identifier or URI for the person.
            - index (str): The generated index for the person.
            - person (str): The name of the person.
            - role (str or None): The role of the person if extracted.
            - thesaurus (list): A list of thesaurus entries related to the person.
            - gender (str or None): The gender of the person if available.
            - otr (list): A list of OTR entries related to the person.
            - doop (list): A list of baptism (doop) entries related to the person.
            - begraaf (list): A list of burial (begraaf) entries related to the person.
            - rkd (list): A list of RKD entries related to the person.
            - wikidata (list): A list of Wikidata entries related to the person.
            - ecartico (list): A list of ECARTICO entries related to the person.
            - na (list): A list of NA entries related to the person.
            - sameAs_other (list): A list of other URIs related to the person.
    """
    plist = []

    if type(persons) is str:
        persons = [persons]
    elif persons is None:
        return []

    for _, person in enumerate(persons, 1):
        if getRole and ". " in person:
            if person.count(".") > 1:
                # initials
                person, role = person.rsplit(".", 1)
                if not person.endswith((")", "van", "de")):  # e.g. (wed.)
                    person += "."
            else:
                person, role = person.rsplit(". ", 1)

            person = person.strip()
            role = role.strip()

            # We are not interested in these names
            if role in ("Overige functies", "Comp", "Med", "Pap"):
                continue
        else:
            role = None

        if recordID and recordID in ID2THESAURUS:
            if role == "Drukker/uitgever":
                thesaurus = ID2THESAURUS[recordID]["printer"].get(person, [])
            elif role is None:
                thesaurus = ID2THESAURUS[recordID]["author"].get(person, [])
            else:
                thesaurus = ID2THESAURUS[recordID]["person"].get(person, [])
        else:
            thesaurus = []

        uri = None
        sameAs_other = []
        for i in thesaurus:
            if "data.bibliotheken.nl/id/" in i:
                uri = i
            elif "http://thesaurus.cerl.org/record/cni" in i:
                uri = i
            else:
                sameAs_other.append(i)

        if recordID and recordID in ID2GENDER:
            gender = ID2GENDER[recordID].get(person)
        else:
            gender = None

        if recordID and recordID in ID2OTR:
            otr = ID2OTR[recordID].get(person, [])
        else:
            otr = []

        if recordID and recordID in ID2DOOP:
            doop = ID2DOOP[recordID].get(person, [])
        else:
            doop = []

        if recordID and recordID in ID2BEGRAAF:
            begraaf = ID2BEGRAAF[recordID].get(person, [])
        else:
            begraaf = []

        if recordID and recordID in ID2RKD:
            rkd = ID2RKD[recordID].get(person, [])
        else:
            rkd = []

        if recordID and recordID in ID2WIKIDATA:
            wikidata = ID2WIKIDATA[recordID].get(person, [])
        else:
            wikidata = []

        if recordID and recordID in ID2ECARTICO:
            ecartico = ID2ECARTICO[recordID].get(person, [])
        else:
            ecartico = []

        # NA
        na = []
        if recordID and recordID in ID2NA_HV:
            na += ID2NA_HV[recordID].get(person, [])
        if recordID and recordID in ID2NA_BOEDEL:
            na += ID2NA_BOEDEL[recordID].get(person, [])
        if recordID and recordID in ID2NA_TESTAMENT:
            na += ID2NA_TESTAMENT[recordID].get(person, [])

        # index = "urn:goldenagents:ggd:person:ggd" + str(next(personCounter)).zfill(4)
        index = f"urn:goldenagents:ggd:person:{recordID}:{str(next(recordCounter[recordID])).zfill(2)}"
        indexMapping[recordID][person] = uri or index  # we prefer the thesaurus URI

        plist.append(
            {
                "id": uri or index,
                "index": index,
                "person": person,
                "role": role,
                "thesaurus": thesaurus,
                "gender": gender,
                "otr": otr,
                "doop": doop,
                "begraaf": begraaf,
                "rkd": rkd,
                "wikidata": wikidata,
                "ecartico": ecartico,
                "na": na,
                "sameAs_other": sameAs_other,
            }
        )

    return plist


def getEvent(record: dict, persons: list) -> dict:
    """
    Parse event information (date, place, actors) from a record and create a JSON-LD formatted event.

    Args:
        record (dict): A dictionary containing the record data.
        persons (list): A list of persons related to the event.

    Returns:
        dict: A dictionary representing the JSON-LD formatted event.
    """

    if record["date"][10:]:
        # Example: 1781-02-01-5-c
        eventid = record["date"][:12]
        record["date"] = record["date"][:10]
    else:
        eventid = record["date"]

    year = record["date"][:4]

    if record["date"].endswith("00-00"):
        timeStamp = None

        if "XX-" in record["date"].upper():
            earliestBeginTimeStamp = record["date"][:2] + "00-01-01"
            latestEndTimeStamp = record["date"][:2] + "99-12-31"
        elif "X-" in record["date"].upper():
            earliestBeginTimeStamp = (
                record["date"].upper().replace("X-", "0-")[:4] + "-01-01"
            )
            latestEndTimeStamp = (
                record["date"].upper().replace("X-", "9-")[:4] + "-12-31"
            )
        else:
            earliestBeginTimeStamp = record["date"][:4] + "-01-01"
            latestEndTimeStamp = record["date"][:4] + "-12-31"

    elif record["date"].endswith("00"):
        timeStamp = None
        earliestBeginTimeStamp = record["date"][:7] + "-01"

        year = int(record["date"][:4])
        month = int(record["date"][5:7])
        _, lastday = calendar.monthrange(year, month)

        latestEndTimeStamp = record["date"][:7] + "-" + str(lastday).zfill(1)
    else:
        timeStamp = record["date"]
        earliestBeginTimeStamp = record["date"]
        latestEndTimeStamp = record["date"]

    if record.get("place") and type(record["place"]) is str:
        place = [record["place"]]
    else:
        place = record.get("place", [])

    place = [PLACE2ECARTICO[i] for i in place]

    if record.get("event") and type(record["event"]) is str:
        eType = [record["event"]]
    else:
        eType = record.get("event", [])

    eTypes = [{"id": eventtype2uri[i], "type": "EventType", "label": i} for i in eType]

    # Participants, this can be shortened to id + name
    actors = [{"id": p["id"], "name": p["name"][0]} for p in persons]

    event = {
        "type": "Event",
        "id": eventid,
        "label": f"{' & '.join(eType)} ({year})",
        "eventType": eTypes,
        "hasEarliestBeginTimeStamp": earliestBeginTimeStamp,
        "hasLatestEndTimeStamp": latestEndTimeStamp,
        "hasActor": actors,
    }

    if timeStamp:
        event["hasTimeStamp"] = timeStamp

    if place:
        event["location"] = place

    return event


def getMelody(record_id, melody_name):
    """
    Retrieve melody information and create a music composition arrangement
    to link to the Liederenbank.

    Args:
        record_id (str): The identifier for the record in the ID2MELODIE dictionary.
        melody_name (str): The name of the melody to be used in the arrangement.

    Returns:
        dict: A dictionary representing the music composition arrangement (cf. schema.org).
    """

    liederenbank = ID2MELODIE.get(record_id, None)

    arrangement = {"type": "MusicComposition", "name": melody_name}

    if liederenbank:
        arrangement["arrangementOf"] = []

        for liederenbank_name, liederenbank_uri in liederenbank.items():
            melody = {
                "id": liederenbank_uri,
                "name": liederenbank_name,
                "type": "MusicComposition",
            }

            arrangement["arrangementOf"].append(melody)  # inverse: musicalArrangement

    return arrangement


def parseRecordJSONLD(record: dict):
    """
    Parses a GGD record dictionary into a valid JSON-LD formatted document.

    Args:
        record (dict): A dictionary containing the record data.

    Returns:
        dict: A dictionary representing the JSON-LD formatted document.
    """

    _stcn = GGD2STCN.get(record["id"])

    _all_persons = getPersons(record.get("person"), recordID=record["id"], getRole=True)
    _authors = getPersons(record.get("author"), recordID=record["id"])

    _printer_publishers = [i for i in _all_persons if i["role"] == "Drukker/uitgever"]
    _persons = [i for i in _all_persons if i["role"] != "Drukker/uitgever"]

    persons = getPerson(_persons)

    if record["id"] in IMPRESSUMDATA and IMPRESSUMDATA[record["id"]]["place"]:
        _printer_publisher_place = PLACE2ECARTICO[IMPRESSUMDATA[record["id"]]["place"]]
    else:
        _printer_publisher_place = None

    # impressum date
    if record["id"] in IMPRESSUMDATA and IMPRESSUMDATA[record["id"]]["year"]:
        _printer_publisher_year = IMPRESSUMDATA[record["id"]]["year"]
    else:
        _printer_publisher_year = None

    _event = getEvent(record, persons)

    doc = {
        "id": record["id"],
        "type": ["CreativeWork", "ProductModel", "Book"],
        "mainEntityOfPage": {
            "id": record["id"] + "#description",
            "type": ["Dataset", "WebPage"],
            "dateCreated": datetime.strptime(record["created"], "%d-%m-%Y").strftime(
                "%Y-%m-%d"
            ),
            "dateModified": datetime.strptime(record["modified"], "%d-%m-%Y").strftime(
                "%Y-%m-%d"
            ),
            "description": record["description"],
            "identifier": record["id"],
            "isPartOf": "https://data.goldenagents.org/datasets/ggd/",
        },
        "workExample": getWorkExample(record),
        "inLanguage": [languages[i] for i in record["language"]],
        "publication": getPublication(
            record["id"],
            record.get("impressum"),
            _printer_publishers,
            _printer_publisher_place,
            _printer_publisher_year,
        ),
        "author": getPerson(_authors),
        "about": [_event] + persons,
    }

    if record.get("title"):
        doc["name"] = record["title"]

    if record.get("format"):
        doc["bibliographicFormat"] = record["format"]

    if _stcn:
        doc["sameAs"] = _stcn

    if record.get("collate"):
        doc["stcnCollationalFormula"] = record["collate"]

    if record.get("pages"):
        pages, _ = record["pages"].split(" ", 1)
        pages = int(pages)
        doc["numberOfPages"] = pages

    if record.get("melody"):
        doc["lyricsOf"] = getMelody(record["id"], record["melody"])  # inverse: lyrics

    return doc


def getPerson(person_data):
    """
    Further parse and structure information about a person.

    This function parses names and external links for a person. These are
    added in separate keys in the person's dictionary, to make it easier to
    see where a link came from (e.g. SAA, Ecartico, or Wikidata).

    Args:
        person_data (list): A list of dictionaries, where each dictionary
                            contains information about a person.

    Returns:
        list: A list of dictionaries, where each dictionary represents
              a person with structured data.
    """

    persons = []

    for p in person_data:
        p_personnames, p_names = parsePersonName(
            p["person"], ns="https://data.goldenagents.org/datasets/ggd/personname/"
        )

        person = {
            "type": "Person",
            "label": p["person"],
            "name": p_names,
            "hasName": p_personnames,
        }

        if p["gender"]:
            person["gender"] = p["gender"]

        # External links (SAA, Ecartico, Wikidata)
        # Use the JSON-LD context and structure to make it easier to see where a link came from.
        if p["doop"]:
            person["sameAs_saa_doop"] = p["doop"]

        if p["otr"]:
            person["sameAs_saa_otr"] = p["otr"]

        if p["begraaf"]:
            person["sameAs_saa_begraaf"] = p["begraaf"]

        if p["na"]:
            person["sameAs_saa_na"] = p["na"]

        if p["ecartico"]:
            person["sameAs_ecartico"] = p["ecartico"]

        if p["wikidata"]:
            person["sameAs_wikidata"] = p["wikidata"]

        if p["rkd"]:
            person["sameAs_rkd"] = p["rkd"]

        if p.get("sameAs_other"):
            person["sameAs_other"] = p["sameAs_other"]

        person["id"] = p["id"]

        persons.append(person)

    return persons


def getPublication(
    record_id: str,
    impressum: str,
    printer_publishers: list,
    place: dict,
    year: int,
) -> dict:
    """
    Create a publication event dictionary with provided details.

    Args:
        record_id (str): The unique identifier for the record.
        impressum (str): The impressum or description of the publication.
        printer_publishers (list): A list of printer or publisher details.
        place (dict): A dictionary containing location details of the publication.
        year (int): The year of publication.

    Returns:
        dict: A dictionary representing the publication event with keys such as:
            - 'id'
            - 'type'
            - 'publishedBy'
            - 'description'
            - 'location'
            - 'startDate'
            - 'hasEarliestBeginTimeStamp'
            - 'hasLatestEndTimeStamp'
    """

    publicationEvent = {
        "id": f"{record_id}#publication",
        "type": "PublicationEvent",
        "publishedBy": getPublisher(printer_publishers),
    }

    if impressum:
        publicationEvent["description"] = impressum

    if place:
        publicationEvent["location"] = place

    if year:
        publicationEvent["startDate"] = year
        publicationEvent["hasEarliestBeginTimeStamp"] = f"{year}-01-01"
        publicationEvent["hasLatestEndTimeStamp"] = f"{year}-12-31"

    return publicationEvent


def getPublisher(printer_publishers: list) -> List[Dict]:
    publishers = []

    for p in printer_publishers:
        p_personnames, p_names = parsePersonName(
            p["person"], ns="https://data.goldenagents.org/datasets/ggd/personname/"
        )

        publisher = {
            "id": p["id"],  # this is the STCN/CERL URI
            "type": "Organization",
            "label": p["person"],
            "name": p_names,
            "hasName": p_personnames,
        }

        publishers.append(publisher)

    return publishers


def getWorkExample(record: dict, archives: dict = k2archive) -> List[Dict]:
    """
    Get the item (=book) in the library or archive, modelled as a 'IndividualProduct'.

    These books are given in the data, but have no unique identifier. We tried to
    reconcile these with the items in the STCN by holding archive and item location (=shelfmark).

    Args:
        record (dict): _description_
        archives (dict, optional): _description_. Defaults to k2archive.

    Returns:
        list: _description_
    """

    books = []

    for ex_archive in archives:
        if record.get(ex_archive):
            # The item
            items = record[ex_archive]

            # Any annotation
            comment = record.get(ex_archive + "_annotation")

            for i in items:
                book = {
                    "type": [
                        "CreativeWork",
                        "ArchiveComponent",
                        "Book",
                        "IndividualProduct",
                    ],
                    "label": f"{archives[ex_archive]} {i}",
                    "holdingArchive": archives[ex_archive],
                    "itemLocation": i,
                }

                if comment:
                    book["comment"] = comment

                if SHELFMARK2ITEM[archives[ex_archive]].get(i):
                    book["sameAs"] = SHELFMARK2ITEM[archives[ex_archive]][i]

                books.append(book)

    return books


def parseLinkJSONLD(link: dict) -> dict:
    """
    Parse a link between two persons, based on the sameAs clusters.

    Args:
        link (dict): _description_

    Returns:
        dict: _description_
    """

    names = []
    ids = []
    for name, record_ids in link.items():
        for i in record_ids:
            id = indexMapping[i][name]
            names.append(name)
            ids.append(id)

    first_name, rest_name = names[0], names[1:]
    first_id, rest_id = ids[0], ids[1:]
    link = {
        "id": first_id,
        "label": first_name,
        "sameAs": [
            {"id": i, "label": n} for i, n in zip(rest_id, rest_name) if i != first_id
        ],
    }
    return link


def main(filepath: str):
    # 1. Read in the GGD data from the data dump
    records = getRecords(filepath)

    # 2. Parse the records into JSON-LD (RDF)
    records = {
        "@context": CONTEXT,
        "@id": "https://data.goldenagents.org/datasets/ggd/",
        "@graph": [parseRecordJSONLD(r) for r in records],
    }

    # 3. Links and URIs for persons are made based on their index in the record
    # and how the person is referred to. Order matters, so let's save this mapping.
    with open("data/indexMapping.json", "w") as f:
        json.dump(indexMapping, f, indent=2)

    # 4. Parse the links between authors/persons into a separate JSON-LD file.
    with open("data/authorSameAs.json") as f:
        sameAs_clusters = json.load(f)

    with open("data/personSameAs.json") as f:
        sameAs_clusters.update(json.load(f))

    links = {
        "@context": CONTEXT_LINKS,
        "@id": "https://data.goldenagents.org/datasets/ggd/links/",
        "@graph": [parseLinkJSONLD(i) for i in sameAs_clusters.values()],
    }

    # 5. Write the JSON-LD files to disk
    print("Writing records to rdf/ggd.jsonld")
    with open("rdf/ggd.jsonld", "w", encoding="utf-8") as outfile:
        json.dump(records, outfile, indent=2)

    print("Writing links to rdf/ggd_linkset.jsonld")
    with open("rdf/ggd_linkset.jsonld", "w", encoding="utf-8") as outfile:
        json.dump(links, outfile, indent=2)


if __name__ == "__main__":
    main(filepath=GGDFILE)
