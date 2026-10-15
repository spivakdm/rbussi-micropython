#!/bin/bash
set -e
for attempt in {1..100}; do
    if xdpyinfo -display :0 >/dev/null 2>&1; then
        exec "$@"
    fi
    sleep 0.1
done
echo 'The graphical display did not start.' >&2
exit 1
