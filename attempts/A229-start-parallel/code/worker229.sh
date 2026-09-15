#!/bin/bash
# A229 worker -- the A211 worker (worker211.sh) with the queue at START-NODE granularity instead of PAGE granularity.
# A start node is an independent hypothesis (Lemma INHERIT, attempts/A211-coarse-tree/notes/coarse_tree.md s.4), so
# N workers may take N start nodes OF THE SAME PAGE at once; each writes its OWN certificate
# certs/coarsetree211_<nid>__<TAG>.json (never the page certificate, never a sibling's), and inherit211 merges them all
# on the path key afterwards (attempts/A229-start-parallel/notes/parallel229.md).
#
#   bash worker229.sh <slot name> <wall> <queue file> [<queue file> ...]
#
# Queue line (queue229.py writes exactly this):   <nid> <pad>:<start label> [<wall>]     # trailing comment ignored
# A bare <start label> without a pad prefix runs BOTH pads (pad 0 first), as run211.py's default does.
#
# Same gates as worker211.sh: the lab ceiling (10 pythons excluding "Claude Extensions"), A211's own count (<= 6), free
# memory (>= 3072 MB); BLAS pinned; BelowNormal + affinity 0xFFFF set INSIDE run211.py; the node re-checked against the
# closure ledgers before it runs (Lemma K1); after every shard: audit of its DEAD leaves, fold211, progress211, the
# CURRENT pages refreshed, git add / commit with explicit pathspecs.  Exits when logs/STOP exists.
cd "$(dirname "$0")/../../.." || exit 1
ATT=attempts/A211-coarse-tree; RES=$ATT/results; PAGES=docs/residue_map/campaigns/A211-coarsetree; A229=attempts/A229-start-parallel
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
SLOT=${1:-w}; WALL=${2:-1800}; shift 2
labcount() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -notmatch 'Claude Extensions' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
mine() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -match 'run211|audit211' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
freemb() { powershell -NoProfile -Command "[int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1024)" | tr -d '\r '; }
mkdir -p $ATT/logs/claims229 $A229/logs
for Q in "$@"; do
  while read -r NID START W REST; do
    NID=${NID//$'\r'/}; START=${START//$'\r'/}; W=${W//$'\r'/}
    [ -z "$NID" ] && continue
    case "$NID" in \#*) continue;; esac
    case "$W" in \#*) W="";; esac
    [ -z "$START" ] && { echo "$(date +%H:%M:%S) [$SLOT] $NID: no start node on the queue line -- skipped"; continue; }
    [ -f $ATT/logs/STOP ] && { echo "$(date +%H:%M:%S) [$SLOT] STOP present: exiting"; exit 0; }
    # <pad>:<label>, or a bare <label> meaning both pads (pad 0 first, as run211.py defaults)
    case "$START" in
      zero:*|g1:*) PAD=${START%%:*}; LABEL=${START#*:};;
      *)           PAD="zero,g1";   LABEL=$START;;
    esac
    TAG=$(printf '%s_%s' "${PAD//,/+}" "$LABEL" | tr -c 'A-Za-z0-9._-' '_')
    mkdir "$ATT/logs/claims229/${NID}__${TAG}" 2>/dev/null || continue
    if python $ATT/code/fold211.py --closed "$NID" >/dev/null 2>&1; then echo "$(date +%H:%M:%S) [$SLOT] $NID already closed (ledger / ancestor): skipped"; continue; fi
    WW=${W:-$WALL}
    while [ "$(labcount)" -ge 10 ] || [ "$(mine)" -ge 6 ] || [ "$(freemb)" -lt 3072 ]; do sleep 60; done
    LOG=$ATT/logs/coarsetree211_${NID}__${TAG}.log
    T0=$(date +%s); echo "$(date +%H:%M:%S) [$SLOT] start $NID pad $PAD node $LABEL wall $WW (lab $(labcount), free $(freemb) MB)" | tee -a $LOG
    timeout -s KILL $(( 2 * WW + 1200 )) python $ATT/code/run211.py page "$NID" --pads "$PAD" --wall $WW \
        --start "$LABEL" --cert-suffix "$TAG" >> $LOG 2>&1
    RC=$?
    # A228: a row for EVERY non-zero exit (a crashed / killed run is ALIVE + killed, never a verdict; a CRASH releases
    # its claim and is written to logs/requeue229.txt so the start node is offered again next pass).
    if [ $RC -ne 0 ]; then
      case $RC in
        137) WHY="process wall $(( 2 * WW + 1200 )) s reached (killed)";;
        139) WHY="CRASHED: SIGSEGV (rc 139) -- see A228";;
        134) WHY="CRASHED: abort (rc 134)";;
        *)   WHY="run211 exited rc=$RC";;
      esac
      echo "{\"nid\": \"$NID\", \"run\": \"process\", \"mode\": \"page\", \"pad\": \"g1\", \"shard\": true, \"cert_suffix\": \"$TAG\", \"start_filter\": [\"$LABEL\"], \"verdict\": \"ALIVE\", \"leaf\": \"$WHY: undecided\", \"seconds\": $(( $(date +%s) - T0 )), \"killed\": true, \"rc\": $RC, \"when\": \"$(date '+%Y-%m-%d %H:%M:%S')\"}" >> $RES/coarsetree211.jsonl
      echo "$(date '+%Y-%m-%d %H:%M:%S') [$SLOT] $NID $PAD:$LABEL rc=$RC $WHY" >> $A229/logs/requeue229.txt
      echo "$NID $PAD:$LABEL $WW" >> $A229/logs/requeue229.txt
      if [ $RC -ne 137 ]; then rmdir "$ATT/logs/claims229/${NID}__${TAG}" 2>/dev/null; fi
    fi
    # the audit of this shard's DEAD leaves (sampling; <= 6 leaves, <= 240 s each) -- audit211 reads the page's rows
    python $ATT/code/audit_queue211.py --nid "$NID" 2>/dev/null | tr -d '\r' | head -6 | while read -r ANID KEY LEAF; do
      [ -z "$ANID" ] && continue
      ALOG=$ATT/logs/audit_${ANID}_${KEY}.log
      echo "$(date +%H:%M:%S) audit $ANID $KEY $LEAF" >> $ALOG
      timeout -s KILL 240 python $ATT/code/audit211.py "$ANID" "$KEY" "$LEAF" >> $ALOG 2>&1 && echo "$ANID $KEY $LEAF" >> $ATT/logs/audit_done.txt
    done
    python $ATT/code/fold211.py >> $ATT/logs/fold211.log 2>&1
    python $ATT/code/progress211.py >> $ATT/logs/progress211.log 2>&1
    python docs/residue_map/refresh_current.py > /dev/null 2>&1
    V=$(grep -o "== $NID: g1 [^|]*| pad0 [^(]*" $LOG | tail -1)
    for i in 1 2 3 4 5 6; do
      git add -- $RES $ATT/certs $ATT/logs $PAGES $A229/logs docs/residue_map/current 2>/dev/null
      if git commit -q -m "A229: $NID $PAD:$LABEL [$V] $(( $(date +%s) - T0 ))s rc=$RC" -- $RES $ATT/certs $ATT/logs $PAGES $A229/logs docs/residue_map/current 2>/dev/null; then break; fi
      sleep $((5*i))
    done
    echo "$(date +%H:%M:%S) [$SLOT] $NID $PAD:$LABEL $V rc=$RC $(( $(date +%s) - T0 ))s" | tee -a $LOG
  done < "$Q"
  echo "$(date +%H:%M:%S) [$SLOT] queue $Q done"
done
