#!/bin/bash
# A215 -- closed-node benchmark: run each already-closed node ROOT-TO-KILL under the CURRENT A211 runner
# (all optimisation flags at their defaults), ONE process at a time, isolated cert-dir / results / --no-fig.
#   bash attempts/A215-closed-node-benchmark/code/bench215.sh
cd "$(dirname "$0")/../../.." || exit 1
ATT=attempts/A215-closed-node-benchmark
RUN=attempts/A211-coarse-tree/code/run211.py
RES=$ATT/results/bench215.jsonl
TIM=$ATT/results/times215.tsv
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1

commit () {
  for i in 1 2 3; do
    git add -- "$ATT/results" "$ATT/logs" "$ATT/certs" "$ATT/code" 2>/dev/null
    if git commit -q -m "$1" -- "$ATT/results" "$ATT/logs" "$ATT/certs" "$ATT/code" 2>/dev/null; then return 0; fi
    sleep $((5*i))
  done
  echo "   commit failed: $1"
}

# nid  pad  old_campaign  old_seconds
SET="k5_11_interior_Y0308 g1 A205 203.2
k5_16_interior_Y0054 g1 A205 312.2
k5_16_interior_Y0027 g1 A205 365.2
k5_16_interior_Y0565 g1 A205 397.1
k5_16_interior_Y0839 g1 A205 526.2
k5_16_interior_Y0881 g1 A211p1 879.1
k5_16_interior_Y0719 g1 A211 236.6
k5_16_interior_Y1110 g1 A209 1765.5
k5_11_interior_Y0036_D07 zero A211f 106.2
k5_11_interior_Y0985 g1 A206 2120.8
k5_11_interior_Y1104 g1 A206 2401.3"

echo "$(date '+%F %T') A215 benchmark start"
[ -f "$TIM" ] || printf 'nid\tpad\told_campaign\told_seconds\tnew_wall\trc\n' > "$TIM"
while read -r NID PAD CAMP OLD; do
  [ -z "$NID" ] && continue
  if grep -q "^$NID	$PAD	" "$TIM" 2>/dev/null; then echo "skip $NID (done)"; continue; fi
  LOG=$ATT/logs/${NID}_${PAD}.log
  echo "$(date +%H:%M:%S) start $NID pad $PAD (old $CAMP ${OLD}s)"
  T0=$(date +%s)
  timeout -s KILL 4200 python "$RUN" page "$NID" --pads "$PAD" --wall 3600 --no-inherit \
      --cert-dir $ATT/certs --results "$RES" --no-fig > "$LOG" 2>&1
  RC=$?
  T=$(( $(date +%s) - T0 ))
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$NID" "$PAD" "$CAMP" "$OLD" "$T" "$RC" >> "$TIM"
  echo "$(date +%H:%M:%S) done  $NID pad $PAD ${T}s rc=$RC :: $(tail -3 "$LOG" | head -1)"
  commit "A215: $NID pad $PAD ${T}s rc=$RC (old $CAMP ${OLD}s)"
done <<< "$SET"

echo "$(date '+%F %T') A215 benchmark done; profiling the two cheapest nodes"
PROF=$(sort -t$'\t' -k5 -n "$TIM" | grep -v '^nid' | head -2 | cut -f1,2)
while read -r NID PAD; do
  [ -z "$NID" ] && continue
  echo "$(date +%H:%M:%S) profile $NID pad $PAD"
  timeout -s KILL 7200 python -m cProfile -o $ATT/logs/prof_${NID}_${PAD}.prof "$RUN" page "$NID" --pads "$PAD" --wall 3600 \
      --no-inherit --cert-dir $ATT/certs/prof --results $ATT/results/prof215.jsonl --no-fig > $ATT/logs/prof_${NID}_${PAD}.log 2>&1
  echo "$(date +%H:%M:%S) profile $NID rc=$?"
done <<< "$PROF"
python attempts/A211-coarse-tree/code/profstage211.py $ATT/logs/*.prof > $ATT/results/stagetable215.txt 2>&1
commit "A215: profiles + stage table"
echo "$(date '+%F %T') A215 ALL DONE"
