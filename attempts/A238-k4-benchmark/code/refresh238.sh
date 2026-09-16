#!/bin/bash
# A238 -- keep the deliverables current while the sweep runs: every REFRESH seconds regenerate results/bench238.md,
# results/bench238_summary.json and the residue-map pages from whatever certificates exist, and commit them.
#
#   nohup bash attempts/A238-k4-benchmark/code/refresh238.sh 900 > attempts/A238-k4-benchmark/logs/refresh238.log 2>&1 &
#
# report238.py and pages238.py are READ-ONLY over the certificates and take well under a second each, so this is a
# bookkeeping chore, not a third worker; it still waits if more than two heavy A238 pythons are ever running.
# `touch logs/STOP` stops it with the workers.  Idempotent: re-running it is always safe.
cd "$(dirname "$0")/../../.." || exit 1
A=attempts/A238-k4-benchmark
R=${1:-900}
export PYTHONDONTWRITEBYTECODE=1
PATHS="$A/results $A/logs docs/residue_map/campaigns/A238-k4-benchmark"
heavy() { powershell -NoProfile -Command "(Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { \$_.CommandLine -like '*run238.py page*' } | Measure-Object).Count" | tr -d '\r '; }
echo "$(date +%H:%M:%S) refresh238: every ${R}s"
while true; do
  sleep "$R"
  [ -f $A/logs/STOP ] && { echo "$(date +%H:%M:%S) STOP present: exiting"; exit 0; }
  while [ "$(heavy)" -gt 2 ] 2>/dev/null; do sleep 60; done
  python $A/code/report238.py > /dev/null 2>&1
  python $A/code/pages238.py  > /dev/null 2>&1
  n=$(wc -l < $A/results/bench238.jsonl 2>/dev/null)
  for k in 1 2 3; do
    git add -- $PATHS 2>/dev/null
    git diff --cached --quiet -- $PATHS 2>/dev/null && break
    git commit -q -m "A238: report + pages refreshed ($n nodes)

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>" -- $PATHS 2>/dev/null && break
    sleep $((4 * k))
  done
  echo "$(date +%H:%M:%S) refreshed at $n nodes"
done
