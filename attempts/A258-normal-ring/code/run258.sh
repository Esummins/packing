#!/bin/bash
# A258 launcher.  RESUME BLOCK: every mode is resumable (rows keyed in results/*.jsonl); `touch logs/STOP` stops a
# detached run between rows; remove logs/STOP before relaunching.  ONE heavy process: scan (detached).
#   bash run258.sh test | dom | norm | poker | pages        (sub-minute .. few minutes, foreground)
#   bash run258.sh side                                      (detached, ~1 h: least side per pattern + extent of D)
#   bash run258.sh scan                                      (detached, ~2 h: margin scan, superseded by side)
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
case "$1" in
  test) python test258.py 60000 ;;
  dom) python dom258.py ;;
  norm) python norm258.py ;;
  poker) python poker258.py ;;
  pages) python pages258.py ;;
  scan) ( nohup python scan258.py >> ../logs/scan258.log 2>&1 & echo $! >> ../logs/pids.txt ) ;;
  side) ( nohup python side258.py >> ../logs/side258.log 2>&1 & echo $! >> ../logs/pids.txt ) ;;
  *) echo "usage: run258.sh test|dom|norm|poker|pages|side|scan" ;;
esac
