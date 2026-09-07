"""A119 regression: A119's keyed row builder must be row-for-row A116's, and the A119 tree must
reproduce A116's verdicts.  Read-only on A116.

  python xcheck119.py rows        -- LP value of KRows vs a116lib.Rows on random (cell, selection) nodes
  python xcheck119.py tree        -- verdict / certified min / wall of both trees on a few N
"""
from __future__ import annotations
import math, random, sys, time
import a119lib as L
import a116lib as A


def rand_node(rng, bodies, nv, tilted):
    cells = {}
    for b in bodies:
        if b.kind == "free":
            a0, a1 = b.t0, b.t1
            w = (a1 - a0) * rng.uniform(0.05, 1.0)
            lo = rng.uniform(a0, a1 - w)
            cells[b.name] = (lo, lo + w)
    near, far, imp = A.census(bodies, A.S_LO, A.S_HI_DEFAULT, cells)
    fx = {}
    for pr, poss in near.items():
        fx[pr] = poss[rng.randrange(len(poss))]
    return cells, fx


def rows(n=40):
    rng = random.Random(11)
    worst = 0.0
    for tag, cls, r, rho, cut in (("S02", "k5_11", 0.1, 10.0, None), ("S07", "trump5", 0.2, 10.0, 41.565)):
        bodies, nv, s_sh, P = A.build_bodies(tag, cls, r, rho, tilt_floor_deg=cut)
        for it in range(n):
            cells, fx = rand_node(rng, bodies, nv, None)
            qs = {}
            R1 = A.build_lp(bodies, nv, A.S_LO, A.S_HI_DEFAULT, fx, cells, qranges=qs)
            R2 = L.build_krows(bodies, nv, A.S_LO, A.S_HI_DEFAULT, fx, cells, qranges=qs)
            assert len(R1.A) == len(R2.A), (len(R1.A), len(R2.A))
            for a1, a2, b1, b2 in zip(R1.A, R2.A, R1.b, R2.b):
                assert abs(b1 - b2) < 1e-15 and max(abs(a1 - a2)) < 1e-15
            v1 = R1.solve()[0]; v2 = R2.solve()[0]
            d = abs(v1 - v2) if (math.isfinite(v1) and math.isfinite(v2)) else (0.0 if v1 == v2 else 1e9)
            worst = max(worst, d)
            if len(set(R2.keys)) != len(R2.keys):
                dup = [k for k in R2.keys if R2.keys.count(k) > 1]
                raise SystemExit("DUPLICATE ROW KEYS: %s" % dup[:4])
        print("%s/%s: %d random nodes, rows identical, worst |v_A116 - v_A119| = %.3g" % (tag, cls, n, worst))
    print("ROWS OK (keys unique, coefficients bit-identical)")


def tree():
    for tag, cls, r, rho, cut in (("S02", "k5_11", 0.05, 5.0, None),
                                  ("S02", "k5_11", 0.1, 10.0, None),
                                  ("S07", "trump5", 0.2, 10.0, 41.565)):
        bodies, nv, s_sh, P = A.build_bodies(tag, cls, r, rho, tilt_floor_deg=cut)
        _, Pe, _, _ = A.anchored(tag, s_sh)
        ss = A.shadow_selections(bodies, Pe)
        t0 = time.time()
        T1 = A.Tree(bodies, nv, contact_pairs=list(ss), min_cell_deg=0.05, node_cap=2000000,
                    time_cap=1200.0, target=A.S0, tighten_cap=0)
        v1 = T1.run(); w1 = time.time() - t0
        for inh in (False, True):
            t0 = time.time()
            T2 = L.RecTree(bodies, nv, contact_pairs=list(ss), min_cell_deg=0.05,
                           node_cap=2000000, time_cap=1200.0, inherit=inh)
            v2 = T2.run(); w2 = time.time() - t0
            print("%s/%s r=%.2f rho=%.0f | A116 dead=%s nodes=%d cert=%.7f %.1fs || A119(inherit=%s) "
                  "dead=%s nodes=%d lp=%d inh=%d cert=%.7f %.1fs  speedup %.2fx" %
                  (tag, cls, r, rho, v1["dead"], v1["stats"]["nodes"], v1["certified_min"], w1, inh,
                   v2["dead"], v2["stats"]["nodes"], v2["stats"]["lp_calls"],
                   v2["stats"]["dead_inherited"], v2["certified_min"], w2, w1 / max(w2, 1e-9)))
            assert v2["dead"] == v1["dead"], "VERDICT MISMATCH"


if __name__ == "__main__":
    {"rows": rows, "tree": tree}[sys.argv[1]]()
