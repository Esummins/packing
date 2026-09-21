#!/bin/bash
# A256 worker -- A229's worker229.sh over the TRUMP5 population and A256's own directories.
#
#   bash worker256.sh <slot name> <wall> <max own workers> <queue file> [<queue file> ...]
#
# Queue line (queue256.py writes exactly this):   <nid> <pad>:<start label> [<wall>]     # trailing comment ignored
# A bare <start label> without a pad prefix runs BOTH pads, as run211.py's default does.
#
# Gates: the lab ceiling (12 pythons excluding "Claude Extensions"), A256's own count (<= the 3rd argument), free
# memory (>= 3072 MB); BLAS pinned to 1 thread; BelowNormal + affinity 0xFFFF set INSIDE run211.py.  A211's claims,
# logs, certificates, results and pages are NEVER touched: A256 has its own claims dir, its own STOP file, its own
# certs/ (A229_CERT_DIR) and its own results jsonl.  A228: a row for EVERY non-zero exit (a crashed or killed run is
# ALIVE + killed, never a verdict) and the start node is offered again next pass through logs/requeue256.txt.
# Stop: touch attempts/A256-trump5-passes/logs/STOP  (the running shard finishes its start node first).
cd "$(dirname "$0")/../../.." || exit 1
ATT=attempts/A256-trump5-passes; RES=$ATT/results/trump5passes256.jsonl; CODE=$ATT/code
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export A220_NOROOM_INHERIT=1 A221_LANE=1 A224_SNAP=1
export A229_CERT_DIR="$(pwd)/$ATT/certs"
SLOT=${1:-w}; WALL=${2:-1800}; MAXMINE=${3:-3}; shift 3
labcount() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -notmatch 'Claude Extensions' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
mine() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -match 'run256.py' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
freemb() { powershell -NoProfile -Command "[int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1024)" | tr -d '\r '; }
mkdir -p $ATT/logs/claims256 $ATT/certs $ATT/results
for Q in "$@"; do
  while read -r NID START W REST; do
    NID=${NID//$'\r'/}; START=${START//$'\r'/}; W=${W//$'\r'/}
    [ -z "$NID" ] && continue
    case "$NID" in \#*) continue;; esac
    case "$W" in \#*) W="";; esac
    [ -z "$START" ] && { echo "$(date +%H:%M:%S) [$SLOT] $NID: no start node on the queue line -- skipped"; continue; }
    [ -f $ATT/logs/STOP ] && { echo "$(date +%H:%M:%S) [$SLOT] STOP present: exiting"; exit 0; }
    case "$START" in
      zero:*|g1:*) PAD=${START%%:*}; LABEL=${START#*:};;
      *)           PAD="zero";      LABEL=$START;;
    esac
    TAG=$(printf '%s_%s' "${PAD//,/+}" "$LABEL" | tr -c 'A-Za-z0-9._-' '_')
    mkdir "$ATT/logs/claims256/${NID}__${TAG}" 2>/dev/null || continue
    WW=${W:-$WALL}
    while [ "$(labcount)" -ge 12 ] || [ "$(mine)" -ge "$MAXMINE" ] || [ "$(freemb)" -lt 3072 ]; do sleep 60; done
    LOG=$ATT/logs/trump5passes256_${NID}__${TAG}.log
    T0=$(date +%s); echo "$(date +%H:%M:%S) [$SLOT] start $NID pad $PAD node $LABEL wall $WW (lab $(labcount), mine $(mine), free $(freemb) MB)" | tee -a $LOG
    timeout -s KILL $(( 2 * WW + 1200 )) python $CODE/run256.py page "$NID" --pads "$PAD" --wall $WW \
        --start "$LABEL" --cert-suffix "$TAG" >> $LOG 2>&1
    RC=$?
    if [ $RC -ne 0 ]; then
      case $RC in
        137) WHY="process wall $(( 2 * WW + 1200 )) s reached (killed)";;
        139) WHY="CRASHED: SIGSEGV (rc 139) -- see A228";;
        134) WHY="CRASHED: abort (rc 134)";;
        *)   WHY="run256 exited rc=$RC";;
      esac
      echo "{\"nid\": \"$NID\", \"run\": \"process\", \"mode\": \"page\", \"pad\": \"$PAD\", \"shard\": true, \"cert_suffix\": \"$TAG\", \"start_filter\": [\"$LABEL\"], \"verdict\": \"ALIVE\", \"leaf\": \"$WHY: undecided\", \"seconds\": $(( $(date +%s) - T0 )), \"killed\": true, \"rc\": $RC, \"when\": \"$(date '+%Y-%m-%d %H:%M:%S')\"}" >> $RES
      echo "$(date '+%Y-%m-%d %H:%M:%S') [$SLOT] $NID $PAD:$LABEL rc=$RC $WHY" >> $ATT/logs/requeue256.txt
      echo "$NID $PAD:$LABEL $WW" >> $ATT/logs/requeue256.txt
      if [ $RC -ne 137 ]; then rmdir "$ATT/logs/claims256/${NID}__${TAG}" 2>/dev/null; fi
    fi
    python $CODE/progress256.py >> $ATT/logs/progress256.log 2>&1
    V=$(grep -o "== $NID: g1 [^|]*| pad0 [^(]*" $LOG | tail -1)
    for i in 1 2 3 4 5 6; do
      git add -- $ATT/results $ATT/certs $ATT/logs 2>/dev/null
      if git commit -q -m "A256: $NID $PAD:$LABEL [$V] $(( $(date +%s) - T0 ))s rc=$RC" -- $ATT/results $ATT/certs $ATT/logs 2>/dev/null; then break; fi
      sleep $((5*i))
    done
    echo "$(date +%H:%M:%S) [$SLOT] $NID $PAD:$LABEL $V rc=$RC $(( $(date +%s) - T0 ))s" | tee -a $LOG
  done < "$Q"
  echo "$(date +%H:%M:%S) [$SLOT] queue $Q done"
done
