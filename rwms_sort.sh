#!/usr/bin/env bash
SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PYVERSION=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:1])))')
if [ $PYVERSION = 2 ]; then
    python3 "$SCRIPTDIR/rwms_sort.py" "$@"
else
    python "$SCRIPTDIR/rwms_sort.py" "$@"
fi
