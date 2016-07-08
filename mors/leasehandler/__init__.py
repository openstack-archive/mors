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
from nova_lease_handler import NovaLeaseHandler
from fake_lease_handler import FakeLeaseHandler
import constants


def get_lease_handler(conf):
    if conf.get("DEFAULT", "lease_handler") == "test":
        return FakeLeaseHandler(conf)
    else:
        return NovaLeaseHandler(conf)
