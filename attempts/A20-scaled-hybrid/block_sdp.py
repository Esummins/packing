"""A20 -- D4-block-diagonalised hybrid SDP (A19's (k+1)-cone Schur form, R-cone split into
isotypic blocks of the D4 action on R-atoms + fixed border node).

The (k+1)x(k+1) cone  Z = [[diag(g_R)+F, w_R],[w_R^T, tail]]  is D4-invariant by construction
(g orbit-constant, F = sum_o f_o A_o over D4 pair orbits, w_R orbit-constant, border fixed), so
Z >= 0  <=>  Z_rho := (1/d_rho) sum_r T_rho^(r)^T Z T_rho^(r) >= 0 per irrep rho (A16 machinery).
Block sizes ~ k/8 (A1,A2,B1,B2) and ~ k/4 (E) instead of k+1 -> Clarabel survives k ~ 600.

Extras over A19's HybridSDP:
  * vectorised row-coefficient extraction (the per-row Python pair loops die at k ~ 600);
  * optional F-support restriction to atom pairs at distance <= fdist (co-occurrence bound
    sqrt(2): more distant pairs never appear in any diagonal row).
"""
import math, os, sys, time
import numpy as np
import scipy.sparse as sp

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "attempts", "A19-hybrid-kernel"))
sys.path.insert(0, os.path.join(ROOT, "attempts", "A17-kernel-root"))
sys.path.insert(0, os.path.join(ROOT, "attempts", "A16-theta-casetree"))

from hybrid import HybridSDP, atom_orbits          # noqa: E402
import theta_sdp                                    # noqa: E402


def rpair_orbits_fast(fm, r_idx, fdist=None):
    """D4 orbits of unordered R-atom pairs, vectorised. Optionally only pairs at
    Euclidean distance <= fdist (others get pair_oid -1 = F zero there).
    Returns pair_oid (k,k), n_orb, orb_pairs (list of lists of local (i,j))."""
    k = len(r_idx)
    pos = -np.ones(fm.m, dtype=np.int64)
    pos[r_idx] = np.arange(k)
    iu, ju = np.triu_indices(k, 1)
    if fdist is not None:
        A = fm.A[r_idx]
        d2 = (A[iu, 0] - A[ju, 0]) ** 2 + (A[iu, 1] - A[ju, 1]) ** 2
        keep = d2 <= fdist * fdist + 1e-12
        iu, ju = iu[keep], ju[keep]
    if len(iu) == 0:
        return np.full((k, k), -1, np.int32), 0, []
    gi_glob = fm.G_atoms[:, r_idx]                     # (8,k) global indices of images
    gl = pos[gi_glob]                                  # (8,k) local indices
    assert (gl >= 0).all()
    a = gl[:, iu]; b = gl[:, ju]                       # (8,npair)
    key = np.minimum(a, b).astype(np.int64) * k + np.maximum(a, b)
    canon = key.min(axis=0)
    uniq, inv = np.unique(canon, return_inverse=True)
    n_orb = len(uniq)
    # all image pairs (vectorised member enumeration)
    K = key.ravel()
    O = np.tile(inv, 8)
    uk, first = np.unique(K, return_index=True)
    uo = O[first]
    ui = (uk // k).astype(int); uj = (uk % k).astype(int)
    pair_oid = np.full((k, k), -1, dtype=np.int32)
    pair_oid[ui, uj] = uo
    pair_oid[uj, ui] = uo
    orb_pairs = [[] for _ in range(n_orb)]
    order = np.argsort(uo, kind="stable")
    for t in order:
        orb_pairs[uo[t]].append((int(ui[t]), int(uj[t])))
    return pair_oid, n_orb, orb_pairs


class BlockHybridSDP(HybridSDP):
    def __init__(self, fm, region, delta_pair=1e-3, psd_eps=0.0, r_mask=None, fdist=None):
        self.fdist = fdist
        import hybrid as _hyb
        _orig = _hyb.rpair_orbits
        _hyb.rpair_orbits = lambda fm_, r_idx_: rpair_orbits_fast(fm_, r_idx_, fdist)
        try:
            super().__init__(fm, region, delta_pair=delta_pair, psd_eps=psd_eps, r_mask=r_mask)
        finally:
            _hyb.rpair_orbits = _orig
        self._sym = None

    # -------- vectorised row-coefficient extraction (override the Python pair loops)
    def _quad_forb_counts(self, nzR):
        rp = self.rpos[nzR]
        sub = self.pair_oid[np.ix_(rp, rp)]
        iu = np.triu_indices(len(rp), 1)
        o = sub[iu]
        o = o[o >= 0]
        if len(o) == 0:
            return {}
        cnt = np.bincount(o)
        nz = np.nonzero(cnt)[0]
        return {int(i): 2.0 * float(cnt[i]) for i in nz}

    def _cross_forb_counts(self, nzR1, nzR2):
        r1 = self.rpos[nzR1]; r2 = self.rpos[nzR2]
        o = self.pair_oid[np.ix_(r1, r2)].ravel()
        o = o[o >= 0]
        if len(o) == 0:
            return {}
        cnt = np.bincount(o)
        nz = np.nonzero(cnt)[0]
        return {int(i): float(cnt[i]) for i in nz}

    # -------- symmetry blocks for the extended (k+1) node set
    def build_blocks(self, log=print):
        """isotypic maps: for each irrep, sparse gmap (mrho^2, n_orb), fmap (mrho^2, n_forb),
        tailmat (mrho, mrho), Cconst (mrho, mrho) with vec in C order."""
        t0 = time.time()
        k = self.k
        kp = k + 1
        Gext = np.empty((8, kp), dtype=np.int64)
        pos = -np.ones(self.fm.m, dtype=np.int64)
        pos[self.r_idx] = np.arange(k)
        Gext[:, :k] = pos[self.fm.G_atoms[:, self.r_idx]]
        assert (Gext[:, :k] >= 0).all()
        Gext[:, k] = k                                     # border node fixed
        rho = theta_sdp.d4_rep_matrices()
        oid, orbs = theta_sdp.orbits(Gext)
        SB = theta_sdp.symmetry_basis(Gext, orbs, rho)
        wR = self.fm.w[self.r_idx]
        blocks = {}
        # flattened ordered pair lists for fmap
        allI, allJ, allO = [], [], []
        for o, mem in enumerate(self.orb_pairs):
            for (i, j) in mem:
                allI += [i, j]; allJ += [j, i]; allO += [o, o]
        allI = np.array(allI, dtype=np.int64); allJ = np.array(allJ, dtype=np.int64)
        allO = np.array(allO, dtype=np.int64)
        # ordered diag "pairs" for gmap: node i with orbit column = atom orbit id
        gI = np.arange(k, dtype=np.int64)
        gO = self.oid[self.r_idx].astype(np.int64)         # global atom-orbit ids
        for n in SB["names"]:
            m = SB["m"][n]
            if m == 0:
                continue
            d = SB["dims"][n]
            dmax = SB["dmax"]
            col = SB["col"][n]                             # (kp, dmax)
            tv = [SB["t"][n][r] for r in range(d)]          # (kp, dmax) each
            # fmap entries
            fr, fc, fv = [], [], []
            gr, gc, gv = [], [], []
            for a in range(dmax):
                ca_f = col[allI, a]; ca_g = col[gI, a]
                for b in range(dmax):
                    cb_f = col[allJ, b]; cb_g = col[gI, b]
                    val_f = np.zeros(len(allI)); val_g = np.zeros(k)
                    for r in range(d):
                        val_f += tv[r][allI, a] * tv[r][allJ, b]
                        val_g += tv[r][gI, a] * tv[r][gI, b]
                    val_f /= d; val_g /= d
                    ok = (ca_f >= 0) & (cb_f >= 0) & (val_f != 0)
                    fr.append(ca_f[ok] * m + cb_f[ok]); fc.append(allO[ok]); fv.append(val_f[ok])
                    okg = (ca_g >= 0) & (cb_g >= 0) & (val_g != 0)
                    gr.append(ca_g[okg] * m + cb_g[okg]); gc.append(gO[okg]); gv.append(val_g[okg])
            fmap = sp.csr_matrix((np.concatenate(fv), (np.concatenate(fr), np.concatenate(fc))),
                                 shape=(m * m, self.n_forb)) if self.n_forb else None
            gmap = sp.csr_matrix((np.concatenate(gv), (np.concatenate(gr), np.concatenate(gc))),
                                 shape=(m * m, self.n_orb))
            if fmap is not None:
                fmap.sum_duplicates()
            gmap.sum_duplicates()
            # tail + border const: dense (kp small relative)
            Ts = [theta_sdp.dense_T(SB, n, r) for r in range(d)]
            tailmat = sum(np.outer(T[k], T[k]) for T in Ts) / d
            C0row = np.zeros(kp); C0row[:k] = wR
            Cconst = sum(np.outer(T[k], C0row @ T) + np.outer(C0row @ T, T[k]) for T in Ts) / d
            blocks[n] = dict(m=m, gmap=gmap, fmap=fmap,
                             tailmat=tailmat if np.abs(tailmat).max() > 1e-14 else None,
                             Cconst=Cconst)
        self._sym = dict(SB=SB, blocks=blocks)
        sizes = {n: b["m"] for n, b in blocks.items()}
        log(f"  [blocks] k={k} sizes {sizes} n_forb={self.n_forb} build t={time.time()-t0:.1f}s")
        return blocks

    # -------- solve with per-irrep PSD blocks
    def solve(self, solver="auto", verbose=False, lam_ub=None, allow_F=True, log=print, **kw):
        import cvxpy as cp
        if self.k and self._sym is None:
            self.build_blocks(log=log)
        nd = len(self.diag_meta); npair = len(self.pair_meta)
        g = cp.Variable(self.n_orb)
        lam = cp.Variable()
        use_F = allow_F and self.n_forb > 0
        f = cp.Variable(self.n_forb) if use_F else None
        cons = [g >= 1e-9]
        N_orbs = np.nonzero(~self.orb_in_R)[0]
        wN = self.w_orb[N_orbs]; szN = self.size_orb[N_orbs].astype(float)
        posm = wN > 0
        if posm.any():
            t = cp.Variable(int(posm.sum()))
            cons.append(t >= cp.multiply(wN[posm] ** 2, cp.inv_pos(g[N_orbs[posm]])))
            tail = 1.0 - szN[posm] @ t
        else:
            tail = cp.Constant(1.0)
        if self.k:
            for n, B in self._sym["blocks"].items():
                m = B["m"]
                expr = cp.reshape(B["gmap"] @ g, (m, m), order="C") + B["Cconst"]
                if use_F and B["fmap"] is not None:
                    expr = expr + cp.reshape(B["fmap"] @ f, (m, m), order="C")
                if B["tailmat"] is not None:
                    expr = expr + cp.multiply(tail, B["tailmat"])
                Zs = (expr + expr.T) / 2
                cons.append(Zs >> self.psd_eps * np.eye(m))
        else:
            cons.append(tail >= self.psd_eps)
        if nd:
            Gc = sp.csr_matrix((self.dG_v, (self.dG_r, self.dG_c)), shape=(nd, self.n_orb))
            m2 = np.array(self.d_m2)
            lhs = Gc @ g
            if use_F and self.dF_r:
                Fq = sp.csr_matrix((self.dF_v, (self.dF_r, self.dF_c)), shape=(nd, self.n_forb))
                lhs = lhs + Fq @ f
            cons.append(lhs <= m2 * lam)
        if npair and use_F:
            Fp = sp.csr_matrix((self.pF_v, (self.pF_r, self.pF_c)), shape=(npair, self.n_forb))
            mm = np.array(self.p_mm)
            cons.append(Fp @ f <= -self.delta_pair * mm)
        if lam_ub is not None:
            cons.append(lam <= lam_ub)
        prob = cp.Problem(cp.Minimize(lam), cons)
        t0 = time.time()
        if solver in ("auto", "CLARABEL"):
            prob.solve(solver="CLARABEL", verbose=verbose, **kw)
        elif solver == "SCS":
            prob.solve(solver="SCS", verbose=verbose, eps=2e-6, max_iters=60000, **kw)
        else:
            prob.solve(solver=solver, verbose=verbose, **kw)
        if prob.status not in ("optimal", "optimal_inaccurate"):
            raise RuntimeError(f"solver status {prob.status}")
        g_orb = np.array(g.value)
        f_val = np.array(f.value) if use_F else np.zeros(self.n_forb)
        return dict(lam=float(lam.value), g_orb=g_orb, f=f_val, status=prob.status,
                    time=time.time() - t0)

    # -------- validation helper: dense Z vs block eigs for a random member
    def check_blocks(self, rng):
        if self._sym is None:
            self.build_blocks()
        g_orb = rng.uniform(0.5, 2.0, self.n_orb)
        fv = rng.normal(0, 0.3, self.n_forb)
        tail = 0.37
        k = self.k
        Zd = np.zeros((k + 1, k + 1))
        Zd[:k, :k] = np.diag(g_orb[self.oid[self.r_idx]])
        if self.n_forb:
            Zd[:k, :k] += np.asarray((self.Bas @ fv)).reshape(k, k)
        wR = self.fm.w[self.r_idx]
        Zd[k, :k] = wR; Zd[:k, k] = wR; Zd[k, k] = tail
        ev_full = np.sort(np.linalg.eigvalsh(Zd))
        ev_blocks = []
        for n, B in self._sym["blocks"].items():
            m = B["m"]
            Zb = (B["gmap"] @ g_orb).reshape(m, m) + B["Cconst"]
            if B["fmap"] is not None:
                Zb = Zb + (B["fmap"] @ fv).reshape(m, m)
            if B["tailmat"] is not None:
                Zb = Zb + tail * B["tailmat"]
            Zb = (Zb + Zb.T) / 2
            ev = np.linalg.eigvalsh(Zb)
            d = self._sym["SB"]["dims"][n]
            for _ in range(d):
                ev_blocks.extend(ev)
        ev_blocks = np.sort(np.array(ev_blocks))
        assert len(ev_blocks) == k + 1, (len(ev_blocks), k + 1)
        return float(np.abs(ev_full - ev_blocks).max())
