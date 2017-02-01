#!/usr/bin/env python
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
from setuptools import setup

setup(name='mors',
      version='0.1',
      description='Platform9 Mors (lease manager)',
      author='Platform9',
      author_email='opensource@platform9.com',
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
          'requests==2.13',
          'nose',
          'proboscis'
      ],
      scripts=['mors/pf9_mors.py', 'mors/mors_manage.py']
      )
