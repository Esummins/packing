#!/bin/bash
# A257 SEAM PILOT launcher -- ONE python process at a time, one shard per near-Trump sibling, a commit after each.
#
#   nohup bash attempts/A257-trump5-window/code/pilot257.sh <wall spine> <wall sibling> <max own pythons> <pad> \
#        > attempts/A257-trump5-window/logs/pilot257.log 2>&1 &
#
# Defaults: 5400 1800 1 g1.  The THIRD argument is the worker count gate (the lab ceiling is 12 python processes;
# A257 holds ONE until the coordinator raises it -- stop, edit nothing, relaunch with a bigger number and the shards
# already in the journal are skipped).
#
# STOP:    touch attempts/A257-trump5-window/logs/STOP        (exits before the next sibling shard)
# RESUME:  rm -f attempts/A257-trump5-window/logs/STOP  and relaunch the same command line: the spine row and every
#          finished sibling are in results/pilot257.jsonl and are skipped, an interrupted sibling is re-run whole.
cd "$(dirname "$0")/../../.." || exit 1
ATT=attempts/A257-trump5-window; CODE=$ATT/code
WALLS=${1:-5400}; WALLB=${2:-1800}; MAXMINE=${3:-1}; PAD=${4:-g1}
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export A220_NOROOM_INHERIT=1 A221_LANE=1 A224_SNAP=1 A230_EPS=1
export A229_CERT_DIR="$(pwd)/$ATT/certs"
mkdir -p $ATT/logs $ATT/certs $ATT/results
labcount() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -notmatch 'Claude Extensions' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
mine() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -match 'pilot257.py' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
freemb() { powershell -NoProfile -Command "[int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1024)" | tr -d '\r '; }
gate() { while [ "$(labcount)" -ge 12 ] || [ "$(mine)" -ge "$MAXMINE" ] || [ "$(freemb)" -lt 3072 ]; do sleep 60; done; }
commit() {
  for i in 1 2 3 4 5 6; do
    git add -- $ATT/results $ATT/certs $ATT/logs $ATT/notes docs/residue_map/campaigns/A257-trump5-window 2>/dev/null
    if git commit -q -m "A257: $1" -- $ATT/results $ATT/certs $ATT/logs $ATT/notes docs/residue_map/campaigns/A257-trump5-window 2>/dev/null; then return 0; fi
    sleep $((5*i))
  done
}

[ -f $ATT/logs/STOP ] && { echo "$(date +%H:%M:%S) STOP present: exiting"; exit 0; }
echo "$(date +%H:%M:%S) A257 seam pilot: pad $PAD, spine wall $WALLS s, sibling wall $WALLB s, max own pythons $MAXMINE"
gate
T0=$(date +%s)
timeout -s KILL $(( WALLS + 1800 )) python $CODE/pilot257.py --phase spine --pad "$PAD" --wall-spine "$WALLS" 2>&1 | tee -a $ATT/logs/pilot257_spine.log
commit "seam pilot SPINE (pad $PAD, wall $WALLS) $(( $(date +%s) - T0 ))s"

for L in $(python $CODE/pilot257.py --list-siblings --pad "$PAD"); do
  L=${L//$'\r'/}
  [ -z "$L" ] && continue
  [ -f $ATT/logs/STOP ] && { echo "$(date +%H:%M:%S) STOP present: exiting before sibling $L"; exit 0; }
  gate
  T1=$(date +%s)
  echo "$(date +%H:%M:%S) sibling $L (lab $(labcount), mine $(mine), free $(freemb) MB)"
  timeout -s KILL $(( WALLB + 1800 )) python $CODE/pilot257.py --phase siblings --pad "$PAD" --only-sibling "$L" \
      --wall-sib "$WALLB" 2>&1 | tee -a $ATT/logs/pilot257_sib_${L//./_}.log
  RC=$?
  commit "seam pilot sibling $L (rc=$RC) $(( $(date +%s) - T1 ))s"
done
python $CODE/table257.py >> $ATT/logs/pilot257.log 2>&1
commit "seam pilot: sibling table"
echo "$(date +%H:%M:%S) A257 seam pilot: all shards done"
