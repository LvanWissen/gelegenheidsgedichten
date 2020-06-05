import os
import json
from datetime import datetime
import calendar

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


def getPersons(persons, role=False):

    plist = []

    if type(persons) == str:
        persons = [persons]

    for person in persons:

        if role and '. ' in person:
            person, role = person.rsplit('. ', 1)
        else:
            role = None

        plist.append({'person': person, 'role': role})

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
        record['language'] = [record['language']]

    # persons/roles
    if record.get('person'):
        record['person'] = getPersons(record['person'], role=True)

    if record.get('author'):
        record['author'] = getPersons(record['author'])
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

    return record


def main(filepath: str):

    records = getRecords(filepath)

    records = [parseRecord(r) for r in records]

    with open('data/ggd.json', 'w', encoding='utf-8') as outfile:
        json.dump(records, outfile, indent=4)


if __name__ == "__main__":
    print(main(filepath=GGDFILE))