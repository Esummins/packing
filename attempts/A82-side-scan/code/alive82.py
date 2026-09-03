r"""
A82 (a) -- the ALIVE GATE at side m.

A57's alivewitness lemma (disjoint-family bound): if Q_1..Q_r are unit squares inside
[0,m]^2 that are pairwise disjoint with a STRICTLY positive gap and strictly disjoint from
every pin core, then every feasible measure of the node LP has mu(Q_i) >= 1, so
tau*(class, m) >= r.  With r = budget = 11 - k the node is LP-UNKILLABLE at side m
(A57 lemma; the quarantined k5_16_m5.json lesson: unkillable needs r >= budget, a smaller
family is a lower bound only).

This module measures, per (class, side m):
    m_fam(m)  = the largest strictly-separated family found at side m
    min_gap   = its exact rational separation margin
and, per class, the shrink study
    s_fit     = the smallest side at which a full budget-size family was still found.

Geometry is A65 crowdfam.py's (imported read-only); the two differences are that the
container side and the pin slots are BOTH parameters, and that the acceptance test is
STRICT positivity (crowdfam allowed touching, since it measured interior-disjointness).

Seeds: (A) Trump-image -- take the symmetry image of Trump's packing whose upright squares
realise the class's pin pattern, keep the N non-pin squares, and RELOCATE them to side m by
the A56 P3 anchor rule (gap anchoring on the family's own coordinates: a square above the
threshold rides the moving wall, one below stays put), which is the standard normalisation;
then max-min inflate against the side-m pins.  (B) blind multistart at side m.

    python code\alive82.py --classes k4_08 --blind 20
"""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse                                                     # noqa: E402
import json                                                         # noqa: E402
import math                                                         # noqa: E402
import sys                                                          # noqa: E402
import time                                                         # noqa: E402
from fractions import Fraction as Fr                                # noqa: E402

import numpy as np                                                  # noqa: E402
from scipy.optimize import least_squares, minimize                  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sides82 import (BASE, BOXSPEC, TRUMP_JSON, S0, S_HAT, SIDES, CLASSES,   # noqa: E402
                     load_spec, pins_at, commit_free_gb)

_HALF = np.array([[-0.5, -0.5], [0.5, -0.5], [0.5, 0.5], [-0.5, 0.5]])


# ------------------------------------------------------------------ float geometry
def corners(X):
    X = np.asarray(X, dtype=float).reshape(-1, 3)
    c, s = np.cos(X[:, 2]), np.sin(X[:, 2])
    R = np.empty((len(X), 2, 2))
    R[:, 0, 0], R[:, 0, 1], R[:, 1, 0], R[:, 1, 1] = c, -s, s, c
    return X[:, None, :2] + np.einsum("kj,nij->nki", _HALF, R)


def normals(X):
    X = np.asarray(X, dtype=float).reshape(-1, 3)
    c, s = np.cos(X[:, 2]), np.sin(X[:, 2])
    return np.stack([np.stack([c, s], -1), np.stack([-s, c], -1)], 1)


def _pairgap(Ca, Na, Cb, Nb):
    AX = np.concatenate([Na, Nb], axis=1)
    pa = np.einsum("mkd,mad->mak", Ca, AX)
    pb = np.einsum("mkd,mad->mak", Cb, AX)
    return np.maximum(pb.min(2) - pa.max(2), pa.min(2) - pb.max(2)).max(1)


def gaps(Xf, Cp, Np_, s):
    Cf, Nf = corners(Xf), normals(Xf)
    n = len(Cf)
    parts = [np.concatenate([Cf[:, :, 0].min(1), Cf[:, :, 1].min(1),
                             s - Cf[:, :, 0].max(1), s - Cf[:, :, 1].max(1)])]
    if n >= 2:
        I, J = np.triu_indices(n, 1)
        parts.append(_pairgap(Cf[I], Nf[I], Cf[J], Nf[J]))
    if len(Cp):
        I = np.repeat(np.arange(n), len(Cp))
        J = np.tile(np.arange(len(Cp)), n)
        parts.append(_pairgap(Cf[I], Nf[I], Cp[J], Np_[J]))
    return np.concatenate(parts)


def per_square_gap(Xf, Cp, Np_, s):
    """(n,) worst constraint gap attributable to each square (for greedy shedding)."""
    Cf, Nf = corners(Xf), normals(Xf)
    n = len(Cf)
    g = np.minimum.reduce([Cf[:, :, 0].min(1), Cf[:, :, 1].min(1),
                           s - Cf[:, :, 0].max(1), s - Cf[:, :, 1].max(1)])
    if n >= 2:
        I, J = np.triu_indices(n, 1)
        pg = _pairgap(Cf[I], Nf[I], Cf[J], Nf[J])
        for a, b, v in zip(I, J, pg):
            g[a] = min(g[a], v)
            g[b] = min(g[b], v)
    if len(Cp):
        I = np.repeat(np.arange(n), len(Cp))
        J = np.tile(np.arange(len(Cp)), n)
        pg = _pairgap(Cf[I], Nf[I], Cp[J], Np_[J]).reshape(n, len(Cp))
        g = np.minimum(g, pg.min(1))
    return g


def pin_arrays(pins_f):
    P = np.array([[a, b, 0.0] for (a, b) in pins_f]).reshape(-1, 3)
    if len(P) == 0:
        return np.zeros((0, 4, 2)), np.zeros((0, 2, 2))
    return corners(P), normals(P)


def polish(Xf, Cp, Np_, s, margin, maxiter=200):
    def res(v):
        return np.maximum(0.0, margin - gaps(v.reshape(-1, 3), Cp, Np_, s))
    r = least_squares(res, np.asarray(Xf, float).ravel(), method="trf", diff_step=1e-9,
                      xtol=3e-16, ftol=3e-16, gtol=3e-16, max_nfev=maxiter)
    return r.x.reshape(-1, 3)


def inflate(Xf, Cp, Np_, s, ladder=(3e-4, 1e-4, 1e-5, 1e-6, 3e-7,
                                    1.2e-7, 5e-8, 1.5e-8, 5e-9), maxiter=400):
    best, bestm = np.asarray(Xf, float), gaps(Xf, Cp, Np_, s).min()
    for mgn in ladder:
        Y = polish(Xf, Cp, Np_, s, mgn, maxiter=maxiter)
        gm = gaps(Y, Cp, Np_, s).min()
        if gm > bestm:
            best, bestm = Y, gm
        if bestm >= 0.9 * mgn:
            break
    return best, bestm


# ------------------------------------------------------------------ Trump seeds
def trump_images():
    """the 8 container symmetries of Trump's packing, at his own side s_trump."""
    T = json.load(open(TRUMP_JSON))
    X = np.array(T["X"], dtype=float)
    st = float(T["s"])
    out = []
    for k in range(8):
        x, y, th = X[:, 0].copy(), X[:, 1].copy(), X[:, 2].copy()
        if k & 1:
            x, th = st - x, -th
        if k & 2:
            y, th = st - y, -th
        if k & 4:
            x, y, th = y.copy(), x.copy(), math.pi / 2 - th
        out.append((k, np.stack([x, y, np.mod(th, math.pi / 2)], 1)))
    return out, st


def _gap_threshold(vals, lo=1.9, hi=2.7):
    """A56 P3 gap anchoring: split point in the widest gap of `vals` inside [lo, hi];
    falls back to the band midpoint when no coordinate lies in the band."""
    v = sorted(x for x in vals if lo <= x <= hi)
    if len(v) < 2:
        return 0.5 * (lo + hi)
    best, bt = -1.0, 0.5 * (lo + hi)
    for a, b in zip(v, v[1:]):
        if b - a > best:
            best, bt = b - a, 0.5 * (a + b)
    return bt


def relocate(Xf, s_from, s_to):
    """standard normalisation (A56 P3): per axis, coordinates above the gap-anchored
    threshold ride the moving wall (beta = 1), the rest stay put (beta = 0)."""
    Y = np.asarray(Xf, float).copy()
    d = s_to - s_from
    for ax in (0, 1):
        thr = _gap_threshold(Y[:, ax])
        Y[Y[:, ax] > thr, ax] += d
    return Y


def trump_seeds(cls, m, spec, pins_f, tol=2e-5):
    """free families seeded from every Trump image whose upright squares realise the
    class's pin pattern AT s0, relocated to side m."""
    imgs, st = trump_images()
    lam = float(S0) / st
    pin0 = [(float(a), float(b)) for a, b in pins_at(cls, S0, spec)]
    out = []
    for k, Z0 in imgs:
        Z = Z0.copy()
        Z[:, :2] *= lam                      # scale to s0: every contact opens ~5e-8
        up = [i for i in range(11) if min(Z[i, 2], math.pi / 2 - Z[i, 2]) < 1e-9]
        used, ok = [], True
        for (px, py) in pin0:
            c = [i for i in up if abs(Z[i, 0] - px) < tol and abs(Z[i, 1] - py) < tol
                 and i not in used]
            if not c:
                ok = False
                break
            used.append(c[0])
        if not ok:
            continue
        fam = [i for i in range(11) if i not in used]
        out.append(("trump-sym%d" % k, relocate(Z[fam], float(S0), m)))
    return out


def blind_seeds(N, m, rng, n_starts):
    out = []
    for _ in range(n_starts):
        out.append(("blind", np.array(
            [[rng.uniform(.5, m - .5), rng.uniform(.5, m - .5), rng.uniform(0, math.pi / 2)]
             for _ in range(N)])))
    return out


# ------------------------------------------------------------------ exact check
def exact_corners(cx, cy, t):
    d = 1 + t * t
    co, si = (1 - t * t) / d, (2 * t) / d
    h = Fr(1, 2)
    return ([(cx + co * ux - si * uy, cy + si * ux + co * uy)
             for ux, uy in ((-h, -h), (h, -h), (h, h), (-h, h))], co, si)


def exact_gap(Ca, axa, Cb, axb):
    """exact max-over-axes SAT separation; > 0 iff strictly disjoint."""
    best = None
    for ax in list(axa) + list(axb):
        pa = [ax[0] * p[0] + ax[1] * p[1] for p in Ca]
        pb = [ax[0] * p[0] + ax[1] * p[1] for p in Cb]
        v = max(min(pb) - max(pa), min(pa) - max(pb))
        best = v if best is None else max(best, v)
    return best


def exact_family_check(Xf, pins_fr, m_fr, D):
    """snap to denominator D and verify STRICT separation exactly.  Returns
    (ok, min_gap Fraction, records)."""
    fam = []
    for (cx, cy, th) in Xf:
        fam.append((Fr(round(cx * D), D), Fr(round(cy * D), D),
                    Fr(round(math.tan(th / 2.0) * D), D)))
    C, AX = [], []
    for (cx, cy, t) in fam:
        cs, co, si = exact_corners(cx, cy, t)
        C.append(cs)
        AX.append([(co, si), (-si, co)])
    h = Fr(1, 2)
    PC = [[(px - h, py - h), (px + h, py - h), (px + h, py + h), (px - h, py + h)]
          for (px, py) in pins_fr]
    PAX = [[(Fr(1), Fr(0)), (Fr(0), Fr(1))]] * len(PC)
    gmin, ok = None, True
    # containment (strict interior of the container is not required, but admissibility is)
    for cs in C:
        for (x, y) in cs:
            g = min(x, y, m_fr - x, m_fr - y)
            gmin = g if gmin is None else min(gmin, g)
            if g < 0:
                ok = False
    for i in range(len(C)):
        for j in range(i + 1, len(C)):
            g = exact_gap(C[i], AX[i], C[j], AX[j])
            gmin = min(gmin, g)
            if g <= 0:
                ok = False
        for j in range(len(PC)):
            g = exact_gap(C[i], AX[i], PC[j], PAX[j])
            gmin = min(gmin, g)
            if g <= 0:
                ok = False
    recs = [dict(cx=str(a), cy=str(b), t=str(c),
                 theta_deg=float(math.degrees(2 * math.atan(float(c)))))
            for (a, b, c) in fam]
    return ok, gmin, recs


def exact_gate(Xf, pins_fr, m_fr):
    for D in (10 ** 6, 10 ** 8, 10 ** 10, 10 ** 12, 10 ** 14):
        ok, gmin, recs = exact_family_check(Xf, pins_fr, m_fr, D)
        if ok:
            return True, D, gmin, recs
    return False, None, gmin, recs


# ------------------------------------------------------------------ the gate
def best_family(N, m, pins_f, seeds, rng, blind_budget, log, keep_blind=8, shed_from=6,
                cell_cap=90.0, carry=None):
    """largest strictly-separated family found at side m; returns (r, Xf, min_gap).

    `carry` = (r, X, s_from), the best family found at the NEXT SMALLER side: a family that
    fits at side m' < m fits at m too (the container only grows and the L-anchored pins do
    not move, while the R-anchored ones move outward), so relocating it forward gives a
    monotone floor and removes the search's non-monotone artifacts."""
    Cp, Np_ = pin_arrays(pins_f)
    best = (0, None, -np.inf)
    if carry is not None:
        r0, X0, s_from = carry
        Y, gm = inflate(relocate(X0, s_from, m), Cp, Np_, m)
        if gm > 0:
            best = (r0, Y, gm)
    blind = []
    t_end = time.time() + blind_budget
    while time.time() < t_end and len(blind) < 200:
        (src, X0), = blind_seeds(N, m, rng, 1)
        X0 = polish(X0, Cp, Np_, m, 0.0, maxiter=150)
        blind.append((gaps(X0, Cp, Np_, m).min(), X0))
    blind.sort(key=lambda z: -z[0])
    cands = list(seeds) + [("blind", X) for _, X in blind[:keep_blind]]

    # phase 1: is the FULL budget-size family feasible?  (the alive gate proper)
    t1 = time.time() + 0.45 * cell_cap
    for src, X0 in cands:
        X, gm = inflate(X0, Cp, Np_, m)
        # SIZE dominates gap: a full-size family with a 1e-7 margin beats a carried
        # (budget-1)-family with a 4e-3 margin.  (Comparing on gap alone made the s0
        # canary cell report 6/7 -- caught by the Trump canary, fixed here.)
        if gm > 0 and (N > best[0] or (N == best[0] and gm > best[2])):
            best = (N, X, gm)
        if time.time() > t1:
            break
    if best[0] == N:
        return best
    # phase 2: greedy shedding -- drop the worst square and re-inflate, N-1, N-2, ...
    t2 = time.time() + 0.55 * cell_cap
    floor = best[0]
    for src, X0 in cands[:shed_from]:
        X = np.asarray(X0, float).copy()
        for r in range(N - 1, floor - 1, -1):
            g = per_square_gap(X, Cp, Np_, m)
            X = np.delete(X, int(np.argmin(g)), axis=0)
            Y, gm = inflate(X, Cp, Np_, m, ladder=(1e-3, 1e-4, 1e-5, 1e-6, 1e-7),
                            maxiter=200)
            if gm > 0:
                if r > best[0] or (r == best[0] and gm > best[2]):
                    best = (r, Y, gm)
                break
            X = Y
            if time.time() > t2:
                break
        if time.time() > t2:
            break
    return best


def _feasible_at(cls, spec, X_seed, s_try, N):
    Cp, Np_ = pin_arrays([(float(a), float(b)) for a, b in
                          pins_at(cls, Fr(s_try).limit_denominator(10 ** 13), spec)])
    best = (None, -np.inf)
    for X0 in (relocate(X_seed[0], X_seed[1], s_try), X_seed[0]):
        Y, gm = inflate(X0, Cp, Np_, s_try)
        if gm > best[1]:
            best = (Y, gm)
        if gm > 0:
            break
    return best


def shrink_study(N, cls, spec, seeds0, rng, budget, log, iters=34):
    """s_fit = smallest side at which a full N-family still survives shrink-and-repair.
    Bisection on [S_LO, s0] (s0 known feasible for every Trump-realised class)."""
    s_hi = float(S0)
    Cp, Np_ = pin_arrays([(float(a), float(b)) for a, b in pins_at(cls, S0, spec)])
    X_hi = None
    for src, X0 in seeds0:
        Y, gm = inflate(X0, Cp, Np_, s_hi)
        if gm > 0:
            X_hi = Y
            break
    if X_hi is None:
        return None, None
    # geometric bracket first (s_fit sits a few 1e-7 below s0 for Trump-realised classes,
    # so a plain bisection of [3.82, s0] burns 17 probes before it even reaches the region)
    s_lo, t_end = 3.82, time.time() + budget
    for d in (1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8):
        s_try = float(S0) - d
        Y, gm = _feasible_at(cls, spec, (X_hi, s_hi), s_try, N)
        if gm > 0:
            s_hi, X_hi = s_try, Y
            break
        s_lo = s_try
        if time.time() > t_end:
            break
    for _ in range(iters):
        if time.time() > t_end or s_hi - s_lo < 1e-12:
            break
        s_mid = 0.5 * (s_lo + s_hi)
        Y, gm = _feasible_at(cls, spec, (X_hi, s_hi), s_mid, N)
        if gm > 0:
            s_hi, X_hi = s_mid, Y
        else:
            s_lo = s_mid
    return s_hi, X_hi


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--classes", nargs="*", default=CLASSES)
    ap.add_argument("--sides", nargs="*", default=SIDES)
    ap.add_argument("--blind", type=float, default=25.0, help="s of blind multistart per cell")
    ap.add_argument("--shrink", type=float, default=180.0, help="s of shrink study per class")
    ap.add_argument("--cell_cap", type=float, default=90.0, help="s cap per (class, side)")
    ap.add_argument("--seed", type=int, default=20260902)
    ap.add_argument("--out", default=os.path.join(BASE, "results", "alive_gate.json"))
    ap.add_argument("--min_headroom", type=float, default=2.5)
    a = ap.parse_args()

    lf = open(os.path.join(BASE, "logs", "alive82.log"), "a", buffering=1, encoding="utf-8")

    def log(*x):
        print(*x, file=lf, flush=True)
        print(*x, flush=True)

    g = commit_free_gb()
    log("=== A82 alive gate; free commit %.2f GB (single light process, ~200 MB)" % g)
    if g < a.min_headroom:
        log("headroom %.2f GB below %.2f: aborting" % (g, a.min_headroom))
        return 2
    spec = load_spec()
    rng = np.random.default_rng(a.seed)
    out = {"generated_by": "alive82.py", "s0": str(S0), "s_hat": S_HAT,
           "note": "m_fam = largest STRICTLY separated family found at side m "
                   "(A57 disjoint-family bound: tau* >= m_fam); alive iff m_fam >= budget",
           "classes": {}}
    if os.path.exists(a.out):                                   # resume completed classes
        try:
            prev = json.load(open(a.out))
            out["classes"] = prev.get("classes", {})
        except Exception:
            pass
    for cls in a.classes:
        if cls in out["classes"] and len(out["classes"][cls].get("rows", [])) >= len(a.sides):
            log("--- %s: already complete, skipping" % cls)
            continue
        cl = spec["classes"][cls]
        N, k = cl["N"], cl["k"]
        rows = []
        seeds_s0 = trump_seeds(cls, float(S0), spec, None)
        log("--- %s (k=%d, budget=%d): %d Trump-image seed(s) at s0"
            % (cls, k, N, len(seeds_s0)))
        s_fit, X_fit = shrink_study(N, cls, spec, seeds_s0, rng, a.shrink, log) \
            if seeds_s0 else (None, None)
        log("    shrink study: s_fit = %s" % ("%.9f" % s_fit if s_fit else "n/a"))
        carry = None                       # monotone floor from the next smaller side
        for ms in sorted({Fr(x) for x in a.sides}):
            m_fr = ms
            ms = str(m_fr)
            m = float(m_fr)
            pins_fr = pins_at(cls, m_fr, spec)
            pins_f = [(float(x), float(y)) for x, y in pins_fr]
            seeds = trump_seeds(cls, m, spec, pins_f)
            if X_fit is not None:
                seeds.append(("shrink", relocate(X_fit, s_fit, m)))
            t0 = time.time()
            r, X, gm = best_family(N, m, pins_f, seeds, rng, a.blind, log,
                                   cell_cap=a.cell_cap, carry=carry)
            if X is not None and r > 0:
                carry = (r, X, m)
            rec = dict(side=ms, side_float=m, budget=N, m_fam=r, min_gap_float=float(gm),
                       alive=bool(r >= N), seconds=round(time.time() - t0, 1),
                       exact=False, denominator=None, min_gap_exact=None,
                       tau_lower_bound=r, eta_lower_bound=r - N)
            # EXACTLY verify whatever family was found, not only the full-size ones: an
            # r-family that is exactly strictly separated is a RIGOROUS lower bound
            # tau*(class, m) >= r, hence eta(m) >= r - budget.  That is what turns the
            # scan's alive column into a theorem about the A60 law.
            if X is not None and r >= 1:
                ok, D, ge, recs = exact_gate(X, pins_fr, m_fr)
                rec.update(exact=bool(ok), denominator=D,
                           min_gap_exact=(str(ge) if ge is not None else None),
                           min_gap_exact_float=(float(ge) if ge is not None else None),
                           squares=recs)
                if not ok:
                    rec["tau_lower_bound"] = None
                    rec["eta_lower_bound"] = None
            rows.append(rec)
            log("    m=%-16s m_fam=%d/%d gap=%9.3e %-9s%s (%.1fs)"
                % (ms, r, N, gm, "ALIVE" if rec["alive"] else "dead-gate",
                   " EXACT@1e%d => tau* >= %d, eta >= %+d"
                   % (round(math.log10(rec["denominator"])), r, r - N)
                   if rec.get("exact") else " (NOT exactly verified)", rec["seconds"]))
        out["classes"][cls] = dict(k=k, budget=N, s_fit=s_fit, rows=rows)
        json.dump(out, open(a.out, "w"), indent=1)
    json.dump(out, open(a.out, "w"), indent=1)
    log("wrote %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
