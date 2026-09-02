#!/bin/bash
# wait for PID $1 to exit, then run the remaining arguments as a command (detached driver)
cd "$(dirname "$0")/.." || exit 1
PID=$1; shift
while tasklist //FI "PID eq $PID" 2>/dev/null | grep -q " $PID "; do sleep 30; done
"$@" >> logs/chain_after.out 2>&1
echo "CHAIN_DONE $*" >> logs/chain_after.out
