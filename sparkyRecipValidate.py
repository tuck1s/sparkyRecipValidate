#!/usr/bin/env python3

from datetime import datetime,timedelta
import argparse, configparser, time, sys, os, csv, requests
from requests.compat import urljoin
import persistentRequestThreads
from common import eprint

def getConfig(configFile):
    """
    Read SparkPost API sending config (or SMTP sending config) from file
    :param configFile: str
    :return: dict
    """
    cp = configparser.ConfigParser()
    cp.read_file(open(configFile))
    section = cp['SparkPost']
    cfg = {
        'Host': section.get('Host', 'https://api.sparkpost.com'),
        'Authorization': section.get('Authorization'),
        'Threads': section.getint('Threads', 10),
        'FileCharacterEncodings': section.get('FileCharacterEncodings'),
        'SnoozeTime': section.getint('SnoozeTime')
    }
    # Clean up Host parameter
    if not cfg['Host'].startswith('https://'):
        cfg['Host'] = 'https://' + cfg['Host']
    if cfg['Host'].endswith('/'):
        cfg['Host'] = cfg['Host'][:-1]  # Strip /

    if cfg['Authorization'] == None:
        eprint('Error: missing Authorization line in ' + configFile)
        exit(1)
    else:
        return cfg


def helloWorld():
    return 'hello'


def validateRecipient(url, apiKey, recip, snooze):
    """
    Validate a single recipient
    :param url: SparkPost URL including the endpoint
    :param apiKey: SparkPost API key
    :param recip: single recipient
    :return:
    """
    try:
        h = {'Authorization': apiKey, 'Accept': 'application/json'}
        thisReq = urljoin(url, recip)
        # Allow for possible rate-limiting responses in future, even if not happening now
        while True:
            response = requests.get(thisReq, timeout=60, headers=h)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                eprint(response.json(),'.. pausing', snooze, 'seconds for rate-limiting')
                time.sleep(snooze)
                continue                # try again
            else:
                eprint('Error:', response.status_code, ':', response.text)
                return None

    except ConnectionError as err:
        eprint('error code', err.status_code)
        exit(1)


def processFile(infile, outfile, url, apiKey, threads, snooze):
    """
    Process the input file - a list of email addresses to validate. Write results to outfile.
    Two pass approach. First pass checks file is readable and contains email addresses. Second pass calls validation.
    :param infile:
    :param outfile:
    :param url: str
    :param apiKey: str
    :param threads: int
    :param snooze: int
    """
    f = csv.reader(infile)
    count_OK, count_bad = 0, 0
    # very simple, superficial check for valid inputs before we start validation
    for r in f:
        if len(r) == 1 and '@' in r[0]:
            count_OK += 1
        else:
            count_bad += 1
    eprint('Scanned input file {}, contains {} syntactically OK and {} bad addresses. Validating ..'.format(infile.name, count_OK, count_bad))

    infile.seek(0)
    f = csv.reader(infile)
    fList = ['email', 'valid', 'reason', 'is_role', 'is_disposable']
    fh = csv.DictWriter(outfile, fieldnames=fList, restval='', extrasaction='ignore')
    fh.writeheader()
    recipBatch = []
    for r in f:
        recip = r[0]
        res = validateRecipient(url, apiKey, recip, snooze)
        if res and 'results' in res:
            row = res['results']
            row['email'] = recip
            fh.writerow(row)
        else:
            eprint('Error: response {}'.format(res))
    eprint('Done')


# -----------------------------------------------------------------------------------------
# Main code
# -----------------------------------------------------------------------------------------
parser = argparse.ArgumentParser(
    description='Validate recipients with SparkPost. Reads from specified input file (or stdin), \
    results to specified output file or stdout (i.e. can act as a filter)')
parser.add_argument('-i', '--infile', type=argparse.FileType('r'), default='-', help='filename to read email recipients from (in .CSV format)')
parser.add_argument('-o', '--outfile', type=argparse.FileType('w'), default='-', help='filename to write validation results to (in .CSV format)')
args = parser.parse_args()
cfg = getConfig('sparkpost.ini')
url = cfg['Host'] + '/api/v1/recipient-validation/single/'

processFile(args.infile, args.outfile, url, cfg['Authorization'], cfg['Threads'], cfg['SnoozeTime'])
