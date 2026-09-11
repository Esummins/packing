#!/bin/bash
# A205 EXTENDED pass (coordinator, 2026-09-11): the clip tree at wall 3600 s, g1 pad (window-valid) over the pages given,
# N workers gated on the lab ceiling (<= 8 pythons so the k0 cascade keeps its slots); per-page commit with pathspecs.
#   bash run205_ext.sh <nworkers> <pages...>
cd "$(dirname "$0")/../../.." || exit 1
ATT=attempts/A205-clip-tree
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
NW=$1; shift
labcount() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -notmatch 'Claude Extensions' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
mine() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -match 'run205.py' -and \$_.CommandLine -match '_w3600' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
one() {
  P=$1; LOG=$ATT/logs/cliptree205_${P}_w3600.log
  if [ -f "$ATT/certs/extended/cliptree205_${P}_w3600.json" ]; then echo "skip $P (done)"; return; fi
  T0=$(date +%s); echo "$(date +%H:%M:%S) start $P (w3600)"
  timeout -s KILL 4500 python $ATT/code/run205.py $P --wall 3600 --tag _w3600 --pads g1 >> $LOG 2>&1
  echo "$(date +%H:%M:%S) $P rc=$? $(( $(date +%s) - T0 ))s"
  git add -- $ATT/results $ATT/certs/extended docs/residue_map/campaigns/A205-cliptree 2>/dev/null
  git commit -q -m "A205 ext (w3600, g1): $P" -- $ATT/results $ATT/certs/extended docs/residue_map/campaigns/A205-cliptree 2>/dev/null
}
for P in "$@"; do
  while [ "$(mine)" -ge "$NW" ] || [ "$(labcount)" -ge 8 ]; do sleep 60; done
  one $P &
  sleep 20
done
wait
git push -q 2>/dev/null
echo "$(date +%H:%M:%S) extended pass done"
