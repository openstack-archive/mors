#!/opt/pf9/pf9-mors/bin/python
# Copyright (c) 2016 Platform9 Systems Inc.
# All Rights reserved
import argparse, logging
import ConfigParser
from migrate.versioning.api import upgrade, create, version_control

def _get_arg_parser():
    parser = argparse.ArgumentParser(description="Lease Manager for VirtualMachines")
    parser.add_argument('--config-file', dest='config_file', default='/etc/pf9/pf9-mors.ini')
    parser.add_argument('--command', dest='command', default='db_sync')
    return parser.parse_args()

if __name__ == '__main__':
    parser = _get_arg_parser()
    conf = ConfigParser.ConfigParser()
    conf.readfp(open(parser.config_file))
    if 'db_sync' == parser.command:
        version_control(conf.get("DEFAULT", "db_conn"), conf.get("DEFAULT", "repo"))
        upgrade(conf.get("DEFAULT", "db_conn"), , conf.get("DEFAULT", "repo"))
        exit(0)
    else:
        print 'Unknown command'
        exit(1)



