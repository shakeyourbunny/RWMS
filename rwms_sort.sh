#!/bin/bash

PYVERSION=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:1])))')
if [ $PYVERSION = 2 ]; then
    python3 rwms_sort.py
else
    python rwms_sort.py
fi