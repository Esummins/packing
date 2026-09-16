#!/usr/bin/env bash
# A240 -- resume block: the whole campaign is recomputable in ~2 min (1 python at a time, BelowNormal set inside).
cd "$(dirname "$0")/../../.." || exit 1
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
A=attempts/A240-cross
python $A/code/cross240.py        # results/cross240.jsonl (13 s)
python $A/code/summarise240.py    # results/cross240.md
python $A/code/pages240.py        # docs/residue_map/campaigns/A240-cross/*.svg (geometry-checked)
python $A/code/test240.py         # 5 checks
python lean/audit.py              # lake build + AUDIT.md (~5 min); Statements/Open/Cross.lean
