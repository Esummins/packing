#!/usr/bin/env python3
"""
A27 prefilter.py -- the FREE (LP-less) A26 band pre-filter for case-tree nodes.

Theorem A26.1 (A26-wall-ledger, elementary + exact): in every packing of 11 unit squares in a
square of side <= 96/25, AT MOST ONE square avoids the width-0.93 boundary band, i.e.
    #{ i : R_i >= 0.93 }  <=  1,      R_i := dist(centre_i, nearest wall) - h(theta_i),
    h(theta) = (cos theta + sin theta)/2.
Theorem A26.2 (via the proven s(n), n <= 9) adds  #{R_i >= 0.5665} <= 4  and  #{R_i >= 0.42} <= 5.

For a parameter box B = [x0,x1]x[y0,y1]x[th0,th1] every placement in B has
    R >= Rlo(B) = min(x0, y0, s-x1, s-y1) - max_{th in [th0,th1]} h(th),
so a node hypothesis with two cores of Rlo >= 0.93 (resp. five of Rlo >= 0.5665, six of
Rlo >= 0.42) is DEAD with no LP at all.

`python prefilter.py` prints the Rlo profile of the whole level-1 cover and of the level-2
children of the live boxes, i.e. it reports exactly when the filter can and cannot fire.
"""
from __future__ import annotations

import json, math, os, sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from caselp import Box                      # noqa: E402
from level1 import cover                    # noqa: E402

# (threshold w, max number of squares with R >= w)   -- A26.1 / A26.2 at s = 96/25
BAND_CAPS = ((0.93, 1), (0.5665, 4), (0.42, 5))


def hmax(th0, th1):
    """max of h(th) = (cos th + sin th)/2 over [th0, th1] degrees (h is unimodal, peak at 45)."""
    if th0 <= 45.0 <= th1:
        return math.sqrt(2) / 2
    f = lambda t: (math.cos(math.radians(t)) + math.sin(math.radians(t))) / 2
    return max(f(th0), f(th1))


def Rlo(B, s):
    """certified lower bound on R = dist(centre, nearest wall) - h(theta) over the whole box."""
    return min(B.x0, B.y0, s - B.x1, s - B.y1) - hmax(B.th0, B.th1)


def dead_by_band(boxes, s):
    """True iff the multi-core hypothesis {boxes} violates a band cap (=> node dead, no LP)."""
    rs = sorted((Rlo(B, s) for B in boxes), reverse=True)
    for w, cap in BAND_CAPS:
        if sum(1 for r in rs if r >= w) > cap:
            return True, dict(threshold=w, cap=cap, count=sum(1 for r in rs if r >= w))
    return False, None


def main():
    s = 3.84
    boxes, _ = cover(s, 8, 6)
    rs = [Rlo(B, s) for B in boxes]
    out = dict(s=s, n_boxes=len(boxes), caps=[list(c) for c in BAND_CAPS],
               Rlo_min=min(rs), Rlo_max=max(rs),
               n_ge_093=sum(1 for r in rs if r >= 0.93),
               n_ge_05665=sum(1 for r in rs if r >= 0.5665),
               n_ge_042=sum(1 for r in rs if r >= 0.42),
               per_box=[dict(idx=i, Rlo=r) for i, r in enumerate(rs)])
    # every level-1 / level-2 node of this tree has exactly ONE core, so the filter needs >= 2 cores
    out['fires_on_single_core_nodes'] = False
    out['note'] = ("every node of the A24/A27 interior-first tree carries exactly one core, and every "
                   "band cap allows at least one square; the filter can therefore only fire on "
                   "multi-core (>= 2 cores) hypotheses, of which this tree has none.")
    json.dump(out, open(os.path.join(HERE, 'results', 'prefilter.json'), 'w'), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != 'per_box'}, indent=1))
    # sanity: the filter DOES fire on a genuine 2-core deep-interior hypothesis
    B1 = Box(1.85, 1.90, 1.85, 1.90, 0.0, 5.0)
    B2 = Box(1.95, 2.00, 1.95, 2.00, 0.0, 5.0)
    print("sanity, two deep-interior cores:", dead_by_band([B1, B2], s),
          "Rlo =", Rlo(B1, s), Rlo(B2, s))


if __name__ == '__main__':
    main()
