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
Set up the `sparkpost.ini` file as per the example file. 
Replace `<YOUR API KEY>` with your specific, private API key. 

`Host` is only needed for SparkPost EU and SparkPost Enterprise service usage; you can omit for US-hosted [sparkpost.com](https://www.sparkpost.com/).


## Usage

```
$ ./sparkyRecipValidate.py -h
usage: sparkyRecipValidate.py [-h] [-i INFILE] [-o OUTFILE]

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
```

## Example output

The program can act as a Unix-style "filter" so you can pipe / redirect input and output; alternatively you
can use the `'-i` and '-o` options to specify input and output files.

An example input file is included in the project. Progress reporting is sent to stderr, so it doesn't
interfere with stdout. Here is a filter example, then displaying the output file.

The output file follows the same form as the SparkPost web application.

```
$ ./sparkyRecipValidate.py <valtest.csv >out.csv
Scanned input file <stdin>, contains 15 syntactically OK and 0 bad addresses. Validating ..
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

## See Also
[SparkPost Developer Hub](https://developers.sparkpost.com/)


