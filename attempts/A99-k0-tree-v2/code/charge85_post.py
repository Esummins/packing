"""charge85_post.py -- A85 chore: post-analysis of charge85 + an independent
soundness check of the Trump TL canary.

(1) VALIDATION.  Recompute the certified dead rectangles of Trump's TL corner
    pair (the point-box canary) and check, against the exact 11-square Trump
    packing mapped into the same BL frame, that NO Trump square meets any of
    them.  A hit would falsify the certificate: the rectangles are supposed to
    be unreachable by any legal unit square disjoint from the two intruders,
    and Trump's other nine squares are exactly such squares.

(2) CAP VARIANTS.  The PI's cap question ("max offset g for an OTHER corner
    plus three minimum-charge non-JAM corners") is reported by charge85.py; a
    minimum-charge triple turns out not to bite, so this script also prices the
    variants that do: three median non-JAM corners, three JAM corners (Trump's
    own pattern), and four OTHER corners of the same offset bin.

Writes results/charge85.summary.json only.  One process, OMP_NUM_THREADS=1.
"""
from __future__ import annotations

import os
import sys

for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[_v] = '1'

import json
import math
from collections import defaultdict
from decimal import Decimal, getcontext
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import charge85 as C                                              # noqa: E402

RES = C.RES
E = float(C.E_S0)
G_BINS = C.G_BINS


# ------------------------------------------------------------ (1) validation
def sq_corners(cx, cy, th_deg):
    c, s = math.cos(math.radians(th_deg)), math.sin(math.radians(th_deg))
    return [(cx + c * u - s * v, cy + s * u + c * v)
            for (u, v) in ((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5))]


def sat_disjoint(A, B):
    """True iff convex polygons A, B are separated on some edge normal (sound
    one-way test: separation => disjoint)."""
    for P, Q in ((A, B), (B, A)):
        n = len(P)
        for i in range(n):
            x0, y0 = P[i]
            x1, y1 = P[(i + 1) % n]
            ax, ay = (y1 - y0), -(x1 - x0)
            sp = max(ax * x + ay * y for (x, y) in P)
            sq = min(ax * x + ay * y for (x, y) in Q)
            if sq > sp + 1e-12:
                return True
    return False


def validate_trump():
    getcontext().prec = 200
    d = json.load(open(os.path.join(C.ATT, 'A03-upper-reconstruct',
                                    'trump11_exact.json')))
    s = float(Decimal(d['s']))
    si = float(Decimal(d['sin_theta']))
    th_t = math.degrees(math.asin(si))
    # BL frame: (x, y) -> (x, s - y), theta -> 90 - theta (mod 90)
    sqs = []
    for k, sq in enumerate(d['squares']):
        cx, cy = float(Decimal(sq['cx'])), float(Decimal(sq['cy']))
        thd = math.degrees(float(Decimal(sq['theta'])))     # radians in the file
        sqs.append((k, cx, s - cy, (90.0 - thd) % 90.0))
    assert abs(max(abs(t[3] % 90.0) for t in sqs)) > 0.0 and abs(th_t) > 0.0
    hyps, meta, _s = C.trump_TL_hyp()
    r = C._one_cell(hyps)
    cells = r['cells_pass']
    hits = []
    for (x0, y0, x1, y1) in cells:
        R = [(float(x0), float(y0)), (float(x1), float(y0)),
             (float(x1), float(y1)), (float(x0), float(y1))]
        for (k, cx, cy, th) in sqs:
            if not sat_disjoint(R, sq_corners(cx, cy, th)):
                hits.append(dict(cell=[str(x0), str(y0), str(x1), str(y1)],
                                 square=k, cx=cx, cy=cy, th=th))
    return dict(n_cells=len(cells), area=str(r['area']), area_f=float(r['area']),
                n_hits=len(hits), hits=hits[:8],
                PASS=(len(hits) == 0),
                note='a hit would mean a Trump square meets a cell certified '
                     'unreachable -- i.e. a falsified certificate')


# ------------------------------------------------------------ (2) cap variants
def main():
    recs = [json.loads(l) for l in
            open(os.path.join(RES, 'charge85.pairs.jsonl'))]
    by = defaultdict(list)
    for r in recs:
        by[r['stratum']].append(r['charge_f'])
    nonjam = sorted(v for k in by if k != 'JAM' for v in by[k])
    jam = sorted(by.get('JAM', []))
    m_nonjam = nonjam[0]
    med_nonjam = nonjam[len(nonjam) // 2]
    m_jam = jam[0] if jam else 0.0

    out = dict(E_s0=E, s0=float(C.S0),
               min_nonJAM=m_nonjam, median_nonJAM=med_nonjam, min_JAM=m_jam)
    caps = {}
    for name, triple in (('3x min non-JAM', 3 * m_nonjam),
                         ('3x median non-JAM', 3 * med_nonjam),
                         ('3x min JAM (Trump pattern)', 3 * m_jam)):
        head = E - triple
        rows = {}
        for (lo, hi) in G_BINS:
            key = 'OTHER[%.1f,%.1f)' % (lo, hi)
            v = sorted(by.get(key, []))
            if not v:
                continue
            rows[key] = dict(
                bin_min=v[0], bin_median=v[len(v) // 2], bin_max=v[-1],
                head=head,
                every_pair_dead=(v[0] > head),      # SOUND kill for the whole bin
                some_pair_dead=(v[-1] > head))
        caps[name] = dict(triple=triple, head_for_OTHER=head, per_bin=rows,
                          any_bin_fully_dead=any(r['every_pair_dead']
                                                 for r in rows.values()))
    # four OTHER corners of the same bin
    allother = {}
    for (lo, hi) in G_BINS:
        key = 'OTHER[%.1f,%.1f)' % (lo, hi)
        v = sorted(by.get(key, []))
        if v:
            allother[key] = dict(four_min=4 * v[0], four_median=4 * v[len(v) // 2],
                                 four_max=4 * v[-1],
                                 all_dead=(4 * v[0] > E), some_dead=(4 * v[-1] > E))
    caps['4x same-bin OTHER'] = allother
    out['caps'] = caps

    # D4 four-corner orbit fractions on several pools
    pools = dict(all=[r['charge_f'] for r in recs],
                 nonJAM=nonjam,
                 OTHER=[r['charge_f'] for r in recs
                        if r['stratum'].startswith('OTHER')],
                 OTHER_g_ge_0p3=[r['charge_f'] for r in recs
                                 if r['stratum'].startswith('OTHER')
                                 and r['g'] is not None and r['g'] >= 0.3])
    fc = {}
    for pk, pv in pools.items():
        if not pv:
            continue
        fc[pk] = {}
        for tn, T in (('E_s0', E), ('3.5', 3.5)):
            g, t = C.four_corner_orbits(pv, T)
            fc[pk][tn] = dict(n_pool=len(pv), orbits_dead=g, orbits_total=t,
                              fraction=g / t)
    out['four_corner_orbits'] = fc

    print('=== validating the Trump TL canary against the real packing ===',
          flush=True)
    out['trump_validation'] = validate_trump()
    print('  PASS=%s  %d cells, %d hits' % (out['trump_validation']['PASS'],
                                            out['trump_validation']['n_cells'],
                                            out['trump_validation']['n_hits']),
          flush=True)
    p = os.path.join(RES, 'charge85.summary.json')
    json.dump(out, open(p, 'w'), indent=1)
    print('wrote', p)


if __name__ == '__main__':
    main()
