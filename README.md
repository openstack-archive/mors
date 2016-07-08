# Mors - OpenStack Lease Manager

![Mors](https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcRIzc5fgaiZfJnbym_ZEx4CsZJ7qIiYjcrxth5hi80Q0IhfnxOg)
https://en.wikipedia.org/wiki/Mors_(mythology) 
is a simple lease manager for OpenStack objects like Instances.

Mors is a useful tool for OpenStack based cloud used for dev, test or lab setups.
Typical usage in these scenarios include automatically or manual creation of Instances for demo, test or experiments.
In most cases these Instances are forgotten and never deleted eating up valuable resources.

Mors is a simple service that helps enforce a policy per Tenant or Instance and automatically delete Instances after
a specified duration.


## Details

Mors works by specification of lease policy in a hierarchical fashion, first at a Tenant level and further at
individual Instance level.

### Tenant Lease Policy

Mors lease policy can be enabled or disabled at Tenant level. If Mors policy is disabled (default for each tenant)
no lease policies apply to the instances within that tenant.

At Tenant level, policy is specified in terms of _duration_ . Once Mors policy is enabled, any Instance will be deleted
after `instance.created_time + tenant.lease duration = instance_expiration`

#### Roles
Tenant leases can be viewed by user with 'member' role and modified by users with 'admin' role

### Instance Lease Policy

By default Instance leases are governed by the policies at Instance's Tenant level. As mentioned earlier:
 `instance.created_time + tenant.lease duration = instance_expiration`

A member of tenant can change the Instance expiry at any time, but it can never be later than now + tenant.lease duration

 `max instance lease <= now + tenant.lease duration`
 
A user can always come back at a later point of time and renew the release again.

#### Roles
Instance leases can be modified by both 'member' and 'admin' roles.

## Build & Installation
Support subdirectory contains Makefile to build a RPM, apart from python 2.7, virtualenv it needs [fpm](https://github.com/jordansissel/fpm), _fpm_
is a simple package build utility that can build both RPM and deb packages. RPM itself is a thin wrapper on top of the virtualenv.

Configuration files are expected to be in /etc/pf9 directory. These are usual OpenStack style config files:
* pf9-mors.ini: configure the nova section with the user/password that can be used by mors to perform delete operations on nova instances.
  The user needs to be an administrator.
* pf9-mors-api-paste.ini: configure the keystone middleware with keystone auth tokens.

The packages comes with an init script that works on RHEL 7 compatible systems

