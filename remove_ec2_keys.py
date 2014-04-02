#!/usr/bin/env python
import argparse
import boto.ec2

def cmdline():
    argp = argparse.ArgumentParser(description='Removes key pairs from EC2')
    argp.add_argument(
            '-r', '--region', default='eu-west-1',
            help='EC2 region to work with')
    argp.add_argument(
            '-n', '--dry-run', action='store_true',
            help='Shoot with blanks, only print matching key names')
    argp.add_argument(
            'keyname', nargs='+',
            help='Key names to delete (globbing accepted)')
    return argp.parse_args()

def main():
    args = cmdline()
    ec2 = boto.ec2.connect_to_region(args.region)
    for keyname in args.keyname:
        keys = ec2.get_all_key_pairs(filters={'key-name': keyname})
        for key in keys:
            print key.name
            if not args.dry_run:
                ec2.delete_key_pair(key.name, dry_run=args.dry_run)

if __name__ == '__main__':
    main()
