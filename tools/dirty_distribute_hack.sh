#!/bin/bash

for d in poller storage common; do
    pip install -e $d
done
