#!/usr/bin/env bash
# A250 -- FAMILY-STUCK.  At most TWO pythons at a time (BelowNormal, affinity 0xFFFF).
#   bash attempts/A250-family-stuck/code/run250.sh test        # self-tests (gradient, kmax=1 == A244, verifier)
#   bash attempts/A250-family-stuck/code/run250.sh laneA       # the descent lane (a244 seeds, then random) -- detached-safe
#   bash attempts/A250-family-stuck/code/run250.sh laneB       # the control (kmax=1) + the residual ladder
#   bash attempts/A250-family-stuck/code/run250.sh count       # the ILP count ladder + the corpus test
#   bash attempts/A250-family-stuck/code/run250.sh pages       # the two SVG pages
#   bash attempts/A250-family-stuck/code/run250.sh summary     # results/family250.md
# stop: touch attempts/A250-family-stuck/logs/STOP ; resume: rm logs/STOP and rerun (rows done are skipped).
# Every lane appends one JSON row per job and commits its own results file with an explicit pathspec.
set -u
export PYTHONDONTWRITEBYTECODE=1
PY="${PYTHON:-C:/Users/esumm/AppData/Local/Python/bin/python.exe}"; command -v "$PY" >/dev/null 2>&1 || PY=python
HERE="$(cd "$(dirname "$0")" && pwd)"
ATT="$(cd "$HERE/.." && pwd)"
mkdir -p "$ATT/logs" "$ATT/results"
stopped() { [ -f "$ATT/logs/STOP" ] && { echo "STOP present"; return 0; } || return 1; }
case "${1:-}" in
  test)   "$PY" "$HERE/fam250.py"; "$PY" "$HERE/fast250.py"; "$PY" "$HERE/test250.py" ;;
  laneA)  stopped && exit 0
          "$PY" "$HERE/search250.py" --tag a244 --mode descent --maxfam 3 --seeds a244 \
                --n 489 --deltas 0.001 --S 4.3 --commit 25
          stopped && exit 0
          "$PY" "$HERE/search250.py" --tag rand --mode descent --maxfam 3 --seeds random \
                --n 700 --deltas 0.001 --S 3.95 --seed 11 --commit 25 ;;
  laneB)  stopped && exit 0
          "$PY" "$HERE/search250.py" --tag ctrl --mode descent --maxfam 1 --seeds a217 \
                --n 40 --deltas 0.001 --S 4.3 --commit 10
          stopped && exit 0
          "$PY" "$HERE/search250.py" --tag res --mode residual --maxfam 3 --seeds random \
                --n 90 --deltas 0.001 --seed 7 --S 4.0 --commit 25 \
                --sides 3.82,3.877084,3.92,3.96,3.999,4.05,4.3,4.6
          stopped && exit 0
          "$PY" "$HERE/search250.py" --tag resb --mode residual --maxfam 3 --seeds border \
                --n 90 --deltas 0.001 --seed 5 --S 4.0 --commit 25 \
                --sides 3.82,3.877084,3.92,3.96,3.999,4.05,4.3,4.6 ;;
  count)  "$PY" "$HERE/count250.py" --what all ;;
  pages)  "$PY" "$HERE/pages250.py" ;;
  summary) "$PY" "$HERE/summarise250.py" ;;
  *) echo "usage: run250.sh test|laneA|laneB|count|pages|summary"; exit 1 ;;
esac
