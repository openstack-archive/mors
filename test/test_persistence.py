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
from proboscis import test
from mors.persistence import DbPersistence
import uuid
import logging
from migrate.versioning.api import upgrade,create,version_control
from datetime import datetime, timedelta
import os
import shutil

logger = logging.getLogger(__name__)
db_persistence = None
TEST_DB="test/test_db11"

@test
def setup_module():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    global db_persistence
    DB_URL = "sqlite:///"+TEST_DB
    if os.path.exists(DB_URL):
        shutil.rmtree(DB_URL)
    create(DB_URL, "./mors_repo")
    version_control(DB_URL, "./mors_repo")
    upgrade(DB_URL,"./mors_repo")
    db_persistence = DbPersistence(DB_URL)
    return db_persistence

def teardown_module():
    os.unlink(TEST_DB)

def _verify_tenant_lease(tenants):
    for tenant in tenants:
        t_lease = db_persistence.get_tenant_lease(tenant)
        assert (t_lease.tenant_uuid == tenant)
        assert (t_lease.created_by == tenants[tenant]["user"])
        assert (t_lease.created_at == tenants[tenant]["tenant_created_date"])
        if "updated_by" in tenants[tenant].keys():
            assert (t_lease.updated_by == tenants[tenant]["updated_by"])
        if "updated_at" in tenants[tenant].keys():
            assert (t_lease.updated_at == tenants[tenant]["updated_at"])

def _verify_instance_lease(instances):
    for instance_uuid in instances:
        instance = instances[instance_uuid]
        i_lease = db_persistence.get_instance_lease(instance['instance_uuid'])
        assert (i_lease.instance_uuid == instance['instance_uuid'])
        assert (i_lease.tenant_uuid == instance['tenant_uuid'])
        assert (i_lease.expiry == instance['expiry'])
        assert (i_lease.created_by == instance["created_by"])
        if "updated_by" in instance.keys():
            assert (i_lease.updated_by == instance["updated_by"])
        if "updated_at" in instance.keys():
            assert (i_lease.updated_at == instance["updated_at"])

@test(depends_on=[setup_module])
def test_apis():
    tenants = {"tenant-1": { "user": "a@xyz.com",
                             "expiry_mins": 3,
                             "tenant_created_date": datetime.utcnow()},
               "tenant-2": { "user": "c@xyz.com",
                             "expiry_mins": 1,
                             "tenant_created_date": datetime.utcnow()}}

    for tenant in tenants:
        db_persistence.add_tenant_lease(tenant, tenants[tenant]["expiry_mins"],
                                        tenants[tenant]["user"],
                                        tenants[tenant]["tenant_created_date"])
    _verify_tenant_lease(tenants)

    # Now try update
    tenants["tenant-1"]["updated_by"] = "b@xyz.com"
    tenants["tenant-2"]["updated_by"] = "d@xyz.com"
    tenant_updated_date = datetime.utcnow()

    for tenant in tenants:
        tenants[tenant]["updated_at"] = tenant_updated_date
        tenant_values = tenants[tenant]
        db_persistence.update_tenant_lease(tenant, tenant_values["expiry_mins"],
                                           tenant_values["updated_by"],
                                           tenant_values["updated_at"])
    _verify_tenant_lease(tenants)

    now = datetime.utcnow()
    # Instance lease now
    instances = {"instance-1": {"instance_uuid": "instance-1",
                                "tenant_uuid": "tenant-1",
                                "expiry": now,
                                "created_at": now,
                                "created_by": "d@xyz.com"},
                 "instance-2": {"instance_uuid": "instance-2",
                                "tenant_uuid": "tenant-2",
                                "expiry": now + timedelta(seconds=60),
                                "created_at": now + timedelta(seconds=60),
                                "created_by": "e@xyz.com"}}
    tenant_id = tenants.keys()[0]
    now = datetime.utcnow()
    for instance_uuid in instances:
        instance = instances[instance_uuid]
        db_persistence.add_instance_lease(instance['instance_uuid'], instance['tenant_uuid'],
                                          instance['expiry'], instance["created_by"],
                                          instance["created_at"])
    _verify_instance_lease(instances)

    newtime1 = datetime.utcnow() + timedelta(seconds=240)
    newtime2 = datetime.utcnow() + timedelta(seconds=120)
    instances['instance-1']['expiry'] = newtime1
    instances['instance-1']['updated_at'] = newtime1
    instances['instance-2']['expiry'] = newtime2
    instances['instance-2']['updated_at'] = newtime2

    for instance_uuid in instances:
        instance = instances[instance_uuid]
        db_persistence.update_instance_lease(instance['instance_uuid'], instance['tenant_uuid'],
                                             instance['expiry'], instance["created_by"],
                                             instance["updated_at"])

    _verify_instance_lease(instances)
