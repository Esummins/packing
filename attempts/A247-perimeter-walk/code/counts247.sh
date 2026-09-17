#!/usr/bin/env bash
# A247: the walk counts under each set of facts (lemmas only / + SLOT-MET / + the conditional type-F picture),
# and the corpus reproduction check at level 0 (all 764 packings) -- one python at a time.
set -u
export PYTHONDONTWRITEBYTECODE=1
HERE="$(cd "$(dirname "$0")" && pwd)"; ATT="$(cd "$HERE/.." && pwd)"
PAIRS="${1:-results/pairs247_window_exact_0.05.jsonl}"
L0="$ATT/results/lemmas_only_level0.jsonl"
echo '{"key": "none", "status": "FEASIBLE", "eta": 0.0, "eta_avoid": 0.0}' > "$L0"
python "$HERE/walks247.py" --pairs "$L0" --tag lemmas_level0 --corpus --list-cap 0
python "$HERE/walks247.py" --pairs "$L0" --tag lemmas_level0_slotmet --slotmet --list-cap 0
python "$HERE/walks247.py" --pairs "$L0" --tag lemmas_level0_typef --type-f --list-cap 0
python "$HERE/walks247.py" --pairs "$L0" --tag lemmas_level0_typef_slotmet --type-f --slotmet --list-cap 200000
[ -f "$ATT/$PAIRS" ] && python "$HERE/walks247.py" --pairs "$PAIRS" --list-cap 0
