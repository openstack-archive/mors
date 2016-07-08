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
import constants
import logging
from datetime import datetime

# @TODO: Need to move this to a test folder

class FakeLeaseHandler:
    # Singleton tenants
    tenants = {}

    def __init__(self,conf):
        self.logger = logging.getLogger("test-lease-handler")
        pass

    def add_tenant_data(self, tenant_id, instances):
        FakeLeaseHandler.tenants[tenant_id] = instances
        print FakeLeaseHandler.tenants

    def get_tenant_data(self, tenant_id):
        return FakeLeaseHandler.tenants[tenant_id]

    def get_all_vms(self, tenant_uuid):
        return FakeLeaseHandler.tenants[tenant_uuid]

    def delete_vm(self, tenant_uuid, vm_id):
        vms = FakeLeaseHandler.tenants[tenant_uuid]
        new_vm_data = filter(lambda x: x['instance_uuid'] != vm_id, vms)
        FakeLeaseHandler.tenants[tenant_uuid] = new_vm_data


    def delete_vms(self, vms):
        result = {}
        for vm in vms:
            self.logger.info("Deleting VM  vm %s", vm)
            self.delete_vm(vm['tenant_uuid'], vm['instance_uuid'])
            result[vm['instance_uuid']] = constants.SUCCESS_OK
        return result
