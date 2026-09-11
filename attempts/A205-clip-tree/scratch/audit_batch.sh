#!/bin/bash
# audit every DEAD leaf of the given (nid, pad) certificates by sampling; waits for a free A205 slot (<= 2 A205 pythons)
cd "$(dirname "$0")/../../.." || exit 1
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
slots() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -match 'A205' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
while [ $# -ge 2 ]; do
  N=$1; PAD=$2; shift 2
  while [ "$(slots)" -ge 2 ]; do sleep 30; done
  LOG=attempts/A205-clip-tree/logs/audit_${N#k5_}_${PAD}.log
  for L in $(python -c "
import json,sys
c=json.load(open('attempts/A205-clip-tree/certs/cliptree205_$N.json',encoding='utf-8'))
print(' '.join(n['label'] for n in c['pads']['$PAD']['nodes'] if n.get('verdict')=='DEAD'))"); do
    python attempts/A205-clip-tree/scratch/audit205.py $N $PAD $L >> $LOG 2>&1
  done
  grep -h "leaf\|configurations" $LOG | tail -4
done
