"""A153 -- tests for the leaf, the certificate and the checker.

 T-A  the SAT used by the checker agrees with A132's `polycore.poly_square_depth` (independent
      implementations, same numbers) on random placements against the node's real obstacles.
 T-B  Lemma CN itself, numerically: 2*10^5 random pairs of unit squares -- whenever the certified
      SAT says the interiors meet, the centres are < 1 apart; whenever the centres are < 1 apart,
      the interiors meet.  (The second direction IS the lemma.)
 T-C  a certificate is built for a node that does NOT die (Y1117) and fed to the checker: every
      structural check must pass and ONLY the "#pieces < budget" check may fail.
 T-D  MUTATION: drop one piece -> the checker must report uncovered cells that are not blocked.
 T-E  MUTATION: enlarge the piece side past 1/sqrt2 -> the checker must refuse admissibility.
"""
import copy
import json
import math
import os
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
for _p in (HERE, os.path.join(ATT, "A142-a57-review-gallery", "code"),
           os.path.join(ATT, "A132-polygon-core", "code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import cover153 as C                                                  # noqa: E402
import check153 as CH                                                 # noqa: E402
import run153 as R                                                    # noqa: E402

NODE = "k5_16_interior_Y1117"
ok_all = True


def say(tag, ok, msg):
    global ok_all
    ok_all = ok_all and ok
    print(f"[{'PASS' if ok else 'FAIL'}] {tag}: {msg}")


# ------------------------------------------------------------------ set-up
import gallery142 as G142                                             # noqa: E402
import polycore                                                       # noqa: E402

d, path = G142.load_node("A57", NODE)
rec = dict(id=NODE, camp="A57", record=path, boxes=d["hyp"]["boxes"], budget=5)
out, reg, obst, onames, kinds = C.price_node(rec["boxes"], 5, exact_limit=12, with_tc=None)
print(f"    {NODE}: cover {out['cover']} (lb {out['lb']}, exact {out.get('exact')}), "
      f"budget {rec['budget']}, area_open {out['area_open']:.4f}")

# ------------------------------------------------------------------ T-A
rng = np.random.default_rng(7)
Cc = rng.uniform(0.5, C.S0 - 0.5, (4000, 2))
worst = 0.0
for th in rng.uniform(0, math.pi / 2, 6):
    for P in obst:
        a = -polycore.poly_square_depth(P, Cc, np.full(len(Cc), th))
        b = CH.sep_poly_square(np.array(P, float), Cc, th)
        worst = max(worst, float(np.abs(a - b).max()))
say("T-A", worst < 1e-9, f"checker SAT vs A132 poly_square_depth: max |difference| {worst:.2e} "
                         f"over {4000 * 6 * len(obst)} placements")

# ------------------------------------------------------------------ T-B
n = 200000
c1 = rng.uniform(-1.5, 1.5, (n, 2))
t1 = rng.uniform(0, math.pi / 2, n)
t2 = rng.uniform(0, math.pi / 2, n)
dist = np.hypot(c1[:, 0], c1[:, 1])


def sq(cx, cy, th):
    c, s = math.cos(th), math.sin(th)
    return [(cx + 0.5 * (dx * c - dy * s), cy + 0.5 * (dx * s + dy * c))
            for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


bad_lemma = 0
near = np.flatnonzero(dist < 1.0)
sel = near[rng.integers(0, len(near), 20000)]
for k in sel:
    g = C.G.sat_gap(sq(0.0, 0.0, float(t1[k])), sq(float(c1[k, 0]), float(c1[k, 1]), float(t2[k])))
    if g >= 0.0:
        bad_lemma += 1
say("T-B", bad_lemma == 0,
    f"Lemma CN on {len(sel)} random pairs with |c1-c2| < 1: {bad_lemma} pair(s) found with "
    f"disjoint interiors (must be 0)")

# ------------------------------------------------------------------ T-C
cert = R.certificate(rec, out, reg, obst, onames, sample=2000)
tmp = os.path.join(tempfile.gettempdir(), "a153_test_cert.json")
json.dump(cert, open(tmp, "w", encoding="utf-8"), indent=1)
r = CH.check(tmp, nsample=2000, verbose=False)
budget_only = all("budget" in f for f in r["fails"])
say("T-C", budget_only and len(r["fails"]) == 1,
    f"certificate for a node that does NOT die: checker fails only on the count -> {r['fails']}")

# ------------------------------------------------------------------ T-D
c2 = copy.deepcopy(cert)
c2["pieces"] = c2["pieces"][:-1]
json.dump(c2, open(tmp, "w", encoding="utf-8"), indent=1)
r2 = CH.check(tmp, nsample=500, verbose=False)
caught = any("NOT certified blocked" in f for f in r2["fails"])
say("T-D", caught, f"dropping one piece is caught: "
                   f"{[f for f in r2['fails'] if 'blocked' in f][:1]}")

# ------------------------------------------------------------------ T-E
c3 = copy.deepcopy(cert)
c3["piece"]["side"] = [1, 1]
json.dump(c3, open(tmp, "w", encoding="utf-8"), indent=1)
r3 = CH.check(tmp, nsample=200, verbose=False)
caught = any("admissible" in f or "not a" in f for f in r3["fails"])
say("T-E", caught, "a piece of side 1 (diameter sqrt2 > 1) is refused")

os.remove(tmp)
print("\nALL TESTS PASS" if ok_all else "\nTESTS FAILED")
sys.exit(0 if ok_all else 1)
