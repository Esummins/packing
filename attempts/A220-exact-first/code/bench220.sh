#!/bin/bash
# A220 benchmark lane -- runs the (config, page) jobs of ONE plan file in sequence, detached, one python at a time.
# Each job writes its OWN certificate dir and result row, so nothing of A211's live state is touched and the 6 running
# run211/run212 workers are never disturbed (the lab gate below waits while the lab is full).
#   nohup bash attempts/A220-exact-first/code/bench220.sh <lane> <plan file> > attempts/A220-exact-first/logs/lane_<lane>.out 2>&1 &
# RESUME: the same command -- a job whose marker results/done/<tag>__<nid> exists is skipped (delete the marker to redo
# one job; the per-job log is logs/<tag>__<nid>.log).  Plan line: <tag>|<nid>|inh|noinh|<wall>|<code dir>|<VAR=v ...>
cd "$(dirname "$0")/../../.." || exit 1
A220=attempts/A220-exact-first
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
LANE=${1:-a}; PLAN=${2:?plan file}
labcount() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -notmatch 'Claude Extensions' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
mkdir -p $A220/results/done $A220/results/rows $A220/results/certs $A220/logs
echo "$(date '+%F %T') [lane $LANE] plan $PLAN" | tee -a $A220/logs/bench220.log
while IFS='|' read -r TAG NID INH WALL CODE ENVS; do
  TAG=${TAG//$'\r'/}; NID=${NID//$'\r'/}; INH=${INH//$'\r'/}; WALL=${WALL//$'\r'/}; CODE=${CODE//$'\r'/}; ENVS=${ENVS//$'\r'/}
  [ -z "$TAG" ] && continue
  case "$TAG" in \#*) continue;; esac
  MARK=$A220/results/done/${TAG}__${NID}
  [ -f "$MARK" ] && { echo "$(date +%T) [lane $LANE] $TAG $NID: done (marker)"; continue; }
  [ -f $A220/logs/STOP ] && { echo "$(date +%T) [lane $LANE] STOP present: exiting"; exit 0; }
  while [ "$(labcount)" -ge 9 ]; do sleep 60; done
  LOG=$A220/logs/${TAG}__${NID}.log
  CD=$A220/results/certs/$TAG
  mkdir -p "$CD"
  EXTRA=""; [ "$INH" = "noinh" ] && EXTRA="--no-inherit"
  T0=$(date +%s)
  echo "$(date +%T) [lane $LANE] START $TAG $NID ($INH, wall $WALL, code $CODE, env: $ENVS)" | tee -a $LOG $A220/logs/bench220.log
  ( export $ENVS; timeout -s KILL $((WALL + 900)) python $CODE/run211.py page "$NID" --pads g1 --wall "$WALL" $EXTRA --no-fig \
      --cert-dir "$CD" --results $A220/results/rows/${TAG}.jsonl >> $LOG 2>&1 )
  RC=$?
  SEC=$(( $(date +%s) - T0 ))
  echo "$TAG $NID rc=$RC ${SEC}s $(date '+%F %T')" > "$MARK"
  echo "$(date +%T) [lane $LANE] DONE  $TAG $NID rc=$RC ${SEC}s" | tee -a $LOG $A220/logs/bench220.log
  python $A220/code/analyze220.py --quiet >> $A220/logs/analyze220.log 2>&1
  for i in 1 2 3; do
    git add -- $A220/results $A220/logs 2>/dev/null
    git commit -q -m "A220: bench $TAG $NID rc=$RC ${SEC}s" -- $A220/results $A220/logs 2>/dev/null && break
    sleep $((5*i))
  done
done < "$PLAN"
echo "$(date '+%F %T') [lane $LANE] plan $PLAN done" | tee -a $A220/logs/bench220.log
