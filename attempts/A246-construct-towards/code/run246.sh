#!/usr/bin/env bash
# A246 -- construct towards a 12-stuck ring.  One python at a time (BelowNormal, affinity 0xFFFF).
#   bash attempts/A246-construct-towards/code/run246.sh test      # self-tests (~2 min)
#   bash attempts/A246-construct-towards/code/run246.sh check     # the corpus run -> results/construct246.{md,jsonl}
#   bash attempts/A246-construct-towards/code/run246.sh slotmet   # SLOT-MET(eta) ladder, resumable (detach it)
#   bash attempts/A246-construct-towards/code/run246.sh pages     # the two SVG pages
# stop:   touch attempts/A246-construct-towards/logs/STOP
# resume: rm attempts/A246-construct-towards/logs/STOP ; bash ... run246.sh slotmet   (each eta resumes from
#         logs/slotmet_<eta>.npz; an eta with results/slotmet246_<eta>.json is skipped)
set -u
export PYTHONDONTWRITEBYTECODE=1
PY="${PYTHON:-C:/Users/esumm/AppData/Local/Python/bin/python.exe}"; command -v "$PY" >/dev/null 2>&1 || PY=python
HERE="$(cd "$(dirname "$0")" && pwd)"
ATT="$(cd "$HERE/.." && pwd)"
mkdir -p "$ATT/logs" "$ATT/results"
case "${1:-}" in
  test)    "$PY" "$HERE/test246.py" ;;
  check)   "$PY" "$HERE/check246.py" --fresh 6 ;;
  slotmet)
    for eta in 0.0001 1e-05 1e-06 1e-07; do
      [ -f "$ATT/logs/STOP" ] && { echo "STOP present"; exit 0; }
      [ -f "$ATT/results/slotmet246_$eta.json" ] && grep -q CERTIFIED "$ATT/results/slotmet246_$eta.json" && continue
      "$PY" "$HERE/slotmet246.py" --eta "$eta" --hmin 1e-5 --budget-min 90 --batch 40000 >> "$ATT/logs/slotmet_ladder.log" 2>&1
    done ;;
  pages)   "$PY" "$HERE/pages246.py" ;;
  *) echo "usage: run246.sh test|check|slotmet|pages"; exit 1 ;;
esac
