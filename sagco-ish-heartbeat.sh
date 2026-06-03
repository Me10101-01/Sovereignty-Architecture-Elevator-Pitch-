#!/bin/sh
STAMP="$(date +%Y%m%d_%H%M%S)"
HOST="$(hostname 2>/dev/null || echo ish)"
PWD_NOW="$(pwd)"
if [ -f Cargo.toml ]; then
    CARGO=YES
else
    CARGO=NO
fi
echo "STATUS=SAGCO_ISH_HEARTBEAT"
echo "TIME=$STAMP"
echo "HOST=$HOST"
echo "PWD=$PWD_NOW"
echo "CARGO=$CARGO"
