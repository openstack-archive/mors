# Copyright Platform9 Systems Inc. 2016

from sqlalchemy.pool import QueuePool
from sqlalchemy import create_engine, text
from sqlalchemy import Table, Column, Integer, String, MetaData, DateTime
import logging, functools

logger = logging.getLogger(__name__)


def db_connect(transaction=False):
    """
    Generates a decorator that get connection from a pool and returns
    it to the pool when the internal function is done
    :param transaction bool: should this function create and end transaction.
    """

    def _db_connect(fun):
        if hasattr(fun, '__name__'):
            fun.__name__ = 'method_decorator(%s)' % fun.__name__
        else:
            fun.__name__ = 'method_decorator(%s)' % fun.__class__.__name__

        @functools.wraps(fun)
        def newfun(self, *args, **kwargs):
            conn = self.engine.connect()
            if transaction:
                trans = conn.begin()
            try:
                ret = fun(self, conn, *args, **kwargs)
                if transaction:
                    trans.commit()
                return ret
            except Exception as e:
                if transaction:
                    trans.rollback()
                logger.exception("Error during transaction ")
                raise
            finally:
                conn.close()

        return newfun

    return _db_connect


class DbPersistence:
    def __init__(self, db_conn_string):
        self.engine = create_engine(db_conn_string, poolclass=QueuePool)
        self.metadata = MetaData(bind=self.engine)
        self.tenant_lease = Table('tenant_lease', self.metadata, autoload=True)
        self.instance_lease = Table('instance_lease', self.metadata, autoload=True)

    @db_connect(transaction=False)
    def get_all_tenant_leases(self, conn):
        return conn.execute(self.tenant_lease.select()).fetchall()

    @db_connect(transaction=False)
    def get_tenant_lease(self, conn, tenant_uuid):
        return conn.execute(self.tenant_lease.select(self.tenant_lease.c.tenant_uuid == tenant_uuid)).first()

    @db_connect(transaction=True)
    def add_tenant_lease(self, conn, tenant_uuid, expiry_mins, created_by, created_at):
        logger.debug("Adding tenant lease %s %d %s %s", tenant_uuid, expiry_mins, str(created_at), created_by)
        conn.execute(self.tenant_lease.insert(), tenant_uuid=tenant_uuid, expiry_mins=expiry_mins,
                     created_at=created_at, created_by=created_by)

    @db_connect(transaction=True)
    def update_tenant_lease(self, conn, tenant_uuid, expiry_mins, updated_by, updated_at):
        logger.debug("Updating tenant lease %s %d %s %s", tenant_uuid, expiry_mins, str(updated_at), updated_by)
        conn.execute(self.tenant_lease.update().\
                            where(self.tenant_lease.c.tenant_uuid == tenant_uuid).\
                                    values(expiry_mins=expiry_mins,
                                           updated_at=updated_at, updated_by=updated_by))

    @db_connect(transaction=True)
    def delete_tenant_lease(self, conn, tenant_uuid):
        # Should we just soft delete ?
        logger.debug("Deleting tenant lease %s", tenant_uuid)
        conn.execute(self.tenant_lease.delete().where(tenant_uuid == tenant_uuid))
        conn.execute(self.instance_lease.delete().where(tenant_uuid == tenant_uuid))

    @db_connect(transaction=False)
    def get_instance_leases_by_tenant(self, conn, tenant_uuid):
        return conn.execute(self.instance_lease.select(\
                self.instance_lease.c.tenant_uuid == tenant_uuid)).fetchall()
 
    @db_connect(transaction=False)
    def get_instance_lease(self, conn, instance_uuid):
        return conn.execute(self.instance_lease.select((\
                        self.instance_lease.c.instance_uuid == instance_uuid))).first()

    @db_connect(transaction=True)
    def add_instance_lease(self, conn, instance_uuid, tenant_uuid, expiry, created_by, created_at):
        logger.debug("Adding instance lease %s %s %s %s", instance_uuid, tenant_uuid, expiry, created_by)
        conn.execute(self.instance_lease.insert(), instance_uuid=instance_uuid, tenant_uuid=tenant_uuid,
                     expiry=expiry,
                     created_at=created_at, created_by=created_by)

    @db_connect(transaction=True)
    def update_instance_lease(self, conn, instance_uuid, tenant_uuid, expiry, updated_by, updated_at):
        logger.debug("Updating instance lease %s %s %s %s", instance_uuid, tenant_uuid, expiry, updated_by)
        conn.execute(self.instance_lease.update(instance_uuid == instance_uuid), tenant_uuid=tenant_uuid,
                     expiry=expiry,
                     updated_at=updated_at, updated_by=updated_by)

    @db_connect(transaction=True)
    def delete_instance_leases(self, conn, instance_uuids):
        # Delete 10 at a time, should we soft delete
        logger.debug("Deleting instance leases %s", str(instance_uuids))
        conn.execute(self.instance_lease.delete().where(self.instance_lease.c.instance_uuid.in_(instance_uuids)))
