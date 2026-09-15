#!/bin/bash
# A224 benchmark -- ONE python at a time, BelowNormal + affinity 0xFFFF (set inside each runner), BLAS pinned,
# PYTHONDONTWRITEBYTECODE=1, an ISOLATED cert dir and results file (A211's certs are read ONLY, by INHERIT), --no-fig,
# and RESUMABLE: every step writes a stamp in logs/done/ and is skipped on a re-run.  The running run211 / run212
# workers are never touched.
#     bash attempts/A224-snap-rule/code/bench224.sh [wall]
# Resume after a kill: re-run the same line; delete a stamp in attempts/A224-snap-rule/logs/done/ to force a step.
cd "$(dirname "$0")/../../.." || exit 1
A=attempts/A224-snap-rule
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
WALL=${1:-420}
mkdir -p $A/logs/done $A/results/certs_on $A/results/certs_off
LOG=$A/logs/bench224.log
stamp() { [ -f "$A/logs/done/$1" ]; }
mark() { touch "$A/logs/done/$1"; }
labcount() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -notmatch 'Claude Extensions' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
gate() { while [ "$(labcount)" -ge 9 ]; do sleep 60; done; }

echo "$(date '+%F %T') == A224 bench start (wall $WALL s per run)" | tee -a $LOG

# ---------------------------------------------------------------- phase A: the OFFLINE scan over every A211 page
if ! stamp scan_all; then
  gate
  echo "$(date '+%F %T') -- phase A: snapscan224 over every A211 certificate (g1)" | tee -a $LOG
  A224_SNAP=1 python $A/code/snapscan224.py ALL --run g1_page --out $A/results/snapscan224.jsonl >> $LOG 2>&1 && mark scan_all
fi

# ---------------------------------------------------------------- phase B: the live A/B on the brief's pages
run_one() {  # <nid> <on|off> <extra args>
  local NID=$1 MODE=$2; shift 2
  stamp "live_${NID}_${MODE}" && return 0
  gate
  local CD=$A/results/certs_$MODE
  echo "$(date '+%F %T') -- live $NID SNAP=$MODE wall $WALL $*" | tee -a $LOG
  local T0=$(date +%s)
  if [ "$MODE" = "on" ]; then export A224_SNAP=1; else unset A224_SNAP; fi
  timeout -s KILL $(( 2 * WALL + 900 )) python attempts/A211-coarse-tree/code/run211.py page "$NID" \
      --pads g1 --wall $WALL --no-fig --cert-dir $CD --results $A/results/bench224.jsonl "$@" >> $A/logs/live_${NID}_${MODE}.log 2>&1
  echo "$(date '+%F %T')    $NID $MODE rc=$? $(( $(date +%s) - T0 ))s" | tee -a $LOG
  mark "live_${NID}_${MODE}"
}

for NID in k5_16_interior_Y0865 k5_16_interior_Y0402 k5_11_interior_Y0738 k5_16_interior_Y1056; do
  run_one "$NID" on
  run_one "$NID" off
done
run_one k5_16_interior_Y0500 on --no-inherit
run_one k5_16_interior_Y0500 off --no-inherit

A224_SNAP=1 python $A/code/report224.py >> $LOG 2>&1
echo "$(date '+%F %T') == A224 bench done" | tee -a $LOG
