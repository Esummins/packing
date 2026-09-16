#!/bin/bash
# A236 resume block: the capacity test (25 s), the table, the summary, the pages, the tests, then the Lean build +
# audit through lakeb (~5 min).  Idempotent; rerun from the repo root:  bash attempts/A236-ring-capacity/code/run236.sh
cd "$(dirname "$0")/../../.." || exit 1
export PYTHONDONTWRITEBYTECODE=1
LOG=attempts/A236-ring-capacity/logs
CODE=attempts/A236-ring-capacity/code
mkdir -p $LOG
if [ "$1" != "--lean-only" ]; then
  python $CODE/capacity236.py > $LOG/capacity236.log 2>&1
  python $CODE/table236.py > $LOG/table236.log 2>&1
  python $CODE/summarise236.py > $LOG/summarise236.log 2>&1
  python $CODE/pages236.py > $LOG/pages236.log 2>&1
  python $CODE/test236.py > $LOG/test236.log 2>&1
fi
python attempts/A78-lean-wave6/code/lakeb.py PackingCertMathlib.Statements.Open.RingCapacity > $LOG/lean_build236.log 2>&1
echo "lakeb RingCapacity rc=$?" >> $LOG/lean_build236.log
python attempts/A78-lean-wave6/code/lakeb.py PackingCertMathlib.Statements >> $LOG/lean_build236.log 2>&1
echo "lakeb Statements rc=$?" >> $LOG/lean_build236.log
python lean/audit.py > $LOG/audit236.log 2>&1
echo "audit rc=$?" >> $LOG/audit236.log
echo DONE >> $LOG/lean_build236.log
