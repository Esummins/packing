#!/bin/bash
# A212 worker (A211's worker211 adapted): drain queue files (one nid per line) through run212.py (pad 0 only), one node at a
# time; claims by mkdir (atomic) so several workers share a queue; gated before EVERY launch on the lab ceiling (10 pythons
# excluding "Claude Extensions" command lines), on A212's own count (<= 3) and on free memory (>= 3072 MB physical);
# BLAS pinned; BelowNormal + affinity 0xFFFF set INSIDE run212.py (A210's working fix); the node re-checked against the A60
# closure ledgers (A149 / A137 / A212) before it runs; after every node: the audit of its DEAD leaves (audit212, capped),
# fold212 (the ledger), progress212 (results/progress.md, the price and the STOP rule), git add / commit with explicit
# pathspecs.  Exits when logs/STOP exists.        bash worker212.sh <slot name> <wall> <queue file> [<queue file> ...]
cd "$(dirname "$0")/../../.." || exit 1
ATT=attempts/A212-trump5-tree; RES=$ATT/results; PAGES=docs/residue_map/campaigns/A212-trump5tree
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
SLOT=${1:-w}; WALL=${2:-1800}; shift 2
labcount() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -notmatch 'Claude Extensions' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
mine() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -match 'run212|audit212' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
freemb() { powershell -NoProfile -Command "[int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1024)" | tr -d '\r '; }
mkdir -p $ATT/logs/claims
for Q in "$@"; do
  while read -r NID W; do
    NID=${NID//$'\r'/}; W=${W//$'\r'/}
    [ -z "$NID" ] && continue
    case "$NID" in \#*) continue;; esac
    [ -f $ATT/logs/STOP ] && { echo "$(date +%H:%M:%S) [$SLOT] STOP present: exiting"; exit 0; }
    mkdir "$ATT/logs/claims/$NID" 2>/dev/null || continue
    if python $ATT/code/fold212.py --closed "$NID" >/dev/null 2>&1; then echo "$(date +%H:%M:%S) [$SLOT] $NID already closed (A60 ledger): skipped"; continue; fi
    WW=${W:-$WALL}
    while [ "$(labcount)" -ge 10 ] || [ "$(mine)" -ge 3 ] || [ "$(freemb)" -lt 3072 ]; do sleep 60; done
    LOG=$ATT/logs/trump5tree212_${NID}.log
    T0=$(date +%s); echo "$(date +%H:%M:%S) [$SLOT] start $NID wall $WW (lab $(labcount), free $(freemb) MB)" | tee -a $LOG
    timeout -s KILL $(( 2 * WW + 1200 )) python $ATT/code/run212.py page $NID --wall $WW >> $LOG 2>&1
    RC=$?
    if [ $RC -eq 137 ]; then echo "{\"nid\": \"$NID\", \"run\": \"process\", \"mode\": \"page\", \"pad\": \"zero\", \"verdict\": \"ALIVE\", \"leaf\": \"process wall $(( 2 * WW + 1200 )) s reached (killed by the worker's timeout, labelled): undecided\", \"seconds\": $(( $(date +%s) - T0 )), \"killed\": true, \"when\": \"$(date '+%Y-%m-%d %H:%M:%S')\"}" >> $RES/trump5tree212.jsonl; fi
    # the audit of this node's DEAD leaves (sampling; <= 6 leaves, <= 240 s each)
    python $ATT/code/audit_queue212.py --nid "$NID" 2>/dev/null | tr -d '\r' | head -6 | while read -r ANID KEY LEAF; do
      [ -z "$ANID" ] && continue
      ALOG=$ATT/logs/audit_${ANID}_${KEY}.log
      echo "$(date +%H:%M:%S) audit $ANID $KEY $LEAF" >> $ALOG
      timeout -s KILL 240 python $ATT/code/audit212.py "$ANID" "$KEY" "$LEAF" >> $ALOG 2>&1 && echo "$ANID $KEY $LEAF" >> $ATT/logs/audit_done.txt
    done
    python $ATT/code/fold212.py >> $ATT/logs/fold212.log 2>&1
    python $ATT/code/progress212.py >> $ATT/logs/progress212.log 2>&1
    V=$(grep -o "== $NID: pad0 [^(]*" $LOG | tail -1)
    for i in 1 2 3 4 5 6; do
      git add -- $RES $ATT/certs $ATT/logs $PAGES 2>/dev/null
      if git commit -q -m "A212: $NID [$V] $(( $(date +%s) - T0 ))s rc=$RC" -- $RES $ATT/certs $ATT/logs $PAGES 2>/dev/null; then break; fi
      sleep $((5*i))
    done
    echo "$(date +%H:%M:%S) [$SLOT] $NID $V rc=$RC $(( $(date +%s) - T0 ))s" | tee -a $LOG
  done < "$Q"
  echo "$(date +%H:%M:%S) [$SLOT] queue $Q done"
done
