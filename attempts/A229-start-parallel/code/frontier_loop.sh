#!/bin/bash
# frontier_loop.sh -- after the page-level frontier workers (worker211 fr*) drain queue_frontier_rest.txt, hand the
# frontier nodes still alive to the start-node pass loop (loop_passes.sh) so their surviving start nodes run in
# parallel shards until nothing is left.  No LLM in the loop.
#   nohup bash attempts/A229-start-parallel/code/frontier_loop.sh 6 > attempts/A211-coarse-tree/logs/frontier_loop.log 2>&1 &
cd "$(dirname "$0")/../../.." || exit 1
N=${1:-6}
ATT=attempts/A211-coarse-tree; A229=attempts/A229-start-parallel/code
export PYTHONDONTWRITEBYTECODE=1
busy() { powershell -NoProfile -Command "(Get-CimInstance Win32_Process | Where-Object { (\$_.Name -eq 'python.exe' -and \$_.CommandLine -match 'run211.py page') -or (\$_.Name -eq 'bash.exe' -and \$_.CommandLine -match 'worker211.sh fr') } | Measure-Object).Count" | tr -d '\r '; }
echo "$(date +%H:%M:%S) frontier_loop: waiting for the fr workers (busy=$(busy))"
while [ "$(busy)" != "0" ]; do sleep 180; done
ALIVE=$(python - <<'EOF'
import json
Q=[l.split()[0] for l in open('attempts/A211-coarse-tree/code/queue_frontier.txt',encoding='utf-8',errors='replace') if l.strip() and not l.startswith('#')]
dead=set()
for l in open('attempts/A211-coarse-tree/results/coarsetree211.jsonl',encoding='utf-8',errors='replace'):
    try: r=json.loads(l)
    except: continue
    if r.get('nid') in Q and r.get('pad')=='g1' and r.get('verdict')=='DEAD' and not r.get('shard'): dead.add(r['nid'])
print(' '.join(n for n in Q if n not in dead))
EOF
)
echo "$(date +%H:%M:%S) fr workers done; alive frontier nodes: $(echo $ALIVE | wc -w)"
[ -z "$ALIVE" ] && { echo "$(date +%H:%M:%S) frontier closed"; exit 0; }
exec bash $A229/loop_passes.sh $N $ALIVE
