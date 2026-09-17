#!/usr/bin/env bash
# A247 -- the perimeter walk.  At most TWO pythons at a time (BelowNormal, affinity 0xFFFF).
#   bash attempts/A247-perimeter-walk/code/run247.sh test        # self-tests + the known pairs (~3 min)
#   bash attempts/A247-perimeter-walk/code/run247.sh catalogue   # task 1 -> results/catalogue247.{md,jsonl} (~1 min)
#   bash attempts/A247-perimeter-walk/code/run247.sh pairs ETA   # task 2's pair table on the window (resumable; detach it)
#   bash attempts/A247-perimeter-walk/code/run247.sh walks ETA   # task 2 -> results/walks247_window_ETA.jsonl
#   bash attempts/A247-perimeter-walk/code/run247.sh triples ETA # task 3 -> results/triples247_window_ETA.jsonl (resumable)
#   bash attempts/A247-perimeter-walk/code/run247.sh pages       # the SVG pages
# stop: touch attempts/A247-perimeter-walk/logs/STOP ; resume: rm logs/STOP, rerun the same command
set -u
export PYTHONDONTWRITEBYTECODE=1
PY="${PYTHON:-C:/Users/esumm/AppData/Local/Python/bin/python.exe}"; command -v "$PY" >/dev/null 2>&1 || PY=python
HERE="$(cd "$(dirname "$0")" && pwd)"
ATT="$(cd "$HERE/.." && pwd)"
mkdir -p "$ATT/logs" "$ATT/results"
ETA="${2:-0.05}"
case "${1:-}" in
  test)      "$PY" "$HERE/test247.py" --eta "$ETA" ;;
  catalogue) "$PY" "$HERE/catalogue247.py" ;;
  pairs)     [ -f "$ATT/logs/STOP" ] && { echo "STOP present"; exit 0; }
             "$PY" "$HERE/pairs247.py" --range window --eta "$ETA" --budget 2000000 ;;
  walks)     "$PY" "$HERE/walks247.py" --pairs "results/pairs247_window_$ETA.jsonl" ;;
  triples)   [ -f "$ATT/logs/STOP" ] && { echo "STOP present"; exit 0; }
             "$PY" "$HERE/triples247.py" --eta "$ETA" ;;
  pages)     "$PY" "$HERE/pages247.py" ;;
  *) echo "usage: run247.sh test|catalogue|pairs|walks|triples|pages [ETA]"; exit 1 ;;
esac
