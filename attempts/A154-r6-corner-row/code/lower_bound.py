"""A59: a RIGOROUS lower bound on the Level-0 grain count.

The Monte-Carlo headline estimates the effect of the two filters that do not
factor over pairs (capacity caps, full planarity).  To make "the census is
astronomically large" a theorem rather than an estimate, count exactly a
SUB-FAMILY of grains on which both of those filters hold automatically:

    E = empty (no square-square contact), and the six anchor masks are
    pairwise element-DISJOINT and pairwise non-interleaving and pairwise
    coexistent.

  * capacity caps: every anchor element is touched by at most one square,
    and every computed cap is >= 2.                                   [holds]
  * planarity: with no square-square edges, each square is a star attached
    to its own anchor set; the six supports are pairwise disjoint and
    pairwise non-crossing on the boundary cycle, i.e. a non-crossing
    (laminar) family, which is realizable by pairwise disjoint trees inside
    the disc bounded by the cycle.                                    [holds]
  * coexistence / touching window / hop bound: imposed / vacuous.     [holds]

Every member of this family is therefore a grain that survives every hard
filter, so its exact count is a lower bound for the census.
"""
import json
import os

import numpy as np

import geomlib as G
import count_exact as CE
from census import build_masks, build_tables

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, '..', 'results')


def main():
    g = G.Geometry()
    adm, BX = build_masks(g)
    n = len(adm)
    COEX, INTER, TOUCH, MIND = build_tables(adm, BX)
    DISJ = np.zeros((n, n), bool)
    for a in range(n):
        for b in range(n):
            DISJ[a, b] = (adm[a] & adm[b]) == 0
    # w = 1  ->  exactly one admissible edge status (non-edge)
    W = (COEX & ~INTER & DISJ).astype(float)
    tot, _ = CE.burnside(W)
    print('rigorous lower bound (E = empty, pairwise element-disjoint '
          'non-crossing masks): %d  (%.4e)' % (tot, tot))
    p = os.path.join(RES, 'lower_bound.json')
    json.dump(dict(lower_bound=tot,
                   family='E empty; masks pairwise element-disjoint, '
                          'non-interleaving, coexistent',
                   why_caps='every element used at most once, all caps >= 2',
                   why_planar='non-crossing laminar family of disjoint stars '
                              'inside the boundary disc'), open(p, 'w'), indent=1)
    return tot


if __name__ == '__main__':
    main()
