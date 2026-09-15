#!/bin/bash
# A231 chain: the anchored re-alignment over every input (resumable), then the tables and pages, then commit.
# Resume block:
#   cd C:/Users/esumm/code/packing; export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1
#   bash attempts/A231-realign/code/run231.sh            # rows appended + committed every 25; summary + pages at the end
cd "$(dirname "$0")/../../.." || exit 1
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1
A=attempts/A231-realign
python $A/code/realign231.py --resume >> $A/logs/realign231.log 2>&1
for s in summarise231 pages231; do
  if [ -f $A/code/$s.py ]; then python $A/code/$s.py >> $A/logs/$s.log 2>&1; else echo "$s.py missing" >> $A/logs/run231.log; fi
done
git add $A/results/realign231.jsonl $A/results/realign231.md docs/residue_map/campaigns/A231-realign 2>/dev/null
git commit -q -m "A231 realign: run complete (rows, table, pages)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- $A/results/realign231.jsonl $A/results/realign231.md docs/residue_map/campaigns/A231-realign 2>/dev/null
echo "chain done $(date)" >> $A/logs/run231.log
