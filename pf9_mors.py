#!/opt/pf9/pf9-mors/bin/python
# Copyright (c) 2016 Platform9 Systems Inc.
# All Rights reserved

from paste.deploy import loadapp
from eventlet import wsgi
import eventlet
import argparse, logging
import logging.handlers
import ConfigParser, os
from mors import mors_wsgi

eventlet.monkey_patch()
def _get_arg_parser():
    parser = argparse.ArgumentParser(description="Lease Manager for VirtualMachines")
    parser.add_argument('--config-file', dest='config_file', default='/etc/pf9/pf9-mors.ini')
    parser.add_argument('--paste-ini', dest='paste_file')
    return parser.parse_args()

def _configure_logging(conf):
    log_filename = conf.get("DEFAULT", "log_file")
    logging.basicConfig(filename=log_filename,
                        level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M')
    handler = logging.handlers.RotatingFileHandler(
        log_filename, maxBytes=1024 * 1024 * 5, backupCount=5)
    logging.root.addHandler(handler)


def start_server(conf, paste_ini):
    _configure_logging(conf)
    paste_file = None
    if paste_ini:
        paste_file = paste_ini
    else:
        paste_file = conf.get("DEFAULT", "paste-ini")

    wsgi_app = loadapp('config:%s' % paste_file, 'main')
    mors_wsgi.start_server(conf)
    wsgi.server(eventlet.listen(('', conf.getint("DEFAULT", "listen_port"))), wsgi_app)


if __name__ == '__main__':
    parser = _get_arg_parser()
    conf = ConfigParser.ConfigParser()
    conf.readfp(open(parser.config_file))
    start_server(conf, parser.paste_file)
