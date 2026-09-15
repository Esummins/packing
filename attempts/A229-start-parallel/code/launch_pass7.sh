#!/bin/bash
# launch_pass7.sh -- wait for the pass-6 page workers (worker211 p6a/p6b/p6c and their run211 pythons) to finish,
# then rebuild the start-node queue from the merged certificates and start N shard workers (worker229.sh).
# No LLM in the loop: this is the coordinator's "queue the next pass before the current one drains" as a script.
#   nohup bash attempts/A229-start-parallel/code/launch_pass7.sh 6 > attempts/A211-coarse-tree/logs/launch_pass7.log 2>&1 &
cd "$(dirname "$0")/../../.." || exit 1
N=${1:-6}
ATT=attempts/A211-coarse-tree; A229=attempts/A229-start-parallel/code
export PYTHONDONTWRITEBYTECODE=1
busy() { powershell -NoProfile -Command "(Get-CimInstance Win32_Process | Where-Object { (\$_.Name -eq 'python.exe' -and \$_.CommandLine -match 'run211.py page') -or (\$_.Name -eq 'bash.exe' -and \$_.CommandLine -match 'worker211.sh p6') } | Measure-Object).Count" | tr -d '\r '; }
echo "$(date +%H:%M:%S) launch_pass7: waiting for pass 6 (busy=$(busy))"
while [ "$(busy)" != "0" ]; do sleep 120; done
echo "$(date +%H:%M:%S) pass 6 finished; rebuilding the start-node queue"
python $A229/queue229.py k5_16_interior_Y0402 k5_11_interior_Y0738 k5_16_interior_Y1056 --out $ATT/code/queue_pass7.txt
echo "$(date +%H:%M:%S) queue_pass7.txt: $(grep -vc '^#' $ATT/code/queue_pass7.txt) start nodes"
git add -- $ATT/code/queue_pass7.txt 2>/dev/null; git commit -q -m "A211: pass-7 start-node queue (A229) rebuilt after pass 6" -- $ATT/code/queue_pass7.txt 2>/dev/null
for i in $(seq 1 $N); do
  SLOT=p7$(printf "\\x$(printf %x $((96 + i)))")
  A220_NOROOM_INHERIT=1 A221_LANE=1 A224_SNAP=1 nohup bash $A229/worker229.sh $SLOT 1800 $ATT/code/queue_pass7.txt > $ATT/logs/worker_$SLOT.log 2>&1 &
  echo "$(date +%H:%M:%S) started $SLOT"
  sleep 15
done
echo "$(date +%H:%M:%S) launch_pass7 done"
