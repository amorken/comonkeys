#!/usr/bin/env python
#
# Scan AWS Elastic Load Balancers for certificates that are about to expire.
#

import argparse 
import boto.ec2.elb
import boto.iam
from datetime import datetime, timedelta
import M2Crypto.X509
from pprint import pprint
from pytz import UTC

def cmdline():
    parser = argparse.ArgumentParser()
    parser.add_argument(
            '-d', '--deadline',
            help='Number of days before certificate expiration to warn. (default: 30)',
            default=30, type=int)
    parser.add_argument(
            '-r', '--region',
            help='AWS Region to check for ELBs with certificates at risk. (default: eu-west-1)',
            default='eu-west-1')
    return parser.parse_args()


def check_elb_certs(lb, deadline):
    iam_connection = boto.iam.connect_to_region('universal')
    for listener in lb.listeners:
        lbport, beport, proto = listener.get_tuple()
        if proto in ('HTTPS', 'SSL'):
            cert_arn = listener.ssl_certificate_id
            # Retrieving the certificate names and actual certificate body from the AWS responses is a bit clumsy:
            certname = cert_arn.split(':')[5].split('/')[-1]
            cert = (iam_connection.get_server_certificate(certname)
                        ['get_server_certificate_response']
                        ['get_server_certificate_result']
                        ['server_certificate']
                        ['certificate_body'])  # dictception! (Courtesy of JSON)
            # M2Crypto/OpenSSL doesn't like unicode strings, so wrap cert in str()
            x509 = M2Crypto.X509.load_cert_string(str(cert))  
            notafter = x509.get_not_after().get_datetime()
            if notafter < deadline:
                days_left = (notafter - datetime.now(UTC)).days
                print "Certificate {0}, used by ELB {1}, expires in {2} days!".format(certname, lb.name, days_left)

def main():
    opts = cmdline()
    elbc = boto.ec2.elb.connect_to_region(opts.region)

    lbs = elbc.get_all_load_balancers()
    deadline = datetime.now(UTC) + timedelta(days=opts.deadline)

    for lb in lbs:
        check_elb_certs(lb, deadline)

if __name__ == '__main__':
    main()
