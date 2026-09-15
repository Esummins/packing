"""A222 SWAP-RIGIDITY of Trump (the uniqueness obligation of ring_swap.md s.1.7): for subsets Y of Trump's
squares (|Y| = 1, 2, 3, every Y containing a corner slot square, plus every pair), search re-packings of |Y|
unit squares inside U(Y) = container minus the other squares (region222: c-space for |Y| = 1 exactly, greedy +
penalty restarts otherwise) and record every placement that DIFFERS from the original (some square of Y not
within 1e-3 of an original pose of Y) and whether it UN-SETTLES a corner (no slot square left at that corner).
Trump here = certs/trump11_certificate.json (side s0 = 969271/250000, slack 4.1e-7 above s-hat).
    python trump222.py      -> results/trump222.jsonl, results/trump222.md
"""
import itertools
import json
import math
import os
import sys
import time
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import region222 as RG        # noqa: E402
import geom217 as G           # noqa: E402

ATT = os.path.abspath(os.path.join(HERE, '..'))
REPO = os.path.abspath(os.path.join(ATT, '..', '..'))
OUT = os.path.join(ATT, 'results', 'trump222.jsonl')
MD = os.path.join(ATT, 'results', 'trump222.md')


def load_trump():
    t = json.load(open(os.path.join(REPO, 'certs', 'trump11_certificate.json'), encoding='utf-8'))
    sq = []
    for q in t['squares']:
        cx, cy, tm = float(Fraction(q['cx'])), float(Fraction(q['cy'])), float(Fraction(q['t']))
        sq.append((cx, cy, 2 * math.atan(tm)))
    s = float(Fraction(t['container_side']))
    return sq, s


def slot_at(sq, s):
    """corner -> index of the slot square there (or None)."""
    out = {}
    for c in G.CORNER_NAMES:
        cx, cy = G.slot_centre(c, s)
        out[c] = next((i for i, (x, y, th) in enumerate(sq) if abs(x - cx) < 1e-6 and abs(y - cy) < 1e-6
                       and G.axis_dev(th) < 1e-6), None)
    return out


def differs(new, old, tol=1e-3):
    """some new pose is not within tol (position and tilt mod 90 deg) of any old pose."""
    for (x, y, th) in new:
        if not any(abs(x - a) < tol and abs(y - b) < tol and G.axis_dev(th - c) < tol for (a, b, c) in old):
            return True
    return False


def unsettles(new, s, corner):
    cx, cy = G.slot_centre(corner, s)
    return not any(abs(x - cx) < 1e-6 and abs(y - cy) < 1e-6 and G.axis_dev(th) < 1e-6 for (x, y, th) in new)


def search(sq, s, Y, restarts=12, rng=None):
    """all distinct placements found for |Y| squares in U(Y): the seeds (old poses) and random restarts."""
    fixed = [sq[i] for i in range(G.N) if i not in Y]
    k = len(Y)
    rng = rng or np.random.default_rng(1)
    found = []
    # one square: exact c-space at 1-degree tilts, every pole recorded
    if k == 1:
        for t in np.arange(0, 90, 1.0):
            pt, d = RG.best_point(RG.cspace(fixed, s, math.radians(t)))
            if pt is not None and d > 1e-7:
                z, f = RG.polish(fixed, [(pt[0], pt[1], math.radians(t))], s)
                ok, gap, wall = RG.exact_check(z)
                if ok:
                    found.append([tuple(float(v) for v in z[3 * (G.N - 1):3 * (G.N - 1) + 3])])
    else:
        for t in range(restarts):
            placed = [(rng.uniform(0.5, s - 0.5), rng.uniform(0.5, s - 0.5), rng.uniform(0, math.pi / 2)) for _ in range(k)]
            z, f = RG.polish(fixed, placed, s, iters=400)
            ok, gap, wall = RG.exact_check(z)
            if ok:
                found.append([tuple(float(v) for v in z[3 * i:3 * i + 3]) for i in range(G.N - k, G.N)])
        g = RG.greedy(fixed, s, k, [math.radians(t) for t in range(0, 90, 5)], beam=2)
        if g is not None:
            z, f = RG.polish(fixed, g, s)
            if RG.exact_check(z)[0]:
                found.append([tuple(float(v) for v in z[3 * i:3 * i + 3]) for i in range(G.N - k, G.N)])
    old = [sq[i] for i in Y]
    return {'n_found': len(found), 'n_different': sum(1 for p in found if differs(p, old)),
            'different': [p for p in found if differs(p, old)][:3]}


def main():
    sq, s = load_trump()
    slots = slot_at(sq, s)
    corner_slots = {c: i for c, i in slots.items() if i is not None}
    rows = []
    t0 = time.time()
    subsets = [[i] for i in range(G.N)]
    subsets += [list(p) for p in itertools.combinations(range(G.N), 2)]
    for c, i in corner_slots.items():
        subsets += [sorted([i] + list(p)) for p in itertools.combinations([j for j in range(G.N) if j != i], 2)]
    with open(OUT, 'w', encoding='utf-8') as f:
        for Y in subsets:
            r = search(sq, s, Y)
            r['Y'] = Y
            r['corners_in_Y'] = [c for c, i in corner_slots.items() if i in Y]
            r['unsettles'] = [c for c in r['corners_in_Y'] if any(unsettles(p, s, c) for p in r['different'])]
            rows.append(r)
            f.write(json.dumps(r) + '\n')
    dt = time.time() - t0
    lines = ['# A222 SWAP-RIGIDITY test on Trump (certs/trump11_certificate.json, side %.7f; %d subsets, %.0f s)' % (s, len(rows), dt), '',
             'Trump\'s slot squares: %s.  For each subset Y: re-packings of |Y| squares inside U(Y) found by the region '
             'search (|Y| = 1 exact per tilt; |Y| >= 2 greedy + 12 penalty restarts), those that differ from the '
             'original poses, and those that leave a corner of Y un-settled.' % corner_slots, '',
             '| size | subsets | with a different re-packing | un-settling a corner |', '|---|---|---|---|']
    for k in (1, 2, 3):
        R = [r for r in rows if len(r['Y']) == k]
        lines.append('| %d | %d | %d | %d |' % (k, len(R), sum(1 for r in R if r['n_different']), sum(1 for r in R if r['unsettles'])))
    diff = [r for r in rows if r['n_different']]
    lines += ['', 'Subsets with a different re-packing: ' + (', '.join('%s (%d)' % (r['Y'], r['n_different']) for r in diff[:40]) or 'none')]
    open(MD, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
