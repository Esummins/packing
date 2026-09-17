#!/usr/bin/env bash
# A253 driver: bash attempts/A253-min-tilt/code/run253.sh test|limit|curve|room|bisect|minimax|exact|oneparam|summary|pages|ladder
# At most TWO pythons (BelowNormal + affinity 0xFFFF are set inside the scripts).  Every stage is
# RESUMABLE: rows are keyed in results/*.jsonl and a rerun skips what is done.  logs/STOP is
# honoured between stages and inside every loop -- `touch attempts/A253-min-tilt/logs/STOP` stops
# the ladder cleanly; delete it and rerun the same command to resume.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
ATT="$(cd "$HERE/.." && pwd)"
ROOT="$(cd "$ATT/../.." && pwd)"
SELF="$HERE/run253.sh"
export PYTHONDONTWRITEBYTECODE=1
mkdir -p "$ATT/logs" "$ATT/results"
stage="${1:-ladder}"
SIDES="${SIDES:-3.82,3.85,3.877084,3.92,3.95,3.99}"
CTAUS="${CTAUS:-14.545,8,4,2,1,0.5,0.25,0.1}"   # the curve ladder (theta_min)
RTAUS="${RTAUS:-26,22,18,14.545,10,6,4,2,1}"      # the room ladder (capacity vs tilt)
SIG="${SIG:-00110011}"
stop() { [ -f "$ATT/logs/STOP" ] && { echo "STOP present"; exit 0; }; return 0; }
PATHS="attempts/A253-min-tilt/results attempts/A253-min-tilt/logs docs/residue_map/campaigns/A253-min-tilt"
shard() {  # commit the stage's rows, explicit pathspecs only (retried: the two lanes share the index)
 ( cd "$ROOT"
  for k in 1 2 3 4 5; do
    if git add -- $PATHS >/dev/null 2>&1 && \
       git commit -q -m "A253: $1 rows" -- $PATHS >/dev/null 2>&1; then exit 0; fi
    sleep 7
  done ) || true
  return 0
}
case "$stage" in
  test)     python "$HERE/test253.py" ;;
  limit)    python "$HERE/limit253.py" --sides "$SIDES,3.999" ;;
  curve)    python "$HERE/mintilt253.py" --mode curve --force-sigmas "$SIG" --sides "$SIDES" \
                   --taus "$CTAUS" --maxiter "${2:-900}" --tries 1 ;;
  room)     python "$HERE/room253.py" --mode tiltsweep --sides "$SIDES" --taus "$RTAUS" --restarts 4 ;;
  bisect)   python "$HERE/mintilt253.py" --mode bisect --force-sigmas "$SIG" --sides "$SIDES" \
                   --lo "${2:-0.05}" --hi "${3:-20.0}" --iters "${4:-10}" --maxiter 900 --tries 1 ;;
  minimax)  python "$HERE/mintilt253.py" --mode minimax --force-sigmas "$SIG" --sides "$SIDES" \
                   --starts "${2:-6}" --maxiter 2500 ;;
  exact)    python "$HERE/cert253.py" --mode exact ;;
  oneparam) python "$HERE/cert253.py" --mode oneparam --boxes "${2:-12}" --taus "${3:-14.545,6,2}" ;;
  summary)  python "$HERE/summarise253.py" ;;
  pages)    python "$HERE/pages253.py" ;;
  ladder)   stop; bash "$SELF" limit;    shard limit;    stop
            bash "$SELF" curve;    shard curve;    stop
            bash "$SELF" summary;  bash "$SELF" pages; shard "summary + pages"; stop
            bash "$SELF" bisect;   shard bisect;   stop
            bash "$SELF" exact;    shard exact;    stop
            bash "$SELF" oneparam; shard oneparam; stop
            bash "$SELF" minimax;  shard minimax;  stop
            bash "$SELF" summary;  bash "$SELF" pages; shard "summary + pages"
            echo "LADDER DONE" ;;
  roomlane) stop; bash "$SELF" room; shard room; bash "$SELF" summary; bash "$SELF" pages
            shard "room summary + pages"; echo "ROOMLANE DONE" ;;
  *) echo "usage: run253.sh test|limit|curve|room|bisect|minimax|exact|oneparam|summary|pages|ladder|roomlane"; exit 1 ;;
esac
