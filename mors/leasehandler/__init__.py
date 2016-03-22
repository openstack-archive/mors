# Copyright 2016 Platform9 Systems Inc.

from nova_lease_handler import NovaLeaseHandler
from fake_lease_handler import FakeLeaseHandler
import constants


def get_lease_handler(conf):
    if conf.get("DEFAULT", "lease_handler") == "test":
        return FakeLeaseHandler(conf)
    else:
        return NovaLeaseHandler(conf)
