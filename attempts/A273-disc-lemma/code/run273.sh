#!/bin/bash
# A273 RUN -- the DROP-LEMMA tree over the (theta, phi) cells (tree273.py, 4 parameters h_u, theta, D, phi; h_v only in
# PRUNE), each cell then re-derived by verify273.py (independent code, bisect-on-disagreement), one commit + push per
# cell.  ONE python at a time (BelowNormal + affinity 0xFFFF set inside the scripts; BLAS threads 1).
#
#   ( "/c/Program Files/Git/bin/bash.exe" -c "cd /c/Users/esumm/code/packing && nohup bash attempts/A273-disc-lemma/code/run273.sh \
#        > attempts/A273-disc-lemma/logs/run273.log 2>&1" & )
#
# Env: A273_CORNER_DEG (default "5,5": boxes with theta <= 5 deg AND phi <= 5 deg are OPEN, the boundary layer),
#      A273_BOX_CAP (default 400000 boxes per cell; the rest of a capped cell is OPEN).
# STOP:    touch attempts/A273-disc-lemma/logs/STOP273     (exits between cells; nothing is killed)
# RESUME:  rm -f attempts/A273-disc-lemma/logs/STOP273, relaunch the SAME line: cells in certs/index273.jsonl are not
#          re-run, cells in results/verify273_index.jsonl are not re-verified; an interrupted cell restarts.
cd "$(dirname "$0")/../../.." || exit 1
ATT=attempts/A273-disc-lemma; CODE=$ATT/code
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export A273_CORNER_DEG=${A273_CORNER_DEG:-5,5} A273_BOX_CAP=${A273_BOX_CAP:-400000}
mkdir -p $ATT/logs $ATT/certs $ATT/results
echo "$(date +%H:%M:%S) A273 run: corner $A273_CORNER_DEG, cap $A273_BOX_CAP"
for TI in 1 2 3 4 5 6 7 8 0; do
  for PJ in 0 1 2 3 4 5 6 7 8; do
    C=c${TI}_${PJ}
    [ -f $ATT/logs/STOP273 ] && { echo "$(date +%H:%M:%S) STOP273 present: exiting"; exit 0; }
    T0=$(date +%s)
    if ! grep -q "\"cell\": \"$C\"" $ATT/certs/index273.jsonl 2>/dev/null; then
      python $CODE/tree273.py cell $TI $PJ >> $ATT/logs/tree273.log 2>&1 || { echo "$(date +%H:%M:%S) $C tree rc=$?"; continue; }
    fi
    if ! grep -q "\"cell\": \"$C\"" $ATT/results/verify273_index.jsonl 2>/dev/null; then
      python $CODE/verify273.py $C >> $ATT/logs/verify273.log 2>&1 || echo "$(date +%H:%M:%S) $C verify rc=$?"
    fi
    V=$(grep "\"cell\": \"$C\"" $ATT/results/verify273_index.jsonl 2>/dev/null | tail -1 | grep -o '"verdict": "[^"]*"')
    L=$(grep "\"cell\": \"$C\"" $ATT/certs/index273.jsonl 2>/dev/null | tail -1 | grep -o '"leaves": {[^}]*}')
    echo "$(date +%H:%M:%S) $C $L $V $(( $(date +%s) - T0 ))s"
    P="$ATT/certs/index273.jsonl $ATT/results/verify273_index.jsonl"
    for f in $ATT/certs/tree273_$C.jsonl.gz $ATT/results/verify273_$C.json $ATT/logs/run273.log $ATT/logs/tree273.log $ATT/logs/verify273.log; do
      [ -e "$f" ] && P="$P $f"
    done
    for i in 1 2 3 4 5; do
      git add -- $P 2>/dev/null
      if git commit -q -m "A273 cell $C: $L $V" -- $P 2>/dev/null; then
        git fetch -q 2>/dev/null && git merge -q --no-edit 2>/dev/null; git push -q 2>/dev/null; break
      fi
      sleep $((5*i))
    done
  done
done
echo "$(date +%H:%M:%S) A273 run: all cells done; page"
python $CODE/pages273.py >> $ATT/logs/run273.log 2>&1
P="docs/residue_map/campaigns/A273-disc-lemma/disc_lemma.svg $ATT/results/pages273.json $ATT/logs/run273.log"
git add -- $P 2>/dev/null; git commit -q -m "A273: page -- certified map over (theta, phi) after the run" -- $P 2>/dev/null && { git fetch -q; git merge -q --no-edit; git push -q; }
