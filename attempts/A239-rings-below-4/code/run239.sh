#!/bin/bash
# A239 resume block: the ring study (15 s), the click / swap (3 s), the pages (10 s), the tests (10 s), then the Lean
# build + audit through lakeb (~5 min).  Idempotent; from the repo root:
#   bash attempts/A239-rings-below-4/code/run239.sh          (--lean-only for the build alone)
cd "$(dirname "$0")/../../.." || exit 1
export PYTHONDONTWRITEBYTECODE=1
LOG=attempts/A239-rings-below-4/logs
CODE=attempts/A239-rings-below-4/code
mkdir -p $LOG
if [ "$1" != "--lean-only" ]; then
  python $CODE/rings239.py > $LOG/rings239.log 2>&1
  python $CODE/click239.py > $LOG/click239.log 2>&1
  python $CODE/pages239.py > $LOG/pages239.log 2>&1
  python $CODE/test239.py > $LOG/test239.log 2>&1
fi
python attempts/A78-lean-wave6/code/lakeb.py PackingCertMathlib.Statements.Open.WedgedSeal > $LOG/lean_build239.log 2>&1
echo "lakeb WedgedSeal rc=$?" >> $LOG/lean_build239.log
python attempts/A78-lean-wave6/code/lakeb.py PackingCertMathlib.Statements >> $LOG/lean_build239.log 2>&1
echo "lakeb Statements rc=$?" >> $LOG/lean_build239.log
python lean/audit.py > $LOG/audit239.log 2>&1
echo "audit rc=$?" >> $LOG/audit239.log
echo DONE >> $LOG/lean_build239.log
