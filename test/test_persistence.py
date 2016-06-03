from proboscis import test
from mors.persistence import DbPersistence
import uuid
import logging
from migrate.versioning.api import upgrade,create,version_control
from datetime import datetime
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
                                       tenant_values["updated_by"], tenant_values["updated_at"])
    _verify_tenant_lease(tenants)

    # Instance lease now
    instance_uuids = [str(uuid.uuid4()), str(uuid.uuid4())]
    tenant_id = tenants.keys()[0]
    now = datetime.utcnow()
    for instance_uuid in instance_uuids:
        db_persistence.add_instance_lease(instance_uuid, tenant_id, now, tenants[tenant_id]["user"], now)

    for instance_uuid in instance_uuids:
        logger.debug("1" + str(tenant_id))
        logger.debug("2"+ str(instance_uuid)) 
        i_lease = db_persistence.get_instance_lease(instance_uuid)
        assert (i_lease.instance_uuid == instance_uuid)
        assert (i_lease.tenant_uuid == tenant_id)
        assert (i_lease.expiry == now)
        assert (i_lease.created_by == tenants[tenant_id]["user"])

