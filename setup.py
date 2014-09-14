
# Dirty hack to build numeter api doc with virtualenv (for readthedoc)
# You should not use this script. It's for readthedocs only while all python
# modules are not merged into one numeter directory

import subprocess
import sys
from os.path import dirname, join
import os

on_readthedocs = os.environ.get('READTHEDOCS', None) == 'True'

if 'install' in sys.argv and on_readthedocs:

    for package in ['common', 'storage', 'poller']:
        pip = join(dirname(sys.executable), 'pip')
        subprocess.call("%s install -U %s" % (pip, package), shell=True)
        subprocess.call("%s install -e %s" % (pip, package), shell=True)
