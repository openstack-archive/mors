#!/opt/pf9/pf9-mors/bin/python
# Copyright (c) 2016 Platform9 Systems Inc.
# All Rights reserved
import argparse, logging
import ConfigParser
from migrate.versioning.api import upgrade, create, version_control
from migrate.exceptions import DatabaseAlreadyControlledError

def _get_arg_parser():
    parser = argparse.ArgumentParser(description="Lease Manager for VirtualMachines")
    parser.add_argument('--config-file', dest='config_file', default='/etc/pf9/pf9-mors.ini')
    parser.add_argument('--command', dest='command', default='db_sync')
    return parser.parse_args()

def _version_control(conf):
    try:
        version_control(conf.get("DEFAULT", "db_conn"), conf.get("DEFAULT", "repo"))
    except DatabaseAlreadyControlledError as e:
        print e
        # Ignore the already controlled error

if __name__ == '__main__':
    parser = _get_arg_parser()
    conf = ConfigParser.ConfigParser()
    conf.readfp(open(parser.config_file))
    if 'db_sync' == parser.command:
        _version_control(conf)
        upgrade(conf.get("DEFAULT", "db_conn"), conf.get("DEFAULT", "repo"))
        exit(0)
    else:
        print 'Unknown command'
        exit(1)



