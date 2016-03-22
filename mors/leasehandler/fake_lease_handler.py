# Copyright Platform9 Systems Inc. 2016
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
