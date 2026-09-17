#!/usr/bin/env bash
# A247 -- the perimeter walk.  At most TWO pythons at a time (BelowNormal, affinity 0xFFFF).
#   bash attempts/A247-perimeter-walk/code/run247.sh test            # self-tests + known pairs
#   bash attempts/A247-perimeter-walk/code/run247.sh catalogue       # monotone + exact catalogues -> results/catalogue247*.{md,jsonl}
#   bash attempts/A247-perimeter-walk/code/run247.sh pairs [ETA AV]  # the exact pair table on the window (resumable; run 2 shards detached)
#   bash attempts/A247-perimeter-walk/code/run247.sh walks [ETA]     # the walk counts / lists from the table (+ lemmas, SLOT-MET, type-F)
#   bash attempts/A247-perimeter-walk/code/run247.sh triples [ETA AV]# triple searches over the type-F list (resumable)
#   bash attempts/A247-perimeter-walk/code/run247.sh pages           # the three SVG pages
#   bash attempts/A247-perimeter-walk/code/run247.sh summary         # results/walk247.md
# stop: touch attempts/A247-perimeter-walk/logs/STOP ; resume: rm logs/STOP, rerun the same command (rows done are skipped)
set -u
export PYTHONDONTWRITEBYTECODE=1
PY="${PYTHON:-C:/Users/esumm/AppData/Local/Python/bin/python.exe}"; command -v "$PY" >/dev/null 2>&1 || PY=python
HERE="$(cd "$(dirname "$0")" && pwd)"
ATT="$(cd "$HERE/.." && pwd)"
mkdir -p "$ATT/logs" "$ATT/results"
ETA="${2:-0.05}"; AV="${3:-0.07}"
T="results/pairs247_window_exact_$ETA.jsonl"
case "${1:-}" in
  test)      "$PY" "$HERE/test247.py" --eta "$ETA" ;;
  catalogue) "$PY" "$HERE/catalogue247.py"; "$PY" "$HERE/catalogue247.py" --exact --eta "$ETA" --eta-avoid "$AV" --bins 6 ;;
  pairs)     [ -f "$ATT/logs/STOP" ] && { echo "STOP present"; exit 0; }
             "$PY" "$HERE/pairs247.py" --range window --eta "$ETA" --eta-avoid "$AV" --exact --budget 200000 --shard "${4:-0/1}" ;;
  walks)     bash "$HERE/counts247.sh" "$T"
             "$PY" "$HERE/walks247.py" --pairs "$T" --slotmet --list-cap 0
             "$PY" "$HERE/walks247.py" --pairs "$T" --type-f --list-cap 1000000
             "$PY" "$HERE/walks247.py" --pairs "$T" --type-f --slotmet --list-cap 1000000 ;;
  triples)   [ -f "$ATT/logs/STOP" ] && { echo "STOP present"; exit 0; }
             "$PY" "$HERE/triples247.py" --three-in-box --eta "$ETA" --eta-avoid "$AV" --budget 300000
             "$PY" "$HERE/triples247.py" --walks "results/walks247_window_exact_${ETA}_typef.jsonl" --max-walks 5000 --eta "$ETA" --eta-avoid "$AV" --budget 200000 ;;
  pages)     "$PY" "$HERE/pages247.py" ;;
  summary)   "$PY" "$HERE/summarise247.py" ;;
  *) echo "usage: run247.sh test|catalogue|pairs|walks|triples|pages|summary [ETA AV [shard]]"; exit 1 ;;
esac
