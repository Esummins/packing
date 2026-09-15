#!/bin/bash
# A228 -- the verdict-agreement check on two CLOSED pages with the PATCHED A221 pocket path (A221's own `closed`
# lane, re-pointed at A228's results so A221's bench file is not written).  Waits for the reproduction's python to
# exit first, so the attempt never runs more than ONE python of its own.
#   bash verify228.sh [<pid to wait for>]
cd "$(dirname "$0")/../../.." || exit 1
A=attempts/A228-segfault; C=attempts/A211-coarse-tree/certs; B=attempts/A221-lane-cover/code
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
LOG=$A/logs/verify228.log; OUT=$A/results/verify228.jsonl
W=${1:-}
if [ -n "$W" ]; then
  echo "$(date '+%H:%M:%S') waiting for pid $W" >> $LOG
  while kill -0 "$W" 2>/dev/null; do sleep 60; done
fi
for PAGE in k5_16_interior_Y0500 k5_16_interior_Y0460; do
  echo "$(date '+%H:%M:%S') === closed lane $PAGE ===" >> $LOG
  python -u $B/bench221.py --cert "$C/coarsetree211_${PAGE}.json" --run g1_page --verdict any \
      --cap 180 --pk-deadline 45 --tag a228closed --out "$OUT" >> $LOG 2>&1
  echo "$(date '+%H:%M:%S') rc=$? $PAGE" >> $LOG
done
echo "$(date '+%H:%M:%S') VERIFY DONE" >> $LOG
