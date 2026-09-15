#!/bin/bash
# A230 chain -- ONE benchmark python at a time (BelowNormal + affinity 0xFFFF inside run211), PYTHONDONTWRITEBYTECODE=1,
# ISOLATED cert dirs (certs_off / certs_on) and results jsonl -- A211's own certs/ are READ only and the running
# pass-6 workers p6a/p6b/p6c are never touched.  RESUMABLE: re-run the same line; phase stamps in logs/done/, the
# re-scan skips nodes already in its jsonl.
#     bash attempts/A230-eps-branch/code/bench230.sh [wall]
# Phase A: the re-scan of Rule EPS (all candidates + taper) over every A211 g1 certificate.
# Phase B: Y0865 g1 from its A203 root (--no-inherit), pass-6 flags OFF vs ON (A230_EPS=1).
# Phase C: the verdict-agreement check on Y0500 g1, same pair.   Phase D: the report, committed with pathspecs.
cd "$(dirname "$0")/../../.." || exit 1
A=attempts/A230-eps-branch
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
PASS6="A220_NOROOM_INHERIT=1 A221_LANE=1 A224_SNAP=1"          # the pass-6 flag set (A229's BRIEF)
WALL=${1:-900}
mkdir -p $A/logs/done $A/results/certs_off $A/results/certs_on
LOG=$A/logs/bench230.log
stamp() { [ -f "$A/logs/done/$1" ]; }
mark() { touch "$A/logs/done/$1"; }
labcount() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -notmatch 'Claude Extensions' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
gate() { while [ "$(labcount)" -ge 9 ]; do sleep 60; done; }

echo "$(date '+%F %T') == A230 chain start (wall $WALL s per live run)" | tee -a $LOG

if ! stamp scan_all; then
  gate
  echo "$(date '+%F %T') -- phase A: epsscan230 over every A211 certificate (g1)" | tee -a $LOG
  A230_EPS=1 python $A/code/epsscan230.py ALL --run g1_page --out $A/results/eps230.jsonl >> $LOG 2>&1 && mark scan_all
fi

run_one() {  # <nid> <off|on>
  local NID=$1 TAG=$2
  stamp "live_${NID}_${TAG}" && return 0
  gate
  echo "$(date '+%F %T') -- live $NID flags=$TAG wall $WALL" | tee -a $LOG
  local T0=$(date +%s)
  local EPS=""
  [ "$TAG" = "on" ] && EPS="A230_EPS=1"
  env $PASS6 $EPS timeout -s KILL $(( 2 * WALL + 900 )) python attempts/A211-coarse-tree/code/run211.py page "$NID" \
      --pads g1 --wall $WALL --no-fig --no-inherit --force --no-resume \
      --cert-dir $A/results/certs_${TAG} --results $A/results/bench230_${TAG}.jsonl >> $A/logs/live_${NID}_${TAG}.log 2>&1
  echo "$(date '+%F %T')    $NID/$TAG rc=$? $(( $(date +%s) - T0 ))s" | tee -a $LOG
  mark "live_${NID}_${TAG}"
  python $A/code/report230.py >> $LOG 2>&1
}

run_one k5_16_interior_Y0865 off
run_one k5_16_interior_Y0865 on
run_one k5_16_interior_Y0500 off
run_one k5_16_interior_Y0500 on

python $A/code/report230.py >> $LOG 2>&1
git add -- $A/results $A/logs/bench230.log 2>/dev/null
git commit -q -m "A230: Rule EPS re-scan + the off/on benchmark results (detached chain)

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>" -- $A/results $A/logs/bench230.log >> $LOG 2>&1
echo "$(date '+%F %T') == A230 chain done" | tee -a $LOG
