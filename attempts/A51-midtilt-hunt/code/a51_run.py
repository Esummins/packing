#!/usr/bin/env python
"""a51_run.py -- A51 driver.

Runs the A49 protocol VERBATIM (same code objects: hunt_a49, stratum_a49,
audit_a49, and a49_common with the FIXED `repair_ok`) but re-aimed at the A51
mid-tilt seeds and the A51 results/work/logs directories.  No A49 file is
edited or copied: this module only rebinds `a49_common`'s output directories
(which every A49 driver reads at RUN time via `C.RESULTS` / `C.WORK` /
`C.LOGS`) and, for the negative control, swaps in an A51 control-seed set.

  python a51_run.py census   [--reps N] [--fresh]   -> results/hunt.json
  python a51_run.py control  [--reps N] [--fresh]   -> results/control.json
  python a51_run.py stratum  [--reps N] [--fresh]   -> results/stratum.json
  python a51_run.py lstratum [--reps N] [--fresh]   -> results/stratum_local.json
  python a51_run.py audit    [--recheck ID]         -> results/candidates/

[NUM] float64 throughout -- a hunt, not a certificate run.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
A51 = os.path.abspath(os.path.join(HERE, '..'))
ATT = os.path.abspath(os.path.join(A51, '..'))
A49C = os.path.join(ATT, 'A49-flushfree-hunt', 'code')
for p in (A49C, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import a49_common as C                      # noqa: E402

# --- re-aim the shared machinery at A51's directories (before any A49 driver
#     is imported, because audit_a49 resolves its candidate dir at import).
C.RESULTS = os.path.join(A51, 'results')
C.WORK = os.path.join(A51, 'work')
C.LOGS = os.path.join(A51, 'logs')
for d in (C.RESULTS, C.WORK, C.LOGS):
    os.makedirs(d, exist_ok=True)

D, P, pack11 = C.D, C.P, C.pack11


# --------------------------------------------------------- A51 control seeds
# A49's control jittered three atlas VALLEYs; A51's must exercise the flush
# detector in the MID-TILT regime, so the control set is the mid-tilt atlas
# families the (i) seeds were opened FROM, taken UNOPENED (flush contacts
# intact, at full precision from the A04 catalogue point).  Expected: every
# landing has flush contacts, and the un-jittered base runs hold at their own s.
CONTROL_FAMS = (0, 13, 31)


def control_seeds_a51():
    at = os.path.join(ATT, 'A37-cp-atlas', 'results', 'atlas_final.json')
    with open(at) as f:
        cls_of = {str(e['family_id']): e['class'] for e in
                  json.load(f)['entries']}
    out = []
    for fid in CONTROL_FAMS:
        z, fam, ci = P.load_family(fid)
        out.append({'id': 'CTRL-%d' % fid, 'mode': 'control',
                    'profile': cls_of.get(str(fid), '?'), 'roles': None,
                    'x_a04': [float(v) for v in fam['best_x']],
                    'true_family': str(fid),
                    's_ref': float(fam['s_min'])})
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    task = sys.argv[1]
    rest = sys.argv[2:]
    if task == 'census':
        import hunt_a49 as H
        sys.argv = ['hunt_a49'] + rest
        return H.main()
    if task == 'control':
        import hunt_a49 as H
        H.control_seeds = control_seeds_a51
        sys.argv = ['hunt_a49', '--control'] + rest
        return H.main()
    if task in ('stratum', 'lstratum'):
        import stratum_a49 as S
        sys.argv = (['stratum_a49'] + (['--local'] if task == 'lstratum'
                                       else []) + rest)
        return S.main()
    if task == 'audit':
        import audit_a49 as A
        sys.argv = ['audit_a49'] + rest
        return A.main()
    print('unknown task %r' % task)
    return 2


if __name__ == '__main__':
    sys.exit(main())
