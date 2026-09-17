#!/usr/bin/env bash
# A247 phase B (after the pair table): the walk counts with the table, the conditional type-F lists, pages, summary,
# then the triple searches over the type-F list (resumable; logs/STOP stops them).  One python at a time.
set -u
export PYTHONDONTWRITEBYTECODE=1
HERE="$(cd "$(dirname "$0")" && pwd)"; ATT="$(cd "$HERE/.." && pwd)"; cd "$ATT"
T="results/pairs247_window_exact_0.05.jsonl"
python code/walks247.py --pairs "$T" --list-cap 0
python code/walks247.py --pairs "$T" --slotmet --list-cap 0
python code/walks247.py --pairs "$T" --type-f --list-cap 1500000
python code/walks247.py --pairs "$T" --type-f --slotmet --list-cap 1500000
python code/pages247.py
python code/summarise247.py > /dev/null
echo PHASE_B_DONE
[ -f logs/STOP ] && exit 0
python code/triples247.py --walks results/walks247_window_exact_0.05_typef_slotmet.jsonl --eta 0.05 --eta-avoid 0.07 --budget 200000
python code/summarise247.py > /dev/null
echo TRIPLES_DONE
