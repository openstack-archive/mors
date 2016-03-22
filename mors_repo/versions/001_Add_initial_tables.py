# Copyright Platform9 Systems Inc. 2016
from sqlalchemy import Table, Column, Integer, String, MetaData, DateTime

meta = MetaData()

tenant_lease = Table(
    'tenant_lease', meta,
    Column('tenant_uuid', String(40), primary_key=True),
    Column('expiry_days', Integer),
    Column('created_at', DateTime),
    Column('updated_at', DateTime),
    Column('created_by', String(40)),
    Column('updated_by', String(40))
)

vm_lease = Table(
    'instance_lease', meta,
    Column('instance_uuid', String(40), primary_key=True),
    Column('tenant_uuid', String(40)),
    Column('expiry', DateTime),
    Column('created_at', DateTime),
    Column('updated_at', DateTime),
    Column('created_by', String(40)),
    Column('updated_by', String(40))
)

def upgrade(migrate_engine):
    meta.bind = migrate_engine
    tenant_lease.create()
    vm_lease.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    vm_lease.drop()
    tenant_lease.drop()
