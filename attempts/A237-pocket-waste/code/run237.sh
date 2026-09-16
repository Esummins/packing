#!/bin/bash
# A237 resume block: the TILT-MIN test (5 s), the pocket census (~3 min), the window family + table (~5 min), the
# summary, the pages, the tests, then the Lean build + audit through lakeb (~5 min).  Idempotent; from the repo root:
#   bash attempts/A237-pocket-waste/code/run237.sh          (--lean-only for the build alone)
cd "$(dirname "$0")/../../.." || exit 1
export PYTHONDONTWRITEBYTECODE=1
LOG=attempts/A237-pocket-waste/logs
CODE=attempts/A237-pocket-waste/code
mkdir -p $LOG
if [ "$1" != "--lean-only" ]; then
  python $CODE/tiltmin237.py > $LOG/tiltmin237.log 2>&1
  python $CODE/pocket237.py > $LOG/pocket237.log 2>&1
  python $CODE/family237.py > $LOG/family237.log 2>&1
  python $CODE/summarise237.py > $LOG/summarise237.log 2>&1
  python $CODE/pages237.py > $LOG/pages237.log 2>&1
  python $CODE/test237.py > $LOG/test237.log 2>&1
fi
python attempts/A78-lean-wave6/code/lakeb.py PackingCertMathlib.Statements.Open.PocketWaste > $LOG/lean_build237.log 2>&1
echo "lakeb PocketWaste rc=$?" >> $LOG/lean_build237.log
python attempts/A78-lean-wave6/code/lakeb.py PackingCertMathlib.Statements >> $LOG/lean_build237.log 2>&1
echo "lakeb Statements rc=$?" >> $LOG/lean_build237.log
python lean/audit.py > $LOG/audit237.log 2>&1
echo "audit rc=$?" >> $LOG/audit237.log
echo DONE >> $LOG/lean_build237.log
