#!/bin/bash
# A227 chain -- ONE python at a time (BelowNormal + affinity 0xFFFF inside each runner), PYTHONDONTWRITEBYTECODE=1,
# an ISOLATED cert dir and results file (A211's certs are READ only), --no-fig, RESUMABLE (phase stamps in
# logs/done/, the scan skips nodes already in its jsonl).  The running run211 / run212 workers are never touched.
#     bash attempts/A227-lemma-eps/code/bench227.sh [wall]        # resume: re-run the same line
# Phase A: the offline replay of Rule EPS over every A211 g1 certificate.  Phase B: the live wiring (patched copies
# of tree211/leaves211 = integration227.diff) on Y0402 g1 and on the CLOSED page Y0865 g1.  Phase C: the report,
# committed with explicit pathspecs.
cd "$(dirname "$0")/../../.." || exit 1
A=attempts/A227-lemma-eps
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export A227_EPS=1
WALL=${1:-420}
mkdir -p $A/logs/done $A/results/certs_on
LOG=$A/logs/bench227.log
stamp() { [ -f "$A/logs/done/$1" ]; }
mark() { touch "$A/logs/done/$1"; }
labcount() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -notmatch 'Claude Extensions' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
gate() { while [ "$(labcount)" -ge 9 ]; do sleep 60; done; }

echo "$(date '+%F %T') == A227 chain start (wall $WALL s per live run)" | tee -a $LOG

if ! stamp scan_all; then
  gate
  echo "$(date '+%F %T') -- phase A: epsscan227 over every A211 certificate (g1)" | tee -a $LOG
  python $A/code/epsscan227.py ALL --run g1_page --out $A/results/eps227.jsonl >> $LOG 2>&1 && mark scan_all
fi

run_one() {  # <nid> <extra args>
  local NID=$1; shift
  stamp "live_${NID}" && return 0
  gate
  echo "$(date '+%F %T') -- live $NID EPS=on wall $WALL $*" | tee -a $LOG
  local T0=$(date +%s)
  timeout -s KILL $(( 2 * WALL + 900 )) python $A/code/bench227.py page "$NID" \
      --pads g1 --wall $WALL --no-fig --cert-dir $A/results/certs_on --results $A/results/bench227.jsonl "$@" >> $A/logs/live_${NID}.log 2>&1
  echo "$(date '+%F %T')    $NID rc=$? $(( $(date +%s) - T0 ))s" | tee -a $LOG
  mark "live_${NID}"
}

run_one k5_16_interior_Y0402
run_one k5_16_interior_Y0865

python $A/code/report227.py >> $LOG 2>&1
git add -- $A/results/eps227.md $A/results/eps227.jsonl $A/results/bench227.jsonl $A/logs/bench227.log 2>/dev/null
git commit -q -m "A227: Rule EPS replay + live benchmark results (detached chain)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- $A/results/eps227.md $A/results/eps227.jsonl $A/results/bench227.jsonl $A/logs/bench227.log >> $LOG 2>&1
echo "$(date '+%F %T') == A227 chain done" | tee -a $LOG
