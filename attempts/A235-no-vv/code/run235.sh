#!/bin/bash
# A235 resume block: the selection enumeration (3 min), the Lean build + audit through lakeb (~5 min), the summary.
cd "$(dirname "$0")/../../.." || exit 1
export PYTHONDONTWRITEBYTECODE=1
LOG=attempts/A235-no-vv/logs
python attempts/A235-no-vv/code/select235.py > $LOG/select235.log 2>&1
python attempts/A78-lean-wave6/code/lakeb.py PackingCertMathlib.Statements.Open.NoVV > $LOG/lean_build235.log 2>&1
echo "lakeb NoVV rc=$?" >> $LOG/lean_build235.log
python attempts/A78-lean-wave6/code/lakeb.py PackingCertMathlib.Statements >> $LOG/lean_build235.log 2>&1
echo "lakeb Statements rc=$?" >> $LOG/lean_build235.log
python lean/audit.py > $LOG/audit235.log 2>&1
echo "audit rc=$?" >> $LOG/audit235.log
python attempts/A235-no-vv/code/summarise235.py > $LOG/summarise235.log 2>&1
echo DONE >> $LOG/summarise235.log
