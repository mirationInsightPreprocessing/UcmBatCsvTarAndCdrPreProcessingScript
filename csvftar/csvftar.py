import os
import re
import sys
import csv
import uuid
import shutil
import tarfile
import logging
import tempfile
import argparse
from os.path import isfile, join, getmtime


FILTER_CSV_FILE_HEADER = ['csvFileName', 'filterName', 'filterValues', 'filterValuesFile']
CSV_FILE_FILTER_MAP = {}

PHONE_CSV_FILE_NAME = 'phone.csv'
PHONE_CSV_EXCLUDED_FIELDS = ['Services Provisioning','CSS','AAR CSS','Network Locale','Media Resource Group List',
                             'User Hold MOH Audio Source','Network Hold MOH Audio Source','Device User Locale',
                             'Packet Capture Mode','Packet Capture Duration','Built in Bridge','Privacy',
                             'Retry Video Call as Audio','Ignore Presentation Indicators','Module #',
                             'Phone Load Name','Module # Load Name','Information','Directory','Messages',
                             'Services','Authentication Server','Proxy Server','Idle','Idle Timer',
                             'MLPP Indication','MLPP Preemption','MLPP Domain','MTP Required','Digest User',
                             'Allow CTI Control Flag','Device Presence Group','Device Security Profile',
                             'Device Subscribe CSS','Unattended Port','Require DTMF Reception','RFC2833 Disabled',
                             'Certificate Operation','Authentication String','Operation Completes By',
                             'Device Protocol','Secure Shell User','Secure Shell Password','XML','Dial Rules',
                             'CSS Reroute','Rerouting Calling Search Space','DTMF Signalling','Default DTMF Capability',
                             'MTP Preferred Originating Codec','Logout Profile','Signaling Port','Outgoing Caller ID Pattern',
                             'Calling Party Selection','Calling Party Presentation','Display IE Delivery',
                             'Redirecting Number IE Delivery Outbound','Redirecting Number IE Delivery Inbound',
                             'Gatekeeper Name','Technology Prefix','Zone','Motorola WSM Connection',
                             'Subscriber Cellular Number','Follow me only when caller has dialed cellular num',
                             'Disable Application Dial Rules','AAR Group','Logged Into Hunt Group','Remote Device',
                             'Device Mobility Mode','DND Option','DND Incoming Call Alert','BLF Audible Alert Setting (Phone Busy)',
                             'BLF Audible Alert Setting (Phone Idle)','Protected Device','Join Across Lines','Single Button Barge',
                             'Application User #','Always Use Prime Line','Always Use Prime Line for Voice Message',
                             'Use Trusted Relay Point','Outbound Call Rollover','Phone Personalization','Primary Phone',
                             'Hotline Device','Secure Directory URL','Secure Idle URL',
                             'Secure Information URL','Secure Messages URL','Secure Services URL','SRTP Allowed',
                             'Feature Control Policy','Device Trust Mode','Allow presentation sharing using BFCP',
                             'Early Offer support for voice and video calls (insert MTP if needed)',
                             'Caller ID Calling Party Transformation CSS','Caller ID Use Device Pool Calling Party Transformation CSS',
                             'Remote Number Calling party Transformation CSS','Remote Number Use Device Pool Calling Party Transformation CSS',
                             'Allow iX Applicable Media','Require off-premise location','Confidential Access Mode',
                             'Confidential Access Level','Route calls to all remote destinations when client is not connected',
                             'Emergency Location (ELIN) Group','Third-party Registration Required','Block Incoming Calls while Roaming',
                             'Home Network ID','Mobility Identity Name','Mobility Identity Destination Number',
                             'Mobility Identity Answer Too Soon Timer','Mobility Identity Answer Too Late Timer',
                             'Mobility Identity Delay Before Ringing Cell','Mobility Identity Time Zone','Mobility Identity Is Mobile Phone',
                             'Mobility Identity Enable Mobile Connect','Mobility Identity Mobility Profile','Line CSS #',
                             'AAR Group(Line) #','Line User Hold MOH Audio Source #','Line Network Hold MOH Audio Source #',
                             'Auto Answer #','Forward All CSS #','Forward Busy Internal CSS #','Forward Busy External CSS #',
                             'Forward No Answer Internal CSS #','Forward No Answer External CSS #','Forward No Coverage Internal CSS #',
                             'Forward No Coverage External CSS #','MLPP Target #','MLPP CSS #','MLPP No Answer Ring Duration #',
                             'Busy Trigger #','Visual Message Waiting Indicator Policy #','Ring setting (Phone Idle) #',
                             'Ring Setting (Phone Active) #','Caller Name #','Caller Number #','Redirected Number #',
                             'Dialed Number #','Line Description #','Line Presence Group #','Secondary CSS for Forward All #',
                             'Forward on CTI Failure Voice Mail #','Forward on CTI Failure Destination #',
                             'Forward on CTI Failure CSS #','AAR Destination Mask #','AAR Voice Mail #','Forward Unregistered Internal CSS #',
                             'Forward Unregistered External CSS #','Hold Reversion Ring Duration #','Hold Reversion Notification Interval #',
                             'Recording Profile #','Monitoring Calling Search Space #','Calling Search Space Activation Policy #',
                             'CPG Audio Alert Setting(Phone Idle) #','CPG Audio Alert Setting(Phone Active) #',
                             'Park Monitor Forward No Retrieve Ext Destination #','Park Monitor Forward No Retrieve Int Destination #',
                             'Park Monitor Forward No Retrieve Int Voice Mail #','Park Monitor Forward No Retrieve Ext Voice Mail #',
                             'Park Monitor Forward No Retrieve Ext CSS #','Park Monitoring Reversion Timer #','Park Monitor Forward No Retrieve Int CSS #',
                             'Party Entrance Tone #','Log Missed Calls #','Allow Control of Device from CTI #','URI # on Directory Number #',
                             'URI # Route Partition on Directory Number #','URI # Is Primary on Directory Number #',
                             'Reject Anonymous Calls #','Urgent Priority #','Recording Media Source #','Enterprise Is Urgent #',
                             'Enterprise Advertise via globally #','Enterprise Add to Local Route Partition #','Enterprise Route Partition #',
                             'E.164 Is Urgent #','E.164 Advertise via globally #','E.164 Add to Local Route Partition #',
                             'E.164 Route Partition #','Line Confidential Access Mode #','Line Confidential Access Level #','External Call Control Profile #',
                             'Call Control Agent Profile #','IsEnterprise Advertised Failover Number #','IsE.164 Advertised Failover Number #',
                             'URI # Advertise Globally via ILS #','Calling Line ID Presentation When Diverted #',
                             'Intercom Maximum Number of Calls #','Intercom Directory Number #','Intercom Route Partition #',
                             'Intercom Description #','Intercom Alerting Name #','Intercom ASCII Alerting Name #','Intercom CSS #','Intercom Presence Group #',
                             'Intercom Display #','Intercom ASCII Display #','Intercom Line Text Label #','Intercom Speed Dial #',
                             'Intercom External Phone Number Mask #','Intercom Caller Name #','Intercom Caller Number #','Intercom Auto Answer #',
                             'Intercom Default Activated Device #']

ENDUSER_CSV_FILE_NAME = 'enduser.csv'
ENDUSER_CSV_EXCLUDED_FIELDS = ['ASSOCIATED PC','MIDDLE NAME','PAGER','HOME PHONE','BUILDING','SITE','UNIQUE IDENTIFIER',
                                'NICKNAME','DELETED TIME STAMP','DIGEST CREDENTIALS','PRESENCE GROUP','SUBSCRIBE CSS',
                                'ALLOW CONTROL OF DEVICE FROM CTI','MAX. DESK PICKUP WAIT TIME','REMOTE DESTINATION LIMIT',
                                'ENABLE USER FOR UNIFIED CM IM AND PRESENCE','ENABLE EMCC',
                                'INCLUDE MEETING INFORMATION IN PRESENCE','ASSIGNED PRESENCE SERVER',
                                'ENABLE END USER TO HOST CONFERENCE NOW','MEETING NUMBER','ATTENDEES ACCESS CODE',
                                'EM MAX LOGIN TIME','SELF-SERVICE USER ID','PASSWORD LOCKED BY ADMIN #',
                                'PASSWORD CANT CHANGE #','PASSWORD MUST CHANGE AT NEXT LOGIN #','PASSWORD DOES NOT EXPIRE #',
                                'PASSWORD AUTHENTICATION RULE #','PASSWORD #','PIN LOCKED BY ADMIN #','PIN CANT CHANGE #',
                                'PIN MUST CHANGE AT NEXT LOGIN #','PIN DOES NOT EXPIRE #','PIN AUTHENTICATION RULE #',
                                'PIN #','APPLICATION SERVER NAME #','CONTENT #','ACCESS CONTROL GROUP #',
                                'DEFAULT PROFILE #','DESCRIPTION #','TYPE USER ASSOCIATION #','TYPE PATTERN USAGE #',
                                'NAME DIALING #','MLPP PRECEDENCE AUTHORIZATION LEVEL #','MLPP USER IDENTIFICATION NUMBER #',
                                'MLPP PASSWORD #','HEADSET SERIAL NUMBER #']


# global variables
output_path = None


logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO)


def clean_temp_dir(dirname):
    if dirname != None and os.path.exists(dirname):
        try:
            shutil.rmtree(dirname)
        except OSError as ex:
            logging.error('Error occured: %s : %s' % (dirname, ex.strerror))


def exit_with_cleanup(ex, dirname):
    logging.error('Error happened: %s' % ex)
    clean_temp_dir(dirname)
    logging.info('Exit...')
    exit(1)


def get_filterValues_from_file(dir, filename):
    file_path = join(dir, filename)
    if not os.path.exists(file_path):
        logging.warning('The filter values file ' + filename + ' does not exist. Skipped!')
        return None

    values = []
    try:
        with open(file_path, newline='') as txtFilterFile:
            for row in txtFilterFile:
                values.extend([s.strip() for s in row.split(',') if s.strip()])
            return values

    except Exception as ex:
        logging.error('In get_filterValues_from_file, error happened: %s' % ex)
        return None


def process_filter_csv(filter_csv):
    global PHONE_CSV_FILE_NAME
    global ENDUSER_CSV_FILE_NAME

    if filter_csv != None:
        if not os.path.exists(filter_csv):
            logging.warning('The filter ' + filter_csv + ' does not exist! Skip the filtering')
            return
        if not os.path.isfile(filter_csv) or not filter_csv.endswith('csv'):
            logging.warning('The filter ' + filter_csv + ' is not a csv file! Skip the filtering')
            return

        try:
            with open(filter_csv, newline='') as csvFilterFile:
                csvreader = csv.DictReader(csvFilterFile, delimiter=',', quotechar='"')
                if csvreader.fieldnames != FILTER_CSV_FILE_HEADER:
                    logging.error('The filter csv header must be: ' + ','.join(FILTER_CSV_FILE_HEADER))
                    exit(1)

                filter_dir = os.path.dirname(filter_csv)
                for row in csvreader:
                    if not row['csvFileName'] in CSV_FILE_FILTER_MAP.keys():
                        CSV_FILE_FILTER_MAP[row['csvFileName']] = []
                    filter = {}

                    values = [s.strip() for s in row['filterValues'].split(',') if s.strip()]
                    filter_file = row['filterValuesFile']
                    if filter_file != None and filter_file.strip() != '':
                        valuesFromFile = get_filterValues_from_file(filter_dir, filter_file)
                        if valuesFromFile != None:
                            values.extend(valuesFromFile)

                    filter['filterName'] = row['filterName']
                    filter['filterValues'] = values
                    CSV_FILE_FILTER_MAP[row['csvFileName']].append(filter)

        except Exception as ex:
            logging.error('In process_filter_csv, error happened: %s' % ex)
            exit(1)

    if PHONE_CSV_FILE_NAME not in CSV_FILE_FILTER_MAP.keys():
        CSV_FILE_FILTER_MAP[PHONE_CSV_FILE_NAME] = []
    if ENDUSER_CSV_FILE_NAME not in CSV_FILE_FILTER_MAP.keys():
        CSV_FILE_FILTER_MAP[ENDUSER_CSV_FILE_NAME] = []

    #logging.info(CSV_FILE_FILTER_MAP)


def get_included_columns(csvheader, excluded_columns):
    included = []
    for column in csvheader:
        temp = re.sub(' \d+ | \d+', ' # ', column).strip()
        if temp not in excluded_columns:
            included.append(column)

    return included


def do_filtering(work_dir, filename):
    global PHONE_CSV_FILE_NAME
    global ENDUSER_CSV_FILE_NAME

    try:
        with open(join(work_dir, filename), newline='') as csvInputFile:
            csvreader = csv.DictReader(csvInputFile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            csvheader = csvreader.fieldnames

            if filename == PHONE_CSV_FILE_NAME:
                CSV_INCLUDED_FIELDS = get_included_columns(csvheader, PHONE_CSV_EXCLUDED_FIELDS)
            elif  filename == ENDUSER_CSV_FILE_NAME:
                CSV_INCLUDED_FIELDS = get_included_columns(csvheader, ENDUSER_CSV_EXCLUDED_FIELDS)
            else:
                CSV_INCLUDED_FIELDS = csvheader

            temp_file = join(work_dir, 'temp_' + filename)
            csvOutputFile = open(temp_file, 'w+')
            csvwriter = csv.writer(csvOutputFile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            csvwriter.writerow(CSV_INCLUDED_FIELDS)

            for row in csvreader:
                skip = False
                for lfilter in CSV_FILE_FILTER_MAP[filename]:
                    filtername = lfilter['filterName']
                    if filtername in csvheader:
                        if not any(x for x in lfilter['filterValues'] if x.lower() in row[filtername].lower()):
                            skip = True
                            break
                if skip:
                    continue

                newrow = [row[x] for x in CSV_INCLUDED_FIELDS]
                csvwriter.writerow(newrow)

            csvOutputFile.close()

        shutil.move(temp_file, join(work_dir, filename))
    except Exception as ex:
        exit_with_cleanup(ex, work_dir)


def untar_filter_tar(tar_file_path, output_tar_path):

    if output_tar_path == None:
        output_path = os.path.dirname(tar_file_path)
    else:
        if os.path.isdir(output_tar_path) or not os.path.exists(output_tar_path):
            output_path = output_tar_path
        else:
            if os.path.exists(output_tar_path):
                logging.error('In untar_filter_tar, file %s can not be used as output folder'
                      % output_tar_path)
                exit(1)
            output_path = os.path.dirname(output_tar_path)

    temp_work_dir = join(output_path, '.temp_' + str(uuid.uuid4()))
    if not os.path.exists(temp_work_dir):
        try:
            os.makedirs(temp_work_dir)
        except OSError as ex:
            logging.error('In untar_filter_tar, could not make directory %s : %s'
                          % (temp_work_dir, ex.strerror))
            exit(1)

    try:
        tar = tarfile.open(tar_file_path)
        tar.extractall(temp_work_dir)
        tar.close()
    except Exception as ex:
        logging.error('In untar_filter_tar, when untar file %s, error happened: %s'
                      % (tar_file_path, ex))
        exit(1)

    for file in CSV_FILE_FILTER_MAP.keys():
        if not os.path.exists(join(temp_work_dir, file)):
            logging.info('Skipping %s since not in tar file %s' % (file, tar_file_path))
            continue

        do_filtering(temp_work_dir, file)

    tar_file_basename = os.path.basename(tar_file_path)
    try:
        with tarfile.open(join(output_path, tar_file_basename), 'w') as new_tar_file:
            for name in [f for f in os.listdir(temp_work_dir)]:
                new_tar_file.add(join(temp_work_dir, name), arcname=name)
    except Exception as ex:
        exit_with_cleanup(ex, temp_work_dir)

    clean_temp_dir(temp_work_dir)


def main():
    argParser = argparse.ArgumentParser()
    argParser.add_argument('-i', '--input', help='input tarfile path', required='true')
    argParser.add_argument('-f', '--filter', help='filter csv file path. Filter csv header: ' +
                           ','.join(FILTER_CSV_FILE_HEADER))
    argParser.add_argument('-o', '--output', help='output dir. Optional; If not specified,' +
                           ' the dir of input tarfile path will be used')

    args = argParser.parse_args()
    if not os.path.exists(args.input):
        logging.error('The tarfile ' + args.input + ' does not exist! Please specify the correct file path\n')
        argParser.print_help()
        sys.exit(1)
    if not os.path.isfile(args.input) or not os.path.basename(args.input).endswith('tar'):
        logging.error('The specified tarfile ' + args.input + ' is not a tarfile! Please specify the correct file path\n')
        argParser.print_help()
        sys.exit(1)

    logging.info('Untar the file to process ...')
    process_filter_csv(args.filter)
    untar_filter_tar(args.input, args.output)
    logging.info('The process is done successfully.')


if __name__ == '__main__':
    main()
