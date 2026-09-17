#!/usr/bin/env bash
# A245 -- one python at a time (BelowNormal, affinity 0xFFFF inside the scripts).  Resumable: click245
# appends per (rid, wall) and skips rows already present under --resume; `touch logs/STOP` stops it.
#   bash attempts/A245-snap-down/code/run245.sh stack    # Lemma STACK's sampling (fast)
#   bash attempts/A245-snap-down/code/run245.sh click    # the click + reduce on every testbed (detached)
#   bash attempts/A245-snap-down/code/run245.sh test     # the self-tests
#   bash attempts/A245-snap-down/code/run245.sh pages    # summary + pages
# RESUME: rm attempts/A245-snap-down/logs/STOP; bash .../run245.sh click
set -u
cd "$(dirname "$0")/../../.."
export PYTHONDONTWRITEBYTECODE=1
P=attempts/A245-snap-down
case "${1:-test}" in
  stack) python -u $P/code/stack245.py --n 4000 > $P/logs/stack245.log 2>&1 ;;
  click) nohup python -u $P/code/click245.py --steps 20 --resume >> $P/logs/click245.log 2>&1 & ;;
  test)  python $P/code/test245.py ;;
  pages) python $P/code/summarise245.py && python $P/code/pages245.py ;;
esac
