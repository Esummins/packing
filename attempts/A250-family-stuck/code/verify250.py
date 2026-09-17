"""A250 EXACT verification of a FAMILY-STUCK candidate (mpmath interval arithmetic, 40 digits).

Built on A244's `verify244` (same inflation lam -> a genuine packing, same interval depth), with
the family checks added.  Two certified verdicts, each conservative in its own direction:

  FAMILY_STUCK = True   uses the SURE meeters (depth interval entirely > 0) and every family that
                        is not PROVABLY overlapping -- so it only claims |M(Pi)| > |Pi| when that
                        holds for the true meeter sets and for every genuinely disjoint family;
  NOT_FAMILY_STUCK      uses the MAYBE meeters (depth interval reaching above 0) and only families
                        whose cells are PROVABLY pairwise interior-disjoint -- so a witness family
                        with |M(Pi)| <= |Pi| is a certified exchange by Lemma CELLS.

Both use the certified side S' = lam s and A244's certified containment + disjointness.
"""
import itertools
import json
import os
import sys

from mpmath import iv

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts/A244-twelve-stuck/code'))
sys.path.insert(0, HERE)

import cells244 as C                                             # noqa: E402
import verify244 as V                                            # noqa: E402
import fam250 as FM                                              # noqa: E402

iv.dps = 40
N = 11
CELLS = list(C.CELLS)


def cell_overlap_flags(S):
    """for each pair of cells: (sure_overlap, maybe_overlap) at the interval side S."""
    R = V.rects(S)
    sure, maybe = set(), set()
    for i, j in itertools.combinations(range(len(CELLS)), 2):
        ax0, ax1, ay0, ay1 = R[CELLS[i]]
        bx0, bx1, by0, by1 = R[CELLS[j]]
        ox = V.imin(ax1, bx1) - V.imax(ax0, bx0)
        oy = V.imin(ay1, by1) - V.imax(ay0, by0)
        if ox.a > 0 and oy.a > 0:
            sure.add((i, j))
        if ox.b > 0 and oy.b > 0:
            maybe.add((i, j))
    return sure, maybe


def scan(sets, conf, kmax=12):
    """min over disjoint families (conflicts `conf`) of |M(Pi)| - |Pi|, with the argmin."""
    worst, arg, bad = None, None, []
    for k in range(1, kmax + 1):
        for comb in itertools.combinations(range(len(CELLS)), k):
            if any((i, j) in conf for i, j in itertools.combinations(comb, 2)):
                continue
            u = set()
            for i in comb:
                u |= sets[i]
            d = len(u) - k
            if worst is None or d < worst:
                worst, arg = d, comb
            if d <= 0 and len(bad) < 200:
                bad.append({'cells': [CELLS[i] for i in comb], 'meeters': sorted(u)})
    return worst, [CELLS[i] for i in (arg or ())], bad


def certify_family(cent, th, s, kmax=12, lam=None):
    """the full exact verdict for one candidate."""
    base = V.certify(cent, th, s, need=('twelve',), lam=lam)
    L = iv.mpf(repr(base['lam']))
    sq, S = V.build(cent, th, s, L)
    R = V.rects(S)
    sure_sets, maybe_sets = [], []
    depths = {}
    for name in CELLS:
        ds = [V.depth(sq[i], R[name]) for i in range(N)]
        depths[name] = [float(d.a) for d in ds]
        sure_sets.append({i for i in range(N) if ds[i].a > 0})
        maybe_sets.append({i for i in range(N) if ds[i].b > 0})
    sure_ov, maybe_ov = cell_overlap_flags(S)
    w_stuck, arg_stuck, _ = scan(sure_sets, maybe_ov, kmax)          # for a PASS
    w_fail, arg_fail, bad = scan(maybe_sets, sure_ov, kmax)          # for a certified failure
    out = dict(base)
    out.pop('cells', None)
    out.update({
        'kmax': kmax,
        'sure_meeters': {CELLS[i]: sorted(sure_sets[i]) for i in range(len(CELLS))},
        'min_excess_sure': w_stuck, 'argmin_sure': arg_stuck,
        'min_excess_maybe': w_fail, 'argmin_maybe': arg_fail,
        'n_cell_overlaps_sure': len(sure_ov), 'n_cell_overlaps_maybe': len(maybe_ov),
        'FAMILY_STUCK': bool(base['contained'] and base['disjoint'] and w_stuck is not None
                             and w_stuck >= 1),
        'NOT_FAMILY_STUCK': bool(w_fail is not None and w_fail <= 0),
        'witness_families': bad[:12]})
    out['PASS'] = out['FAMILY_STUCK']
    return out


def certify_z(z, kmax=12, lam=None):
    z = [float(v) for v in z]
    cent = [(z[3 * i], z[3 * i + 1]) for i in range(N)]
    th = [z[3 * i + 2] for i in range(N)]
    return certify_family(cent, th, z[33], kmax=kmax, lam=lam)


def main():
    path = sys.argv[1]
    kmax = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    best = None
    for line in open(path):
        if not line.strip():
            continue
        r = json.loads(line)
        if 'z' not in r:
            continue
        c = certify_z(r['z'], kmax)
        print('%-44s s %.6f -> cert %.6f  FAMILY_STUCK=%s  min_excess %s at %s' % (
            str(r.get('rid'))[-44:], r['z'][33], c['s_cert'], c['FAMILY_STUCK'],
            c['min_excess_sure'], FM.describe([FM.IDX[x] for x in c['argmin_sure']])), flush=True)
        if c['FAMILY_STUCK'] and (best is None or c['s_cert'] < best[0]):
            best = (c['s_cert'], r.get('rid'))
    print('best certified FAMILY-STUCK:', best)


if __name__ == '__main__':
    main()
