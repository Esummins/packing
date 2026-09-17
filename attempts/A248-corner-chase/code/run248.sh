#!/usr/bin/env bash
# A248 driver: bash attempts/A248-corner-chase/code/run248.sh test|chase|external [side]|summary|pages|all
# One python at a time (BelowNormal, affinity 0xFFFF set inside the scripts); logs/STOP is honoured
# by the driver between stages.  Resume: every stage is idempotent and re-runs from scratch (seconds
# to minutes); results are overwritten.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
ATT="$(cd "$HERE/.." && pwd)"
export PYTHONDONTWRITEBYTECODE=1
mkdir -p "$ATT/logs" "$ATT/results"
stage="${1:-all}"
stop() { [ -f "$ATT/logs/STOP" ] && { echo "STOP present"; exit 0; }; return 0; }
case "$stage" in
  test)     python "$HERE/test248.py" ;;
  chase)    python "$HERE/chase248.py" ;;
  twopokers) python "$HERE/twopokers248.py" ;;
  notches)  python "$HERE/notches248.py" --side "${2:-3.877084}" --restarts "${3:-150}" ;;
  external) python "$HERE/external248.py" --side "${2:-3.85}" --restarts "${3:-40}" --pocket "${4:-40}" ;;
  summary)  python "$HERE/summarise248.py" ;;
  pages)    python "$HERE/pages248.py" ;;
  all)      stop; python "$HERE/test248.py"; stop; python "$HERE/chase248.py"; stop
            python "$HERE/external248.py" --side 3.85; stop; python "$HERE/summarise248.py"; python "$HERE/pages248.py" ;;
  *) echo "usage: run248.sh test|chase|twopokers|notches [side restarts]|external [side restarts pocket]|summary|pages|all"; exit 1 ;;
esac
