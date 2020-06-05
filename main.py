import json
from rdflib import Graph, Namespace, OWL, Literal, URIRef, BNode, XSD, RDFS
from rdfalchemy import rdfSubject, rdfSingle, rdfMultiple

ggd = Namespace('http://data.bibliotheken.nl/id/dataset/ggd/')
ggddoc = Namespace('http://data.bibliotheken.nl/doc/dataset/ggd/')

bio = Namespace("http://purl.org/vocab/bio/0.1/")
schema = Namespace('http://schema.org/')
void = Namespace('http://rdfs.org/ns/void#')
foaf = Namespace('http://xmlns.com/foaf/0.1/')
sem = Namespace('http://semanticweb.cs.vu.nl/2009/11/sem/')

kbdef = Namespace("http://data.bibliotheken.nl/def#ppn")

JSONFILE = 'data/ggd.json'


class Thing(rdfSubject):
    rdf_type = None

    label = rdfMultiple(RDFS.label)
    comment = rdfSingle(RDFS.comment)

    name = rdfSingle(schema.name)
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


class Person(Thing):
    rdf_type = schema.Person


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


def toRdf(filepath: str, target: str):

    g = rdfSubject.db = Graph()
    eventTypes = dict()

    with open(filepath) as infile:
        data = json.load(infile)

    for r in data:

        abouts = []
        printers = []
        workExamples = []
        authors = [Role(None, name=a['person']) for a in r['author']]

        book = Book(ggd.term(r['id']),
                    name=r['title'],
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
            eventType = eventTypes.get(eType)
            if eventType is None:
                eventTypes[eType] = EventType(BNode(eType.lower().replace(
                    ' ', '').replace(',', 'en')),
                                              label=[eType])
                eventType = eventTypes.get(eType)
            eTypes.append(eventType)

        event = Event(
            None,
            hasTimeStamp=Literal(r['event']['timeStamp'], datatype=XSD.date)
            if r['event']['timeStamp'] else None,
            hasEarliestBeginTimeStamp=Literal(
                r['event']['earliestBeginTimeStamp'], datatype=XSD.date),
            hasLatestEndTimeStamp=Literal(r['event']['latestEndTimeStamp'],
                                          datatype=XSD.date),
            hasPlace=r['event']['place'],
            eventType=eTypes,
            subjectOf=book)
        abouts.append(event)

        identifiers = [PropertyValue(None, name='GGD id', value=r['id'])]
        if r.get('steurid'):
            identifiers.append(
                PropertyValue(None,
                              name='Van der Steur id',
                              value=r['steurid']))

        for p in r.get('person', []):

            if p['role'] == 'Drukker/uitgever':
                person = Person(None, name=p['person'])

                printers.append(person)
            else:
                role = Role(None,
                            about=Person(None, name=p['person']),
                            roleName=p['role'],
                            name=p['person'])
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