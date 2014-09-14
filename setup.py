
# Dirty hack for readthedoc and virtualenv (needed for api doc)

import subprocess

subprocess.call("cd common && python setup.py install", shell=True)
subprocess.call("cd storage && python setup.py install", shell=True)
subprocess.call("cd poller && python setup.py install", shell=True)
