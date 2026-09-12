#!/bin/bash
# A209: results/progress.md rewritten and committed every hour while the workers run (the workers also do it per node).
cd "$(dirname "$0")/../../.." || exit 1
ATT=attempts/A209-k5-killer
export PYTHONDONTWRITEBYTECODE=1
while true; do
  sleep 3600
  python $ATT/code/fold209.py >> $ATT/logs/fold209.log 2>&1
  python $ATT/code/progress209.py >> $ATT/logs/progress209.log 2>&1
  git add -- $ATT/results/progress.md $ATT/results/superseded_by_k5killer_A209.jsonl 2>/dev/null
  git commit -q -m "A209: hourly progress.md $(date '+%Y-%m-%d %H:%M')" -- $ATT/results/progress.md $ATT/results/superseded_by_k5killer_A209.jsonl 2>/dev/null
  [ -f $ATT/logs/HOURLY_STOP ] && exit 0
done
