#!/usr/bin/env python
"""
Removes SSH keys registered in EC2.
Optionally also terminates instances started with those keys.
Really handy for i.e. cleaning up after puppet, or if an employee departs.

WARNING: You may want to run this in dry-run mode (-n) first.

Invoke with a "packer*" argument to clean up after Packer (packer.io)
"""
import argparse
from datetime import datetime, timedelta
import boto.ec2

def cmdline():
    argp = argparse.ArgumentParser(description='Removes key pairs from EC2')
    def timedelta_s(seconds):
        return timedelta(0, seconds=int(seconds))

    argp.add_argument(
            '-r', '--region', default='eu-west-1',
            help='EC2 region to work with')
    argp.add_argument(
            '-t', '--terminate_instances', action='store_true',
            help='Terminate instances started with matching keys')
    argp.add_argument(
            '--min_instance_age_s', type=timedelta_s, default=timedelta_s(3000),
            help='Only terminate instances started at least this many seconds ago')
    argp.add_argument(
            '-n', '--dry-run', action='store_true',
            help='Shoot with blanks, only print matching key names')
    argp.add_argument(
            'keyname', nargs='+',
            help='Key names to delete (wildcards [*?] accepted)')
    return argp.parse_args()

def main():
    args = cmdline()
    ec2 = boto.ec2.connect_to_region(args.region)
    for keyname in args.keyname:
        delete_keys(ec2, keyname, args.dry_run)
        if args.terminate_instances:
            kill_instances(ec2, keyname, args.min_instance_age_s, args.dry_run)

def delete_keys(ec2, keyname, dry_run):
    keys = ec2.get_all_key_pairs(filters={'key-name': keyname})
    for key in keys:
        print key.name
        if not dry_run:
            ec2.delete_key_pair(key.name)

def kill_instances(ec2, keyname, min_age, dry_run):
    now = datetime.utcnow()
    instances = ec2.get_only_instances(filters={'key-name': keyname})
    kill_list = []
    for instance in instances:
        launchtime = datetime.strptime(instance.launch_time, '%Y-%m-%dT%H:%M:%S.%fZ')
        if (now - launchtime) > min_age:
            print "Going to kill", instance.id, "launched", instance.launch_time
            kill_list.append(instance.id)
    if not dry_run:
        ec2.terminate_instances(kill_list, dry_run)

if __name__ == '__main__':
    main()
