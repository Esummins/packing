"""A160 T1(a) -- polish the S02 shadow to machine precision so the eps -> 0 limit of f0's slide is
not an artefact of the gallery's six printed decimals.

The gallery configuration (a111lib.S02_FREE, six decimals, worst pair SAT gap -2.9e-7) is refined in
two stages, both READ-ONLY on every campaign:

  1. SLSQP on (s, the free centres, the COMMON tilt) with the slot squares pinned to their slot
     cells at s, minimising s subject to every pair's SAT gap >= 0 and containment -- run for the
     ten-square CORE (f1, f2, f3 + the seven slots) and for all ELEVEN, so that the question "is f0
     load-bearing for s*" is answered by the two minima, not by a label;
  2. a Newton solve of the ACTIVE contact system (the equalities of the contacts SLSQP finds tight)
     on the same variables, which converges to ~1e-16 and is what the slide is measured against.

    python polish160.py [--tag S02]   ->  results/polish160.json
"""
from __future__ import annotations

import argparse, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "attempts", "A116-local-selection-tree", "code"))
import a116lib as A               # noqa: E402
import numpy as np                # noqa: E402
from scipy.optimize import minimize, least_squares   # noqa: E402

RES = os.path.join(BASE, "results")
os.makedirs(RES, exist_ok=True)


def unpack(z, free):
    s = z[0]
    th = z[-1]
    P = {n: (z[1 + 2 * i], z[2 + 2 * i], th) for i, n in enumerate(free)}
    return s, th, P


def all_poses(z, free, slots):
    s, th, P = unpack(z, free)
    for n in slots:
        x, y = A.slot_xy(n, s)
        P[n] = (x, y, 0.0)
    return s, th, P


def cons_vec(z, free, slots):
    s, th, P = all_poses(z, free, slots)
    names = list(free) + list(slots)
    out = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = P[names[i]], P[names[j]]
            out.append(A.sat_gap(a[:2], a[2], b[:2], b[2]))
    h = 0.5 * A.wfun(th)
    for n in free:
        x, y, _ = P[n]
        out += [x - h, s - h - x, y - h, s - h - y]
    return np.array(out)


def solve(free, slots, z0):
    best = None
    for k in range(6):
        z = np.array(z0, dtype=float)
        if k:
            rs = np.random.RandomState(k)
            z[1:-1] += rs.uniform(-0.02, 0.02, len(z) - 2)
            z[-1] += rs.uniform(-0.02, 0.02)
        r = minimize(lambda v: v[0], z, method="SLSQP",
                     constraints=[{"type": "ineq", "fun": lambda v: cons_vec(v, free, slots)}],
                     bounds=[(3.5, 4.2)] + [(0.0, 4.2)] * (len(z) - 2) + [(0.2, 1.3)],
                     options=dict(maxiter=600, ftol=1e-16))
        g = cons_vec(r.x, free, slots)
        if g.min() >= -1e-9 and (best is None or r.x[0] < best[0]):
            best = (float(r.x[0]), r.x.copy(), float(g.min()))
    return best


def newton(free, slots, z, tol=1e-10):
    """Refine on the active set: solve {active gaps = 0} in least squares (the system is square or
    over-determined at a critical configuration), keeping s as a variable."""
    g = cons_vec(z, free, slots)
    act = np.where(g <= 1e-5)[0]
    if len(act) == 0:
        return z, g.min(), act

    def F(v):
        return cons_vec(v, free, slots)[act]

    meth = "lm" if len(act) >= len(z) else "trf"
    r = least_squares(F, z, xtol=1e-15, ftol=1e-15, gtol=1e-15, method=meth, max_nfev=20000)
    return r.x, float(cons_vec(r.x, free, slots).min()), act


def run(tag, which, free, slots, z0):
    b = solve(free, slots, z0)
    if b is None:
        return dict(which=which, ok=False)
    s1, z1, g1 = b
    z2, g2, act = newton(free, slots, z1)
    s2, th2, P2 = all_poses(z2, free, slots)
    return dict(which=which, free=list(free), slots=list(slots),
                s_slsqp=s1, worst_gap_slsqp=g1,
                s=float(s2), tilt_deg=math.degrees(th2), worst_gap=g2,
                n_active=int(len(act)),
                poses={n: [P2[n][0], P2[n][1], math.degrees(P2[n][2])] for n in P2},
                z=list(map(float, z2)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="S02")
    a = ap.parse_args()
    s_sh, P, slots, free = A.shadow_poses(a.tag)
    out = dict(tag=a.tag, gallery_s=s_sh,
               gallery_poses={n: [P[n][0], P[n][1], math.degrees(P[n][2])] for n in P},
               gallery_worst_gap=min(
                   A.sat_gap(P[m][:2], P[m][2], P[n][:2], P[n][2])
                   for i, m in enumerate(P) for n in list(P)[i + 1:]))
    th0 = P[free[0]][2]
    # ELEVEN squares
    z11 = [s_sh] + [v for n in free for v in P[n][:2]] + [th0]
    out["eleven"] = run(a.tag, "eleven", list(free), slots, z11)
    # the TEN-square core (f0 removed)
    core = [n for n in free if n != "f0"]
    z10 = [s_sh] + [v for n in core for v in P[n][:2]] + [th0]
    out["core_no_f0"] = run(a.tag, "core_no_f0", core, slots, z10)
    for k in ("eleven", "core_no_f0"):
        r = out[k]
        print("%-12s s* = %.12f  tilt = %.9f deg  worst gap %.3e  active %d"
              % (k, r["s"], r["tilt_deg"], r["worst_gap"], r["n_active"]))
    out["f0_is_loadbearing_for_s"] = bool(
        out["eleven"]["s"] - out["core_no_f0"]["s"] > 1e-9)
    print("s*(11) - s*(10 core) = %.3e  ->  f0 load-bearing for s*: %s"
          % (out["eleven"]["s"] - out["core_no_f0"]["s"], out["f0_is_loadbearing_for_s"]))
    json.dump(out, open(os.path.join(RES, "polish160.json"), "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
