#!/usr/bin/env python
#
# Sets owner tags on EBS volumes that do not already have an owner tag set.
# The value of the ownership tag is copied from the instance the volume is
# attached to.
#
#

import argparse 
import boto.ec2

def cmdline():
    parser = argparse.ArgumentParser(description='Updates EBS volume ownership to match instance ownership')
    parser.add_argument(
            '-r', '--region',
            help='AWS Region to act on. (default: eu-west-1)',
            default='eu-west-1')
    parser.add_argument(
            '-n', '--dry-run',
            help='Do not actually write ownership tags',
            action='store_true')
    return parser.parse_args()

def get_owners(ec2_connection, type='instance'):
    """
    Queries the owner tags for a type of EC2 resource.
    Returns a dictionary, key: resource id, value: content of 'owner' tag.
    """
    tags = ec2_connection.get_all_tags({'resource-type': type, 'tag:owner': '*'})
    owner_by_id = {tag.res_id: tag.value for tag in tags}
    return owner_by_id

def set_owner_tag_on_resources(ec2_connection, resources_by_owner):
    """
    Sets 'owner' tags on EC2 resources. 
    ec2_connection: An boto.ec2.connection object
    resources_by_owner: A dictionary, keyed by owner, containing
    lists of resource ids that should have their owner tag set.
    """
    for owner, identifiers in resources_by_owner.iteritems():
        print 'set owner: {0} on {1}'.format(owner, ', '.join(identifiers))
        ec2_connection.create_tags(identifiers, {'owner': owner})

def main():
    opts = cmdline()
    ec2c = boto.ec2.connect_to_region(opts.region)
    owners_by_instance = get_owners(ec2c, 'instance')
    owners_by_volume = get_owners(ec2c, 'volume')
    volumes = ec2c.get_all_volumes()
    volumes_by_owner = {}
    for v in volumes:
        if v.status == 'in-use' and v.id not in owners_by_volume:
            attached_to = v.attach_data.instance_id
            if attached_to in owners_by_instance:
                owner = owners_by_instance.get(v.attach_data.instance_id)
                #print v.id, v.status, v.attach_data.instance_id, owner
                if owner in volumes_by_owner:
                    volumes_by_owner[owner].append(v.id)
                else:
                    volumes_by_owner[owner] = list((v.id,))
    if opts.dry_run:
        for owner, volumes in volumes_by_owner.iteritems():
            print owner, volumes
    else:
        set_owner_tag_on_resources(ec2c, volumes_by_owner)

if __name__ == '__main__':
    main()
