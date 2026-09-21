#!/usr/bin/env bash
# A254 driver.  bash run254.sh table|cells|pages|search   (search = the detached small-budget ladder; resumable;
# touch attempts/A254-peel/logs/STOP to stop between starts; rerun to resume).  ONE python at a time.
cd "$(dirname "$0")/../../.." || exit 1
export PYTHONDONTWRITEBYTECODE=1
A=attempts/A254-peel
case "$1" in
  table) python $A/code/table254.py ;;
  cells) python $A/code/cells254.py --m 3,4,5,6 ;;
  pages) python $A/code/pages254.py ;;
  search)
    python $A/code/search254.py --n 5  --sides 2.60,2.72,2.80,2.90 --starts 6 >> $A/logs/search254.log 2>&1
    python $A/code/search254.py --n 10 --sides 3.72,3.80,3.90,3.97 --starts 6 >> $A/logs/search254.log 2>&1
    python $A/code/search254.py --n 17 --sides 4.68,4.75,4.85,4.95 --starts 6 >> $A/logs/search254.log 2>&1
    python $A/code/summarise254.py >> $A/logs/search254.log 2>&1
    git add $A/results/search254.jsonl $A/results/search254.md
    git commit -q -m "A254: search254 ladder rows (detached run)" -- $A/results/search254.jsonl $A/results/search254.md
    git fetch -q && git merge -q --no-edit origin/master && git push -q ;;
  *) echo "usage: run254.sh table|cells|pages|search" ;;
esac
