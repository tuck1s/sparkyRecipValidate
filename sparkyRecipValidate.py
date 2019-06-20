#!/usr/bin/env python3

import argparse, time, csv, requests, io
from email_validator import validate_email, EmailNotValidError
from common import eprint, getenv_check, getenv, hostCleanup


def validateRecipient(url, apiKey, recip, snooze):
    """
    Validate a single recipient. Allows for possible future rate-liming on this endpoint.
    :param url: SparkPost URL including the endpoint
    :param apiKey: SparkPost API key
    :param recip: single recipient
    :return: dict containing JSON-decode of response
    """
    try:
        h = {'Authorization': apiKey, 'Accept': 'application/json'}
        thisReq = requests.compat.urljoin(url, recip)
        # Allow for possible rate-limiting responses in future, even if not happening now
        while True:
            response = requests.get(thisReq, timeout=60, headers=h)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                eprint(response.json(), '.. pausing', snooze, 'seconds for rate-limiting')
                time.sleep(snooze)
                continue  # try again
            else:
                eprint('Error:', response.status_code, ':', response.text)
                return None

    except ConnectionError as err:
        eprint('error code', err.status_code)
        exit(1)


def processFile(infile, outfile, url, apiKey, snooze, skip_precheck):
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
    if infile.seekable() and not skip_precheck:
        # Check & report syntactically-OK & bad email addresses before we start API-based validation, if we can
        f = csv.reader(infile)
        count_ok, count_bad = 0, 0
        for r in f:
            if len(r) == 1:
                recip = r[0]
                try:
                    validate_email(recip, check_deliverability=False)
                    count_ok += 1
                except EmailNotValidError as e:
                    # email is not valid, exception message is human-readable
                    eprint(f.line_num, recip, str(e))
                    count_bad += 1
            else:
                count_bad += 1
        eprint('Scanned input {}, contains {} syntactically OK and {} bad addresses. Validating with SparkPost..'
               .format(infile.name, count_ok, count_bad))
        infile.seek(0)
    else:
        eprint('Skipping input file syntax pre-check. Validating with SparkPost..')

    f = csv.reader(infile)
    fList = ['email', 'valid', 'reason', 'is_role', 'is_disposable', 'is_free']
    fh = csv.DictWriter(outfile, fieldnames=fList, restval='', extrasaction='ignore')
    fh.writeheader()
    for r in f:
        recip = r[0]
        res = validateRecipient(url, apiKey, recip, snooze)
        if res and 'results' in res:
            row = res['results']
            row['email'] = recip
            fh.writerow(row)
        else:
            eprint('Error: response {}'.format(res))

    infile.close()
    outfile.close()
    eprint('Done')


# -----------------------------------------------------------------------------------------
# Main code
# -----------------------------------------------------------------------------------------
parser = argparse.ArgumentParser(
    description='Validate recipients with SparkPost. \
        Checks a single email address, or reads from specified input file (or stdin). \
        Results to specified output file or stdout (i.e. can act as a filter).')
inp = parser.add_mutually_exclusive_group(required=False)
inp.add_argument('-i', '--infile', type=argparse.FileType('r'), default='-',
                    help='filename to read email recipients from (in .CSV format)')
inp.add_argument('-e', '--email', type=str, action='store',
                    help='email address to validate. May carry multiple addresses, comma-separated, no spaces')
parser.add_argument('-o', '--outfile', type=argparse.FileType('w'), default='-',
                    help='filename to write validation results to (in .CSV format)')
parser.add_argument('--skip_precheck', action='store_true', help='Skip the precheck of input file email syntax')
args = parser.parse_args()

apiKey = getenv_check('SPARKPOST_API_KEY')                      # API key is mandatory
host = hostCleanup(getenv('SPARKPOST_HOST', default='api.sparkpost.com'))
url = host + '/api/v1/recipient-validation/single/'

if args.email:
    cmdInfile = io.StringIO(args.email.replace(',', '\n'))
    cmdInfile.name = 'from command line'
    processFile(cmdInfile, args.outfile, url, apiKey, 120, args.skip_precheck)
else:
    processFile(args.infile, args.outfile, url, apiKey, 120, args.skip_precheck)
