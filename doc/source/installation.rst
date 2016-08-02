============
Installation
============

From PyPi
~~~~~~~~~~~~~~~~~~~~~
At the command line::

    $ pip install mors

Or, if you have virtualenvwrapper installed::

    $ mkvirtualenv mors
    $ pip install mors


RPM BUILD
~~~~~~~~~~~~~~~~~~~~~

Mors comes with an RPM installation and associated init.d scripts. Run the makefile under 'support' directory
and it will produce RPM under the build directory.

Support subdirectory contains Makefile to build a RPM, apart from python
2.7, virtualenv it needs `fpm`_, *fpm* is a simple package build utility
that can build both RPM and deb packages. RPM itself is a thin wrapper
on top of the virtualenv.

Configuration files are expected to be in /etc/pf9 directory. These are
usual OpenStack style config files: \* pf9-mors.ini: configure the nova
section with the user/password that can be used by mors to perform
delete operations on nova instances. The user needs to be an
administrator. \* pf9-mors-api-paste.ini: configure the keystone
middleware with keystone auth tokens.

The packages comes with an init script that works on RHEL 7 compatible
systems

.. _fpm: https://github.com/jordansissel/fpm
