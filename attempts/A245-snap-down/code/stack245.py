"""A245 Lemma STACK -- the geometry of a MUTUAL wall pair, sampled exactly.

Wall frame u = 0, corner c at v = 0, c' at v = s (s < 4).  B (theta, ell) and B' (theta', ell') touch the
wall (H-WALL).  MUTUAL: B meets c00 = (0,1)^2 and c'01 = (0,1) x (s-2, s-1); B' meets c'00 = (0,1) x (s-1, s)
and c01 = (0,1) x (1, 2); interiors disjoint.  Per sample: the ORDER (ell < ell'), the CLEARANCE
y_V' - y_T (< 4 - s), and -- with ell' lowered to the CONTACT value by bisection -- whether the resting
pair still satisfies the cells, the contact TYPE (V'onLT, TonV'R', TonL'V', V'onTR, flush, T=V'), the
handedness pair and the stack height H = ell' + sin' - ell + cos.
    python stack245.py [--n 4000] [--seed 1]     -> results/stack245.jsonl, results/stack245_summary.json
"""
import argparse
import json
import math
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom245 as G      # noqa: E402

RES = os.path.join(HERE, '..', 'results')
SIDES = (3.82, 3.877084, 3.95, 3.99)


def cells(s):
    return G.wall_cells(s)


def mutual(B, Bp, s):
    """the four cell conditions of the mutual supply, exactly (open-cell meeting = SAT gap < 0)."""
    c = cells(s)
    return tuple(bool(v) for v in (G.meets(B, c['c00']), G.meets(B, c["c'01"]),
                                   G.meets(Bp, c["c'00"]), G.meets(Bp, c['c01'])))


def contained(p, s):
    return G.wall_gap(p, s) >= -G.TOL


def contact_ell(th, ell, thp, s):
    """the least ell' >= ell at which B' (thp, ell') is interior-disjoint from B (theta, ell); the pair
    gap is monotone in ell' (B below B': a non-vertical separating line stays separating as B' rises)."""
    B = G.wall_pose(th, ell)
    lo, hi = ell - math.cos(th) + math.cos(thp), s + 2.0       # B' bottom at B's bottom: overlapping
    if G.pair_gap(B, G.wall_pose(thp, lo)) >= 0:
        return None
    for _ in range(60):
        mid = (lo + hi) / 2
        if G.pair_gap(B, G.wall_pose(thp, mid)) >= 0:
            hi = mid
        else:
            lo = mid
    return hi


def named_verts(th, ell):
    co, si = math.cos(th), math.sin(th)
    L = np.array((0.0, ell))
    V = L + (si, -co)
    R = V + (co, si)
    T = L + (co, si)
    return {'L': L, 'V': V, 'R': R, 'T': T}


def _seg_dist(p, a, b):
    d = b - a
    t = float(np.clip((p - a) @ d / (d @ d), 0.0, 1.0))
    return float(np.linalg.norm(p - (a + t * d)))


def contact_type(th, ell, thp, ellp, tol=1e-6):
    """which vertex of which square rests on which edge of the other (all pairs at distance <= tol)."""
    A, Bv = named_verts(th, ell), named_verts(thp, ellp)
    out = []
    for vn, edges, own in (('T', (("L'V'", Bv['L'], Bv['V']), ("V'R'", Bv['V'], Bv['R'])), A),
                           ("V'", (('LT', A['L'], A['T']), ('TR', A['T'], A['R'])), Bv)):
        p = own[vn.replace("'", '')]
        for en, a, b in edges:
            if _seg_dist(p, a, b) <= tol:
                out.append(vn + 'on' + en)
    if abs(th - thp) <= 1e-9 and out:
        out = ['flush:' + '+'.join(out)]
    if np.linalg.norm(A['T'] - Bv['V']) <= tol:
        out = ["T=V'"]
    return '+'.join(out) if out else 'none'


def predicted(th, thp):
    """the table of the note: who arrives first (theta + theta' vs 90 deg) and who catches whom."""
    d = th + thp - math.pi / 2
    if abs(d) <= 1e-9:
        return "T=V' | TonL'V' | V'onLT"
    if d > 0:
        return "TonL'V'" + (" | V'onTR" if thp < th else '') + (' | flush' if abs(th - thp) < 1e-9 else '')
    return "V'onLT" + (" | TonV'R'" if th > thp else '') + (' | flush' if abs(th - thp) < 1e-9 else '')


def sample(rng, s):
    """a mutual pair candidate: (theta, ell) admissible for B, (theta', ell') for B' (cells necessary
    conditions), then the exact test."""
    th = rng.choice([0.0, math.pi / 2]) if rng.random() < 0.04 else rng.uniform(0.0, math.pi / 2)
    if rng.random() < 0.08:
        thp = th
    else:
        thp = rng.choice([0.0, math.pi / 2]) if rng.random() < 0.04 else rng.uniform(0.0, math.pi / 2)
    co, si = math.cos(th), math.sin(th)
    lo, hi = max(co, s - 2 - si), 1 + co
    if lo >= hi:
        return None
    ell = rng.uniform(lo, hi)
    cop, sip = math.cos(thp), math.sin(thp)
    lo2, hi2 = max(s - 1 - sip, ell), min(2 + cop, s - sip)
    if lo2 >= hi2:
        return None
    ellp = rng.uniform(lo2, hi2)
    return th, ell, thp, ellp


def analyse(th, ell, thp, ellp, s):
    B, Bp = G.wall_pose(th, ell), G.wall_pose(thp, ellp)
    m = mutual(B, Bp, s)
    row = {'s': s, 'th': math.degrees(th), 'ell': ell, 'thp': math.degrees(thp), 'ellp': ellp,
           'mutual': all(m), 'cells': m, 'contained': contained(B, s) and contained(Bp, s),
           'disjoint': bool(G.pair_gap(B, Bp) >= 0)}
    if not (row['mutual'] and row['contained'] and row['disjoint']):
        return row
    yT, yVp = ell + math.sin(th), ellp - math.cos(thp)
    row.update({'order_ok': ell < ellp, 'clearance': yVp - yT, 'clear_lt_4ms': bool(yVp - yT < 4 - s),
                'hand': G.handedness(th) + G.handedness(thp),
                'B_meets_c01': bool(G.meets(B, cells(s)['c01'])),
                'Bp_meets_cp01': bool(G.meets(Bp, cells(s)["c'01"]))})
    ec = contact_ell(th, ell, thp, s)
    if ec is None:
        row.update({'ell_contact': None, 'contact_cells_ok': False, 'contact_type': 'n/a',
                    'predicted': predicted(th, thp), 'H_contact': float('nan'),
                    'chord_sum': G.chord(th) + G.chord(thp),
                    'H_sample': ellp + math.sin(thp) - ell + math.cos(th)})
        return row
    Bc = G.wall_pose(thp, ec)
    mc = mutual(B, Bc, s)
    row.update({'ell_contact': ec, 'contact_cells_ok': bool(all(mc) and contained(Bc, s)),
                'contact_type': contact_type(th, ell, thp, ec), 'predicted': predicted(th, thp),
                'H_contact': ec + math.sin(thp) - ell + math.cos(th),
                'chord_sum': G.chord(th) + G.chord(thp),
                'H_sample': ellp + math.sin(thp) - ell + math.cos(th)})
    return row


def summarise(rows, tried):
    hands, types = {}, {}
    for r in rows:
        hands[r['hand']] = hands.get(r['hand'], 0) + 1
        key = '%s %s' % (r['hand'], r['contact_type'].split(':')[0].split('+')[0])
        types[key] = types.get(key, 0) + 1

    def matches(r):
        ts = r['contact_type'].replace('flush:', '').split('+')
        return r['contact_type'] == 'none' or any(t in r['predicted'] for t in ts)
    return {
        'n': len(rows), 'tried': tried,
        'order_ok': sum(r['order_ok'] for r in rows), 'clear_lt_4ms': sum(r['clear_lt_4ms'] for r in rows),
        'max_clearance': max(r['clearance'] for r in rows), 'min_clearance': min(r['clearance'] for r in rows),
        'gap_pairs': sum(r['clearance'] > 0 for r in rows),
        'B_meets_c01': sum(r['B_meets_c01'] for r in rows), 'Bp_meets_cp01': sum(r['Bp_meets_cp01'] for r in rows),
        'contact_cells_ok': sum(r['contact_cells_ok'] for r in rows),
        'contact_matches_table': sum(matches(r) for r in rows),
        'contact_none': sum(r['contact_type'] == 'none' for r in rows),
        'hands': hands, 'types': dict(sorted(types.items())),
        'H_contact_min': min(r['H_contact'] for r in rows), 'H_contact_max': max(r['H_contact'] for r in rows),
        'H_minus_chords_min': min(r['H_contact'] - r['chord_sum'] for r in rows)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=4000)
    ap.add_argument('--seed', type=int, default=1)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    os.makedirs(RES, exist_ok=True)
    out = open(os.path.join(RES, 'stack245.jsonl'), 'w', encoding='utf-8')
    summ = {}
    for s in SIDES:
        rows, tried = [], 0
        while len(rows) < a.n and tried < 40 * a.n:
            tried += 1
            smp = sample(rng, s)
            if smp is None:
                continue
            r = analyse(*smp, s)
            if r['mutual'] and r['contained'] and r['disjoint']:
                rows.append(r)
                out.write(json.dumps(r) + '\n')
        summ[str(s)] = summarise(rows, tried)
        print(s, json.dumps(summ[str(s)]))
    out.close()
    json.dump(summ, open(os.path.join(RES, 'stack245_summary.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
