#!/bin/bash
# A209 worker: drain a queue file (one nid per line, optional wall) through run209.py, one node at a time; claims by
# mkdir (atomic) so several workers share a queue; gated before EVERY launch on the lab ceiling (10 pythons excluding
# "Claude Extensions" command lines), on A209's own count (<= 6), and on free memory (>= 3072 MB free physical -- the 6144 MB figure in the ops rules is the per-process COMMIT gate for LPs, not a free-memory floor; corrected by the coordinator 2026-09-12); BLAS pinned; the
# node re-checked against the closure ledgers before it runs (a kill folded in meanwhile closes it: Lemma K1); after
# every node: fold209 (the closure ledger), progress209 (results/progress.md, the price and the STOP rule), the page's
# CURRENT copy refreshed, git add / commit with explicit pathspecs.  Exits when logs/STOP exists.
#   bash worker209.sh <queue file> <slot name> [wall]
cd "$(dirname "$0")/../../.." || exit 1
ATT=attempts/A209-k5-killer; RES=$ATT/results; PAGES=docs/residue_map/campaigns/A209-k5killer
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
Q=$1; SLOT=${2:-w}; WALL=${3:-3600}
labcount() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -notmatch 'Claude Extensions' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
mine() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -match 'run209|audit209' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
freemb() { powershell -NoProfile -Command "[int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1024)" | tr -d '\r '; }
mkdir -p $ATT/logs/claims
while read -r NID W; do
  NID=${NID//$'\r'/}; W=${W//$'\r'/}                        # a CRLF queue line (Python on Windows) must not leak a CR into the nid
  [ -z "$NID" ] && continue
  case "$NID" in \#*) continue;; esac
  [ -f $ATT/logs/STOP ] && { echo "$(date +%H:%M:%S) [$SLOT] STOP present: exiting"; exit 0; }
  mkdir "$ATT/logs/claims/$NID" 2>/dev/null || continue
  if python $ATT/code/fold209.py --closed "$NID" >/dev/null 2>&1; then echo "$(date +%H:%M:%S) [$SLOT] $NID already closed (ledger / ancestor): skipped"; continue; fi
  WW=${W:-$WALL}
  while [ "$(labcount)" -ge 10 ] || [ "$(mine)" -ge 6 ] || [ "$(freemb)" -lt 3072 ]; do sleep 60; done
  LOG=$ATT/logs/k5killer209_${NID}.log
  T0=$(date +%s); echo "$(date +%H:%M:%S) [$SLOT] start $NID wall $WW (lab $(labcount), free $(freemb) MB)" | tee -a $LOG
  timeout -s KILL $(( 2 * WW + 1800 )) python $ATT/code/run209.py page $NID --wall $WW >> $LOG 2>&1
  RC=$?
  if [ $RC -eq 137 ]; then echo "{\"nid\": \"$NID\", \"run\": \"process\", \"mode\": \"page\", \"pad\": \"g1\", \"verdict\": \"ALIVE\", \"leaf\": \"process wall $(( 2 * WW + 1800 )) s reached (killed): undecided\", \"seconds\": $(( $(date +%s) - T0 )), \"killed\": true, \"when\": \"$(date '+%Y-%m-%d %H:%M:%S')\"}" >> $RES/k5killer209.jsonl; fi
  python $ATT/code/fold209.py >> $ATT/logs/fold209.log 2>&1
  python $ATT/code/progress209.py >> $ATT/logs/progress209.log 2>&1
  python docs/residue_map/refresh_current.py > /dev/null 2>&1
  V=$(grep -o "== $NID: g1 [^|]*| pad0 [^\"]*" $LOG | tail -1)
  for i in 1 2 3 4 5 6; do
    git add -- $RES $ATT/certs $ATT/logs $PAGES docs/residue_map/current 2>/dev/null
    if git commit -q -m "A209: $NID [$V] $(( $(date +%s) - T0 ))s rc=$RC" -- $RES $ATT/certs $ATT/logs $PAGES docs/residue_map/current 2>/dev/null; then break; fi
    sleep $((5*i))
  done
  echo "$(date +%H:%M:%S) [$SLOT] $NID $V rc=$RC $(( $(date +%s) - T0 ))s" | tee -a $LOG
done < "$Q"
echo "$(date +%H:%M:%S) [$SLOT] queue $Q done"
