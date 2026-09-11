#!/bin/bash
# A206 launcher: run (a loaded A205 leaf under Rule NS, or a whole tree) per call, gated on the lab ceiling (12 pythons
# excluding "Claude Extensions" command lines) and on free memory (>= 6144 MB); BLAS pinned; the page's CURRENT copy
# refreshed and git commit with explicit pathspecs after the run.
#   bash run206.sh leaf <nid> <pad> <leaf> [src tag wall]      bash run206.sh tree <nid> <pad> [wall]
cd "$(dirname "$0")/../../.." || exit 1
ATT=attempts/A206-named-split; RES=$ATT/results/namedsplit206.jsonl; PAGES=docs/residue_map/campaigns/A206-namedsplit
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
labcount() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -notmatch 'Claude Extensions' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
mine() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -match 'run206|audit206' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
freemb() { powershell -NoProfile -Command "[int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1024)" | tr -d '\r '; }
MODE=$1; NID=$2; PAD=$3
if [ "$MODE" = "leaf" ]; then LEAF=$4; SRC=${5:-standard}; TAG=${6:-}; [ "$TAG" = "-" ] && TAG=; WALL=${7:-3600}; KEY="${PAD}_${LEAF}"; ARGS="leaf $NID --pad $PAD --leaf $LEAF --src $SRC --wall $WALL"; [ -n "$TAG" ] && ARGS="$ARGS --tag $TAG"
else WALL=${4:-3600}; KEY="${PAD}_tree"; ARGS="tree $NID --pad $PAD --wall $WALL"; fi
while [ "$(labcount)" -ge 12 ] || [ "$(mine)" -ge 3 ] || [ "$(freemb)" -lt 6144 ]; do sleep 60; done
LOG=$ATT/logs/namedsplit206_${NID}_${KEY}.log
T0=$(date +%s); echo "$(date +%H:%M:%S) start $NID $KEY (lab $(labcount), free $(freemb) MB)" | tee -a $LOG
timeout -s KILL $(( WALL + 1200 )) python $ATT/code/run206.py $ARGS >> $LOG 2>&1
RC=$?
if [ $RC -eq 137 ]; then echo "{\"nid\": \"$NID\", \"run\": \"$KEY\", \"pad\": \"$PAD\", \"verdict\": \"ALIVE\", \"leaf\": \"process wall $(( WALL + 1200 )) s reached (killed): undecided\", \"seconds\": $(( $(date +%s) - T0 )), \"killed\": true, \"when\": \"$(date '+%Y-%m-%d %H:%M:%S')\"}" >> $RES; fi
python docs/residue_map/refresh_current.py > /dev/null 2>&1
V=$(grep "\"nid\": \"$NID\"" $RES | grep "\"run\": \"$KEY\"" | tail -1 | grep -o '"verdict": "[A-Z]*"' | tr '\n' ' ')
for i in 1 2 3 4 5 6; do
  git add -- $RES $ATT/certs $ATT/logs $PAGES docs/residue_map/current 2>/dev/null
  if git commit -q -m "A206: $NID $KEY [$V] $(( $(date +%s) - T0 ))s" -- $RES $ATT/certs $ATT/logs $PAGES docs/residue_map/current 2>/dev/null; then break; fi
  sleep $((5*i))
done
echo "$(date +%H:%M:%S) $NID $KEY $V rc=$RC $(( $(date +%s) - T0 ))s" | tee -a $LOG
