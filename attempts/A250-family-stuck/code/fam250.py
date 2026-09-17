"""A250: FAMILIES of pairwise interior-disjoint border cells, and the FAMILY-STUCK condition.

Lemma CELLS (`ring_swap.md` s.1.3, Lean `cells_swap`): if a family Pi of pairwise interior-disjoint
unit cells has |M(Pi)| <= |Pi| (M(Pi) = the squares whose interiors meet a cell of Pi), the packing
exchanges at the SAME side into one containing every cell of Pi as a square.  So the hypothesis a
k0 argument may assume is

    FAMILY-STUCK:  |M(Pi)| > |Pi|  for EVERY family Pi of pairwise disjoint border cells,

not A244's TWELVE-STUCK (which is only the |Pi| = 1 rows).  |Pi| = 2 (a "domino") asks 3 distinct
meeters, |Pi| = 3 asks 4, ...  Which cells are disjoint depends on the side: on each wall the two
middle slots (c01 and c''01, the two facing slots) OVERLAP below side 4 and are disjoint at s >= 4;
all other pairs of the twelve cells are disjoint for every s >= 3.  Hence the conflict graph is a
perfect matching on the eight slots below 4 (max family 8) and empty at s >= 4 (max family 12).
"""
import itertools
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts/A244-twelve-stuck/code'))

import cells244 as C                                             # noqa: E402

CELLS = list(C.CELLS)
IDX = {c: i for i, c in enumerate(CELLS)}


def rect(name, s):
    return C.cell_rect(name, s)


SYM = {'00': (0.0, 1.0, 0.0, 1.0), '01': (0.0, 1.0, 1.0, 2.0), '10': (1.0, 2.0, 0.0, 1.0)}


def rect_sym(name):
    """the cell's (x0, x1, y0, y1) as affine pairs (a, b) meaning a + b*s -- exact, so that a
    comparison of two cell edges is ONE linear expression in s (no interval dependency)."""
    c, k = name[:2], name[2:]
    u0, u1, v0, v1 = SYM[k]
    if c == 'BL':
        return ((u0, 0), (u1, 0), (v0, 0), (v1, 0))
    if c == 'BR':
        return ((-u1, 1), (-u0, 1), (v0, 0), (v1, 0))
    if c == 'TR':
        return ((-u1, 1), (-u0, 1), (-v1, 1), (-v0, 1))
    return ((u0, 0), (u1, 0), (-v1, 1), (-v0, 1))


def overlaps(a, b, s, tol=0.0):
    """do the INTERIORS of cells a, b overlap at side s (by more than tol)?"""
    ax0, ax1, ay0, ay1 = rect(a, s)
    bx0, bx1, by0, by1 = rect(b, s)
    return (min(ax1, bx1) - max(ax0, bx0) > tol) and (min(ay1, by1) - max(ay0, by0) > tol)


def conflicts(s, tol=0.0):
    """the set of unordered index pairs of cells that are NOT interior-disjoint at side s."""
    out = set()
    for i in range(len(CELLS)):
        for j in range(i + 1, len(CELLS)):
            if overlaps(CELLS[i], CELLS[j], s, tol):
                out.add((i, j))
    return out


def is_family(idxs, conf):
    """are the cells (indices) pairwise disjoint?"""
    return all((i, j) not in conf for i, j in itertools.combinations(sorted(idxs), 2))


def families(s, kmax=12, kmin=1, tol=0.0):
    """every family of pairwise disjoint border cells with kmin <= |Pi| <= kmax, as index tuples."""
    conf = conflicts(s, tol)
    out = []
    for k in range(kmin, kmax + 1):
        for comb in itertools.combinations(range(len(CELLS)), k):
            if is_family(comb, conf):
                out.append(comb)
    return out


def max_family_size(s, tol=0.0):
    conf = conflicts(s, tol)
    best = 0
    for k in range(len(CELLS), 0, -1):
        for comb in itertools.combinations(range(len(CELLS)), k):
            if is_family(comb, conf):
                return k
    return best


def family_report(meeters, s, kmax=12, tol=0.0):
    """meeters: {cell name -> list of square indices that MEET it}.  Returns the worst deficiency
    over all disjoint families with |Pi| <= kmax: for each family, |M(Pi)| - |Pi| (family-stuck
    needs >= 1 everywhere), the worst family, and the list of all violating families."""
    conf = conflicts(s, tol)
    sets = [set(meeters.get(c, ())) for c in CELLS]
    worst, arg, bad = None, None, []
    for k in range(1, kmax + 1):
        for comb in itertools.combinations(range(len(CELLS)), k):
            if not is_family(comb, conf):
                continue
            u = set()
            for i in comb:
                u |= sets[i]
            d = len(u) - k
            if worst is None or d < worst:
                worst, arg = d, comb
            if d <= 0:
                bad.append({'cells': [CELLS[i] for i in comb], 'meeters': sorted(u)})
    return {'min_excess': worst, 'argmin': [CELLS[i] for i in (arg or ())],
            'family_stuck': bool(worst is not None and worst >= 1),
            'n_violating': len(bad), 'violating': bad[:40]}


def rows(s, kmax=3, tol=0.0):
    """the optimiser's rows: (tuple of cell indices, need) with need = |Pi| + 1, for every disjoint
    family with |Pi| <= kmax (kmax = 3 is the brief's singles + dominoes + triples)."""
    return [(f, len(f) + 1) for f in families(s, kmax=kmax, tol=tol) if len(f) + 1 <= 11]


# ---------------------------------------------------------------- named families of interest
def corner_triples():
    return [tuple(IDX['%s%s' % (c, k)] for k in C.KINDS) for c in C.CORNERS]


def dominoes():
    out = []
    for c in C.CORNERS:
        for k in ('01', '10'):
            out.append((IDX['%s00' % c], IDX['%s%s' % (c, k)]))
    return out


def boxes_family():
    return tuple(IDX['%s00' % c] for c in C.CORNERS)


def describe(idxs):
    return '{' + ','.join(CELLS[i] for i in idxs) + '}'


if __name__ == '__main__':
    for s in (3.82, 3.877084, 3.99, 4.0, 4.2, 4.6):
        conf = conflicts(s)
        print('s=%.6f  conflicting pairs %2d %s  max family %d  #fam<=3 %d  #fam(all) %d' % (
            s, len(conf), sorted(describe(p) for p in conf)[:6], max_family_size(s),
            len(families(s, kmax=3)), len(families(s))))
