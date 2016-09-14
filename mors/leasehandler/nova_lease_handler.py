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

from novaclient import client
import logging
import novaclient
from datetime import datetime
from constants import SUCCESS_OK, ERR_NOT_FOUND, ERR_UNKNOWN
logger = logging.getLogger(__name__)

DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

def get_vm_data(data):
    return {'instance_uuid': data.id,
            'tenant_uuid': data.tenant_id,
            'created_at': datetime.strptime(data.created, DATE_FORMAT)}

class NovaLeaseHandler:
    def __init__(self, conf):
        self.conf = conf
        self.nova_client = client.Client(self.conf.get("nova", "version"),
                             username=self.conf.get("nova", "user_name"),
                             region_name=self.conf.get("nova", "region_name"),
                             tenant_id=self.conf.get("nova", "tenant_uuid"),
                             api_key=self.conf.get("nova", "password"),
                             auth_url=self.conf.get("nova", "auth_url"),
                             insecure=True, # Insecure to handle test systems
                             connection_pool=False)

    def _get_nova_client(self):
        return self.nova_client

    def get_all_vms(self, tenant_uuid):
        """
        Get all vms for a given tenant
        :param tenant_uuid:
        :return: an iteratble that returns a set of vms (each vm has a UUID and a created_at field)
        """
        try:
            with self._get_nova_client() as nova:
                vms = nova.servers.list(search_opts={'all_tenants':1, 'tenant_id':tenant_uuid})
                return map(lambda x: get_vm_data(x), vms)
        except Exception as e:
            logger.exception("Error getting list of vms for tenant %s", tenant_uuid)

        return []

    def _delete_vm(self, nova, vm_uuid):
        try:
            logger.info("Deleting VM %s", vm_uuid)
            nova.servers.delete(vm_uuid)
            return SUCCESS_OK
        except novaclient.exceptions.NotFound:
            return ERR_NOT_FOUND
        except Exception as e:
            logger.exception("Error deleting vm %s", vm_uuid)
            return ERR_UNKNOWN

    def delete_vms(self, vms):
        """
        Delete a VM on a given tenant
        :param tenant_uuid:
        :param vm_uuid:
        :return: dictionary of vm_id to result
        """
        result = {}
        try:
            with self._get_nova_client() as nova:
                for vm in vms:
                    result[vm['instance_uuid']] = self._delete_vm(nova, vm['instance_uuid'])
            return result
        except Exception as e:
            logger.exception("Error deleting vm %s", vms)
        return result
