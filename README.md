# Comoyo Monkeys

Distant cousins of Netflix' Simian Army.

## elb-ssl-verifier

Small tool to check that SSL certificates configured on ELBs aren't expiring anytime soon.

### Prerequisites

This script is Python2, and requires Boto, M2Crypto (which requires OpenSSL) and
pytz.

(In a virtualenv,) run:

    pip install -r requirements.txt

You will also need to have AWS credentials with read permissions on AWS' ELB and
IAM APIs. These must be available to boto, see
http://code.google.com/p/boto/wiki/BotoConfig

### Usage

    usage: elbcerts.py [-h] [-d DEADLINE] [-r REGION]

    optional arguments:

      -h, --help            show this help message and exit
      -d DEADLINE, --deadline DEADLINE
                            Number of days before certificate expiration to warn 
                            (default: 30)
      -r REGION, --region REGION
                            AWS Region to check for ELBs with certificates at
                            risk. (Default: eu-west-1)

## ebsowners

Small tool to set EBS volume owner tags to the value of the owner tag of the 
instance the volume is attached to.

### Prerequisites

Python 2, Boto.

You will also need to have AWS credentials with read permissions on AWS' ELB and
IAM APIs. These must be available to boto, see
http://code.google.com/p/boto/wiki/BotoConfig

### Usage

    usage: ebsowners.py [-h] [-r REGION] [-n]

    Updates EBS volume ownership to match instance ownership

    optional arguments:
      -h, --help            show this help message and exit
      -r REGION, --region REGION
                            AWS Region to act on. (default: eu-west-1)
      -n, --dry-run         Do not actually write ownership tags

