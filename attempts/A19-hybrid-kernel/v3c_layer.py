"""V3c -- (1) where do the full hybrid solution's below-bound entries live (tiny instance)?
(2) does the 'active block' class (F supported on A x A, free on R x R, <= 0 elsewhere,
diagonal outside A) recover the full-SDP value as A grows?"""
import json, math, os, sys, time
import numpy as np
import scipy.sparse as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "A17-kernel-root"))

from features import FeatureMap, random_placements
from oracle_pair import overlap_depth_many
from hybrid import HybridSDP, Region
from validate import tiny_instance
from v3b_check import solve_full
import cvxpy as cp


def solve_layer(fm, hs, A_mask, delta=1e-3, psd_eps=0.0):
    """active-block class: D = diag(g) + F, supp F in A x A, F free on R x R (off-diag),
    F <= 0 on the rest of the block (off-diag), 0 outside. PSD cone |A|+1."""
    m = fm.m; w = fm.w
    inR = np.zeros(m, bool); inR[hs.r_idx] = True
    assert (inR <= A_mask).all()
    a_idx = np.nonzero(A_mask)[0]
    ka = len(a_idx)
    apos = -np.ones(m, int); apos[a_idx] = np.arange(ka)
    g = cp.Variable(m)
    F = cp.Variable((ka, ka), symmetric=True)
    lam = cp.Variable()
    cons = [g >= 1e-9, cp.diag(F) == 0]
    # sign: F_ij <= 0 for (i,j) in block, not both in R
    iu, ju = np.triu_indices(ka, 1)
    mask = ~(inR[a_idx[iu]] & inR[a_idx[ju]])
    if mask.any():
        G = sp.csr_matrix((np.ones(mask.sum()), (np.arange(mask.sum()),
                                                 iu[mask] * ka + ju[mask])), shape=(mask.sum(), ka * ka))
        cons.append(G @ cp.reshape(F, (ka * ka,), order="C") <= 0)
    # PSD via Schur
    out = ~A_mask
    t = cp.Variable(int(out.sum()))
    wN = w[out]
    cons.append(t >= cp.multiply(wN ** 2, cp.inv_pos(g[np.nonzero(out)[0]])))
    tail = 1.0 - cp.sum(t)
    Z = cp.bmat([[cp.diag(g[a_idx]) + F, w[a_idx].reshape(-1, 1)],
                 [w[a_idx].reshape(1, -1), cp.reshape(tail, (1, 1), order="C")]])
    cons.append(Z >> psd_eps * np.eye(ka + 1))
    # rows
    Pd = np.array(hs.diag_meta)
    pat = fm.patterns(Pd)
    mv = pat @ w
    Ad = pat.toarray()
    AdA = Ad[:, a_idx]
    lhs = Ad @ g + cp.sum(cp.multiply(AdA @ F, AdA), axis=1)
    cons.append(lhs <= lam * mv ** 2)
    if hs.pair_meta:
        Xp = np.array([p[0] for p in hs.pair_meta]); Yp = np.array([p[1] for p in hs.pair_meta])
        pa = fm.patterns(Xp).toarray()[:, a_idx]; pb = fm.patterns(Yp).toarray()[:, a_idx]
        mm = np.array(hs.p_mm)
        cons.append(cp.sum(cp.multiply(pa @ F, pb), axis=1) <= -delta * mm)
    prob = cp.Problem(cp.Minimize(lam), cons)
    prob.solve(solver="CLARABEL")
    return float(lam.value), prob.status


def main():
    fm, region, rng = tiny_instance()
    s = fm.s
    hs = HybridSDP(fm, region, delta_pair=1e-3)
    P = random_placements(s, 800, rng)
    hs.add_diag(P)
    P2 = random_placements(s, 400, rng)
    Xs, Ys = [], []
    for i in range(len(P2)):
        for j in range(i + 1, len(P2)):
            if overlap_depth_many(P2[i][None], P2[j][None])[0] < 0:
                Xs.append(P2[i]); Ys.append(P2[j])
    hs.add_pairs(np.array(Xs), np.array(Ys))
    inR = np.zeros(fm.m, bool); inR[hs.r_idx] = True

    lam_full, S, st = solve_full(fm, hs)
    print(f"full: lam = {lam_full:.6f}")
    # where are below-bound entries?
    w = fm.w
    iu, ju = np.triu_indices(fm.m, 1)
    mask = ~(inR[iu] & inR[ju])
    slack = -(S[iu[mask], ju[mask]] + w[iu[mask]] * w[ju[mask]])
    below = slack > 1e-4
    ri = inR[iu[mask]].astype(int) + inR[ju[mask]].astype(int)   # 0 = NN, 1 = RN
    print(f"below-bound non-R entries: {below.sum()} of {mask.sum()}; "
          f"of these RN: {(ri[below]==1).sum()}, NN: {(ri[below]==0).sum()}")
    # distance of N endpoints (of below-bound NN/RN pairs) from region R (centre box)
    c = s / 2
    dctr = np.hypot(fm.A[:, 0] - c, fm.A[:, 1] - c)
    print(f"R-atoms max dist from centre: {dctr[inR].max():.3f}")
    nn_i = iu[mask][below]; nn_j = ju[mask][below]
    dN = []
    for a, b in zip(nn_i, nn_j):
        for p in (a, b):
            if not inR[p]:
                dN.append(dctr[p])
    dN = np.array(dN)
    if len(dN):
        print(f"N endpoints of below-bound pairs, dist from centre: med {np.median(dN):.3f} "
              f"q90 {np.percentile(dN,90):.3f} max {dN.max():.3f}")

    # layered class: A = R + layer of atoms within dist d of centre
    for extra in (0.0, 0.35, 0.7, 1.2, 99.0):
        Amask = inR.copy()
        rmax = dctr[inR].max()
        Amask |= dctr <= rmax + extra
        lam_l, stt = solve_layer(fm, hs, Amask)
        print(f"layer +{extra}: |A| = {Amask.sum()}, lam = {lam_l:.6f} [{stt}] "
              f"(full {lam_full:.6f}, boundary-param 14.467)")


if __name__ == "__main__":
    main()
