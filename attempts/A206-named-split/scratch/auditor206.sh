#!/bin/bash
# A206 auditor: every DEAD leaf of every finished run audited by pose sampling (audit206.py, A205's full-role sampler with the
# Rule-NS miss hypotheses), one audit at a time and only while fewer than 3 A206 pythons (run206 / audit206) are running.
cd "$(dirname "$0")/../../.." || exit 1
ATT=attempts/A206-named-split
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
mine() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -match 'run206.py|audit206.py' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
while true; do
  python $ATT/scratch/audit_queue.py | tr -d "" | while read -r NID KEY LEAF; do
    [ -z "$NID" ] && continue
    while [ "$(mine)" -ge 3 ]; do sleep 60; done
    LOG=$ATT/logs/audit_${NID}_${KEY}.log
    echo "$(date +%H:%M:%S) audit $NID $KEY $LEAF" | tee -a $LOG
    timeout -s KILL 1500 python $ATT/scratch/audit206.py $NID $KEY $LEAF --nh 150 >> $LOG 2>&1 && echo "$NID $KEY $LEAF" >> $ATT/scratch/audit_done.txt
    sleep 5
    git add -- $LOG $ATT/scratch/audit_done.txt 2>/dev/null; git commit -q -m "A206 audit: $NID $KEY $LEAF" -- $LOG $ATT/scratch/audit_done.txt 2>/dev/null
  done
  sleep 120
done
