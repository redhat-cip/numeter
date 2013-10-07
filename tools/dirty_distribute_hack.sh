#!/bin/bash

for d in poller storage common; do
    pip install -e $d
    (cd $d ; python setup.py install ||true)
done
