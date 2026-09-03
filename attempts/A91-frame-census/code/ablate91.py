"""A91 exact ablation of the census filters (labelled counts, all EXACT)."""
from __future__ import annotations

import json
import math
import os

import census91 as C

RESULTS = C.RESULTS


def total(level, cap, both_cap):
    C.CAP = cap
    C._BOTH = both_cap
    tot = 0.0
    for (ov, tv, nf) in C.shapes():
        v = C.shape_value(ov, tv, nf, level)
        if v:
            tot += v * float(C.label_mult(ov, tv, nf))
    return tot


def main():
    out = {}
    # raw: roles only (no mask filter at all): 12^(#open+#tangent-ish)
    raw0 = 0.0
    raw1 = 0.0
    for (ov, tv, nf) in C.shapes():
        so, st = sum(ov), sum(tv)
        m = float(C.label_mult(ov, tv, nf))
        # colours per square with NO wall/both filter: open 3*4=12, tangent 3*3=9,
        # free 5;  slots = sum over open of (1 or 2) -> the raw L1 bound uses the
        # maximal 7 terminals per slot of frame_census.md section 3
        raw0 += m * 12.0 ** so * 9.0 ** st * 5.0 ** nf
        nsl = 2.0 * so                              # every open intruder D-type
        raw1 += m * 12.0 ** so * 9.0 ** st * 5.0 ** nf * 7.0 ** nsl
    out['raw_L0_no_filter'] = raw0
    out['raw_L1_section3_bound'] = raw1
    for name, cap in (('R1a_wallcap_off', 99), ('R1_full', 3)):
        for lev in ('L0', 'L1'):
            out['%s_%s' % (name, lev)] = total(lev, cap, 1)
    C.CAP = 3
    print(json.dumps(out, indent=1))
    with open(os.path.join(RESULTS, 'ablation91.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    return out


if __name__ == '__main__':
    main()
