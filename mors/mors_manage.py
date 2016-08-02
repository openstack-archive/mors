#!/opt/pf9/pf9-mors/bin/python
"""
Copyright 2016 Platform9 Systems Inc.(http://www.platform9.com)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

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



