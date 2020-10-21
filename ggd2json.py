import os
import json
from datetime import datetime
import calendar
from collections import defaultdict

GGDFILE = "data/Gelegenheidsgedichten_Golden Agents_KB.dmp"

KEYS = {
    'AAR': 'event',
    'ABS': 'description',
    'AN_GA': 'item_saa_annotation',
    'AN_CBG': 'item_cbg_annotation',
    'AN_KB': 'item_kb_annotation',
    'AN_MMW': 'item_mmw_annotation',
    'AN_MNL': 'item_mnl_annotation',
    'AUT': 'author',
    'BYZ': 'comments',
    'COL': 'collate',
    'DAT': 'date',
    'EXE': 'archive',
    'EXF': 'exf',
    'EX_CBG': 'item_cbg',
    'EX_GA': 'item_saa',
    'EX_KB': 'item_kb',
    'EX_MMW': 'item_mmw',
    'EX_MNL': 'item_mnl',
    'FMT': 'format',
    'GED': 'ged',
    'GEN': 'society',
    'ILL': 'illustrator',
    'IMP': 'impressum',
    'INV': 'created',
    'MEL': 'melody',
    'MFN': 'mfn',
    'MOT': 'motif',
    'MUT': 'modified',
    'PAG': 'pages',
    'PLT': 'place',
    'PSN': 'person',
    'REC': 'id',
    'REG': 'registered',
    'STR': 'steurid',
    'TAA': 'language',
    'TIT': 'title',
    'VWN': 'signature',
    'WAT': 'remarks'
}

k2archive = {
    'item_cbg': 'Centraal Bureau voor Genealogie',
    'item_saa': "Stadsarchief Amsterdam",
    'item_kb': "Koninklijke Bibliotheek",
    'item_mmw': "Museum Meermanno",
    'item_mnl': "Bibliotheek van de Maatschappij der Nederlandse Letterkunde",
}

languages = {
    'Duits': 'iso639-3:ger',
    'Engels': 'iso639-3:eng',
    'Frans': 'iso639-3:fre',
    'Fries': 'iso639-3:stq',
    'Grieks': 'iso639-3:gre',
    'Hebreeuws': 'iso639-3:heb',
    'Italiaans': 'iso639-3:ita',
    'Latijn': 'iso639-3:lat',
    'Nederlands': 'iso639-3:dut',
    'Spaans': 'iso639-3:spa',
    'latijn': 'iso639-3:lat'
}

with open('data/ggd2stcn.json') as infile:
    GGD2STCN = json.load(infile)

with open('data/id2author.json') as infile:
    ID2AUTHOR = json.load(infile)

with open('data/id2printer.json') as infile:
    ID2PRINTER = json.load(infile)

ID2PERSON = defaultdict(dict)
for ggdid in ID2AUTHOR:
    for name in ID2AUTHOR[ggdid]:
        ID2PERSON[ggdid][name] = ID2AUTHOR[ggdid][name]
for ggdid in ID2PRINTER:
    for name in ID2PRINTER[ggdid]:
        ID2PERSON[ggdid][name] = ID2PRINTER[ggdid][name]

with open("data/place2ecartico.json") as infile:
    PLACE2ECARTICO = json.load(infile)

with open("data/impressum_place_year.json") as infile:
    IMPRESSUMDATA = json.load(infile)


def getRecords(filepath: str):

    records = []

    with open(filepath, encoding='utf-8-sig') as infile:
        data = infile.read()

        for r in data.split('\n$\n'):

            d = dict()

            for i in r.split('\n'):
                key, value = i.split(' ', 1)
                if '; ' in value:
                    value = value.split('; ')

                d[KEYS[key]] = value

            records.append(d)

    return records


def getPersons(persons, role=False, recordID=None):

    plist = []

    if type(persons) == str:
        persons = [persons]

    for person in persons:

        if role and '. ' in person:
            if person.count('.') > 1:
                # initials
                person, role = person.rsplit('.', 1)
                person += '.'
            else:
                person, role = person.rsplit('. ', 1)

            person = person.strip()
            role = role.strip()
        else:
            role = None

        if recordID and recordID in ID2PERSON:
            thesaurus = ID2PERSON[recordID].get(person)
        else:
            thesaurus = None

        plist.append({'person': person, 'role': role, 'thesaurus': thesaurus})

    return plist


def getEvent(record):

    if record['date'].endswith('00-00'):
        timeStamp = None
        earliestBeginTimeStamp = record['date'][:4] + '-01-01'
        latestEndTimeStamp = record['date'][:4] + '-12-31'

    elif record['date'].endswith('00'):
        timeStamp = None
        earliestBeginTimeStamp = record['date'][:7] + '-01'

        year = int(record['date'][:4])
        month = int(record['date'][5:7])
        _, lastday = calendar.monthrange(year, month)

        latestEndTimeStamp = record['date'][:7] + '-' + str(lastday).zfill(1)
    else:
        timeStamp = record['date']
        earliestBeginTimeStamp = record['date']
        latestEndTimeStamp = record['date']

    if record.get('place') and type(record['place']) == str:
        place = [record['place']]
    else:
        place = record.get('place', [])

    place = [PLACE2ECARTICO[i] for i in place]

    if record.get('event') and type(record['event']) == str:
        eType = [record['event']]
    else:
        eType = record.get('event', [])

    return {
        'timeStamp': timeStamp,
        'earliestBeginTimeStamp': earliestBeginTimeStamp,
        'latestEndTimeStamp': latestEndTimeStamp,
        'place': place,
        'type': eType
    }


def parseRecord(record: dict):

    # these fields should not have been split
    for k in [
            'title', 'impressum', 'collate', 'description', 'comments', 'pages'
    ]:

        if record.get(k) and type(record.get(k)) == list:
            record[k] = "; ".join(record[k])
        elif record.get(k) is None:
            record[k] = None

    # dates
    record['date'] = record['date'][:10]
    record['created'] = datetime.strptime(record['created'],
                                          '%d-%m-%Y').strftime('%Y-%m-%d')
    record['modified'] = datetime.strptime(record['modified'],
                                           '%d-%m-%Y').strftime('%Y-%m-%d')

    # event
    record['event'] = getEvent(record)

    # language
    if type(record['language']) != list:
        record['language'] = [languages[record['language']]]
    else:
        record['language'] = [languages[i] for i in record['language']]

    # persons/roles
    if record.get('person'):
        record['person'] = getPersons(record['person'],
                                      recordID=record['id'],
                                      role=True)

    if record.get('author'):
        record['author'] = getPersons(record['author'], recordID=record['id'])
    else:
        record['author'] = []

    # archives
    record['item'] = []
    for k in ['item_cbg', 'item_saa', 'item_kb', 'item_mmw', 'item_mnl']:
        if record.get(k):

            comment = record.get(k + '_annotation')
            if type(comment) == list:
                comment = "; ".join(comment)

            if type(record[k]) != list:
                items = [record[k]]
            else:
                items = record[k]

            for i in items:

                record['item'].append({
                    'location': i,
                    'holdingArchive': k2archive[k],
                    'comment': comment
                })

    # stcn
    record['stcn'] = GGD2STCN.get(record['id'], None)

    # impressum place
    if record['id'] in IMPRESSUMDATA:
        imp_place = IMPRESSUMDATA[record['id']]['place']
        if imp_place:
            record['impressum_place'] = PLACE2ECARTICO[imp_place]
        else:
            record['impressum_place'] = None
    else:
        record['impressum_place'] = None

    # impressum date
    if record['id'] in IMPRESSUMDATA:
        imp_year = IMPRESSUMDATA[record['id']]['year']
    else:
        imp_year = None
    record['impressum_year'] = imp_year

    return record


def main(filepath: str):

    records = getRecords(filepath)

    records = [parseRecord(r) for r in records]

    with open('data/ggd.json', 'w', encoding='utf-8') as outfile:
        json.dump(records, outfile, indent=4)


if __name__ == "__main__":
    main(filepath=GGDFILE)