#!/bin/bash
# A242 -- the crowd-root cascade worker: one band, a chunk of cells at a time, a commit after every chunk.
#
#   nohup bash attempts/A242-crowd-root/code/run242.sh W 300 25 > attempts/A242-crowd-root/logs/run242_W.log 2>&1 &
#
# RESUME BLOCK: cascade242.py appends every decided cell to results/crowd242_<band>.jsonl and rewrites the live
# DFS stack to results/stack242_<band>.json after EVERY cell (atomic replace); a restart of this exact command
# reloads the stack and skips every label already in the jsonl.  `touch attempts/A242-crowd-root/logs/STOP`
# stops it cleanly between chunks.  Exit code 3 from cascade242.py = the stack is EMPTY (the band is closed).
# Never touches the k5 frontier workers, the frontier loop, A238's sweep, A241's campaign or A211's certs.
cd "$(dirname "$0")/../../.." || exit 1
A=attempts/A242-crowd-root
BAND=${1:-W}; WALL=${2:-300}; CHUNK=${3:-25}; DEPTH=${4:-64}
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
mkdir -p $A/logs $A/certs $A/results docs/residue_map/campaigns/A242-crowd-root
PATHS="$A/results $A/logs $A/certs"

commit() {
  local msg="$1" k
  for k in 1 2 3 4; do
    git add -- $PATHS 2>/dev/null
    if git diff --cached --quiet -- $PATHS 2>/dev/null; then return 0; fi
    if git commit -q -m "$msg

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>" -- $PATHS 2>/dev/null; then return 0; fi
    sleep $((5 * k))
  done
  echo "$(date +%H:%M:%S) commit failed (index busy) for: $msg"
}

echo "$(date +%H:%M:%S) A242 cascade band=$BAND wall=${WALL}s/cell chunk=$CHUNK depth<=$DEPTH"
while : ; do
  [ -f $A/logs/STOP ] && { echo "$(date +%H:%M:%S) STOP present: exiting"; commit "A242: cascade $BAND -- stop"; exit 0; }
  python $A/code/cascade242.py --band "$BAND" --cells "$CHUNK" --wall "$WALL" --max-depth "$DEPTH"
  RC=$?
  N=$(grep -c . $A/results/crowd242_$BAND.jsonl 2>/dev/null | tr -d '\r ')
  commit "A242: cascade $BAND -- $N cells decided"
  if [ "$RC" = "3" ]; then echo "$(date +%H:%M:%S) band $BAND CLOSED (stack empty)"; exit 0; fi
  if [ "$RC" != "0" ]; then echo "$(date +%H:%M:%S) cascade exit $RC -- retrying in 30 s"; sleep 30; fi
done
