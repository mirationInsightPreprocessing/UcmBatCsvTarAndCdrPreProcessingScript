import os
import sys
import csv
import logging
import re
import json
import argparse
from pathlib import Path


DI_JSON_RULE_ENTITY_NAME = 'entity_name'
DI_JSON_RULE_COLUMNS_NAME = 'columns'
DI_JSON_RULE_ENTITY = {}
DI_JSON_RULE_COLUMNS = []

DI_JSON_RULE_ENDUSER_FIELDS_PREFERRED_ORDER = ['USER ID', 'FIRST NAME','LAST NAME','MAIL ID','DEVICE NAME #',
                                               'PRIMARY EXTENSION #','USER PKID']
DI_JSON_RULE_PHONE_FIELDS_PREFERRED_ORDER = ['OWNER USER ID','USER ID #','DEVICE TYPE','DEVICE POOL','DEVICE NAME',
                                             'DIRECTORY NUMBER #','ROUTE PARTITION #','EXTERNAL PHONE NUMBER MASK #',
                                             'E.164 NUMBER MASK #','ALERTING NAME #']


logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO)


def mapColumnName2Key(colName):
    pattern = ' \d+ | \d+'
    if re.search(pattern, colName) == None:
        return colName
    else:
        return re.sub(pattern, ' # ', colName, 1).strip()


def mapToKey(jkey):
    return jkey.replace(' ', '_').replace('#', 'list').replace('.', '')


def isKeyExist(jkey):
    global DI_JSON_RULE_COLUMNS
    for entry in DI_JSON_RULE_COLUMNS:
        if entry['from'] == str(jkey).upper():
            return True
    return False


def generate_jrule(filename):
    global DI_JSON_RULE_COLUMNS

    try:
        with open(filename, newline='') as csvInputFile:
            csvreader = csv.DictReader(csvInputFile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            csvheader = csvreader.fieldnames

            DI_JSON_RULE_ENTITY[DI_JSON_RULE_ENTITY_NAME] = Path(filename).stem

            position = 1

            csvfileName = os.path.basename(filename)
            if csvfileName == 'phone.csv':
                headerWithOrder = DI_JSON_RULE_PHONE_FIELDS_PREFERRED_ORDER
            elif csvfileName == 'enduser.csv':
                headerWithOrder = DI_JSON_RULE_ENDUSER_FIELDS_PREFERRED_ORDER
            else:
                headerWithOrder = []
            jointHeader = headerWithOrder + csvheader

            for name in jointHeader:
                data = {}

                if name not in headerWithOrder:
                    jkey_from = mapColumnName2Key(name)
                else:
                    jkey_from = name
                jkey_to = mapToKey(jkey_from)

                data['from'] = jkey_from.upper()
                data['to'] = jkey_to.lower()
                data['ordinal_position'] = position
                data['data_type'] = 'string'
                if not isKeyExist(jkey_from):
                    DI_JSON_RULE_COLUMNS.append(data)
                    position = position + 1

    except Exception as ex:
        logging.info('Exception happened {}' % ex)


    DI_JSON_RULE_ENTITY[DI_JSON_RULE_COLUMNS_NAME] = DI_JSON_RULE_COLUMNS
    json_formatted_str = json.dumps(DI_JSON_RULE_ENTITY, indent=2)
    logging.info(json_formatted_str)

    with open(Path(filename).stem + '_di_rule.json', 'w') as csvOutputFile:
        json.dump(DI_JSON_RULE_ENTITY, csvOutputFile, indent=2, sort_keys=False)

def main():
    argParser = argparse.ArgumentParser()
    argParser.add_argument('-f', '--filename', help='input csv filename', required='true')

    logging.info('generating json rule ...')
    args = argParser.parse_args()
    generate_jrule(args.filename)
    logging.info('done!')


if __name__ == '__main__':
    main()
