"""A18 -- full-scale optimisation of the restricted (automatic-(ii)) kernel class.

By the collapse theorem (notes.md SS3, machine-checked in theory_check.py) the class optimum at
fixed normalisation weights w is attained on the two-measure boundary family

    K_u(x,x) = W * vt(x) / m(x)^2 - 1,   W = sum_q w_q u_q,  vt(x) = sum_{p in x} w_p/u_p,
    m(x) = sum_{p in x} w_p,             u > 0  (D4-invariant wlog),

with M = [[1, -w^T], [-w, D]], D = diag(w_p W / u_p)  (C = 0!), M psd, (ii) automatic.
lambda = 1 + sup_x K_u(x,x).  Minimising over u is a geometric program: convex in theta = log u.
This module: row-set softmax optimiser over theta (per D4 orbit), oracle shim for A17's
diag_oracle, and a two-measure prefix-sum ratio scan for the binding cells.
"""
import math, os, sys, json, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "A17-kernel-root"))


def atom_orbits(fm):
    """orbit id per atom under D4 (from fm.G_atoms), and one representative per orbit."""
    m = fm.m
    oid = np.full(m, -1, dtype=int)
    orbs = []
    for i in range(m):
        if oid[i] >= 0:
            continue
        img = np.unique(fm.G_atoms[:, i])
        for j in img:
            oid[j] = len(orbs)
        orbs.append(img)
    return oid, orbs


class TwoMeasureKernel:
    """K(x,x) = W * vt(x)/m(x)^2 - 1 for the boundary member S_u of the restricted class."""

    def __init__(self, fm, theta=None):
        self.fm = fm
        self.w = fm.w
        self.oid, self.orbs = atom_orbits(fm)
        self.n_orb = len(self.orbs)
        self.theta_orb = np.zeros(self.n_orb) if theta is None else np.asarray(theta, float)
        self.n_zero = 0

    @property
    def u(self):
        return np.exp(self.theta_orb[self.oid])

    def kvals(self, pat):
        """1 + K on a sparse pattern matrix (values = W*vt/m^2; m(x)=0 counted, valued 0)."""
        u = self.u
        W = float(self.w @ u)
        mv = pat @ self.w
        vt = pat @ (self.w / u)
        bad = mv <= 0
        self.n_zero += int(bad.sum())
        out = np.where(bad, 0.0, W * vt / np.maximum(mv, 1e-300) ** 2)
        return out

    def kdiag(self, P=None, Phi=None):
        """A17 diag_oracle interface: K(x,x) values for raw placements."""
        pat = self.fm.patterns(np.asarray(P, float).reshape(-1, 3))
        return self.kvals(pat) - 1.0

    def u_single(self, x):
        """A17 polish interface: vector whose self-dot is K(x,x) (K >= 0 in this class)."""
        k = float(self.kdiag(np.asarray(x, float)[None])[0])
        return np.array([math.sqrt(max(k, 0.0))])

    # ------------------------------------------------ convex u-optimisation on a row set
    def optimize(self, pat, beta_sched=(30, 100, 300, 1000, 3000, 10000, 30000),
                 maxiter=3000, log=print):
        """min over theta of max_rows log(W * vt / m^2); GP-convex => global optimum."""
        from scipy.optimize import minimize
        w = self.w
        mv = pat @ w
        ok = mv > 1e-12
        pat = pat[np.nonzero(ok)[0]]
        mv = mv[ok]
        logm2 = 2.0 * np.log(mv)
        oid = self.oid
        # per-orbit weight totals for dW/dtheta
        Worb = np.zeros(self.n_orb)
        np.add.at(Worb, oid, w)
        R = pat.shape[0]
        th = self.theta_orb.copy()
        t0 = time.time()
        for beta in beta_sched:
            def f(th_orb):
                u_at = np.exp(th_orb[oid])
                W = float(w @ u_at)
                vt = pat @ (w / u_at)
                g = math.log(W) + np.log(vt) - logm2
                gm = g.max()
                z = np.exp(beta * (g - gm))
                Z = z.sum()
                F = gm + math.log(Z) / beta
                sm = z / Z
                # dF/dth_orb = sum_r sm_r * [ (w*u)_orb/W - (pat_r @ (w/u))_orb / vt_r ]
                dW = np.zeros(self.n_orb)
                np.add.at(dW, oid, w * u_at)
                gW = dW / W * sm.sum()
                # second term: row-weighted atom scores
                colw = np.asarray(pat.T @ (sm / vt)).ravel()   # (m,)
                gv = np.zeros(self.n_orb)
                np.add.at(gv, oid, -(w / u_at) * colw)
                return F, gW + gv
            res = minimize(f, th, jac=True, method="L-BFGS-B",
                           options=dict(maxiter=maxiter, maxcor=20, ftol=1e-18, gtol=1e-14))
            th = res.x
            u_at = np.exp(th[oid])
            val = float(w @ u_at) * (pat @ (w / u_at)) / mv ** 2
            log(f"    [u-opt] beta {beta}: max row lambda = {val.max():.6f} "
                f"({res.nit} it, {time.time()-t0:.0f}s)")
        self.theta_orb = th - th.mean()   # scale-invariant: centre
        return float(val.max())


# ------------------------------------------------ two-measure ratio scan (binding-cell seeds)
def ratio_seeds(fm, s, u, dth_deg=0.25, cstep=0.005, nseed=4000, log=print):
    """A07-style rotated-frame prefix-sum scan of BOTH measures (w and v = w/u):
    approximate W*v(x)/m(x)^2 on a dense (cx,cy,theta) grid; returns top seeds (descending)."""
    A = fm.A
    w = fm.w
    v = fm.w / u
    W = float(fm.w @ u)
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
        score = np.where(cw > 1e-6, W * cv / np.maximum(cw, 1e-300) ** 2, 0.0)
        k = min(60, score.size - 1)
        flat = np.argpartition(-score.ravel(), k)[:k]
        for t in flat:
            best.append((float(score.ravel()[t]), float(CX.ravel()[t]), float(CY.ravel()[t]), float(th)))
    # exact re-rank of ALL collected seeds (the approximate window rounding is very noisy at the
    # admissible boundary and can push the real binding cells out of any truncated list)
    seeds = np.array([[cx, cy, th] for _, cx, cy, th in best])
    patS = fm.patterns(seeds)
    W = float(fm.w @ u)
    mv = patS @ fm.w
    vt = patS @ (fm.w / u)
    val = np.where(mv > 0, W * vt / np.maximum(mv, 1e-300) ** 2, 0.0)
    order = np.argsort(-val)[:nseed]
    log(f"    [ratioscan] {len(seeds)} seeds, exact top lambda {val[order[0]]:.6f} at "
        f"({seeds[order[0],0]:.3f},{seeds[order[0],1]:.3f},{math.degrees(seeds[order[0],2]):.2f}deg)")
    return seeds[order]


# ------------------------------------------------ oracle attack (scan + polish, A17 machinery)
def attack(ke, fm, s, rng, structP=None, n_rand=60000, n_polish=60, bnd_theta=181,
           bnd_step=0.02, with_ratio=True, dth_deg=0.5, cstep=0.01, log=print):
    """strongest float attack on sup_x K_u(x,x); returns (best K, best x, seeds_used)."""
    from oracle_diag import diag_oracle
    extra = None
    if with_ratio:
        extra = ratio_seeds(fm, s, ke.u, dth_deg=dth_deg, cstep=cstep, nseed=1500, log=log)
    rd = diag_oracle(ke, s, structP=structP, rng=rng, n_rand=n_rand, n_polish=n_polish,
                     bnd_theta=bnd_theta, bnd_step=bnd_step, log=log, extra_seeds=extra)
    return rd
