#!/bin/bash
# A281 finisher: waits for the ring search (30 rows, python exit, or logs/STOP -> kill), then page + doc + commit + push.
cd "$(dirname "$0")/../../.." || exit 1
A=attempts/A281-corner-cost
while true; do
  n=$(grep -c margin $A/logs/rings281.log 2>/dev/null)
  if [ -f $A/logs/STOP ]; then
    for pid in $(wmic process where "commandline like '%wall281.py rings%'" get processid 2>/dev/null | grep -E '^[0-9]+'); do taskkill /PID $pid /F >/dev/null 2>&1; done
    echo "STOP: killed ring search at $n rows" >> $A/logs/finish281.log; break
  fi
  [ "$n" -ge 30 ] && break
  wmic process where "commandline like '%wall281.py rings%'" get processid 2>/dev/null | grep -qE '^[0-9]+' || break
  sleep 60
done
PYTHONDONTWRITEBYTECODE=1 python $A/code/pages281.py >> $A/logs/finish281.log 2>&1
PYTHONDONTWRITEBYTECODE=1 python $A/code/assemble281.py >> $A/logs/finish281.log 2>&1
git add $A/results/wall281_rings.json $A/results/pages281.json $A/logs/rings281.log $A/logs/finish281.log docs/proofs/corner_cost.md docs/residue_map/campaigns/A281-corner-cost/corner_cost.svg
git commit -q -m "A281: ring-search rows landed ($(grep -c margin $A/logs/rings281.log) of 30); page + corner_cost.md regenerated

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- $A/results/wall281_rings.json $A/results/pages281.json $A/logs/rings281.log $A/logs/finish281.log docs/proofs/corner_cost.md docs/residue_map/campaigns/A281-corner-cost/corner_cost.svg
git fetch -q origin && git merge -q --no-edit origin/master && git push -q origin master >> $A/logs/finish281.log 2>&1
echo "finished $(date)" >> $A/logs/finish281.log
