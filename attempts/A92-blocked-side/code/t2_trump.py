"""A89 / T2 TASK C (canary): corner blockers of Trump's exact certificate.

Source of the exact configuration: attempts/A03-upper-reconstruct/
trump11_exact.json (the file t3lib.load_trump() reads; there is no
certs/trump11_certificate.json in this repo).  60-digit decimals; the
"uprights" 0..5 carry theta = O(1e-71) rad -- the Gauss-Newton residue of an
exactly axis-aligned pose -- and the tilted 6..10 carry the octic angle
theta = 40.1819372903297164652... deg.

Loaded / rattler status uses A87's row machinery + the BRIEF FJ polytope, as in
Task A.

Usage: python t2_trump.py
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from decimal import Decimal, getcontext
from fractions import Fraction

import numpy as np

import a89lib as L

sys.path.insert(0, os.path.join(L.ATT, 'A87-drain-flow', 'code'))
import t3lib as T                                             # noqa: E402
import fjpolish87 as FJ                                       # noqa: E402
import t2_a87 as TA                                           # noqa: E402

CERT = os.path.join(L.ATT, 'A03-upper-reconstruct', 'trump11_exact.json')
OUT = os.path.join(L.RESULTS, 't2_blockers_trump.jsonl')
SUM = os.path.join(L.RESULTS, 't2_summary_trump.json')


def main():
    t0 = time.time()
    print('free commit %.0f MB' % L.free_commit_mb(), flush=True)
    getcontext().prec = 300
    d = json.load(open(CERT))
    z, _dd = T.load_trump()          # 34 Fractions, exact from the decimals

    # EXACT tilt from the stored decimal (300-digit context), in degrees
    pi = Decimal('3.14159265358979323846264338327950288419716939937510582097494459230781640628620899862803482534211706798214808651328230664709384460955058223172535940812848111745028410270193852110555964462294895493038196')
    exact = []
    for i, sq in enumerate(d['squares']):
        th = Decimal(sq['theta'])
        deg = th * 180 / pi
        m = deg % 90
        tilt = min(m, 90 - m)
        exact.append({'square': i, 'theta_decimal': sq['theta'],
                      'theta_deg_300dps': str(deg),
                      'tilt_deg_300dps': str(tilt),
                      'tilt_float': float(tilt),
                      'theta_is_literal_zero': sq['theta'].strip() in ('0', '0.0'),
                      'tilt_lt_1e-12': bool(abs(tilt) < Decimal('1e-12'))})

    # t3lib's INTERVAL wall rows straddle 0 at an exactly flush corner and
    # test_ab then calls the exact point infeasible; A87 (pilot87.normalise_config
    # / fjpolish87.canonical) works around this with a PAD = 1e-9 shift.  Do the
    # same, in exact Fractions, so the row set and the FJ LP can be built.  The
    # shift is a rigid translation: tilts and corner-frame offsets are unchanged.
    PAD = Fraction(1, 10 ** 9)
    zp = list(z)
    for i in range(11):
        zp[3 * i] = Fraction(z[3 * i]) + PAD
        zp[3 * i + 1] = Fraction(z[3 * i + 1]) + PAD
    zp[33] = Fraction(z[33]) + 2 * PAD

    blockers, pt = TA.analyse('trump', zp, {}, exact=True)
    if 'blockers_per_corner' not in pt:
        print('POINT INFEASIBLE for t3lib: %s' % pt.get('point_reason'), flush=True)
        raise SystemExit(1)
    for b in blockers:
        b['source'] = 'Trump-exact'
        b['tilt_deg_300dps'] = exact[b['square']]['tilt_deg_300dps']
        b['tilt_lt_1e-12'] = exact[b['square']]['tilt_lt_1e-12']
        b['theta_is_literal_zero'] = exact[b['square']]['theta_is_literal_zero']
    with open(OUT, 'w') as f:
        for b in blockers:
            f.write(json.dumps(b, default=str) + '\n')

    x0, y0, sig = L.bbox_sigma([float(v) for v in zp])
    boxes = L.corner_boxes(x0, y0, sig)

    slots = []
    for b in blockers:
        cf = b['centre_corner_frame']
        if max(abs(cf[0] - 0.5), abs(cf[1] - 0.5)) < 1e-9 and b['tilt_lt_1e-12']:
            slots.append(b)

    # canary verdict: no Trump corner blocker with tilt in (1e-7, theta_0)
    th0 = {}
    bad = []
    for t in L.THETA0_CANDIDATES:
        v = [b['square'] for b in blockers if 1e-7 < b['tilt_deg'] < t]
        th0['%g' % t] = {'n_in_open_zone': len(v), 'squares': v}
        bad += v
    verdict = 'PASS' if not bad else 'FAIL'

    tl = [b for b in blockers if b['corner'] == 'TL']
    out = {
        'source': 'Trump exact certificate (A03 trump11_exact.json)',
        's_certificate': d['s'],
        'sigma_measured': sig,
        'theta_deg_tilted': d['theta_deg'],
        't_tan_half_theta': d['t_tan_half_theta'],
        'n_blockers': len(blockers),
        'blockers_per_corner': pt['blockers_per_corner'],
        'blockers': [{'square': b['square'], 'corner': b['corner'],
                      'tilt_deg': b['tilt_deg'],
                      'tilt_deg_300dps': b['tilt_deg_300dps'],
                      'tilt_lt_1e-12': b['tilt_lt_1e-12'],
                      'theta_is_literal_zero': b['theta_is_literal_zero'],
                      'centre': b['centre'],
                      'centre_corner_frame': b['centre_corner_frame'],
                      'meeting_margin': b['meeting_margin'],
                      'is_rattler': b['is_rattler'],
                      'loaded_forced': b['loaded_forced'],
                      'loaded_loadable': b['loaded_loadable'],
                      'n_corner_walls_touched': b['n_corner_walls_touched'],
                      'corner_walls_touched': b['corner_walls_touched'],
                      'partners': b['partners'],
                      'contacts': b['contacts']} for b in blockers],
        'exact_tilts_all_11': exact,
        'slot_squares': [{'square': b['square'], 'corner': b['corner'],
                          'centre': b['centre'],
                          'tilt_deg_300dps': b['tilt_deg_300dps'],
                          'tilt_lt_1e-12': b['tilt_lt_1e-12'],
                          'theta_is_literal_zero': b['theta_is_literal_zero']}
                         for b in slots],
        'n_slot_squares': len(slots),
        'TL_crowd': [{'square': b['square'], 'tilt_deg': b['tilt_deg'],
                      'tilt_deg_300dps': b['tilt_deg_300dps'],
                      'centre': b['centre'],
                      'centre_corner_frame': b['centre_corner_frame'],
                      'meeting_margin': b['meeting_margin'],
                      'loaded_forced': b['loaded_forced'],
                      'loaded_loadable': b['loaded_loadable']} for b in tl],
        'theta0_zone_table': th0,
        'canary_verdict_no_blocker_tilt_in_1e-7_to_theta0': verdict,
        'exact_zero_branch_contains_the_slots': bool(len(slots) >= 3),
        'point_record': pt,
        'corner_boxes': {c: list(v) for c, v in boxes.items()},
        'secs': time.time() - t0,
    }
    json.dump(out, open(SUM, 'w'), indent=1, default=str)
    print(json.dumps({k: v for k, v in out.items()
                      if k not in ('blockers', 'point_record', 'exact_tilts_all_11')},
                     indent=1, default=str), flush=True)
    print('CANARY %s   (%.1f s)' % (verdict, time.time() - t0), flush=True)


if __name__ == '__main__':
    main()
