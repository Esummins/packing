#!/bin/bash
# A57 route-(a) cost probe: 4D verification wall time per leaf, s in [3.82, s0].
cd "C:/Users/esumm/code/packing/attempts/A57-shadow-trees"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
VP="../A56-sparametric/code/verify_param.py"
OUT=results/param_cost.jsonl
: > $OUT
for f in certs/param/*.param.json; do
  b=$(basename "$f" .param.json)
  for m in 0; do
    t0=$(date +%s)
    res=$(timeout 2400 python "$VP" "$f" --slo 191/50 --shi 969271/250000 --depth 48 --jobs 1 --strict-margin $m 2>&1 | tail -40)
    rc=$?
    t1=$(date +%s)
    verdict=$(echo "$res" | grep -oE "^(PASS|FAIL|MALFORMED)" | head -1)
    [ -z "$verdict" ] && verdict="TIMEOUT/ERR(rc=$rc)"
    boxes=$(echo "$res" | grep -oE "boxes = [0-9]+" | head -1)
    echo "{\"leaf\":\"$b\",\"margin\":\"$m\",\"seconds\":$((t1-t0)),\"verdict\":\"$verdict\",\"$boxes\"}" | sed 's/"boxes = \([0-9]*\)"/"boxes":\1/' >> $OUT
    echo "=== $b margin=$m : $verdict in $((t1-t0))s"
    echo "$res" | tail -6
  done
done
