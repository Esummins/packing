"""A250 THE COUNT: the exact minimum number of unit squares an incidence structure needs in order
to satisfy FAMILY-STUCK under the proved lemmas, by integer programming; plus the corpus test.

Variables: one per cell-set a single square may realise.  By PROJECTION [T, A247] that is exactly a
subset of one corner neighbourhood N_c = {c00, c01, c10, c'10, c''01} (c' the corner at the other
end of c's floor, c'' at the other end of c's wall); every subset is realisable below side 4 with an
exact witness (A247 s.2.1), and at s >= 4 only subsets of size <= 4 are (MAX-FIVE).

Constraints:
  FAMILY   for every family Pi of pairwise disjoint border cells: #{squares meeting a cell of Pi}
           >= |Pi| + 1  (Lemma CELLS: <= |Pi| exchanges, so family-stuck needs > |Pi|);
  NSS      NOT-SELF-SUFFICIENT [T, A246]: at most one square has {c00, c01, c10};
  TWOFAR   TWO-FAR [T, A247]: at most one square has {c00, g} for a far slot g of N_c.

min sum x is then a LOWER BOUND on n for a family-stuck packing, valid for every n and depending
only on those [T] lemmas.  `--regime below4` uses the 1295 families of s in [3, 4), `--regime at4`
the 4095 families of s >= 4.
"""
import argparse
import itertools
import json
import os
import sys

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts/A244-twelve-stuck/code'))
sys.path.insert(0, HERE)

import cells244 as C                                             # noqa: E402
import fam250 as FM                                              # noqa: E402
from search244 import belownormal                                # noqa: E402

CELLS = FM.CELLS
IDX = FM.IDX
# N_c: own box, own wall slot, own floor slot, the far floor slot, the far wall slot.
NBR = {'BL': ('BL00', 'BL01', 'BL10', 'BR10', 'TL01'),
       'BR': ('BR00', 'BR01', 'BR10', 'BL10', 'TR01'),
       'TR': ('TR00', 'TR01', 'TR10', 'TL10', 'BR01'),
       'TL': ('TL00', 'TL01', 'TL10', 'TR10', 'BL01')}
FAR = {c: (NBR[c][3], NBR[c][4]) for c in NBR}


def catalogue(maxcells=5):
    """every realisable cell-set, as a sorted tuple of cell indices (the empty set dropped)."""
    out = set()
    for c in C.CORNERS:
        ids = [IDX[x] for x in NBR[c]]
        for k in range(1, min(maxcells, 5) + 1):
            for comb in itertools.combinations(ids, k):
                out.add(tuple(sorted(comb)))
    return sorted(out)


def build(regime='below4', kmax=12, maxcells=5, corner_only=False):
    s = 3.9 if regime == 'below4' else 4.2
    fams = FM.families(s, kmax=kmax)
    if corner_only:          # RAISE only needs families that contain a CORNER cell
        boxes = set(FM.boxes_family())
        fams = [f for f in fams if set(f) & boxes]
    cat = catalogue(maxcells)
    A, lo, hi = [], [], []
    for f in fams:
        row = [1.0 if set(t) & set(f) else 0.0 for t in cat]
        A.append(row)
        lo.append(len(f) + 1.0)
        hi.append(np.inf)
    for c in C.CORNERS:
        trip = {IDX['%s00' % c], IDX['%s01' % c], IDX['%s10' % c]}
        A.append([1.0 if trip <= set(t) else 0.0 for t in cat])
        lo.append(0.0)
        hi.append(1.0)
        for g in FAR[c]:
            pair = {IDX['%s00' % c], IDX[g]}
            A.append([1.0 if pair <= set(t) else 0.0 for t in cat])
            lo.append(0.0)
            hi.append(1.0)
    return cat, fams, np.array(A), np.array(lo), np.array(hi)


def solve(regime='below4', kmax=12, maxcells=5, extra=None, verbose=True, corner_only=False):
    cat, fams, A, lo, hi = build(regime, kmax, maxcells, corner_only)
    rows = [LinearConstraint(A, lo, hi)]
    if extra is not None:
        e = extra(cat)
        rows.extend(e if isinstance(e, list) else [e])
    r = milp(c=np.ones(len(cat)), constraints=rows, integrality=np.ones(len(cat)),
             bounds=Bounds(0, 20))
    if not r.success:
        return {'regime': regime, 'kmax': kmax, 'status': r.message, 'n_min': None,
                'n_types': len(cat), 'n_families': len(fams)}
    x = np.round(r.x).astype(int)
    sol = [(FM.describe(cat[i]), int(x[i])) for i in np.nonzero(x)[0]]
    out = {'regime': regime, 'kmax': kmax, 'maxcells': maxcells, 'n_types': len(cat),
           'n_families': len(fams), 'n_min': int(round(r.fun)), 'solution': sol,
           'corner_only': corner_only}
    if verbose:
        print('%-7s kmax %2d types %3d families %4d%s ->  n_min = %2d   %s' % (
            regime, kmax, len(cat), len(fams), ' CORNER' if corner_only else '      ', out['n_min'],
            ' '.join('%s x%d' % t for t in sol)), flush=True)
    return out


# ---------------------------------------------------------------- extra layers
ROT = {'BL': 'BR', 'BR': 'TR', 'TR': 'TL', 'TL': 'BL'}
REF = {'BL': 'BL', 'BR': 'TL', 'TL': 'BR', 'TR': 'TR'}
SWAP = {'00': '00', '01': '10', '10': '01'}


def _act(cell, m):
    c, k = cell[:2], cell[2:]
    return '%s%s' % (m[c], SWAP[k])


def d4_images(cells):
    """the 8 D4 images of a set of cell names (rotation by 90 deg CCW; reflection in y = x)."""
    out, cur = set(), tuple(cells)
    for r in range(4):
        out.add(frozenset(cur))
        out.add(frozenset(_act(x, REF) for x in cur))
        cur = tuple(_act(x, ROT) for x in cur)
    return out


def d4_pairs(a, b):
    """the 8 D4 images of an unordered pair of cell-sets, moved together."""
    out, ca, cb = set(), tuple(a), tuple(b)
    for r in range(4):
        for m in (None, REF):
            xa = ca if m is None else tuple(_act(x, m) for x in ca)
            xb = cb if m is None else tuple(_act(x, m) for x in cb)
            out.add(frozenset({frozenset(xa), frozenset(xb)}))
        ca = tuple(_act(x, ROT) for x in ca)
        cb = tuple(_act(x, ROT) for x in cb)
    return out


def slotmet_rows(cat):
    """SLOT-MET (A246 [T-computed] at depth >= eta): each own slot is met by one of its corner's
    own meeters."""
    A, lo, hi = [], [], []
    for c in C.CORNERS:
        for k in ('01', '10'):
            need = {IDX['%s00' % c], IDX['%s%s' % (c, k)]}
            A.append([1.0 if need <= set(t) else 0.0 for t in cat])
            lo.append(1.0)
            hi.append(np.inf)
    return LinearConstraint(np.array(A), np.array(lo), np.array(hi))


def pairkill_rows(cat, path='attempts/A247-perimeter-walk/results/pairs247_window_exact_0.05.jsonl'):
    """A247's 62 certified INFEASIBLE cell-set pairs at level (0.05, 0.07) on the window, D4-closed:
    two squares cannot carry those two cell-sets at once."""
    key = {frozenset(t2): i for i, t2 in enumerate(
        [tuple(CELLS[j] for j in t) for t in cat])}
    kills = set()
    for line in open(os.path.join(ROOT, path)):
        r = json.loads(line)
        if r.get('status') != 'INFEASIBLE':
            continue
        sets = [sp[2] if sp[0] == 'M' else sp[1] for sp in r['specs']]
        kills |= d4_pairs(sets[0], sets[1])
    A, lo, hi = [], [], []
    for pr in sorted(kills, key=lambda p: sorted(map(sorted, p))):
        ts = sorted(pr, key=lambda t: sorted(t))
        if any(t not in key for t in ts):
            continue
        row = [0.0] * len(cat)
        for t in ts:
            row[key[t]] += 1.0
        A.append(row)
        lo.append(0.0)
        hi.append(1.0)
    return LinearConstraint(np.array(A), np.array(lo), np.array(hi)), len(kills)


def ladder():
    """the count as the family level rises: kmax = 1 is TWELVE-STUCK, kmax = 12 is FAMILY-STUCK."""
    out = []
    for regime, mc in (('below4', 5), ('at4', 4)):
        for kmax in (1, 2, 3, 4, 6, 8, 12):
            out.append(solve(regime, kmax, mc))
    for regime, mc in (('below4', 5), ('at4', 4)):
        r = solve(regime, 12, mc, corner_only=True)
        r['layer'] = 'corner-cell families only (RAISE)'
        out.append(r)
    for kmax in (1, 12):
        r = solve('below4', kmax, 5, extra=slotmet_rows)
        r['layer'] = 'slotmet'
        out.append(r)
        r = solve('below4', kmax, 5, extra=lambda cat: pairkill_rows(cat)[0])
        r['layer'] = 'pairkills'
        out.append(r)
        r = solve('below4', kmax, 5,
                  extra=lambda cat: [slotmet_rows(cat), pairkill_rows(cat)[0]])
        r['layer'] = 'slotmet+pairkills'
        out.append(r)
    return out


def structure(regime='below4', n=9, kmax=12, maxcells=5):
    """the shape of the SMALLEST family-stuck incidence structures: with the total fixed at n, the
    exact min and max of a few structural functionals (each an ILP over the same constraints)."""
    cat, fams, A, lo, hi = build(regime, kmax, maxcells)
    tot = LinearConstraint(np.ones((1, len(cat))), [n], [n])
    boxes = set(FM.boxes_family())
    funcs = {
        'free_squares': [0.0 if set(t) & boxes else 1.0 for t in cat],
        'five_cell_squares': [1.0 if len(t) == 5 else 0.0 for t in cat],
        'meeters_of_BL': [1.0 if IDX['BL00'] in t else 0.0 for t in cat],
        'cross_corner_squares': [1.0 if len({CELLS[i][:2] for i in t}) > 1 else 0.0 for t in cat],
        'adj_suppliers': [1.0 if (set(t) & boxes) and len({CELLS[i][:2] for i in t}) > 1 else 0.0
                          for t in cat]}
    out = {'regime': regime, 'n': n, 'n_solutions_note': 'min/max over all structures with n squares'}
    for nm, f in funcs.items():
        vals = []
        for sgn in (1.0, -1.0):
            r = milp(c=sgn * np.array(f), constraints=[LinearConstraint(A, lo, hi), tot],
                     integrality=np.ones(len(cat)), bounds=Bounds(0, 20))
            vals.append(None if not r.success else int(round(sgn * r.fun)))
        out[nm] = vals
        print('  n=%d %-22s min %s max %s' % (n, nm, vals[0], vals[1]), flush=True)
    return out


def corpus(kmax=12):
    """the family condition on A244's certified twelve-stuck packings and A217's witnesses."""
    import collections
    out = {}
    for name, path in (('A244_twelve_stuck', 'attempts/A244-twelve-stuck/results/twelve244.jsonl'),
                       ('A217_witnesses', 'attempts/A217-torque-probe/results/witnesses217.jsonl')):
        rs = [json.loads(l) for l in open(os.path.join(ROOT, path)) if l.strip()]
        n, fs, ps, ts = 0, 0, 0, 0
        dom = collections.Counter()
        exc = collections.Counter()
        sides = []
        for r in rs:
            if 'z' not in r:
                continue
            n += 1
            z = r['z']
            sides.append(float(z[33]))
            ms = C.meeter_sets(z)
            rep = FM.family_report(ms, float(z[33]), kmax=kmax)
            fs += rep['family_stuck']
            exc[rep['min_excess']] += 1
            pair = FM.family_report(ms, float(z[33]), kmax=2)
            ps += pair['family_stuck']
            ts += FM.family_report(ms, float(z[33]), kmax=1)['family_stuck']
            for d in FM.dominoes():
                if len(set(ms[CELLS[d[0]]]) | set(ms[CELLS[d[1]]])) <= 2:
                    dom[FM.describe(d)] += 1
        out[name] = {'n': n, 'sides': [min(sides), max(sides)], 'twelve_stuck': ts,
                     'pair_stuck': ps, 'family_stuck': fs,
                     'min_excess_hist': dict(sorted(exc.items())),
                     'stuck_dominoes': dict(dom.most_common())}
        print(name, json.dumps(out[name])[:400], flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--what', default='all', choices=('all', 'count', 'corpus'))
    a = ap.parse_args()
    belownormal()
    res = {}
    if a.what in ('all', 'count'):
        res['ladder'] = ladder()
        res['structure'] = [structure('below4', n) for n in (9, 10, 11)]
    if a.what in ('all', 'corpus'):
        res['corpus'] = corpus()
    p = os.path.join(ATT, 'results', 'count250.json')
    json.dump(res, open(p, 'w'), indent=1)
    print('wrote', p)


if __name__ == '__main__':
    main()
