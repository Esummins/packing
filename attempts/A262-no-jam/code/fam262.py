"""A262: the exact 12-cell ALL-FAMILIES test (A250's fam250.family_report, imported, never edited) for a list of
square vertex arrays at side s, plus the exact packing check.  A square MEETS a cell iff the SAT depth of their
intersection is > tol (open intersection).  family_stuck <=> |M(Pi)| >= |Pi| + 1 for EVERY family Pi of pairwise
interior-disjoint border cells (below side 4: 4 boxes + one slot per wall at most).
"""
import os
import sys

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts/A250-family-stuck/code'))
sys.path.insert(0, os.path.join(ROOT, 'attempts/A259-normal-room/code'))
import fam250 as FM                                                   # noqa: E402
import geom259 as Z                                                   # noqa: E402


def cell_poly(name, s):
    x0, x1, y0, y1 = FM.rect(name, s)
    return np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], float)


def meeters(Vs, s, tol=1e-9):
    out = {}
    for c in FM.CELLS:
        P = cell_poly(c, s)
        out[c] = [i for i, V in enumerate(Vs) if -Z.poly_gap(V, P) > tol]
    return out


def packing_margin(Vs, s):
    m = min(Z.contain_margin(V, s) for V in Vs)
    for i in range(len(Vs)):
        for j in range(i):
            m = min(m, Z.poly_gap(Vs[i], Vs[j]))
    return float(m)


def report(Vs, s, tol=1e-9):
    M = meeters(Vs, s, tol)
    r = FM.family_report(M, s)
    return dict(min_excess=r['min_excess'], argmin=r['argmin'], family_stuck=r['family_stuck'],
                n_violating=r['n_violating'], meeters={k: v for k, v in M.items()}, packing_margin=packing_margin(Vs, s))
