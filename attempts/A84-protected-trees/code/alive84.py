"""
A84 `alive84.py` -- the A57-3 ALIVE gate, run over the IMAGES of a protected class.

Lemma A57-3 (alivewitness.py, verbatim).  If Q_1..Q_k are admissible closed unit squares in
[0,s0]^2, pairwise disjoint with a strictly positive gap, each strictly disjoint from every core
of the node and outside every NO-family, then tau*(node) >= k.  So k >= budget makes the node
PROVABLY uncertifiable.

A60 used ONE witness family (Trump's six scaled free squares).  A protected class S has G_S = 2
Trump images realising its pins, and EACH gives a family of N = 11 - k_S free squares.  The
lemma applies to each family separately, so

    k = max_g k_g,     unkillable  iff  any_g k_g >= budget,
    a box is ATTEMPTABLE iff EVERY image has k_g < budget.

The families are read only from this attempt's `results/witnesses_<cls>.json`, written and
exactly re-verified by class84.py (the analogue of A57's trump5_strict.json).  Everything below
is exact rational arithmetic.
"""
import json, os, sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

from caselp import q, t_lo, t_hi
from alivewitness import gap_exact, admissible_exact

RES = os.path.join(BASE, "results")
_CACHE = {}


def load_witnesses(cls):
    """-> {image_key: [(name, (cx, cy), t), ...]} exact, in Trump-index order."""
    if cls in _CACHE:
        return _CACHE[cls]
    p = os.path.join(RES, "witnesses_%s.json" % cls)
    d = json.load(open(p))
    out = {}
    for g, im in d["images"].items():
        assert im["ok"], "%s image %s failed exact verification" % (cls, g)
        out[g] = [(s["name"], (Fr(s["cx"]), Fr(s["cy"])), Fr(s["t"])) for s in im["squares"]]
    _CACHE[cls] = out
    return out


def in_nofam_exact(fam, c, t):
    """A59 alive59.in_nofam_exact, verbatim (theta and theta + 90 are the same square)."""
    x0, x1 = q(fam.x0), q(fam.x1)
    y0, y1 = q(fam.y0), q(fam.y1)
    if not (x0 <= c[0] <= x1 and y0 <= c[1] <= y1):
        return False
    for (a, b) in fam.thetas:
        if t_lo(a) <= t <= t_hi(b):
            return True
        t2 = (1 - t) / (1 + t)
        if t_lo(a) <= t2 <= t_hi(b):
            return True
    return False


def alive_verdict(hyp, budget, cls, tag=None):
    """exact A57-3 verdict over every image of the class.

    -> dict(k, unkillable, per_image={g: dict(k, family, dropped, min_pairwise_gap)},
            witness_family (of the best image), dropped (of the best image))"""
    W = load_witnesses(cls)
    per = {}
    for g, six in W.items():
        fam, dropped = [], []
        for (nm, c, t) in six:
            if not admissible_exact(c, t):
                dropped.append((nm, "not admissible at s0"))
                continue
            bad = None
            for i, core in enumerate(hyp.cores):
                gg = gap_exact(c, t, Fr(1, 2), (core.kx, core.ky), core.tm, core.a)
                if gg <= 0:
                    bad = "meets core %d (gap %s)" % (i, str(gg))
                    break
            if bad is None:
                for j, f in enumerate(hyp.nofams):
                    if in_nofam_exact(f, c, t):
                        bad = "inside NO-family %d" % j
                        break
            if bad is None:
                fam.append((nm, c, t))
            else:
                dropped.append((nm, bad))
        pg = None
        for i in range(len(fam)):
            for j in range(i + 1, len(fam)):
                gg = gap_exact(fam[i][1], fam[i][2], Fr(1, 2), fam[j][1], fam[j][2], Fr(1, 2))
                pg = gg if pg is None else min(pg, gg)
        ok = (pg is None or pg > 0)
        per[g] = dict(k=(len(fam) if ok else 0), ok=ok,
                      witness_family=[f[0] for f in fam],
                      dropped=[d[0] for d in dropped],
                      dropped_why=dropped,
                      min_pairwise_gap_f=(float(pg) if pg is not None else None))
    k = max(per[g]["k"] for g in per)
    unk = any(per[g]["k"] >= budget for g in per)
    best = max(per, key=lambda g: per[g]["k"])
    return dict(tag=tag, budget=budget, cls=cls, k=k, unkillable=bool(unk),
                best_image=best, per_image=per,
                witness_family=per[best]["witness_family"],
                dropped=[(n, "") for n in per[best]["dropped"]],
                alive_verdict=("ALIVE-CERTIFIED (tau* >= %d >= budget %d on image %s)"
                               % (k, budget, best) if unk else
                               "not alive by these families (k = %d < budget %d)" % (k, budget)))
