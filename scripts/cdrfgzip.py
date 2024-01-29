import os
import sys
import csv
import traceback
import uuid
import gzip
import tarfile
import shutil
import logging
import argparse
import datetime
from os.path import isfile, join, getmtime


# Verify we are running Python 3.10 or newer
if sys.version_info.major < 3:
    print("Python 3.x.x or newer is required to run this tool.")
    exit(-1)


OUTPUT_PATH_KEY = 'output_path'
MAX_LINES_PER_FILE_KEY = 'max_line_per_file'
LAST_COLLECTION_TIME_KEY = 'last_collection_time'

CNF_FILENAME = '.cdr_collector_filter_cfg'
CNF_PROFILE_TAG = '[CDR_COLLECTION_FILTER_CNF]'
CNF_MAXLINES_PERFILE = 1000000

CDR_FILENAME_PREFIXES = ('CDR', 'cdr', 'CMR', 'cmr')
COMBINED_FILENAME_PREFIX = 'combined_filtered_cdr_'


CDR_INCLUDED_HEADERS = []
CDR_INCLUDED_HEADERS_DATATYPE = {}
CDR_EXCLUDED_HEADERS = ['origIpAddr',
                        'origMediaTransportAddress_IP','origMediaTransportAddress_Port',
                        'origVideoTransportAddress_IP','origVideoTransportAddress_Port',
                        'destIpAddr','destMediaTransportAddress_IP',
                        'destMediaTransportAddress_Port','destVideoTransportAddress_IP',
                        'destVideoTransportAddress_Port','outpulsedCallingPartyNumber',
                        'outpulsedCalledPartyNumber','origIpv4v6Addr','destIpv4v6Addr',
                        'origVideoTransportAddress_IP_Channel2','origVideoTransportAddress_Port_Channel2',
                        'destVideoTransportAddress_IP_Channel2','destVideoTransportAddress_Port_Channel2',
                        'outpulsedOriginalCalledPartyNumber','outpulsedLastRedirectingNumber',
                        'callingPartyNumber_uri','originalCalledPartyNumber_uri','finalCalledPartyNumber_uri',
                        'lastRedirectDn_uri','mobileCallingPartyNumber','finalMobileCalledPartyNumber']

CDR_ROW_FILTER_SOURCE = 'phone.csv'
CDR_ROW_FILTER_NAME = 'Device Name'
CDR_ROW_FILTER = []


# global variables
sftp_path = None
envDict = {}
csv_opener = open

logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO)


def make_filename(prefix, timevalue, ext):
    timestr = str(datetime.datetime.fromtimestamp(timevalue)).replace(' ', '_').replace(':', '_')
    return prefix + timestr + '.' + ext


def is_after(newtime, lasttime):
    return newtime > lasttime


def has_common_element(list1, list2):
    if list1 == None or list2 == None:
        return False

    for item in list1:
        if item in list2:
            return True

    return False


def clean_temp_dir(dirname):
    try:
        shutil.rmtree(dirname)
    except OSError as ex:
        logging.error('Error occured: %s : %s' % (dirname, ex.strerror))


def exit_with_cleanup(ex, filename, dirname):
    traceback.print_exc()
    logging.error('exit_with_cleanup: Error happened when processing file %s: %s' % (filename, ex))
    clean_temp_dir(dirname)
    logging.info('Exit...')
    exit(1)


def get_csv_filter(filter_file_path):
    global CDR_ROW_FILTER

    phone_csv_path = None
    #logging.info(filter_file_path)
    if filter_file_path != None:
        if filter_file_path.endswith('tar'):
            try:
                tar = tarfile.open(filter_file_path)
                tar.extract(CDR_ROW_FILTER_SOURCE, envDict[OUTPUT_PATH_KEY])
                tar.close()
                phone_csv_path = join(envDict[OUTPUT_PATH_KEY], CDR_ROW_FILTER_SOURCE)
            except Exception as ex:
                logging.error('In process_env, can not extract %s from %s : %s'
                            % (CDR_ROW_FILTER_SOURCE, filter_file_path, ex))
        elif os.path.basename(filter_file_path) == CDR_ROW_FILTER_SOURCE:
            phone_csv_path = filter_file_path

        try:
            if phone_csv_path != None and os.path.exists(phone_csv_path):
                with open(phone_csv_path, 'r') as phone_csv:
                    csvreader = csv.DictReader(phone_csv, delimiter=',', quotechar='"')
                    for row in csvreader:
                        CDR_ROW_FILTER.append(row[CDR_ROW_FILTER_NAME])

            if filter_file_path.endswith('tar') and phone_csv_path != None:
                os.remove(phone_csv_path)
        except Exception as ex:
                logging.warn('In process_env, some error happend %s' % ex)

        #logging.info(CDR_ROW_FILTER)


def process_env(args):
    global sftp_path
    global csv_opener

    sftp_path = args.path

    try:
        with open(join(sftp_path, CNF_FILENAME), 'r') as f:
            lines = f.read().strip().splitlines()
    except OSError as x:
        lines = []
    lines = [line.strip() for line in lines]
    #logging.info(lines)

    if len(lines) > 0 and lines[0] == CNF_PROFILE_TAG:
        for line in lines:
            if '=' in line:
                key, value = line.split('=')
                envDict[key] = value

    # if cmdline has the same input, use the cmdline ones to replace
    if args.output != None:
        envDict[OUTPUT_PATH_KEY] = args.output
    if args.maxlines != None and args.maxlines.isnumeric():
        envDict[MAX_LINES_PER_FILE_KEY] = args.maxlines if int(args.maxlines) < \
            CNF_MAXLINES_PERFILE else str(CNF_MAXLINES_PERFILE)

    # if the csv file is compressed, use gzip open
    if args.compress != None and args.compress.lower() == "gzip":
        csv_opener = gzip.open

    # last, if still not set, we will use default
    if OUTPUT_PATH_KEY not in envDict.keys():
        envDict[OUTPUT_PATH_KEY] = args.path
    if LAST_COLLECTION_TIME_KEY not in envDict.keys():
        envDict[LAST_COLLECTION_TIME_KEY] = '0.0'
    if MAX_LINES_PER_FILE_KEY not in envDict.keys() or envDict[MAX_LINES_PER_FILE_KEY] == '0':
        envDict[MAX_LINES_PER_FILE_KEY] = str(CNF_MAXLINES_PERFILE)

    get_csv_filter(args.filter)


def write_back_env(collection_time):
    envDict[LAST_COLLECTION_TIME_KEY] = str(collection_time)
    newCfg = [key + '=' + envDict[key] for key in envDict.keys()]
    try:
        with open(join(sftp_path, CNF_FILENAME), 'w+') as f:
            f.write(CNF_PROFILE_TAG + os.linesep)
            f.writelines('\n'.join(newCfg))
    except Exception as ex:
        logging.error('Error happened when writing %s : %s' %
                      (join(sftp_path, CNF_FILENAME), ex.strerror))


def filter_zip_cdr():
    global sftp_path
    global CDR_ROW_FILTER
    global csv_opener

    ftime =float(envDict[LAST_COLLECTION_TIME_KEY])
    #logging.info(ftime)

    try:
        dirs = os.listdir(sftp_path)
    except Exception as ex:
        logging.error('Could not list directory %s : %s' % (sftp_path, ex.strerror))
        exit(1)

    after_lastcollection_files = [f for f in dirs if isfile(join(sftp_path, f)) and
                                  f.startswith(CDR_FILENAME_PREFIXES) and
                                  is_after(getmtime(join(sftp_path, f)), ftime)]
    after_lastcollection_files.sort(key=lambda f: getmtime(join(sftp_path, f)))

    files_count = len(after_lastcollection_files)
    if files_count == 0:
        logging.info('No new cdr files generated after %s' % datetime.datetime.fromtimestamp(ftime))
        return

    #logging.info(after_lastcollection_files)

    # make output directory
    output_temp_path = join(envDict[OUTPUT_PATH_KEY], 'temp_' + str(uuid.uuid4()))
    if not os.path.exists(output_temp_path):
        try:
            os.makedirs(output_temp_path)
        except OSError as ex:
            logging.error('Could not make directory %s : %s' % (output_temp_path, ex.strerror))
            exit(1)

    all_headers = []
    type_row = []
    for f in after_lastcollection_files:
        try:
            with csv_opener(join(sftp_path, f), mode = 'rt', newline='') as csvInputFile:
                csvreader = csv.DictReader(csvInputFile, delimiter=',', quotechar='"')
                all_headers = csvreader.fieldnames
                for row in csvreader:
                    type_row = row
                    break
                if len(all_headers) > 0:
                    break
        except Exception as ex:
            exit_with_cleanup(ex, f, output_temp_path)

    CDR_INCLUDED_HEADERS = list(filter(lambda h: h not in CDR_EXCLUDED_HEADERS, all_headers))
    CDR_INCLUDED_HEADERS_DATATYPE = {x:type_row[x] for x in CDR_INCLUDED_HEADERS}

    line_count = 0
    rows_to_write = []
    file_timestamp = 0.0
    for index, f in enumerate(after_lastcollection_files):
        skip_datatype = 0
        try:
            with csv_opener(join(sftp_path, f), mode = 'rt', newline='', errors='replace') as csvInputFile:
                csvreader = csv.DictReader(csvInputFile, delimiter=',', quotechar='"')
                for row in csvreader:
                    if skip_datatype == 0:
                        skip_datatype = 1
                        continue

                    if len(CDR_ROW_FILTER) > 0:
                        if not has_common_element(row.values(), CDR_ROW_FILTER):
                            continue

                    for x in CDR_INCLUDED_HEADERS:
                        if x not in row:
                            row[x] = ''
                        if CDR_INCLUDED_HEADERS_DATATYPE[x] == 'INTEGER':
                            try:
                                row[x] = int(row[x])
                            except:
                                row[x] = 0

                    new_row = [row[x] for x in CDR_INCLUDED_HEADERS]
                    rows_to_write.append(new_row)
                    line_count = line_count + 1
        except Exception as ex:
            exit_with_cleanup(ex, f, output_temp_path)

        if line_count >= int(envDict[MAX_LINES_PER_FILE_KEY]) or index == (files_count-1):
            file_timestamp = getmtime(join(sftp_path, f))

            temp_file = join(output_temp_path, make_filename(COMBINED_FILENAME_PREFIX, file_timestamp, 'csv'))

            try:
                with open(temp_file, 'w') as csvOutputFile:
                    csvwriter = csv.writer(csvOutputFile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
                    csvwriter.writerow(CDR_INCLUDED_HEADERS)
                    for row in rows_to_write:
                        csvwriter.writerow(row)

                output_gzip_filename = make_filename(COMBINED_FILENAME_PREFIX, file_timestamp, 'csv.gz')
                with open(temp_file, 'rb') as f_in:
                    with gzip.open(join(envDict[OUTPUT_PATH_KEY], output_gzip_filename), 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            except Exception as ex:
                exit_with_cleanup(ex, temp_file, output_temp_path)

            rows_to_write.clear()
            line_count = 0

    clean_temp_dir(output_temp_path)
    write_back_env(file_timestamp)


def main():
    argParser = argparse.ArgumentParser()
    argParser.add_argument('-p', '--path', help='sftp/ftp path to cdr files', required='true')
    argParser.add_argument('-o', '--output', help='output zip file path. If not specified, use PATH')
    argParser.add_argument('-l', '--maxlines', help='the max cdr number in one csv file; max is 1000000')
    argParser.add_argument('-f', '--filter', help='the filter file (phone.csv) path used to process cdr files')
    argParser.add_argument('-c', '--compress', help='specify the compressed format (gzip) used for original cdr file. Default is plain csv')

    args = argParser.parse_args()
    if not os.path.exists(args.path):
        logging.error('The path ' + args.path + ' does not exist! Please make sure your sftp/ftp path correct\n')
        argParser.print_help()
        sys.exit(1)

    logging.info('Start the CDR filtering and zipping process...')
    process_env(args)
    filter_zip_cdr()
    logging.info('The CDR filtering and zipping is complete.')


if __name__ == '__main__':
    main()
