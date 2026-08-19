"""A17 — pair separation oracle: find disjoint pairs (x, y) in P_s x P_s maximising K(x,y).
Disjoint = CLOSED squares disjoint = SAT overlap depth < 0 (touching EXCLUDED: the bridge lemma only
produces pairwise disjoint CLOSED squares, and with closed-square indicator features a touching pair can
share a boundary atom, giving K > -1 there -- observed in the 3.80 calibration).

Stages: (1) full K on a structured node set (all disjoint pairs), (2) random tangent pairs (binary
search on the contact distance), (3) alternating pattern-search polish from the worst pairs (with
re-contacting).  K is evaluated through the factor L (K(x,y) = (L phi(x)) . (L phi(y))).
"""
import math
import numpy as np


# ------------------------------------------------ geometry
def _halfwidth(dth):
    return 0.5 * (np.abs(np.cos(dth)) + np.abs(np.sin(dth)))


def overlap_depth_many(P, Q):
    """SAT overlap depth for aligned placement arrays P, Q (n,3): > 0 iff interiors overlap."""
    P = np.atleast_2d(np.asarray(P, float)); Q = np.atleast_2d(np.asarray(Q, float))
    d = Q[:, :2] - P[:, :2]
    dth = P[:, 2] - Q[:, 2]
    h = _halfwidth(dth)
    out = None
    for th, hw_own, hw_oth in ((P[:, 2], 0.5, h), (Q[:, 2], 0.5, h)):
        for add in (0.0, math.pi / 2):
            a = th + add
            proj = np.abs(d[:, 0] * np.cos(a) + d[:, 1] * np.sin(a))
            dep = hw_own + hw_oth - proj
            out = dep if out is None else np.minimum(out, dep)
    return out


def overlap_depth(p, q):
    return float(overlap_depth_many(np.array([p]), np.array([q]))[0])


def depth_matrix(P, chunk=600):
    """(N,N) SAT depth matrix (interiors overlap iff > 0)."""
    P = np.asarray(P, float)
    N = len(P)
    out = np.empty((N, N))
    for i0 in range(0, N, chunk):
        i1 = min(N, i0 + chunk)
        m = i1 - i0
        Pi = np.repeat(P[i0:i1], N, axis=0)
        Qi = np.tile(P, (m, 1))
        out[i0:i1] = overlap_depth_many(Pi, Qi).reshape(m, N)
    return out


def admissible_many(P, s, tol=0.0):
    w = np.cos(P[:, 2]) + np.sin(P[:, 2])
    return (P[:, 0] >= w / 2 - tol) & (P[:, 0] <= s - w / 2 + tol) & \
           (P[:, 1] >= w / 2 - tol) & (P[:, 1] <= s - w / 2 + tol)


def tangent_pairs(s, n, rng):
    """random barely-disjoint admissible pairs: x random, y = x + t*u with t at the contact distance
    (30-step binary search), both admissible."""
    from features import random_placements
    X = random_placements(s, n, rng, boundary_frac=0.15)
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
    ok = admissible_many(Y, s) & (overlap_depth_many(X, Y) < 0)
    return X[ok], Y[ok]


# ------------------------------------------------ kernel evaluation through the factor
class KernelEval:
    """K(x,y) = (L phi(x)).(L phi(y)); L (R, nf) dense."""
    def __init__(self, fm, L):
        self.fm = fm
        self.L = np.asarray(L)

    def U(self, P=None, Phi=None):
        Phi = self.fm.phi(P) if Phi is None else Phi
        return np.asarray(Phi @ self.L.T)

    def u_single(self, x):
        return self.U(np.array([x]))[0]

    def kdiag(self, P=None, Phi=None):
        U = self.U(P, Phi)
        return np.einsum('ij,ij->i', U, U)

    def kpair_rows(self, P1, P2):
        return np.einsum('ij,ij->i', self.U(P1), self.U(P2))


MOVES = None


def _moves():
    global MOVES
    if MOVES is None:
        M = []
        for k in range(3):
            for sgn in (1.0, -1.0):
                v = np.zeros(3); v[k] = sgn
                M.append(v)
        MOVES = np.array(M)
    return MOVES


def polish_pair(ke, s, x, y, step0=0.04, min_step=2e-4, max_eval=500):
    """alternating pattern search maximising K(x,y) over disjoint admissible pairs (theta step x0.6)."""
    x = np.array(x, float); y = np.array(y, float)
    ux, uy = ke.u_single(x), ke.u_single(y)
    best = float(ux @ uy)
    step = step0
    nev = 0
    while step >= min_step and nev < max_eval:
        improved = False
        for side in (0, 1):
            cur, oth_u = (x, uy) if side == 0 else (y, ux)
            for mv in _moves():
                cand = cur + mv * np.array([step, step, step * 0.6])
                cand[2] %= math.pi / 2
                if not admissible_many(cand[None], s)[0]:
                    continue
                other = y if side == 0 else x
                if overlap_depth(cand, other) >= 0:
                    continue
                u = ke.u_single(cand)
                nev += 1
                v = float(u @ oth_u)
                if v > best + 1e-12:
                    best = v
                    if side == 0:
                        x = cand; ux = u
                    else:
                        y = cand; uy = u
                    improved = True
                    break
        # re-contact: pull y toward x to tangency (may enter a new cell)
        d = y[:2] - x[:2]
        nd = np.linalg.norm(d)
        if nd > 1e-9:
            tlo, thi = 0.5, nd
            if overlap_depth(x, np.array([x[0] + d[0], x[1] + d[1], y[2]])) < 0:
                for _ in range(30):
                    t = 0.5 * (tlo + thi)
                    yy = np.array([x[0] + d[0] / nd * t, x[1] + d[1] / nd * t, y[2]])
                    if overlap_depth(x, yy) > 0:
                        tlo = t
                    else:
                        thi = t
                yy = np.array([x[0] + d[0] / nd * thi, x[1] + d[1] / nd * thi, y[2]])
                if admissible_many(yy[None], s)[0] and overlap_depth(x, yy) < 0:
                    u = ke.u_single(yy)
                    v = float(u @ ux)
                    nev += 1
                    if v > best + 1e-12:
                        best = v; y = yy; uy = u
                        improved = True
        if not improved:
            step *= 0.5
    return best, x, y


def pair_oracle(ke, s, nodesP=None, node_dep=None, rng=None, n_tangent=8000, n_polish=40,
                topk=400, log=print, viol_thresh=None, viol_cap=800):
    """returns dict(best=(K,x,y), cands=[(K,x,y) sorted desc], viols=[...]) over disjoint pairs.
    viols = a diverse sample (top + random) of ALL pairs above viol_thresh, capped at viol_cap."""
    rng = np.random.default_rng(0) if rng is None else rng
    cands = []
    viols = []
    # stage 1: structured node set, all disjoint pairs
    if nodesP is not None:
        U = ke.U(nodesP)
        K = U @ U.T
        dep = depth_matrix(nodesP) if node_dep is None else node_dep
        mask = (dep < 0)
        np.fill_diagonal(mask, False)
        Km = np.where(mask, K, -np.inf)
        iu = np.triu_indices(len(nodesP), 1)
        vals = Km[iu]
        top = np.argsort(-vals)[:topk]
        for t in top:
            if np.isfinite(vals[t]):
                i, j = iu[0][t], iu[1][t]
                cands.append((float(vals[t]), nodesP[i].copy(), nodesP[j].copy()))
        if viol_thresh is not None:
            vi = np.nonzero(np.isfinite(vals) & (vals > viol_thresh))[0]
            if len(vi) > viol_cap:
                vi = np.concatenate([vi[np.argsort(-vals[vi])[:viol_cap // 2]],
                                     rng.choice(vi, viol_cap // 2, replace=False)])
            for t in vi:
                viols.append((float(vals[t]), nodesP[iu[0][t]].copy(), nodesP[iu[1][t]].copy()))
        log(f"    [pair] node-set scan N={len(nodesP)}: max K over disjoint pairs {vals[top[0]]:.6f}")
    # stage 2: random tangent pairs
    if n_tangent:
        X, Y = tangent_pairs(s, n_tangent, rng)
        kv = ke.kpair_rows(X, Y)
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
        log(f"    [pair] {len(X)} tangent pairs: max K {kv.max():.6f}")
    # stage 3: polish the best
    cands.sort(key=lambda c: -c[0])
    seen = set()
    polished = []
    for v, x, y in cands:
        key = (round(x[0], 3), round(x[1], 3), round(x[2], 3), round(y[0], 3), round(y[1], 3), round(y[2], 3))
        if key in seen:
            continue
        seen.add(key)
        if len(polished) >= n_polish:
            break
        vb, xb, yb = polish_pair(ke, s, x, y)
        polished.append((vb, xb, yb))
    all_c = sorted(polished + cands, key=lambda c: -c[0])
    log(f"    [pair] best after polish: {all_c[0][0]:.6f}")
    return dict(best=all_c[0], cands=all_c[:max(topk, 200)], viols=viols)


if __name__ == "__main__":
    # sanity: depth matrix agrees with graph.overlap_matrix
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "A16-theta-casetree"))
    from graph import overlap_matrix
    from features import random_placements
    rng = np.random.default_rng(1)
    P = random_placements(3.84, 400, rng)
    dep = depth_matrix(P)
    ov1 = dep > 1e-9
    np.fill_diagonal(ov1, False)
    ov2 = overlap_matrix(P)
    print("depth_matrix agrees with graph.overlap_matrix:", np.array_equal(ov1, ov2))
    X, Y = tangent_pairs(3.84, 2000, rng)
    d = overlap_depth_many(X, Y)
    print(f"tangent pairs: {len(X)} kept, depth in [{d.min():.2e}, {d.max():.2e}] (should be <= 0, tiny)")
