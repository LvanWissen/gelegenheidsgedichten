import re
import json
import uuid
from itertools import count

from rdflib import Graph, Namespace, OWL, Literal, URIRef, BNode, XSD, RDFS, RDF
from rdfalchemy import rdfSubject, rdfSingle, rdfMultiple

# http://data.bibliotheken.nl/id/dataset/ggd/
ggd = Namespace('http://data.bibliotheken.nl/id/dataset/ggd/')
ggddoc = Namespace('http://data.bibliotheken.nl/doc/dataset/ggd/')

bio = Namespace("http://purl.org/vocab/bio/0.1/")
schema = Namespace('http://schema.org/')
sem = Namespace('http://semanticweb.cs.vu.nl/2009/11/sem/')
pnv = Namespace('https://w3id.org/pnv#')

kbdef = Namespace("http://data.bibliotheken.nl/def#")
gaThes = Namespace(
    "https://data.goldenagents.org/datasets/thesaurus/eventtype/")

ggdItem = Namespace('http://data.bibliotheken.nl/id/dataset/ggd/item/')
ggdEvent = Namespace('http://data.bibliotheken.nl/id/dataset/ggd/event/')
ggdAuthor = Namespace('https://data.create.humanities.uva.nl/id/ggd/author/')
ggdPrinter = Namespace('https://data.create.humanities.uva.nl/id/ggd/printer/')
ggdPerson = Namespace('https://data.create.humanities.uva.nl/id/ggd/person/')

JSONFILE = 'data/ggd.json'


class Thing(rdfSubject):
    rdf_type = None

    label = rdfMultiple(RDFS.label)
    comment = rdfSingle(RDFS.comment)

    name = rdfMultiple(schema.name)
    description = rdfSingle(schema.description)

    sameAs = rdfMultiple(OWL.sameAs)
    isPartOf = rdfSingle(schema.isPartOf)
    license = rdfSingle(schema.license)
    publisher = rdfSingle(schema.publisher)

    mainEntityOfPage = rdfSingle(schema.mainEntityOfPage)

    dateCreated = rdfSingle(schema.dateCreated)
    dateModified = rdfSingle(schema.dateModified)

    subjectOf = rdfMultiple(schema.subjectOf)

    value = rdfSingle(RDF.value)
    url = rdfSingle(schema.url)

    startDate = rdfSingle(schema.startDate)
    hasTimeStamp = rdfSingle(sem.hasTimeStamp)
    hasBeginTimeStamp = rdfSingle(sem.hasBeginTimeStamp)
    hasEndTimeStamp = rdfSingle(sem.hasEndTimeStamp)
    hasEarliestBeginTimeStamp = rdfSingle(sem.hasEarliestBeginTimeStamp)
    hasLatestBeginTimeStamp = rdfSingle(sem.hasLatestBeginTimeStamp)
    hasEarliestEndTimeStamp = rdfSingle(sem.hasEarliestEndTimeStamp)
    hasLatestEndTimeStamp = rdfSingle(sem.hasLatestEndTimeStamp)


class Book(Thing):
    rdf_type = schema.Book

    author = rdfMultiple(schema.author)
    inLanguage = rdfMultiple(schema.inLanguage)
    publication = rdfSingle(schema.publication)

    bibliographicFormat = rdfSingle(kbdef.bibliographicFormat)
    stcnCollationalFormula = rdfSingle(kbdef.stcnCollationalFormula)

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
    gender = rdfSingle(schema.gender)


class Organization(Thing):
    rdf_type = schema.Organization

    hasName = rdfMultiple(pnv.hasName)


class PublicationEvent(Thing):
    rdf_type = schema.PublicationEvent

    publishedBy = rdfMultiple(schema.publishedBy)
    location = rdfSingle(schema.location)


class Document(Thing):
    rdf_type = schema.WebPage, schema.Dataset

    mainEntity = rdfSingle(schema.mainEntity)

    identifier = rdfMultiple(schema.identifier)


class Event(Thing):
    rdf_type = sem.Event

    hasPlace = rdfMultiple(sem.hasPlace)
    hasActor = rdfMultiple(sem.hasActor)

    eventType = rdfMultiple(sem.eventType)

    precedingEvent = rdfMultiple(bio.precedingEvent)
    followingEvent = rdfMultiple(bio.followingEvent)


class EventType(Thing):
    rdf_type = sem.EventType


class SemRole(Thing):
    rdf_type = sem.Role

    roleType = rdfSingle(sem.roleType)


class SemRoleType(Thing):
    rdf_type = sem.RoleType


class PropertyValue(Thing):
    rdf_type = schema.PropertyValue

    value = rdfSingle(schema.value)


class Item(Thing):
    rdf_type = (schema.Book, schema.IndividualProduct, schema.ArchiveComponent)

    itemLocation = rdfSingle(schema.itemLocation)
    holdingArchive = rdfSingle(schema.holdingArchive)
    exampleOfWork = rdfSingle(schema.exampleOfWork)


class Place(Thing):
    rdf_type = schema.Place


class PersonName(Thing):
    rdf_type = pnv.PersonName

    # These map to A2A
    literalName = rdfSingle(pnv.literalName)
    givenName = rdfSingle(pnv.givenName)
    surnamePrefix = rdfSingle(pnv.surnamePrefix)
    baseSurname = rdfSingle(pnv.baseSurname)
    initials = rdfSingle(pnv.initials)

    # These do not
    prefix = rdfSingle(pnv.prefix)
    disambiguatingDescription = rdfSingle(pnv.disambiguatingDescription)
    patronym = rdfSingle(pnv.patronym)
    surname = rdfSingle(pnv.surname)


class MusicComposition(Thing):
    rdf_type = schema.MusicComposition

    musicArrangement = rdfMultiple(schema.musicArrangement)
    lyrics = rdfMultiple(schema.lyrics)


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
        unique_id = uuid.uuid4()
    else:
        unique_id = uuid.uuid5(uuid.NAMESPACE_X500, identifier)

    if ns:
        return URIRef(ns + str(unique_id))
    else:
        return BNode(unique_id)


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
        nameString = re.sub(r' ?\(.*\) ?', '', nameString)

    if ',' in nameString:
        last, first = nameString.split(',', 1)
        nameString = " ".join([first, last]).strip()

    for full_name in nameString.split(' / '):

        # Some static lists
        dets = ['van', 'de', 'den', 'des', 'der', 'ten', "l'", "d'"]
        prefixes = ['Mr.']
        suffixes = ['Jr.', 'Sr.']
        patronymfix = ('sz', 'sz.', 'szoon', 'dr.', 'dr', 'sdochter')

        # Correcting syntax errors
        # full_name = full_name.replace('.', '. ')
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

        if first_name.endswith('.'):
            initials = first_name
            givenName = None
        elif first_name != "":
            givenName = first_name
            initials = None
        else:
            givenName, initials = None, None

        pn = PersonName(
            identifier,
            literalName=full_name.strip()
            if full_name is not None else "Unknown",
            prefix=prefix if prefix != "" else None,
            givenName=givenName,
            initials=initials,
            surnamePrefix=infix if infix != "" else None,
            baseSurname=family_name if family_name != "" else None,
            patronym=patronym if patronym != "" else None,
            disambiguatingDescription=suffix if suffix != "" else None)

        pn.label = [pn.literalName]

        pns.append(pn)
        labels.append(pn.literalName)

    return pns, labels


def getRoleType(roleName):

    if roleName:
        uniqueString = "".join([
            i for i in roleName.lower()
            if i in '123456789-abcdefghijklmnopqrstuvwxyz'
        ])
    else:
        uniqueString = "Unknown"
        roleName = "Unknown"

    rt = SemRoleType(BNode(uniqueString), label=[roleName])

    return rt


def toRdf(filepath: str, target: str, temporalConstraint=False):

    g = rdfSubject.db = Graph()
    eventTypesDict = dict()

    with open(filepath) as infile:
        data = json.load(infile)

    with open('data/authorSameAs.json') as infile:
        authorLinkList = json.load(infile)

    itemCounter = count(1)
    authorCounter = count(1)
    printerCounter = count(1)
    personCounter = count(1)

    # same thesaurus entry hields same uri
    author2uri = dict()
    printer2uri = dict()
    person2uri = dict()

    if temporalConstraint:
        beginConstraint, endConstraint = temporalConstraint
    else:
        beginConstraint, endConstraint = 0, 3000

    for r in data:

        ### Timporal constraint
        year = int(r['event']['earliestBeginTimeStamp'][:4])
        if year < beginConstraint or year >= endConstraint:
            continue
        ### Timporal constraint

        abouts = []
        semRoles = []

        printers = []
        workExamples = []
        authors = []

        for a in r['author']:

            # authorvalues = authorsDict.get(a['person'])
            # if authorvalues:
            #     author, pn, pnLabels = authorvalues
            # else:

            # Attempt to also give the same URIs to authors with same name in
            # poems for the the same event
            authorURI = None
            amatch = tuple([r['event']['eventid'], a['person']] +
                           sorted(a['thesaurus']))
            authorSameAs = []

            if a['thesaurus']:

                for i in sorted(a['thesaurus'], reverse=True):
                    if 'data.bibliotheken.nl/id/thes/' in i or 'viaf.org' in i and authorURI is None:
                        authorURI = URIRef(i)
                    else:
                        authorSameAs.append(URIRef(i))

                if authorURI is None:
                    authorURI = author2uri.get(amatch)

                    if authorURI is None:
                        authorURI = ggdAuthor.term(str(next(authorCounter)))
                        author2uri[amatch] = authorURI

            else:
                # No thesaurus entry, but maybe this author is in the link file

                # already defined?
                authorURI = author2uri.get(amatch)

                # not defined, try to find it in the link file
                # btw, we need a database
                if authorURI is None:
                    for n, link in authorLinkList.items():
                        if r['id'] in link.get(a['person'], []):
                            authorURI = ggdAuthor.term('a' + n)
                            break

                    if authorURI is None:
                        authorURI = ggdAuthor.term(str(next(authorCounter)))

                    author2uri[amatch] = authorURI

            # Single name to unique person
            pn, pnLabels = parsePersonName(a['person'],
                                           identifier=unique(str(authorURI)))
            labelInverseName = [a['person']]

            if a['gender']:
                gender = URIRef(a['gender'])
            else:
                gender = None

            author = Person(authorURI,
                            label=labelInverseName,
                            name=pnLabels,
                            hasName=pn,
                            gender=gender,
                            sameAs=authorSameAs)

            # authorsDict[a['person']] = (author, pn, pnLabels)

            authors.append(
                Role(None,
                     label=labelInverseName,
                     name=pnLabels,
                     author=[author],
                     hasName=pn))

        book = Book(ggd.term(r['id']),
                    name=[r['title']] if r['title'] else [],
                    label=[r['title']] if r['title'] else [],
                    inLanguage=r['language'],
                    author=authors,
                    bibliographicFormat=r.get('format'),
                    stcnCollationalFormula=r['collate'])

        if r.get('pages'):
            pages, _ = r['pages'].split(' ', 1)
            pages = int(pages)
        else:
            pages = None

        book.numberOfPages = pages

        # Parsing impressum info
        impressum = r['impressum']
        printPlace, printYear = r['impressum_place'], r['impressum_year']

        if printPlace:
            if printPlace['thesaurus']:
                printPlace = Place(URIRef(printPlace['thesaurus']),
                                   name=[printPlace['name']],
                                   label=[printPlace['name']])
            else:
                printPlace = Place(None,
                                   name=[printPlace['name']],
                                   label=[printPlace['name']])

        if printYear:
            earliestBeginTimeStampPrint = Literal(f"{printYear}-01-01",
                                                  datatype=XSD.date)
            latestEndTimeStampPrint = Literal(f"{printYear}-12-31",
                                              datatype=XSD.date)
            printYear = Literal(printYear, datatype=XSD.gYear)
        else:
            earliestBeginTimeStampPrint, latestEndTimeStampPrint = None, None

        pubEvent = PublicationEvent(
            None,
            label=[f"{impressum or ''} ({printYear or '?'})"],
            description=impressum,
            location=printPlace,
            startDate=printYear,
            hasEarliestBeginTimeStamp=earliestBeginTimeStampPrint,
            hasLatestEndTimeStamp=latestEndTimeStampPrint)
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

        places = []
        for place in r['event']['place']:
            placeName = place['name']

            placeURI = place['thesaurus']
            if placeURI:
                placeURI = URIRef(placeURI)

            places.append(Place(placeURI, name=[placeName]))

        event = Event(
            ggdEvent.term(str(r['event']['eventid'])),
            hasTimeStamp=Literal(r['event']['timeStamp'], datatype=XSD.date)
            if r['event']['timeStamp'] else None,
            hasEarliestBeginTimeStamp=Literal(
                r['event']['earliestBeginTimeStamp'], datatype=XSD.date),
            hasLatestEndTimeStamp=Literal(r['event']['latestEndTimeStamp'],
                                          datatype=XSD.date),
            hasPlace=places,
            eventType=eTypes,
            subjectOf=[book],
            label=[
                Literal(f"{i} ({r['event']['year']})", lang='nl')
                for i in r['event']['type'] if i
            ],
            precedingEvent=[URIRef(i) for i in r['event']['otr']],
            followingEvent=[
                URIRef(i) for i in r['event']['doop'] + r['event']['begraaf']
            ])
        abouts.append(event)

        identifiers = [
            PropertyValue(None,
                          name=['GGD id'],
                          value=r['id'],
                          label=[f"{r['id']} (GGD id)"])
        ]
        if r.get('steurid'):
            identifiers.append(
                PropertyValue(None,
                              name=['Van der Steur id'],
                              label=[f"{r['steurid']} (Van der Steur id)"],
                              value=r['steurid']))

        # melody
        for m in r['melody']:

            # The melody is arranged for this particular occasion
            arrangement = MusicComposition(
                unique(m, r['id']),
                name=[
                    Literal(f"{r['title']} (Melodie: {m['label']})", lang='nl')
                ],
                label=[
                    Literal(f"{r['title']} (Melodie: {m['label']})", lang='nl')
                ],
                lyrics=[book])

            # melody (MusicComposition) --> arrangement (MusicComposition) --> lyrics (Book)
            melody = MusicComposition(
                unique(m['label']),
                name=[m['label']],
                label=[m['label']],
                url=URIRef(m['liederenbank']) if m['liederenbank'] else None,
                musicArrangement=[arrangement])

        # persons

        for p in r.get('person', []):

            if p['role'] == 'Drukker/uitgever':

                # printer = organizationsDict.get(p['person'])

                if p['thesaurus']:

                    printerSameAs = []
                    printerURI = None

                    for i in p['thesaurus']:
                        if 'data.bibliotheken.nl/id/thes/' in i and printerURI is None:
                            printerURI = URIRef(i)
                        else:
                            printerSameAs.append(URIRef(i))

                    if printerURI is None:
                        printerURI = printer2uri.get(
                            tuple(sorted(p['thesaurus'])))

                        if printerURI is None:
                            printerURI = ggdPrinter.term(
                                str(next(printerCounter)))
                            printer2uri[tuple(sorted(
                                p['thesaurus']))] = printerURI

                else:
                    printerSameAs = []

                    printerURI = ggdPrinter.term(str(next(printerCounter)))

                # Single name to unique person
                pn, pnLabels = parsePersonName(p['person'],
                                               identifier=unique(
                                                   str(printerURI)))
                labelInverseName = [p['person']]

                printer = Organization(printerURI,
                                       label=labelInverseName,
                                       name=pnLabels,
                                       hasName=pn,
                                       sameAs=printerSameAs)

                # printers.append(
                #     Role(None,
                #          label=labelInverseName,
                #          name=pnLabels,
                #          publishedBy=printer,
                #          hasName=pn))
                printers.append(printer)

            elif p['role'] not in ('Overige functies', 'Comp', 'Med', 'Pap'):

                # for persons, being in the same event also counts
                personURI = None
                pmatch = tuple([r['event']['eventid'], p['person']])
                personSameAs = []

                # otr
                personSameAs += [URIRef(i) for i in p['otr']]

                # doop
                personSameAs += [URIRef(i) for i in p['doop']]

                # begraaf
                personSameAs += [URIRef(i) for i in p['begraaf']]

                # rkd
                personSameAs += [URIRef(i) for i in p['rkd']]

                # wikidata
                personSameAs += [URIRef(i) for i in p['wikidata']]

                # ecartico
                personSameAs += [URIRef(i) for i in p['ecartico']]

                if p['thesaurus']:

                    for i in sorted(p['thesaurus'], reverse=True):
                        if 'data.bibliotheken.nl/id/thes/' in i or 'viaf.org' in i and personURI is None:
                            personURI = URIRef(i)
                        else:
                            personSameAs.append(URIRef(i))

                    if personURI is None:
                        personURI = person2uri.get(pmatch)

                        # if personURI is None:
                        #     personURI = ggdPerson.term(str(
                        #         next(personCounter)))
                        #     person2uri[pmatch] = personURI

                if personURI is None:
                    # else:

                    personURI = unique(*sorted(personSameAs), ns=ggdPerson)
                    person2uri[pmatch] = personURI

                # Single name to unique person
                pn, pnLabels = parsePersonName(p['person'],
                                               identifier=unique(
                                                   str(personURI)))
                labelInverseName = [p['person']]

                if p['gender']:
                    gender = URIRef(p['gender'])
                else:
                    gender = None

                person = Person(personURI,
                                label=labelInverseName,
                                hasName=pn,
                                name=pnLabels,
                                gender=gender,
                                sameAs=personSameAs)

                role = Role(unique(p['person'] + r['id'] + 'semrole'),
                            about=person,
                            roleName=p['role'],
                            name=pnLabels,
                            label=pnLabels,
                            hasName=pn)
                abouts.append(role)

                # Attach them to the event
                semRoles.append(
                    SemRole(unique(p['person'] + r['event']['eventid'] +
                                   'semrole'),
                            value=person,
                            name=pnLabels,
                            label=pnLabels,
                            roleType=getRoleType(p['role'])))

        book.about = abouts
        pubEvent.publishedBy = printers

        event.hasActor = semRoles

        for item in r['item']:

            holdingArchive = item['holdingArchive']
            itemLocation = item['location']

            label = [f"{holdingArchive} {itemLocation}"]

            workExample = Item(ggdItem.term(str(next(itemCounter))),
                               name=label,
                               label=label,
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
            isPartOf=URIRef("http://data.bibliotheken.nl/id/dataset/ggd"),
            dateCreated=Literal(r['created'], datatype=XSD.date),
            dateModified=Literal(r['modified'], datatype=XSD.date))

        book.mainEntityOfPage = document
        document.mainEntity = book

        # STCN
        if r['stcn']:
            book.sameAs = [URIRef(r['stcn'])]

    g.bind('schema', schema)
    g.bind('kbdef', kbdef)
    g.bind('owl', OWL)
    g.bind('xsd', XSD)
    g.bind('sem', sem)
    g.bind('bio', bio)
    g.bind('pnv', pnv)

    print(f"Serializing to {target}")
    g.serialize(target, format='turtle')


def main():

    # for temp in [(1620, 1630), (1625, 1635), (1630, 1640), (1635, 1645),
    #              (1640, 1650), (1645, 1655), (1650, 1660), (1655, 1665),
    #              (1660, 1670)]:
    #     toRdf(filepath=JSONFILE,
    #           target=f'ttl/ggd_{temp[0]}-{temp[1]}.ttl',
    #           temporalConstraint=temp)

    toRdf(filepath=JSONFILE, target=f'ttl/ggd.ttl')


if __name__ == "__main__":
    main()