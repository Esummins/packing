#!/usr/bin/env bash
# A249 driver: bash attempts/A249-type-t-chase/code/run249.sh test|chase|wall|ring2|ring|pocket|summary|pages|ladder
# ONE python at a time (BelowNormal + affinity 0xFFFF set inside the scripts); logs/STOP is honoured
# between stages and inside the ladders (per-side checkpoints in results/twotilted249_<mode>.json:
# a rerun skips the sides already done -- the resume block).
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
ATT="$(cd "$HERE/.." && pwd)"
export PYTHONDONTWRITEBYTECODE=1
mkdir -p "$ATT/logs" "$ATT/results"
stage="${1:-ladder}"
stop() { [ -f "$ATT/logs/STOP" ] && { echo "STOP present"; exit 0; }; return 0; }
case "$stage" in
  test)     python "$HERE/test249.py" ;;
  chase)    python "$HERE/chase249.py" ;;
  wall)     python "$HERE/twotilted249.py" --mode wall --sides "${2:-3.82,3.877084}" --restarts "${3:-30}" ;;
  ring2)    python "$HERE/twotilted249.py" --mode ring2 --sides "${2:-3.6,3.7,3.82,3.85,3.877084,3.90,4.0}" --restarts "${3:-30}" ;;
  ring)     python "$HERE/twotilted249.py" --mode ring --sides "${2:-3.82,3.877084}" --restarts "${3:-20}" ;;
  pocket)   python "$HERE/pocket249.py" --restarts "${2:-200}" ;;
  summary)  python "$HERE/summarise249.py" ;;
  pages)    python "$HERE/pages249.py" ;;
  ladder)   stop; bash "$0" wall; stop; bash "$0" ring2; stop; bash "$0" ring; stop; bash "$0" pocket ;;
  *) echo "usage: run249.sh test|chase|wall [sides restarts]|ring2 [..]|ring [..]|pocket [restarts]|summary|pages|ladder"; exit 1 ;;
esac
