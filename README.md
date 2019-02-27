<a href="https://www.sparkpost.com"><img src="https://www.sparkpost.com/sites/default/files/attachments/SparkPost_Logo_2-Color_Gray-Orange_RGB.svg" width="200px"/></a>

[Sign up](https://app.sparkpost.com/join?plan=free-0817?src=Social%20Media&sfdcid=70160000000pqBb&pc=GitHubSignUp&utm_source=github&utm_medium=social-media&utm_campaign=github&utm_content=sign-up) for a SparkPost account and visit our [Developer Hub](https://developers.sparkpost.com) for even more content.

# sparkyRecipValidate
[![Build Status](https://travis-ci.org/tuck1s/sparkyRecipValidate.svg?branch=master)](https://travis-ci.org/tuck1s/sparkyRecipValidate)


## Easy installation

Firstly ensure you have `python3`, `pip` and `git`. Install `pipenv`:

`pip install pipenv`

Get the project, and install dependencies.

```
git clone https://github.com/tuck1s/sparkyRecipValidate.git
cd sparkyRecipValidate
pipenv install
pipenv shell
```

You can now type `./sparkyRecipValidate.py -h` and see usage info.

## Pre-requisites

Set the following environment variables:

```
SPARKPOST_HOST (optional)
    The URL of the SparkPost API service you're using. Defaults to https://api.sparkpost.com.

SPARKPOST_API_KEY
    API key on your SparkPost account, with Recipient Validation rights.
```

## Usage

```
$ ./sparkyRecipValidate.py -h
usage: sparkyRecipValidate.py [-h] [-i INFILE] [-o OUTFILE] [--skip_precheck]

Validate recipients with SparkPost. Reads from specified input file (or
stdin), results to specified output file or stdout (i.e. can act as a filter)

optional arguments:
  -h, --help            show this help message and exit
  -i INFILE, --infile INFILE
                        filename to read email recipients from (in .CSV
                        format)
  -o OUTFILE, --outfile OUTFILE
                        filename to write validation results to (in .CSV
                        format)
  --skip_precheck       Skip the precheck of input file email syntax
```

## Example output

The program can act as a Unix-style "filter" so you can pipe / redirect input and output; alternatively you
can use the `-i` and `-o` options to specify input and output files.

An example input file is included in the project. Progress reporting is sent to stderr, so it doesn't
interfere with stdout. Here is a filter example, then displaying the output file.

The output file follows the same form as the SparkPost web application.

```
$ ./sparkyRecipValidate.py <valtest.csv >out.csv
Scanned input file <stdin>, contains 15 syntactically OK and 0 bad addresses. Validating with SparkPost..
Done

$ cat out.csv
email,valid,reason,is_role,is_disposable
postmaster@yahoo.com,True,,True,False
admin@geekswithapersonality.com,True,,True,False
dahoju@heximail.com,True,,False,False
gpiohwxy@sharklasers.com,True,,False,True
kobapracro@memeil.top,False,Invalid Domain,False,True
planetaryhacksaw@maildrop.cc,True,,False,True
austein@yopmail.com,True,,False,True
vemugi@banit.me,True,,False,True
sales@sparkpost.com,True,,True,False
jeff+friendly@messagesystems.com,True,,False,False
123a@gmail.com,False,Invalid Recipient,False,False
sam@hotmal.com,True,,False,False
abc@yahoo.com,False,Invalid Recipient,False,False
123@hotmail.com,False,Invalid Recipient,False,False
sweettomatoes@hottomattoes.com,False,Invalid Domain,False,False
```

Excel or [csvkit](https://csvkit.readthedocs.io) may be helpful to work with these files.

## Input file email syntax check

The email syntax pre-check uses [this library](https://pypi.org/project/email_validator/) and is fast. It 
also reports how many addresses are in the file before API-based validation starts.

If input is coming from a stream, and therefore not seekable, the pre-check will also be skipped:

Piping in, as expected, is not seekable:
```
$ cat valtest.csv | ./sparkyRecipValidate.py >result3.csv
Skipping input file syntax pre-check. Validating with SparkPost..
Done
```

Redirection with `<` is (perhaps surprisingly) seekable:
```
$ ./sparkyRecipValidate.py <valtest.csv >result2.csv
Scanned input file <stdin>, contains 15 syntactically OK and 0 bad addresses. Validating with SparkPost..
Done
```

Specifying input file is seekable:
```
$ ./sparkyRecipValidate.py -i valtest.csv >result2.csv
Scanned input file valtest.csv, contains 15 syntactically OK and 0 bad addresses. Validating with SparkPost..
Done
```

## See Also
[SparkPost Developer Hub](https://developers.sparkpost.com/)

[Recipient Validation SparkPost API endpoint](https://developers.sparkpost.com/api/recipient-validation/)
