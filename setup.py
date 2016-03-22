#!/usr/bin/env python

from setuptools import setup

setup(name='pf9-mors',
      version='0.1',
      description='Platform9 Mors (lease manager)',
      author='Roopak Parikh',
      author_email='rparikh@platform9.net',
      url='https://github.com/platform9/pf9-mors',
      packages=['mors',
                'mors/leasehandler',
                'mors_repo',
                'mors_repo/versions'],
      install_requires=[
          'pbr==0.11.0',
          'pytz==2015.7',
          'keystoneauth1==2.3.0',
          'oslo.i18n==3.4.0',
          'oslo.serialization==2.4.0',
          'oslo.utils==3.7.0',
          'keystonemiddleware==4.3.0',
          'Paste==1.7.5.1',
          'PasteDeploy==1.5.2',
          'pip==1.5.2',
          'python-novaclient==3.2.0',
          'flask==0.10.0',
          'SQLAlchemy==0.9.8',
          'sqlalchemy-migrate==0.9.5',
          'PyMySQL',
          'eventlet==0.18.4',
          'nose',
          'proboscis'
      ],
      scripts=['pf9_mors.py', 'mors_manage.py']
      )
