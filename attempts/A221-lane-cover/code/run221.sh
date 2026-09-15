#!/bin/sh
# A221 -- the whole benchmark in ONE detached process (so the attempt never runs more than 2 pythons of its own).
#   sh run221.sh            # every lane, in order
#   sh run221.sh closed     # only the closed-page verdict-agreement lane
# Resume: every lane appends to results/bench221.jsonl with its own `tag`; re-running a lane simply appends again,
# and `code/table221.py` keeps the LAST row per (tag, page, run, node).
set -e
cd "$(dirname "$0")/../../.."
ROOT=$(pwd)
C=$ROOT/attempts/A211-coarse-tree/certs
A=$ROOT/attempts/A221-lane-cover
OUT=$A/results/bench221.jsonl
export PYTHONDONTWRITEBYTECODE=1
LANE=${1:-all}

run() { echo "=== $* ==="; python -u "$A/code/bench221.py" "$@" --out "$OUT"; }

if [ "$LANE" = all ] || [ "$LANE" = four ]; then
  # the four target nodes, full leaf (global bisection + the pocket cover)
  run --cert "$C/coarsetree211_k5_11_interior_Y0738.json" --run zero_page \
      --label R.1.1.3.3 --label R.1.2.5.2 --cap 300 --pk-deadline 60 --tag four
  # the same four nodes through Lemma POCKET-INHERIT (the parent's pockets, no global bisection)
  run --cert "$C/coarsetree211_k5_16_interior_Y0402.json" --run zero_page \
      --label R.2.1.1 --inherit --cap 300 --pk-deadline 60 --tag inherit
  run --cert "$C/coarsetree211_k5_11_interior_Y0738.json" --run zero_page \
      --label R.1.1.3.3 --label R.1.2.5.2 --inherit --cap 300 --pk-deadline 60 --tag inherit
fi

if [ "$LANE" = all ] || [ "$LANE" = closed ]; then
  # verdict agreement on two CLOSED pages: every recorded no-room node, whatever A189 said
  run --cert "$C/coarsetree211_k5_16_interior_Y0500.json" --run g1_page --verdict any \
      --cap 180 --pk-deadline 45 --tag closed
  run --cert "$C/coarsetree211_k5_16_interior_Y0460.json" --run g1_page --verdict any \
      --cap 180 --pk-deadline 45 --tag closed
fi
echo "ALL LANES DONE"
