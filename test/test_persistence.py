from mors.persistence import DbPersistence
import pytest
from migrate.versioning.api import upgrade,create,version_control
from datetime import datetime
import os

db_persistence = None
TEST_DB="test/test_db11"

def setup_module(mod):
    global db_persistence
    DB_URL = "sqlite:///"+TEST_DB
    create(DB_URL, "./mors_repo")
    version_control(DB_URL, "./mors_repo")
    upgrade(DB_URL,"./mors_repo")
    db_persistence = DbPersistence(DB_URL)
    return db_persistence

def teardown_module(mod):
    os.unlink(TEST_DB)

def test_apis():
    tenant_id = "aasdsadfsadf"
    tenant_user1 = "a@xyz.com"
    expiry_mins1 = 3
    tenant_created_date = datetime.utcnow()

    db_persistence.add_tenant_lease(tenant_id, expiry_mins1, tenant_user1, tenant_created_date)
    t_lease = db_persistence.get_tenant_lease(tenant_id)
    assert (t_lease.tenant_uuid == tenant_id)
    assert (t_lease.created_by == tenant_user1)
    assert (t_lease.created_at == tenant_created_date)

    # Now try update
    tenant_user2 = "b@xyz.com"
    tenant_updated_date = datetime.utcnow()
    db_persistence.update_tenant_lease(tenant_id, expiry_mins1, tenant_user2, tenant_updated_date)
    t_lease = db_persistence.get_tenant_lease(tenant_id)
    assert (t_lease.tenant_uuid == tenant_id)
    assert (t_lease.created_by == tenant_user1)
    assert (t_lease.updated_by == tenant_user2)
    assert (t_lease.created_at == tenant_created_date)
    assert (t_lease.updated_at == tenant_updated_date)


    # Instance lease now
    instance_uuid = "asdf2-2342-23423"
    now = datetime.utcnow()
    db_persistence.add_instance_lease(instance_uuid, tenant_id, now, tenant_user1, now)
    i_lease = db_persistence.get_instance_lease(instance_uuid, tenant_id)
    assert (i_lease.instance_uuid == instance_uuid)
    assert (i_lease.tenant_uuid == tenant_id)
    assert (i_lease.expiry == now)
    assert (i_lease.created_by == tenant_user1)


