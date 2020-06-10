import re
import json
from itertools import count

from rdflib import Graph, Namespace, OWL, Literal, URIRef, BNode, XSD, RDFS
from rdfalchemy import rdfSubject, rdfSingle, rdfMultiple

# http://data.bibliotheken.nl/id/dataset/ggd/
ggd = Namespace('https://data.goldenagents.org/datasets/ggd/')
ggddoc = Namespace('http://data.bibliotheken.nl/doc/dataset/ggd/')

bio = Namespace("http://purl.org/vocab/bio/0.1/")
schema = Namespace('http://schema.org/')
void = Namespace('http://rdfs.org/ns/void#')
foaf = Namespace('http://xmlns.com/foaf/0.1/')
sem = Namespace('http://semanticweb.cs.vu.nl/2009/11/sem/')
pnv = Namespace('https://w3id.org/pnv#')

kbdef = Namespace("http://data.bibliotheken.nl/def#ppn")
gaThes = Namespace(
    "https://data.goldenagents.org/datasets/thesaurus/eventtype/")

ggdEvent = Namespace('https://data.goldenagents.org/datasets/ggd/event/')
ggdAuthor = Namespace('https://data.goldenagents.org/datasets/ggd/author/')
ggdPrinter = Namespace('https://data.goldenagents.org/datasets/ggd/printer/')
ggdPerson = Namespace('https://data.goldenagents.org/datasets/ggd/person/')

JSONFILE = 'data/ggd.json'


class Thing(rdfSubject):
    rdf_type = None

    label = rdfMultiple(RDFS.label)
    comment = rdfSingle(RDFS.comment)

    name = rdfMultiple(schema.name)
    description = rdfSingle(schema.description)

    sameAs = rdfMultiple(OWL.sameAs)
    inDataset = rdfSingle(void.inDataset)

    isPrimaryTopicOf = rdfSingle(foaf.isPrimaryTopicOf)

    dateCreated = rdfSingle(schema.dateCreated)
    dateModified = rdfSingle(schema.dateModified)

    subjectOf = rdfSingle(schema.subjectOf)


class Book(Thing):
    rdf_type = schema.Book

    author = rdfMultiple(schema.author)
    inLanguage = rdfMultiple(schema.inLanguage)
    publication = rdfSingle(schema.publication)

    bibliographicFormat = rdfSingle(kbdef.bibliographicFormat)
    hasCollationalFormula = rdfSingle(kbdef.hasCollationalFormula)

    about = rdfMultiple(schema.about)

    numberOfPages = rdfSingle(schema.numberOfPages)

    workExample = rdfMultiple(schema.workExample)


class Role(Thing):
    rdf_type = schema.Role
    author = rdfMultiple(schema.author)
    about = rdfSingle(schema.about)
    roleName = rdfSingle(schema.roleName)
    publishedBy = rdfSingle(schema.publishedBy)
    hasName = rdfMultiple(pnv.hasName)


class Person(Thing):
    rdf_type = schema.Person

    hasName = rdfMultiple(pnv.hasName)


class Organization(Thing):
    rdf_type = schema.Organization


class PublicationEvent(Thing):
    rdf_type = schema.PublicationEvent

    publishedBy = rdfMultiple(schema.publishedBy)


class Document(Thing):
    rdf_type = foaf.Document

    primaryTopic = rdfSingle(foaf.primaryTopic)

    identifier = rdfMultiple(schema.identifier)


class Event(Thing):
    rdf_type = sem.Event

    hasTimeStamp = rdfSingle(sem.hasTimeStamp)
    hasBeginTimeStamp = rdfSingle(sem.hasBeginTimeStamp)
    hasEndTimeStamp = rdfSingle(sem.hasEndTimeStamp)
    hasEarliestBeginTimeStamp = rdfSingle(sem.hasEarliestBeginTimeStamp)
    hasLatestBeginTimeStamp = rdfSingle(sem.hasLatestBeginTimeStamp)
    hasEarliestEndTimeStamp = rdfSingle(sem.hasEarliestEndTimeStamp)
    hasLatestEndTimeStamp = rdfSingle(sem.hasLatestEndTimeStamp)

    hasPlace = rdfMultiple(sem.hasPlace)

    eventType = rdfMultiple(sem.eventType)


class EventType(Thing):
    rdf_type = sem.EventType


class PropertyValue(Thing):
    rdf_type = schema.PropertyValue

    value = rdfSingle(schema.value)


class Item(Thing):
    rdf_type = (schema.Book, schema.ArchiveComponent)

    itemLocation = rdfSingle(schema.itemLocation)
    holdingArchive = rdfSingle(schema.holdingArchive)
    exampleOfWork = rdfSingle(schema.exampleOfWork)


class PersonName(Thing):
    rdf_type = pnv.PersonName

    # These map to A2A
    literalName = rdfSingle(pnv.literalName)
    givenName = rdfSingle(pnv.givenName)
    surnamePrefix = rdfSingle(pnv.surnamePrefix)
    baseSurname = rdfSingle(pnv.baseSurname)

    # These do not
    prefix = rdfSingle(pnv.prefix)
    disambiguatingDescription = rdfSingle(pnv.disambiguatingDescription)
    patronym = rdfSingle(pnv.patronym)
    surname = rdfSingle(pnv.surname)


def parsePersonName(nameString, identifier=None):
    """
    Parse a capitalised Notary Name from the notorial acts to pnv format. 
    
    Args:
        full_name (str): Capitalised string

    Returns:
        PersonName: according to pnv
    """

    pns = []
    labels = []

    if '(' in nameString:
        nameString = re.sub(' ?(.*) ?', '', nameString)

    if ',' in nameString:
        last, first = nameString.split(',', 1)
        nameString = " ".join([first, last])

    for full_name in nameString.split(' / '):

        # Some static lists
        dets = ['van', 'de', 'den', 'des', 'der', 'ten', "l'", "d'"]
        prefixes = ['Mr.']
        suffixes = ['Jr.', 'Sr.']
        patronymfix = ('sz', 'sz.', 'szoon', 'dr.', 'dr')

        # Correcting syntax errors
        full_name = full_name.replace('.', '. ')
        full_name = full_name.replace("'", "' ")
        full_name = full_name.replace('  ', ' ')

        # Tokenise
        tokens = full_name.split(' ')
        tokens = [i.lower() for i in tokens]
        tokens = [i.title() if i not in dets else i for i in tokens]
        full_name = " ".join(
            tokens
        )  # ALL CAPS to normal name format (e.g. Mr. Jan van Tatenhove)
        full_name = full_name.replace(
            "' ", "'")  # clunk back the apostrophe to the name

        # -fixes
        infix = " ".join(i for i in tokens if i in dets).strip()
        prefix = " ".join(i for i in tokens if i in prefixes).strip()
        suffix = " ".join(i for i in tokens if i in suffixes).strip()

        name_removed_fix = " ".join(i for i in tokens
                                    if i not in prefixes and i not in suffixes)

        if infix and infix in name_removed_fix:
            name = name_removed_fix.split(infix)
            first_name = name[0].strip()
            family_name = name[1].strip()

        else:
            name = name_removed_fix.split(' ', 1)
            if len(name) == 1:
                first_name = ""
                family_name = name[0]
            else:
                first_name = name[0]
                family_name = name[1]

        family_name_split = family_name.split(' ')
        first_name_split = first_name.split(' ')

        # build first name, family name, patronym and ignore -fixes
        first_name = " ".join(i for i in first_name_split
                              if not i.endswith(patronymfix)).strip()
        family_name = " ".join(i for i in family_name_split
                               if not i.endswith(patronymfix)).strip()
        patronym = " ".join(i for i in first_name_split + family_name_split
                            if i.endswith(patronymfix)).strip()

        full_name = " ".join(tokens).strip(
        )  # ALL CAPS to normal name format (e.g. Mr. Jan van Tatenhove)

        pn = PersonName(
            identifier,
            literalName=full_name.strip()
            if full_name is not None else "Unknown",
            prefix=prefix if prefix != "" else None,
            givenName=first_name if first_name != "" else None,
            surnamePrefix=infix if infix != "" else None,
            surname=family_name if family_name != "" else None,
            patronym=patronym if patronym != "" else None,
            disambiguatingDescription=suffix if suffix != "" else None)

        pn.label = [pn.literalName]

        pns.append(pn)
        labels.append(pn.literalName)

    return pns, labels


def toRdf(filepath: str, target: str):

    g = rdfSubject.db = Graph()
    eventTypesDict = dict()

    with open(filepath) as infile:
        data = json.load(infile)

    eventCounter = count(1)
    authorCounter = count(1)
    printerCounter = count(1)
    personCounter = count(1)

    for r in data:

        abouts = []
        printers = []
        workExamples = []
        authors = []

        for a in r['author']:
            pn, pnLabels = parsePersonName(a['person'])

            authors.append(
                Role(None,
                     name=pnLabels,
                     author=[
                         Person(ggdAuthor.term(str(next(authorCounter))),
                                name=pnLabels,
                                hasName=pn)
                     ],
                     hasName=pn))

        book = Book(ggd.term(r['id']),
                    name=[r['title']] if r['title'] else [],
                    inLanguage=r['language'],
                    author=authors,
                    bibliographicFormat=r.get('format'),
                    hasCollationalFormula=r['collate'])

        if r.get('pages'):
            pages, _ = r['pages'].split(' ', 1)
            pages = int(pages)

        book.numberOfPages = pages

        pubEvent = PublicationEvent(None, description=r['impressum'])
        book.publication = pubEvent

        eTypes = []
        for eType in r['event']['type']:
            eventType = eventTypesDict.get(eType)
            if eventType is None:
                eventTypesDict[eType] = EventType(gaThes.term(
                    eType.lower().replace(' ', '').replace(',', 'en')),
                                                  label=[eType])
                eventType = eventTypesDict.get(eType)
            eTypes.append(eventType)

        event = Event(
            ggdEvent.term(str(next(eventCounter))),
            hasTimeStamp=Literal(r['event']['timeStamp'], datatype=XSD.date)
            if r['event']['timeStamp'] else None,
            hasEarliestBeginTimeStamp=Literal(
                r['event']['earliestBeginTimeStamp'], datatype=XSD.date),
            hasLatestEndTimeStamp=Literal(r['event']['latestEndTimeStamp'],
                                          datatype=XSD.date),
            hasPlace=r['event']['place'],
            eventType=eTypes,
            subjectOf=book,
            label=[Literal(i, lang='nl') for i in r['event']['type'] if i])
        abouts.append(event)

        identifiers = [PropertyValue(None, name=['GGD id'], value=r['id'])]
        if r.get('steurid'):
            identifiers.append(
                PropertyValue(None,
                              name=['Van der Steur id'],
                              value=r['steurid']))

        for p in r.get('person', []):

            if p['role'] == 'Drukker/uitgever':
                person = Organization(ggdPrinter.term(str(
                    next(printerCounter))),
                                      name=[p['person']])

                printers.append(person)
            else:

                pn, pnLabels = parsePersonName(p['person'])

                role = Role(None,
                            about=Person(ggdPerson.term(
                                str(next(personCounter))),
                                         hasName=pn,
                                         name=pnLabels),
                            roleName=p['role'],
                            name=pnLabels,
                            hasName=pn)
                abouts.append(role)

        book.about = abouts
        pubEvent.publishedBy = printers

        for item in r['item']:

            holdingArchive = item['holdingArchive']
            itemLocation = item['location']

            workExample = Item(None,
                               holdingArchive=holdingArchive,
                               itemLocation=itemLocation,
                               comment=item.get('comment'),
                               exampleOfWork=book)
            workExamples.append(workExample)
        book.workExample = workExamples

        document = Document(
            None,
            description=r.get('description'),
            comment=r.get('comments'),
            identifier=identifiers,
            sameAs=[ggddoc.term(r['id'])],
            inDataset=URIRef("http://data.bibliotheken.nl/id/dataset/ggd/"),
            dateCreated=Literal(r['created'], datatype=XSD.date),
            dateModified=Literal(r['modified'], datatype=XSD.date))

        book.isPrimaryTopicOf = document
        document.primaryTopic = book

    g.bind('foaf', foaf)
    g.bind('schema', schema)
    g.bind('kbdef', kbdef)
    g.bind('void', void)
    g.bind('owĺ', OWL)
    g.bind('xsd', XSD)
    g.bind('sem', sem)
    g.bind('bio', bio)

    print(f"Serializing to {target}")
    g.serialize(target, format='turtle')


def main():
    toRdf(filepath=JSONFILE, target='ttl/ggd.ttl')


if __name__ == "__main__":
    main()