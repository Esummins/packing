"""A19 -- oracles for the hybrid kernel.

Diag: A17's diag_oracle on the HybridKernel shim + a generalised two-measure ratio scan
(numerator measure = g, denominator = w) for seeds.
Pair (localised): disjoint pairs with BOTH squares covering an R-atom -- structured-set scan,
localised tangent sampler, direct pattern-search polish.
"""
import math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "A17-kernel-root"))

from oracle_pair import overlap_depth_many, overlap_depth, admissible_many, _moves
from features import random_placements


# ---------------------------------------------------------------- diag ratio scan (seeds)
def ratio_seeds_g(fm, s, g_atom, dth_deg=0.25, cstep=0.005, nseed=2000, log=print):
    """rotated-frame prefix-sum scan of numerator g and denominator w: approximate
    (sum_{p in x} g_p)/m(x)^2 on a dense grid; exact re-rank by patterns. (A18 ratio_seeds
    generalised to an arbitrary numerator measure; F ignored -- seeds only.)"""
    A = fm.A
    w = fm.w
    v = np.asarray(g_atom, float)
    best = []
    for th in np.arange(0.0, 45.0 + 1e-9, dth_deg) * math.pi / 180.0:
        c, sn = math.cos(th), math.sin(th)
        uu = c * A[:, 0] + sn * A[:, 1]
        vv = -sn * A[:, 0] + c * A[:, 1]
        w2 = (c + sn) / 2
        lo, hi = w2, s - w2
        cx = np.arange(lo, hi + 1e-12, cstep)
        CX, CY = np.meshgrid(cx, cx, indexing="ij")
        a = c * CX + sn * CY
        b = -sn * CX + c * CY
        u0, v0 = uu.min() - 0.6, vv.min() - 0.6
        iu = np.floor((uu - u0) / cstep).astype(int)
        iv = np.floor((vv - v0) / cstep).astype(int)
        nu, nv = iu.max() + 2, iv.max() + 2
        Hw = np.zeros((nu + 1, nv + 1)); Hv = np.zeros((nu + 1, nv + 1))
        np.add.at(Hw, (iu + 1, iv + 1), w)
        np.add.at(Hv, (iu + 1, iv + 1), v)
        Sw = Hw.cumsum(0).cumsum(1); Sv = Hv.cumsum(0).cumsum(1)
        i1 = np.clip(np.round((a - 0.5 - u0) / cstep).astype(int), 0, nu)
        i2 = np.clip(np.round((a + 0.5 - u0) / cstep).astype(int) + 1, 0, nu)
        j1 = np.clip(np.round((b - 0.5 - v0) / cstep).astype(int), 0, nv)
        j2 = np.clip(np.round((b + 0.5 - v0) / cstep).astype(int) + 1, 0, nv)
        cw = Sw[i2, j2] - Sw[i1, j2] - Sw[i2, j1] + Sw[i1, j1]
        cv = Sv[i2, j2] - Sv[i1, j2] - Sv[i2, j1] + Sv[i1, j1]
        score = np.where(cw > 1e-6, cv / np.maximum(cw, 1e-300) ** 2, 0.0)
        k = min(60, score.size - 1)
        flat = np.argpartition(-score.ravel(), k)[:k]
        for t in flat:
            best.append((float(score.ravel()[t]), float(CX.ravel()[t]), float(CY.ravel()[t]), float(th)))
    seeds = np.array([[cx, cy, th] for _, cx, cy, th in best])
    return seeds[:nseed * 4]


# ---------------------------------------------------------------- localised pair oracle
def r_meeting_placements(ke, s, n, rng, hull, boundary_frac=0.1):
    """random admissible placements whose closed square covers an R-atom; centres sampled in the
    hull box (x0,x1,y0,y1) inflated by ~0.75."""
    x0, x1, y0, y1 = hull
    infl = 0.75
    out = []
    tries = 0
    while sum(len(o) for o in out) < n and tries < 12:
        th = rng.uniform(0, math.pi / 2, n)
        wv = np.cos(th) + np.sin(th)
        lo = wv / 2; hi = s - wv / 2
        cx = np.clip(rng.uniform(x0 - infl, x1 + infl, n), lo, hi)
        cy = np.clip(rng.uniform(y0 - infl, y1 + infl, n), lo, hi)
        P = np.stack([cx, cy, th], 1)
        keep = ke.meets_R(P)
        out.append(P[keep])
        tries += 1
    return np.vstack(out)[:n] if out else np.zeros((0, 3))


def tangent_pairs_local(ke, s, n, rng, hull):
    """barely-disjoint pairs with both endpoints R-meeting."""
    X = r_meeting_placements(ke, s, n, rng, hull)
    if len(X) == 0:
        return np.zeros((0, 3)), np.zeros((0, 3))
    n = len(X)
    thy = rng.uniform(0, math.pi / 2, n)
    ang = rng.uniform(0, 2 * math.pi, n)
    U = np.stack([np.cos(ang), np.sin(ang)], 1)
    tlo = np.full(n, 0.5); thi = np.full(n, 1.6)
    Y = np.empty((n, 3)); Y[:, 2] = thy
    for _ in range(34):
        t = 0.5 * (tlo + thi)
        Y[:, :2] = X[:, :2] + t[:, None] * U
        dep = overlap_depth_many(X, Y)
        ov = dep > 0
        tlo = np.where(ov, t, tlo)
        thi = np.where(ov, thi, t)
    Y[:, :2] = X[:, :2] + thi[:, None] * U
    ok = admissible_many(Y, s) & (overlap_depth_many(X, Y) < 0) & ke.meets_R(Y)
    return X[ok], Y[ok]


def polish_pair_direct(ke, s, x, y, step0=0.04, min_step=3e-4, max_eval=400):
    """alternating pattern search maximising K(x,y) (direct kpair evaluation), disjoint+admissible."""
    x = np.array(x, float); y = np.array(y, float)
    best = float(ke.kpair(x[None], y[None])[0])
    step = step0
    nev = 0
    while step >= min_step and nev < max_eval:
        improved = False
        for side in (0, 1):
            cur = x if side == 0 else y
            oth = y if side == 0 else x
            for mv in _moves():
                cand = cur + mv * np.array([step, step, step * 0.6])
                cand[2] %= math.pi / 2
                if not admissible_many(cand[None], s)[0]:
                    continue
                if overlap_depth(cand, oth) >= 0:
                    continue
                v = float(ke.kpair(cand[None], oth[None])[0]) if side == 0 else \
                    float(ke.kpair(oth[None], cand[None])[0])
                nev += 1
                if v > best + 1e-12:
                    best = v
                    if side == 0:
                        x = cand
                    else:
                        y = cand
                    improved = True
                    break
        # re-contact
        d = y[:2] - x[:2]
        nd = np.linalg.norm(d)
        if nd > 1e-9 and overlap_depth(x, np.array([y[0], y[1], y[2]])) < 0:
            tlo, thi = 0.5, nd
            for _ in range(25):
                t = 0.5 * (tlo + thi)
                yy = np.array([x[0] + d[0] / nd * t, x[1] + d[1] / nd * t, y[2]])
                if overlap_depth(x, yy) > 0:
                    tlo = t
                else:
                    thi = t
            yy = np.array([x[0] + d[0] / nd * thi, x[1] + d[1] / nd * thi, y[2]])
            if admissible_many(yy[None], s)[0] and overlap_depth(x, yy) < 0:
                v = float(ke.kpair(x[None], yy[None])[0])
                nev += 1
                if v > best + 1e-12:
                    best = v; y = yy
                    improved = True
        if not improved:
            step *= 0.5
    return best, x, y


def pair_oracle_local(ke, s, hull, rng, nodesP=None, seed_pairs=None, n_tangent=12000,
                      n_polish=40, topk=400, viol_thresh=None, viol_cap=900, log=print):
    """max K(x,y) over disjoint R-meeting pairs. Returns dict(best, cands, viols)."""
    cands = []
    viols = []

    def record(kv, X, Y, tag):
        if len(kv) == 0:
            return
        top = np.argsort(-kv)[:topk]
        for t in top:
            cands.append((float(kv[t]), X[t].copy(), Y[t].copy()))
        if viol_thresh is not None:
            vi = np.nonzero(kv > viol_thresh)[0]
            if len(vi) > viol_cap:
                vi = np.concatenate([vi[np.argsort(-kv[vi])[:viol_cap // 2]],
                                     rng.choice(vi, viol_cap // 2, replace=False)])
            for t in vi:
                viols.append((float(kv[t]), X[t].copy(), Y[t].copy()))
        log(f"    [pairR] {tag}: {len(kv)} pairs, max K {kv.max():.6f}")

    # stage 1: structured node set (filtered to R-meeting), all disjoint pairs
    if nodesP is not None and len(nodesP):
        keep = ke.meets_R(nodesP)
        Pn = nodesP[keep]
        if len(Pn) > 1:
            dep = overlap_depth_many(np.repeat(Pn, len(Pn), 0), np.tile(Pn, (len(Pn), 1))
                                     ).reshape(len(Pn), len(Pn))
            iu = np.triu_indices(len(Pn), 1)
            mask = dep[iu] < 0
            ii, jj = iu[0][mask], iu[1][mask]
            kv = ke.kpair(Pn[ii], Pn[jj])
            record(kv, Pn[ii], Pn[jj], f"node-set N_R={len(Pn)}")
    # stage 2: seed pairs (recorded violations, A17 inventory)
    if seed_pairs is not None and len(seed_pairs[0]):
        X, Y = seed_pairs
        ok = (overlap_depth_many(X, Y) < 0) & ke.meets_R(X) & ke.meets_R(Y)
        kv = ke.kpair(X[ok], Y[ok])
        record(kv, X[ok], Y[ok], f"seed pairs ({int(ok.sum())})")
    # stage 3: localised tangent pairs
    if n_tangent:
        X, Y = tangent_pairs_local(ke, s, n_tangent, rng, hull)
        if len(X):
            kv = ke.kpair(X, Y)
            record(kv, X, Y, f"tangent ({len(X)})")
    # stage 4: polish
    cands.sort(key=lambda c: -c[0])
    seen = set()
    polished = []
    for v, x, y in cands:
        key = tuple(np.round(np.concatenate([x, y]), 3))
        if key in seen:
            continue
        seen.add(key)
        if len(polished) >= n_polish:
            break
        vb, xb, yb = polish_pair_direct(ke, s, x, y)
        polished.append((vb, xb, yb))
    all_c = sorted(polished + cands, key=lambda c: -c[0])
    if all_c:
        log(f"    [pairR] best after polish: {all_c[0][0]:.6f}")
    else:
        all_c = [(-1.0, None, None)]
    return dict(best=all_c[0], cands=all_c[:max(topk, 200)], viols=viols)
