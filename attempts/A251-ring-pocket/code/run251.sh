#!/usr/bin/env bash
# A251 driver: bash attempts/A251-ring-pocket/code/run251.sh test|analytic|joint|far|tol|pilot|summary|pages|ladder
# ONE python at a time (BelowNormal + affinity inside the scripts); logs/STOP is honoured between
# stages and inside every ladder (per-side / per-k checkpoints in results/*.json: a rerun skips
# what is done -- the resume block).
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
ATT="$(cd "$HERE/.." && pwd)"
export PYTHONDONTWRITEBYTECODE=1
mkdir -p "$ATT/logs" "$ATT/results"
stage="${1:-ladder}"
SIDES="${SIDES:-3.85,3.877084,3.90,3.95,3.99}"
stop() { [ -f "$ATT/logs/STOP" ] && { echo "STOP present"; exit 0; }; return 0; }
case "$stage" in
  test)     python "$HERE/test251.py" ;;
  analytic) python "$HERE/analytic251.py" ;;
  joint)    python "$HERE/joint251.py" --mode fit --sides "$SIDES" --ks "${2:-1,2,3}" \
                   --rings "${3:-3}" --restarts "${4:-24}" ;;
  far)      python "$HERE/joint251.py" --mode far --sides "$SIDES" --restarts "${2:-24}" ;;
  tol)      python "$HERE/cert251.py" --stage tol --sides "$SIDES" --restarts "${2:-12}" ;;
  pilot)    python "$HERE/cert251.py" --stage pilot --sides "$SIDES" --boxes "${2:-200}" ;;
  summary)  python "$HERE/summarise251.py" ;;
  pages)    python "$HERE/pages251.py" ;;
  ladder)   stop; bash "$0" test; stop; bash "$0" analytic; stop; bash "$0" joint; stop
            bash "$0" far; stop; bash "$0" tol; stop; bash "$0" pilot; stop
            bash "$0" analytic; stop; bash "$0" summary; stop; bash "$0" pages
            echo "LADDER DONE" ;;
  *) echo "usage: run251.sh test|analytic|joint [ks rings restarts]|far|tol|pilot [boxes]|summary|pages|ladder"; exit 1 ;;
esac
