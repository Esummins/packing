#!/bin/bash
# A280 RUN -- the DROP-LEMMA tree with the H2 / LOW prunes (tree280.py) over the steep (theta >= 25 deg) cells that
# are not CERT in A273's index273, each cell re-derived by verify280.py (independent: mpmath.iv prunes + A273's
# verifier for q-cells, bisect on disagreement), one commit + push per cell, the page at the end.
# GATED: starts no python until A273's chain has ended (no python running tree273/verify273/pages273.py and no bash
# running run273.sh, three checks 120 s apart) -- the lab's one-python-per-campaign ceiling.
#
#   ( "/c/Program Files/Git/bin/bash.exe" -c "cd /c/Users/esumm/code/packing && nohup bash attempts/A280-drop-steep/code/run280.sh \
#        >> attempts/A280-drop-steep/logs/run280.log 2>&1" & )
#
# Env: A280_BOX_CAP (default 400000 boxes per cell; the rest of a capped cell is OPEN).
# STOP:    touch attempts/A280-drop-steep/logs/STOP280   (exits while gated or between cells; nothing is killed)
# RESUME:  rm -f attempts/A280-drop-steep/logs/STOP280, relaunch the SAME line: cells in certs/index280.jsonl are not
#          re-run, cells in results/verify280_index.jsonl are not re-verified; an interrupted cell restarts.
cd "$(dirname "$0")/../../.." || exit 1
ATT=attempts/A280-drop-steep; CODE=$ATT/code
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export A280_BOX_CAP=${A280_BOX_CAP:-400000}
mkdir -p $ATT/logs $ATT/certs $ATT/results
busy273() {
  powershell -NoProfile -c "@(Get-CimInstance Win32_Process | Where-Object { (\$_.Name -eq 'python.exe' -and \$_.CommandLine -match '(tree|verify|pages)273\.py') -or (\$_.Name -eq 'bash.exe' -and \$_.CommandLine -match 'run273\.sh\"?\s*$') }).Count" 2>/dev/null | tr -d '\r '
}
echo "$(date '+%F %T') A280 run: gated on A273's chain, cap $A280_BOX_CAP"
free=0
while [ $free -lt 3 ]; do
  [ -f $ATT/logs/STOP280 ] && { echo "$(date '+%F %T') STOP280 present while gated: exiting"; exit 0; }
  n=$(busy273)
  if [ "$n" = "0" ]; then free=$((free+1)); else free=0; fi
  sleep 120
done
echo "$(date '+%F %T') A273 chain ended: starting"
CELLS=$(python -c "import sys; sys.path.insert(0, '$CODE'); import tree280 as T; print(' '.join('%d_%d' % c for c in T.todo()))")
for TP in $CELLS; do
  TI=${TP%_*}; PJ=${TP#*_}; C=c${TI}_${PJ}
  [ -f $ATT/logs/STOP280 ] && { echo "$(date '+%F %T') STOP280 present: exiting"; exit 0; }
  T0=$(date +%s)
  if ! grep -q "\"cell\": \"$C\"" $ATT/certs/index280.jsonl 2>/dev/null; then
    python $CODE/tree280.py cell $TI $PJ >> $ATT/logs/tree280.log 2>&1 || { echo "$(date '+%F %T') $C tree rc=$?"; continue; }
  fi
  if ! grep -q "\"cell\": \"$C\"" $ATT/results/verify280_index.jsonl 2>/dev/null; then
    python $CODE/verify280.py $C >> $ATT/logs/verify280.log 2>&1 || echo "$(date '+%F %T') $C verify rc=$?"
  fi
  V=$(grep "\"cell\": \"$C\"" $ATT/results/verify280_index.jsonl 2>/dev/null | tail -1 | grep -o '"verdict": "[^"]*"')
  L=$(grep "\"cell\": \"$C\"" $ATT/certs/index280.jsonl 2>/dev/null | tail -1 | grep -o '"leaves": {[^}]*}')
  echo "$(date '+%F %T') $C $L $V $(( $(date +%s) - T0 ))s"
  P="$ATT/certs/index280.jsonl $ATT/results/verify280_index.jsonl"
  for f in $ATT/certs/tree280_$C.jsonl.gz $ATT/results/verify280_$C.json $ATT/logs/run280.log $ATT/logs/tree280.log $ATT/logs/verify280.log; do
    [ -e "$f" ] && P="$P $f"
  done
  for i in 1 2 3 4 5; do
    git add -- $P 2>/dev/null
    if git commit -q -m "A280 cell $C: $L $V" -m "Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>" -- $P 2>/dev/null; then
      git fetch -q 2>/dev/null && git merge -q --no-edit 2>/dev/null; git push -q 2>/dev/null; break
    fi
    sleep $((5*i))
  done
done
echo "$(date '+%F %T') A280 run: all cells done; page"
python $CODE/pages280.py >> $ATT/logs/run280.log 2>&1
P="docs/residue_map/campaigns/A280-drop-steep/drop_steep.svg $ATT/results/pages280.json $ATT/logs/run280.log"
git add -- $P 2>/dev/null; git commit -q -m "A280: page -- the steep-C map after the run" -m "Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>" -- $P 2>/dev/null && { git fetch -q; git merge -q --no-edit; git push -q; }
