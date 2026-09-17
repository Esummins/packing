#!/bin/bash
# A243 -- the reach-summary root: design + price only (no cascade was built: notes/reach243.md s.0).
#
#   bash attempts/A243-reach-root/code/run243.sh          # tests (20 s) + price (2-3 min) + page (1 s)
#
# RESUME BLOCK: every step is idempotent and rewrites its outputs (results/reach243.{jsonl,md}, the page); rerun the
# command.  No detached worker, no STOP file needed.  One python process, BelowNormal, affinity 0xFFFF (price243.be_polite).
# Never touches the k5 frontier workers, the frontier loop, A238's sweep, A241's campaign, A242's workers or any cert.
cd "$(dirname "$0")/../../.." || exit 1
A=attempts/A243-reach-root
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1
mkdir -p $A/results $A/logs docs/residue_map/campaigns/A243-reach-root
python $A/code/test243.py 2>&1 | tail -2
python $A/code/price243.py 2>&1 | tail -3
python $A/code/pages243.py
