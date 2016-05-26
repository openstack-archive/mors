# Copyright Platform9 Systems Inc. 2016
from sqlalchemy import MetaData, String, Table

def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    table = Table('tenant_lease', meta, autoload=True)

    tenant_leases = list(table.select().execute())
    for tenant_lease in tenant_leases:
        old_val = tenant_lease['expiry_days']
        new_val = old_val*24*60
        table.update().where(
            table.c.expiry_days == old_val).values(
                expiry_days=str(new_val)).execute()

    col = getattr(table.c, 'expiry_days')
    col.alter(name='expiry_mins')

def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    table = Table('tenant_lease', meta, autoload=True)

    tenant_leases = list(table.select().execute())
    for tenant_lease in tenant_leases:
        old_val = tenant_lease['expiry_mins']
        new_val = old_val/(24*60)
        table.update().where(
            table.c.expiry_mins == old_val).values(
                expiry_mins=str(new_val)).execute()

    col = getattr(table.c, 'expiry_mins')
    col.alter(name='expiry_days')

