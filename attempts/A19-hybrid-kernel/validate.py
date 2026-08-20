"""A19 -- machine validation of the hybrid class algebra (notes.md SS2).

V1  identities: dense M from (w,g,F) vs hybrid kdiag/kpair via A17's feature machinery (1e-12).
V2  psd reduction: Z_R >= 0 (Schur form) <=> M >= 0 (eigenvalue check on solved instances).
V3  small scale: FULL hybrid SDP (S psd free, sign constraints off R) vs the diag+R-block SDP
    on the same rows -- how lossy is the boundary parametrisation?
V4  F = 0 SDP == A18 two-measure GP on the same rows (collapse / gate (a) mechanism).
"""
import json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "A17-kernel-root"))
sys.path.insert(0, os.path.join(HERE, "..", "A18-restricted-kernel"))

from features import FeatureMap, random_placements, d4_images_pt
from oracle_pair import overlap_depth_many
from hybrid import HybridSDP, Region, enrich_atoms
from two_measure import TwoMeasureKernel

RES = {}


def tiny_instance(seed=0, s=3.8):
    rng = np.random.default_rng(seed)
    reps = np.array([[1.0, 1.0], [1.0, 1.9], [0.7, 1.0], [1.4, 1.4], [1.0, 1.53],
                     [1.6, 1.75], [0.55, 0.55], [1.9, 1.6]])
    A = []
    for x, y in reps:
        for q in d4_images_pt(x, y, s):
            if not any(abs(q[0]-r[0]) < 1e-9 and abs(q[1]-r[1]) < 1e-9 for r in A):
                A.append(q)
    A = np.array(A)
    w = np.full(len(A), 0.35)
    # enrichment atoms (weight 0) in the central region
    A, w, n_new = enrich_atoms(A, w, s, [(1.55, 1.55), (1.75, 1.9)], w_new=0.0)
    fm = FeatureMap(A, w, s)
    region = Region([(1.3, 2.5, 1.3, 2.5)], s)
    return fm, region, rng


def main():
    t0 = time.time()
    fm, region, rng = tiny_instance()
    s = fm.s
    hs = HybridSDP(fm, region, delta_pair=1e-3)
    print(f"tiny: {fm.m} atoms ({hs.n_orb} orbits), |R-atoms| k = {hs.k}, F orbits = {hs.n_forb}")

    # rows
    P = random_placements(s, 800, rng)
    nd = hs.add_diag(P)
    P2 = random_placements(s, 400, rng)
    Xs, Ys = [], []
    for i in range(len(P2)):
        for j in range(i + 1, len(P2)):
            if overlap_depth_many(P2[i][None], P2[j][None])[0] < 0:
                Xs.append(P2[i]); Ys.append(P2[j])
    Xs = np.array(Xs); Ys = np.array(Ys)
    npr = hs.add_pairs(Xs, Ys)
    print(f"rows: {nd} diag, {npr} pair (R-meeting, from {len(Xs)} disjoint)")

    r = hs.solve()
    lam_h = r["lam"]
    print(f"V-solve: hybrid diag+R SDP lam = {lam_h:.6f} ({r['time']:.1f}s)")

    # ---- V1 identities on the SOLVED kernel
    M = hs.dense_M(r["g_orb"], r["f"])
    ke = hs.kernel(r["g_orb"], r["f"])
    from features import kdiag as a17_kdiag
    Pt = random_placements(s, 500, rng)
    Phi = fm.phi(Pt)
    kd_ref = a17_kdiag(Phi, M)
    kd_new = ke.kdiag(Pt)
    ok = np.isfinite(kd_new)
    e1 = float(np.abs(kd_ref[ok] - kd_new[ok]).max())
    # pairs: disjoint random pairs, reference via full bilinear form
    U = np.asarray(Phi @ M)
    d_idx = []
    for i in range(0, 400, 2):
        if overlap_depth_many(Pt[i][None], Pt[i+1][None])[0] < 0:
            d_idx.append((i, i+1))
    kp_ref = np.array([float(np.asarray(Phi[i].todense()).ravel() @ M @ np.asarray(Phi[j].todense()).ravel())
                       for i, j in d_idx])
    kp_new = ke.kpair(Pt[[i for i, _ in d_idx]], Pt[[j for _, j in d_idx]])
    e2 = float(np.abs(kp_ref - kp_new).max()) if len(d_idx) else 0.0
    print(f"V1 identities: max|kdiag - phi'Mphi| = {e1:.2e}, max|kpair - phi'Mphi| = {e2:.2e} "
          f"on {len(d_idx)} disjoint pairs")
    RES["V1"] = dict(e_diag=e1, e_pair=e2, n_pairs=len(d_idx))
    assert e1 < 1e-10 and e2 < 1e-10

    # also: non-R-meeting disjoint pairs must be exactly -1
    meets = ke.meets_R(Pt)
    d_no = [(i, j) for (i, j) in d_idx if not (meets[i] and meets[j])]
    if d_no:
        kp_no = ke.kpair(Pt[[i for i, _ in d_no]], Pt[[j for _, j in d_no]])
        e3 = float(np.abs(kp_no + 1.0).max())
        print(f"V1b automaticity: {len(d_no)} non-R-meeting disjoint pairs, max|K+1| = {e3:.2e}")
        RES["V1b"] = dict(n=len(d_no), e=e3)
        assert e3 < 1e-12

    # ---- V2 psd
    ev = np.linalg.eigvalsh(M)
    print(f"V2 psd: min eig M = {ev[0]:.2e} (Schur-reduced Z_R was the only PSD constraint)")
    RES["V2"] = dict(min_eig=float(ev[0]))
    assert ev[0] > -1e-7

    # ---- V3 full hybrid SDP (S free psd + sign constraints) vs diag+R-block
    import cvxpy as cp
    m = fm.m
    w = fm.w
    inR = np.zeros(m, bool); inR[hs.r_idx] = True
    S = cp.Variable((m, m), symmetric=True)
    lam = cp.Variable()
    cons = [S >> 0]
    # sign: S_pq <= -w_p w_q for p != q NOT both in R (K(x,y) = aSb/(m1 m2) in general:
    # aDb = aSb + (w'a)(w'b), so K = -1 + aDb/(m1m2) = aSb/(m1m2))
    iu, ju = np.triu_indices(m, 1)
    mask = ~(inR[iu] & inR[ju])
    sel_i = iu[mask]; sel_j = ju[mask]
    import scipy.sparse as sp
    G = sp.csr_matrix((np.ones(len(sel_i)), (np.arange(len(sel_i)), sel_i * m + sel_j)),
                      shape=(len(sel_i), m * m))
    bnd = -(w[sel_i] * w[sel_j])
    cons.append(G @ cp.reshape(S, (m * m,), order="C") <= bnd)
    # diag rows: K(x,x) = a'Sa/m^2 <= lam - 1
    pat_d = fm.patterns(np.array(hs.diag_meta))
    m2 = np.array(hs.d_m2)
    Ad = pat_d.toarray()
    for i in range(Ad.shape[0]):
        a = Ad[i]
        cons.append(cp.quad_form(a, S, assume_PSD=True) <= (lam - 1.0) * m2[i])
    # pair rows: K(x,y) = aSb/(m1m2) <= -1 - delta
    if hs.pair_meta:
        Xp = np.array([p[0] for p in hs.pair_meta]); Yp = np.array([p[1] for p in hs.pair_meta])
        pa = fm.patterns(Xp).toarray(); pb = fm.patterns(Yp).toarray()
        mm = np.array(hs.p_mm)
        for i in range(pa.shape[0]):
            cons.append(pa[i] @ S @ pb[i] <= -(1.0 + hs.delta_pair) * mm[i])
    prob = cp.Problem(cp.Minimize(lam), cons)
    prob.solve(solver="CLARABEL")
    lam_full = float(lam.value)
    print(f"V3 full hybrid SDP lam = {lam_full:.6f} vs diag+R-block lam = {lam_h:.6f} "
          f"(gap {lam_h - lam_full:+.2e}) [{prob.status}]")
    RES["V3"] = dict(lam_full=lam_full, lam_reduced=lam_h, gap=lam_h - lam_full)

    # ---- V4 F=0 == two-measure GP on the same diag rows
    hs0 = HybridSDP(fm, None, delta_pair=1e-3)
    hs0.add_diag(np.array(hs.diag_meta))
    r0 = hs0.solve(allow_F=False)
    tm = TwoMeasureKernel(fm)
    pat = fm.patterns(np.array(hs.diag_meta))
    lam_gp = tm.optimize(pat, log=lambda *_: None)
    print(f"V4 collapse: F=0 SDP lam = {r0['lam']:.6f} vs two-measure GP lam = {lam_gp:.6f} "
          f"(diff {r0['lam'] - lam_gp:+.2e})")
    RES["V4"] = dict(lam_sdp=r0["lam"], lam_gp=lam_gp, diff=r0["lam"] - lam_gp)

    RES["time"] = time.time() - t0
    json.dump(RES, open(os.path.join(HERE, "results", "validate.json"), "w"), indent=1,
              default=float)
    print(f"validate done ({RES['time']:.0f}s) -> results/validate.json")


if __name__ == "__main__":
    main()
