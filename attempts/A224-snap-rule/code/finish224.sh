#!/bin/bash
# A224 -- the RESUME BLOCK.  Run this after bench224.sh has finished (or at any point: both halves are idempotent).
#   bash attempts/A224-snap-rule/code/finish224.sh
# 1. re-run any benchmark step that did not finish (stamps in logs/done/ make finished steps no-ops);
# 2. rebuild results/bench224.md from results/{snapscan224,bench224}.jsonl;
# 3. commit the results with explicit pathspecs (fetch + plain merge only; never rebase/reset).
cd "$(dirname "$0")/../../.." || exit 1
A=attempts/A224-snap-rule
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
bash $A/code/bench224.sh "${1:-420}"
A224_SNAP=1 python $A/code/report224.py
for i in 1 2 3 4 5 6; do
  git add -- $A/results $A/logs $A/notes
  git commit -q -m "A224: benchmark results (offline scan + live A/B)" -- $A/results $A/logs $A/notes && break
  sleep $((5*i))
done
git log --oneline -1
