"""
A59: the ALIVE-side arbiter applied to the trump5 chain and its SIBLINGS (A57 T7 / Lemma A57-3,
extended to multi-core nodes and NO-families).

Lemma A57-3.  If Q_1..Q_k are admissible closed unit squares in [0,s0]^2, pairwise disjoint with
a strictly positive gap, each strictly disjoint from every core of the node and each outside
every NO-family of the node, then every feasible mu has mu(total) >= k.  Hence tau* >= k, and if
k >= budget NO certificate for the node can exist -- the node is LP-unkillable, whatever compute
is spent on it.

The witness family used here is Trump's own six free squares, scaled about the origin by
lambda = s0/s_T (A57 T8's repair: the unscaled six only touch, and mu is atomic).  The exact
scaled placements are read from A57's banked artefact
    attempts/A57-shadow-trees/results/alive/trump5_strict.json
whose certified pairwise min gap is 144937745660574462730629449381/1370664603569846904878201000000000000
= 1.0574e-7 > 0.  Everything below is exact rational arithmetic.
"""
import json, math, os, sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
sys.path.insert(0, HERE)

from caselp import q, t_lo, t_hi
from alivewitness import gap_exact, admissible_exact

STRICT = os.path.join(ATT, "A57-shadow-trees", "results", "alive", "trump5_strict.json")
NAMES = ["sq4", "sq6", "sq7", "sq8", "sq9", "sq10"]


def trump_strict_six():
    """the six exact scaled placements: [(name, (cx, cy), t)] as Fractions."""
    d = json.load(open(STRICT))
    assert d["result"] == "ALIVE-CERTIFIED" and d["m"] == 6
    return [(NAMES[i], (Fr(s["cx"]), Fr(s["cy"])), Fr(s["t"])) for i, s in enumerate(d["squares"])], \
           Fr(d["min_gap"]) if "min_gap" in d else None


def in_nofam_exact(fam, c, t):
    x0, x1 = q(fam.x0), q(fam.x1)
    y0, y1 = q(fam.y0), q(fam.y1)
    if not (x0 <= c[0] <= x1 and y0 <= c[1] <= y1):
        return False
    for (a, b) in fam.thetas:
        if t_lo(a) <= t <= t_hi(b):
            return True
        # theta and theta + 90 are the same square: t <-> (1-t)/(1+t)
        t2 = (1 - t) / (1 + t)
        if t_lo(a) <= t2 <= t_hi(b):
            return True
    return False


def alive_verdict(hyp, budget, tag=None):
    """exact A57-3 verdict for a node.  Returns a record dict."""
    six, gmin = trump_strict_six()
    fam, dropped = [], []
    for (nm, c, t) in six:
        if not admissible_exact(c, t):
            dropped.append((nm, "not admissible at s0")); continue
        bad = None
        for i, core in enumerate(hyp.cores):
            g = gap_exact(c, t, Fr(1, 2), (core.kx, core.ky), core.tm, core.a)
            if g <= 0:
                bad = "meets core %d (gap %s)" % (i, str(g)); break
        if bad is None:
            for j, f in enumerate(hyp.nofams):
                if in_nofam_exact(f, c, t):
                    bad = "inside NO-family %d" % j; break
        if bad is None:
            fam.append((nm, c, t))
        else:
            dropped.append((nm, bad))
    # exact pairwise gap of the retained family
    pg = None
    for i in range(len(fam)):
        for j in range(i + 1, len(fam)):
            g = gap_exact(fam[i][1], fam[i][2], Fr(1, 2), fam[j][1], fam[j][2], Fr(1, 2))
            pg = g if pg is None else min(pg, g)
    ok = (pg is None or pg > 0)
    k = len(fam)
    if not ok:
        verdict = "NO-WITNESS (retained family is not strictly disjoint)"
    elif k >= budget:
        verdict = "ALIVE-CERTIFIED (tau* >= %d >= budget %d: no certificate can exist)" % (k, budget)
    else:
        verdict = "not alive by this family (k = %d < budget %d): tau* >= %d only" % (k, budget, k)
    return dict(tag=tag, budget=budget, witness_family=[f[0] for f in fam], k=k,
                min_pairwise_gap=(str(pg) if pg is not None else None),
                min_pairwise_gap_float=(float(pg) if pg is not None else None),
                dropped=dropped, alive_verdict=verdict,
                unkillable=bool(ok and k >= budget),
                source=os.path.relpath(STRICT, ATT))
