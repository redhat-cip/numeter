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
import shutil

class my_install(install_data):
    def run(self):
        install_data.run(self)
        for script in self.get_outputs():
            # Rename name.init in name
            if script.endswith(".init"):
                shutil.move(script, script[:-5])

if __name__ == '__main__':

    setup(name='numeter-poller',
          cmdclass={"install_data": my_install},
          version='0.2.3.10',
          description='Numeter Poller',
          long_description="""Numeter is a new graphing solution (like Cacti for \
          example) made by some guys working at eNovance. Poller and collector are \
          written in Python and datas are stored in a Redis DB. The webapp is written in PHP.\
          Documentation is available here: https://numeter.readthedocs.org""",
          author='Gaël Lambert (gaelL)',
          author_email='gael.lambert@enovance.com',
          maintainer='Gaël Lambert (gaelL)',
          maintainer_email='gael.lambert@enovance.com',
          keywords=['numeter','graphing','poller','collector','storage'],
          url='https://github.com/enovance/numeter',
          license='GNU Affero General Public License v3',
          scripts = ['poller/numeter-poller', 'poller/numeter-pollerd'],
          packages = [''],
          package_dir = {'':'poller/module'},
          #package_data={'': ['collector/numeter_collector.py']},
          data_files = [('/etc/numeter', ['poller/numeter_poller.cfg', 'poller/redis-poller.conf']), 
                        ('/var/log/numeter', ''),
                        ('/etc/init.d', ['poller/numeter-poller.init']),
                        ('/etc/init.d', ['poller/numeter-redis-poller.init']),
                        #('/etc/cron.d', ['poller/numeter-poller-cron'])
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
