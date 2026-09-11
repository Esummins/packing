#!/bin/bash
# full-role audit of the given (nid, pad, leaf) triples, one at a time, when fewer than 2 A205 pythons run
cd "$(dirname "$0")/../../.." || exit 1
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
slots() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -match 'A205' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
while [ $# -ge 3 ]; do
  while [ "$(slots)" -ge 2 ]; do sleep 30; done
  python attempts/A205-clip-tree/scratch/audit_roles205.py $1 $2 $3 >> attempts/A205-clip-tree/logs/audit_roles_${1#k5_}_$2.log 2>&1
  shift 3
done
