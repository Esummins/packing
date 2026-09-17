#!/usr/bin/env bash
# A244 -- the 12-STUCK search.  Two lanes, at most one python each (BelowNormal, affinity 0xFFFF
# set inside the scripts).  Everything is resumable: each stage appends to its own jsonl and skips
# rids already present, so re-running the same command resumes.  `touch logs/STOP` stops both
# lanes after the job in flight.
#
#   bash attempts/A244-twelve-stuck/code/run244.sh A [WALL]   # structure + descent (threshold)
#   bash attempts/A244-twelve-stuck/code/run244.sh B [WALL]   # the fixed-side probes
#   bash attempts/A244-twelve-stuck/code/run244.sh test       # the self-tests
#   bash attempts/A244-twelve-stuck/code/run244.sh pages      # regenerate the pages + summary
#
# RESUME: rm attempts/A244-twelve-stuck/logs/STOP; then lane A and lane B again (in that order,
# one python each).  WALL is the total seconds for the lane (default 100000).
set -u
cd "$(dirname "$0")/../../.."
export PYTHONDONTWRITEBYTECODE=1
P=attempts/A244-twelve-stuck
LANE=${1:-test}
WALL=${2:-100000}

case "$LANE" in
  test)
    python $P/code/test244.py
    ;;
  A)  # (0) the structure measurements behind the threshold, (1) the twelve-cell descent from
      # A217's four-crowds, (2) the four-cell control, (3) fresh starts
    [ -f $P/results/hand244.json ] || python -u $P/code/hand244.py >> $P/logs/A_hand.log 2>&1
    python -u $P/code/search244.py --tag main  --mode twelve --seeds a217   --n 600 --seed 0 \
        --deltas 0.001,1e-05 --wall $((WALL*55/100))    >> $P/logs/A_main.log  2>&1
    python -u $P/code/search244.py --tag ctrl  --mode four   --seeds a217   --n 300 --seed 0 \
        --deltas 0.001,1e-05 --wall $((WALL*25/100))    >> $P/logs/A_ctrl.log  2>&1
    python -u $P/code/search244.py --tag fresh --mode twelve --seeds border --n 400 --seed 7 \
        --deltas 0.001 --S 4.35 --wall $((WALL*20/100)) >> $P/logs/A_fresh.log 2>&1
    ;;
  B)  # the question: does anything exist BELOW 4 (and below s-hat)?  and where does the
      # twelve-cell window END above 4 (the cross-corner reach bound 3 + sqrt2 = 4.414214)?
    python -u $P/code/probe244.py --tag below4 --mode twelve --delta 1e-05 --seed 11 \
        --sides 3.9999,3.999,3.998,3.995,3.99,3.98,3.95,3.877084,3.82 --n 240 \
        --wall $((WALL*55/100))                         >> $P/logs/B_below4.log 2>&1
    python -u $P/code/probe244.py --tag above  --mode twelve --delta 1e-05 --seed 13 \
        --sides 4.2,4.35,4.41,4.414,4.42,4.5 --n 120 \
        --wall $((WALL*25/100))                         >> $P/logs/B_above.log  2>&1
    python -u $P/code/probe244.py --tag ctrl4  --mode four   --delta 1e-05 --seed 12 \
        --sides 3.999,3.99,3.95,3.877084,3.82 --n 160 \
        --wall $((WALL*20/100))                         >> $P/logs/B_ctrl4.log  2>&1
    ;;
  pages)
    python -u $P/code/summarise244.py && python -u $P/code/pages244.py
    ;;
  *) echo "usage: run244.sh A|B|test|pages [WALL_SECONDS]"; exit 2;;
esac
