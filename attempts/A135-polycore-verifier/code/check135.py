"""A135 -- sampled soundness controls for the v3 `polycores` clause (A96/A132's discipline:
every exact predicate gets a drawn -> tested -> hits line).

Three controls, all on the polygon that `emitpoly135.py` actually emits:

  A. THE POLYGON.  Draw poses uniformly in the hypothesis box; every certified VERTEX must lie in
     Q(c, theta).  This is the control on `verify_case_v3.point_in_all_poses` (the (P1) check),
     which is itself the proof -- so a hit here would mean the exact test is wrong.
  B. THE EXEMPTION CLAUSE.  Draw random 4-D sub-boxes; whenever `polycore_exempt_frac` accepts,
     draw poses inside that sub-box and check by an INDEPENDENT float SAT that the unit square
     really meets the polygon.  A hit is an unsound exemption -- the failure that would break the
     certificate.
  C. THE NEGATIVE CONTROL.  Count how often the clause REFUSES a sub-box whose poses do all meet
     the polygon, so the measurement is not vacuous (the clause must be conservative, not trivial).

Writes only results/check135.json.
"""
import argparse
import json
import math
import os
import random
import sys
import time
from fractions import Fraction as Fr

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
for _p in (os.path.join(ROOT, "A57-shadow-trees", "code"),
           os.path.join(ROOT, "A132-polygon-core", "code"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import polycore                                                       # noqa: E402
from caselp import Box, t_lo, t_hi                                    # noqa: E402
import verify_case_v3 as v3                                           # noqa: E402


def sat_meets(P, cx, cy, th):
    """INDEPENDENT float SAT: does the closed unit square Q((cx,cy), th) meet the convex polygon P?
    Written from scratch here (projection overlap on the union of both edge-normal families), not
    reusing polycore's vectorised version."""
    c, s = math.cos(th), math.sin(th)
    axes = [(c, s), (-s, c)]
    n = len(P)
    for i in range(n):
        ax, ay = P[i]
        bx, by = P[(i + 1) % n]
        ex, ey = bx - ax, by - ay
        if ex == 0.0 and ey == 0.0:
            continue
        axes.append((ey, -ex))
    for (nx, ny) in axes:
        pp = [nx * px + ny * py for (px, py) in P]
        qc = nx * cx + ny * cy
        h = (abs(nx * c + ny * s) + abs(-nx * s + ny * c)) / 2.0
        if qc - h > max(pp) + 1e-12 or qc + h < min(pp) - 1e-12:
            return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cert", default=os.path.join(BASE, "certs",
                                                   "k5_11_interior_Y1038__poly.json"))
    ap.add_argument("--poses_a", type=int, default=20000)
    ap.add_argument("--subboxes", type=int, default=20000)
    ap.add_argument("--poses_b", type=int, default=20)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    d = json.load(open(a.cert))
    ent = (d["hypotheses"].get("polycores") or [])
    if not ent:
        print("certificate carries no polycores"); return 2
    rep = dict(cert=os.path.relpath(a.cert, ROOT), entries=len(ent), controls=[])
    # the entries are re-certified by the loader itself ((P1) and (P2)); a bad one raises here
    doc, _s, _n, _at, _w, _t = v3.load_certificate_v3(a.cert)
    for pc in doc["_polycores"]:
        bx0, bx1 = float(pc.x0), float(pc.x1)
        by0, by1 = float(pc.y0), float(pc.y1)
        bt0, bt1 = float(pc.t0), float(pc.t1)
        P = [(float(x), float(y)) for (x, y) in pc.verts]
        # ---- A: every vertex in every pose
        drawn = tested = hits = 0
        worst = 0.0
        for _ in range(a.poses_a):
            cx = rng.uniform(bx0, bx1); cy = rng.uniform(by0, by1)
            t = rng.uniform(bt0, bt1); th = 2 * math.atan(t)
            c, sn = math.cos(th), math.sin(th)
            drawn += 1
            for (vx, vy) in P:
                tested += 1
                dx, dy = vx - cx, vy - cy
                u = abs(dx * c + dy * sn); w = abs(-dx * sn + dy * c)
                worst = max(worst, u, w)
                if max(u, w) > 0.5:
                    hits += 1
        rep["controls"].append(dict(control="A vertices in every pose", core=pc.core,
                                    drawn=drawn, tested=tested, hits=hits, max_abs_uv=worst))
        print(f"A: drawn {drawn} -> tested {tested} -> hits {hits} (max |u|,|v| = {worst:.6f})",
              flush=True)
        # ---- B/C: the exemption clause on random sub-boxes
        acc = rej = 0
        b_drawn = b_tested = b_hits = 0
        c_rej_but_all_meet = 0
        for _ in range(a.subboxes):
            w = 10 ** rng.uniform(-3.5, -1.0)
            wt = 10 ** rng.uniform(-4.0, -1.5)
            cx0 = rng.uniform(bx0 - 1.2, bx1 + 1.2); cy0 = rng.uniform(by0 - 1.2, by1 + 1.2)
            t0 = rng.uniform(0.0, 1.0 - wt)
            X0, X1 = Fr(round(cx0 * 10 ** 9), 10 ** 9), Fr(round((cx0 + w) * 10 ** 9), 10 ** 9)
            Y0, Y1 = Fr(round(cy0 * 10 ** 9), 10 ** 9), Fr(round((cy0 + w) * 10 ** 9), 10 ** 9)
            T0, T1 = Fr(round(t0 * 10 ** 9), 10 ** 9), Fr(round((t0 + wt) * 10 ** 9), 10 ** 9)
            ok = v3.polycore_exempt_frac(pc, T0, T1, X0, X1, Y0, Y1)
            samples = []
            for _ in range(a.poses_b):
                scx = rng.uniform(float(X0), float(X1)); scy = rng.uniform(float(Y0), float(Y1))
                st = rng.uniform(float(T0), float(T1))
                samples.append((scx, scy, 2 * math.atan(st)))
            meets = [sat_meets(P, *sm) for sm in samples]
            if ok:
                acc += 1
                b_drawn += len(samples); b_tested += len(samples)
                b_hits += sum(1 for m in meets if not m)
            else:
                rej += 1
                if all(meets):
                    c_rej_but_all_meet += 1
        rep["controls"].append(dict(control="B exemption is sound", core=pc.core,
                                    subboxes=a.subboxes, accepted=acc, rejected=rej,
                                    drawn=b_drawn, tested=b_tested, hits=b_hits))
        rep["controls"].append(dict(control="C conservativeness (not vacuous)", core=pc.core,
                                    rejected=rej, rejected_but_all_poses_meet=c_rej_but_all_meet))
        print(f"B: sub-boxes {a.subboxes} -> accepted {acc} -> drawn {b_drawn} -> tested "
              f"{b_tested} -> hits {b_hits} (an unsound exemption)", flush=True)
        print(f"C: rejected {rej}, of which {c_rej_but_all_meet} have every sampled pose meeting "
              f"the polygon (the clause is conservative, as specified)", flush=True)
    out = os.path.join(BASE, "results", "check135.json")
    json.dump(rep, open(out, "w"), indent=1)
    print("wrote", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
