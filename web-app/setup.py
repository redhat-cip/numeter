#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# $Id: setup.py,v 0.2.3.4 2013-02-27 09:56:56 gaelL Exp $
#
# Copyright (C) 2010-2013  Gaël Lambert (gaelL) <gael.lambert@enovance.com>
#
# This file is part of numeter
#
# Numeter is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup
from distutils.command.install_data import install_data
from pkgutil import walk_packages
import shutil
import os

import numeter
os.environ['DJANGO_SETTINGS_MODULE'] = 'numeter.web_app.numeter.settings'


def find_packages(path='.', prefix=""):
    yield prefix
    prefix = prefix + "."
    for _, name, ispkg in walk_packages(path, prefix):
        if ispkg:
            yield name


def fullsplit(path, result=None):
        """
        Split a pathname into components (the opposite of os.path.join)
        in a platform-neutral way.
        """
        if result is None:
            result = []
        head, tail = os.path.split(path)
        if head == '':
            return [tail] + result
        if head == path:
            return result
        return fullsplit(head, [tail] + result)

packages, package_data = [], {}
for dirpath, dirnames, filenames in os.walk('numeter'):
    # Ignore PEP 3147 cache dirs and those whose names start with '.'
    dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != '__pycache__']
    parts = fullsplit(dirpath)
    package_name = '.'.join(parts)
    if '__init__.py' in filenames:
        packages.append(package_name)
    elif filenames:
        relative_path = []
        while '.'.join(parts) not in packages:
            relative_path.append(parts.pop())
            relative_path.reverse()
            path = os.path.join(*relative_path)
            package_files = package_data.setdefault('.'.join(parts), [])
            package_files.extend([os.path.join(path, f) for f in filenames])


class my_install(install_data):
    def run(self):
        install_data.run(self)
        for script in self.get_outputs():
            # Rename name.init in name
            if script.endswith(".init"):
                shutil.move(script, script[:-5])

if __name__ == '__main__':

    setup(
          name='numeter-webapp',
          cmdclass={"install_data": my_install},
          version='0.2.3.10',
          description='Numeter Webapp',
          long_description="""Numeter is a new graphing solution (like Cacti for \
          example) made by some guys working at eNovance. Poller and collector are \
          written in Python and datas are stored in a Redis DB.
          Documentation is available here: https://numeter.readthedocs.org""",
          author='Anthony MONTHE (ZuluPro)',
          author_email='anthony.monthe@enovance.com',
          maintainer='Anthony MONTHE (ZuluPro)',
          maintainer_email='anthony.monthe@enovance.com',
          keywords=['numeter','webapp','django'],
          url='https://github.com/enovance/numeter',
          license='GNU Affero General Public License v3',
          include_package_data=True,
          # package_dir = {'numeter': 'src'},
          package_data = package_data,
          packages = packages,
          data_files = [
            ('/etc/numeter', ['numeter_webapp.cfg']),
          ],
          classifiers=[
              'Development Status :: 4 - Beta',
              'Environment :: Console',
              'Intended Audience :: Advanced End Users',
              'Intended Audience :: System Administrators',
              'License :: OSI Approved :: GNU Affero General Public License v3',
              'Operating System :: POSIX',
              'Programming Language :: Python',
              'Topic :: System :: Monitoring'

          ],
         )
