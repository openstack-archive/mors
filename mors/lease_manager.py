# Copyright Platform9 Systems Inc. 2016

from datetime import datetime, timedelta

from leasehandler import get_lease_handler
from persistence import DbPersistence
from eventlet.greenthread import spawn_after
import logging
from leasehandler.constants import SUCCESS_OK, ERR_UNKNOWN, ERR_NOT_FOUND

logger = logging.getLogger(__name__)


def get_tenant_lease_data(data):
    """
    Simple function to transform tenant database proxy object into an externally
    consumable dictionary.
    :param data: database row object
    """
    return {'vm_lease_policy': {'tenant_uuid': data['tenant_uuid'],
                                'expiry_days': data['expiry_days'],
                                'created_at': data['created_at'],
                                'created_by': data['created_by'],
                                'updated_at': data['updated_at'],
                                'updated_by': data['updated_by']}}


def get_vm_lease_data(data):
    """
    Simple function to transform instance database proxy object into an externally
    consumable dictionary.
    :param data: database row object
    """
    return {'instance_uuid': data['instance_uuid'],
            'tenant_uuid': data['tenant_uuid'],
            'expiry': data['expiry'],
            'created_at': data['created_at'],
            'created_by': data['created_by'],
            'updated_at': data['updated_at'],
            'updated_by': data['updated_by']}


class LeaseManager:
    """
    Lease Manager is the main class for mors dealing with CRUD operations for the REST API
    as well as the actual deletion of the Instances. Instance deletion and discovery is achieved
    through an object 'leasehandler'.
    """
    def __init__(self, conf):
        self.domain_mgr = DbPersistence(conf.get("DEFAULT", "db_conn"))
        self.lease_handler = get_lease_handler(conf)
        self.sleep_seconds = conf.getint("DEFAULT", "sleep_seconds")

    def add_tenant_lease(self, context, tenant_obj):
        logger.info("Adding tenant lease %s", tenant_obj)
        self.domain_mgr.add_tenant_lease(
            tenant_obj['tenant_uuid'],
            tenant_obj['expiry_days'],
            context.user_id,
            datetime.utcnow())

    def update_tenant_lease(self, context, tenant_obj):
        logger.info("Update tenant lease %s", tenant_obj)
        self.domain_mgr.update_tenant_lease(
            tenant_obj['tenant_uuid'],
            tenant_obj['expiry_days'],
            context.user_id,
            datetime.utcnow())

    def delete_tenant_lease(self, context, tenant_id):
        logger.info("Delete tenant lease %s", tenant_id)
        return self.domain_mgr.delete_tenant_lease(tenant_id)

    def get_tenant_leases(self, context):
        logger.debug("Getting all tenant lease")
        all_tenants = self.domain_mgr.get_all_tenant_leases()
        all_tenants = map(lambda x: get_tenant_lease_data(x), all_tenants)
        logger.debug("Getting all tenant lease %s", all_tenants)
        return all_tenants

    def get_tenant_lease(self, context, tenant_id):
        data = self.domain_mgr.get_tenant_lease(tenant_id)
        logger.debug("Getting tenant lease %s", data)
        if data:
            return get_tenant_lease_data(data)
        return {}

    def get_tenant_and_associated_instance_leases(self, context, tenant_uuid):
        logger.debug("Getting tenant and instances leases %s", tenant_uuid)
        return {
            'tenant_lease': self.get_tenant_lease(context, tenant_uuid),
            'all_vms':
                map(lambda x: get_vm_lease_data(x), self.domain_mgr.get_instance_leases_by_tenant(tenant_uuid))
        }

    # To Be Implemented
    def check_instance_lease_violation(self, instance_lease, tenant_lease):
        return True

    def get_instance_lease(self, context, instance_id):
        data = self.domain_mgr.get_instance_lease(instance_id)
        if data:
            data = get_vm_lease_data(data)
        logger.debug("Get instance lease %s %s", instance_id, data)
        return data

    def add_instance_lease(self, context, tenant_uuid, instance_lease_obj):
        logger.info("Add instance lease %s", instance_lease_obj)
        tenant_lease = self.domain_mgr.get_tenant_lease(tenant_uuid)
        self.check_instance_lease_violation(instance_lease_obj, tenant_lease)
        self.domain_mgr.add_instance_lease(instance_lease_obj['instance_uuid'],
                                           tenant_uuid,
                                           instance_lease_obj['expiry'],
                                           context.user_id,
                                           datetime.utcnow())

    def update_instance_lease(self, context, tenant_uuid, instance_lease_obj):
        logger.info("Update instance lease %s", instance_lease_obj)
        self.domain_mgr.update_instance_lease(instance_lease_obj['instance_uuid'],
                                              tenant_uuid,
                                              instance_lease_obj['expiry'],
                                              context.user_id,
                                              datetime.utcnow())

    def delete_instance_lease(self, context, instance_uuid):
        logger.info("Delete instance lease %s", instance_uuid)
        self.domain_mgr.delete_instance_leases([instance_uuid])

    def start(self):
        spawn_after(self.sleep_seconds, self.run)

    # Could have used a generator here, would save memory but wonder if it is a good idea given the error conditions
    # This is a simple implementation which goes and deletes VMs one by one
    def _get_vms_to_delete_for_tenant(self, tenant_uuid, expiry_days):
        vms_to_delete = []
        vm_ids_to_delete = set()
        now = datetime.utcnow()
        add_days = timedelta(days=expiry_days)
        instance_leases = self.get_tenant_and_associated_instance_leases(None, tenant_uuid)['all_vms']
        for i_lease in instance_leases:
            if now > i_lease['expiry']:
                logger.info("Explicit lease for %s queueing for deletion", i_lease['instance_uuid'])
                vms_to_delete.append(i_lease)
                vm_ids_to_delete.add(i_lease['instance_uuid'])
            else:
                logger.debug("Ignoring vm, vm not expired yet %s", i_lease['instance_uuid'])

        tenant_vms = self.lease_handler.get_all_vms(tenant_uuid)
        for vm in tenant_vms:
            expiry_date = vm['created_at'] + add_days
            if now > expiry_date and not (vm['instance_uuid'] in vm_ids_to_delete):
                logger.info("Instance %s queued up for deletion creation date %s", vm['instance_uuid'],
                            vm['created_at'])
                vms_to_delete.append(vm)
            else:
                logger.debug("Ignoring vm, vm not expired yet or already deleted %s, %s", vm['instance_uuid'],
                             vm['created_at'])

        return vms_to_delete

    def _delete_vms_for_tenant(self, t_lease):
        tenant_vms_to_delete = self._get_vms_to_delete_for_tenant(t_lease['tenant_uuid'], t_lease['expiry_days'])

        # Keep it simple and delete them serially
        result = self.lease_handler.delete_vms(tenant_vms_to_delete)

        remove_from_db = []

        for vm_result in result.items():
            # If either the VM has been successfully deleted or has already been deleted
            # Remove from our database
            if vm_result[1] == SUCCESS_OK or vm_result[1] == ERR_NOT_FOUND:
                remove_from_db.append(vm_result[0])

        if len(remove_from_db) > 0:
            logger.info("Removing vms %s from db", remove_from_db)
            self.domain_mgr.delete_instance_leases(remove_from_db)

    def run(self):
        # Delete the cleanup
        tenant_leases = self.domain_mgr.get_all_tenant_leases()
        for t_lease in tenant_leases:
            self._delete_vms_for_tenant(t_lease)

        # Sleep again for sleep_seconds
        spawn_after(self.sleep_seconds, self.run)
