#!/bin/bash

# Dirty hack for readthedoc and virtualenv (needed for api doc)

cd common && python setup.py install
cd -
cd storage && python setup.py install
cd -
cd poller && python setup.py install
cd -
