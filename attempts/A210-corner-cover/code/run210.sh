#!/bin/bash
# A210 launcher (ONE detached process, BelowNormal, BLAS pinned): rule CC (Lemma CORNER-COVER) over the alive k5
# gallery pages -- stage 0 + A203's CSP + rule CC at PAD 0 first, then the G1 window pad, the page drawn after each
# pad, a git commit with explicit pathspecs after every page -- and then the same rule on A209's named tree nodes.
#   bash attempts/A210-corner-cover/code/run210.sh [pages file]
# Resumable: a (nid, pad) already in results/cornercover210.jsonl is skipped (run210.py --force overrides).
cd "$(dirname "$0")/../../.." || exit 1
ATT=attempts/A210-corner-cover
RES=$ATT/results/cornercover210.jsonl
LEAVES=$ATT/results/cornercover210_leaves.jsonl
PAGES_FILE=${1:-$ATT/results/pages210.txt}
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1

commit () {  # $1 = message; explicit pathspecs only, never -a
  for i in 1 2 3 4 5 6; do
    git add -- "$RES" "$LEAVES" $ATT/certs $ATT/logs $ATT/results docs/residue_map/campaigns/A210-cornercover 2>/dev/null
    if git commit -q -m "$1" -- "$RES" "$LEAVES" $ATT/certs $ATT/logs $ATT/results docs/residue_map/campaigns/A210-cornercover 2>/dev/null; then return 0; fi
    sleep $((5*i))
  done
  echo "   commit failed: $1"
}

echo "$(date '+%Y-%m-%d %H:%M:%S') A210 start; pages $(wc -l < "$PAGES_FILE")"
while read -r P; do
  P=$(printf '%s' "$P" | tr -d '')
  [ -z "$P" ] && continue
  T0=$(date +%s)
  echo "$(date +%H:%M:%S) start $P"
  timeout -s KILL 1800 python $ATT/code/run210.py "$P" --pads zero,g1
  RC=$?
  if [ $RC -eq 137 ]; then
    echo "{\"nid\": \"$P\", \"pad\": \"-\", \"verdict\": \"ALIVE\", \"leaf\": \"wall 1800s reached (process killed): undecided\", \"seconds\": $(( $(date +%s) - T0 )), \"killed\": true, \"when\": \"$(date '+%Y-%m-%d %H:%M:%S')\"}" >> "$RES"
  fi
  V=$(grep "\"nid\": \"$P\"" "$RES" | tail -2 | grep -o '"pad": "[a-z0-9]*", "stage": 0, "verdict": "[A-Z]*"' | tr '\n' ' ')
  commit "A210: $P [$V] rc=$RC $(( $(date +%s) - T0 ))s"
  echo "$(date +%H:%M:%S) done $P $V rc=$RC $(( $(date +%s) - T0 ))s"
done < "$PAGES_FILE"

echo "$(date '+%Y-%m-%d %H:%M:%S') A210 leaves: rule CC on A209's named tree nodes (read-only on A209's certs)"
python $ATT/code/leaves210.py
commit "A210: rule CC on A209's named leaves -> $LEAVES"
echo "$(date '+%Y-%m-%d %H:%M:%S') A210 done"
