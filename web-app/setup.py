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
import os
import sys
from random import choice


# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files, package_data = [], [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
django_dir = 'numeter_webapp'

for dirpath, dirnames, filenames in os.walk(django_dir):
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[len('numeter_webapp')+1:]
        for f in filenames:
            package_data.append(os.path.join(prefix, f))
# Add non-python files which are in a module
package_data.extend([
    'LICENSE',
])

for dirpath, dirnames, filenames in os.walk('media'):
    _files = [os.path.join(dirpath, f) for f in filenames]
    if _files:
        data_files.append((os.path.join('/var/www/numeter', dirpath), _files))

class my_install(install_data):
    def run(self):
        install_data.run(self)
        # Add secret key
        NEW_SECRET_KEY = ''.join([choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for i in range(50)])
        root = self.root or ''
        with open('%s/etc/numeter/secret_key.txt' % root, 'w') as f:
            f.write(NEW_SECRET_KEY)


if __name__ == '__main__':

    setup(
          name = 'numeter-webapp',
          cmdclass = {"install_data": my_install},
          version = '0.2.3.10',
          description = 'Numeter Webapp',
          long_description = """Numeter is a new graphing solution (like Cacti for \
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
          include_package_data = True,
          packages = packages,
          package_dir = {'numeter_webapp': 'numeter_webapp'},
          package_data = {'numeter_webapp': package_data},
          scripts = ['extras/numeter-webapp'],
          data_files = [
              ('/etc/numeter', ['numeter_webapp.cfg']),
              ('/var/log/numeter/webapp', ''),
          ] + data_files,
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
