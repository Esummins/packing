#!/bin/bash
# A209 auditor: every DEAD leaf (not inherited) of every finished run sampled by scratch/audit209.py (A206's audit206b on
# A209's certificates: poses inside the parent's snapshot pieces, exact meets test, FC kills need two meeters, the cap-1
# two-meeter criterion; NOROOM kills need m free squares; BASIN kills a pose outside the basins); one audit at a time.
cd "$(dirname "$0")/../../.." || exit 1
ATT=attempts/A209-k5-killer
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
labcount() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -notmatch 'Claude Extensions' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
while true; do
  [ -f $ATT/logs/AUDIT_STOP ] && exit 0
  python $ATT/scratch/audit_queue209.py | tr -d "\r" | while read -r NID KEY LEAF; do
    [ -z "$NID" ] && continue
    while [ "$(labcount)" -ge 10 ]; do sleep 60; done
    LOG=$ATT/logs/audit_${NID}_${KEY}.log
    echo "$(date +%H:%M:%S) audit $NID $KEY $LEAF" | tee -a $LOG
    timeout -s KILL 1500 python $ATT/scratch/audit209.py $NID $KEY $LEAF --nh 150 >> $LOG 2>&1 && echo "$NID $KEY $LEAF" >> $ATT/scratch/audit_done.txt
    sleep 3
    git add -- $LOG $ATT/scratch/audit_done.txt 2>/dev/null; git commit -q -m "A209 audit: $NID $KEY $LEAF" -- $LOG $ATT/scratch/audit_done.txt 2>/dev/null
  done
  sleep 180
done
