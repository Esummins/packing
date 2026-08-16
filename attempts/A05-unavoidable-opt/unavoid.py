"""
Unavoidable point sets for unit squares in a square (attempt A05, idea I-L1).

A set P of k points in [0,s0]^2 is *unavoidable* if every closed unit square Q contained
in [0,s0]^2 (any orientation) contains a point of P.  Then s(k+1) >= s0.

Reformulation used throughout:
  Q = Q(c,theta): unit square with centre c and orientation theta (theta in [0,pi/2) suffices).
  Q subset [0,s0]^2   <=>   c in D(theta) := [w/2, s0-w/2]^2,  w = cos(theta)+sin(theta).
  p in Q              <=>   || R(-theta)(p-c) ||_inf <= 1/2.
Uncoveredness  d(c,theta) = min_p ||R(-theta)(p-c)||_inf - 1/2   (>0  <=>  Q misses P).
P is unavoidable  <=>  max over theta, c in D(theta) of d <= 0.
Coverage margin m: require d <= -m everywhere.

This module provides
  * grid evaluation of d and refinement of its local maxima (worst squares),
  * linear parametrisations of symmetric point sets,
  * an SLP (sequential linear programming, trust region) minimiser of max d over P,
  * an outer search for the largest s0 with max d <= -m.
"""
import numpy as np
from scipy.optimize import minimize, linprog
from scipy import ndimage

# ----------------------------------------------------------------------------------------
# evaluator
# ----------------------------------------------------------------------------------------

def uncov_point(P, s0, cx, cy, th):
    """d(c,theta) for a single configuration (no domain check)."""
    ct, st = np.cos(th), np.sin(th)
    dx = P[:, 0] - cx
    dy = P[:, 1] - cy
    u = ct * dx + st * dy
    v = -st * dx + ct * dy
    cheb = np.maximum(np.abs(u), np.abs(v))
    return cheb.min() - 0.5


def uncov_grid(P, s0, nth=64, nc=80):
    """d on a grid.  Returns th (nth,), D (nth,nc,nc) and unit-square coords (u,v) grids.
    c = w/2 + (s0-w)*(u,v), u,v in [0,1]."""
    th = np.linspace(0.0, np.pi / 2, nth)
    uu = np.linspace(0.0, 1.0, nc)
    U, V = np.meshgrid(uu, uu, indexing="ij")
    D = np.empty((nth, nc, nc))
    px = P[:, 0][:, None, None]
    py = P[:, 1][:, None, None]
    for i, t in enumerate(th):
        ct, st = np.cos(t), np.sin(t)
        w = ct + st
        CX = w / 2 + (s0 - w) * U
        CY = w / 2 + (s0 - w) * V
        dx = px - CX[None]
        dy = py - CY[None]
        u = ct * dx + st * dy
        v = -st * dx + ct * dy
        np.abs(u, out=u)
        np.abs(v, out=v)
        np.maximum(u, v, out=u)
        D[i] = u.min(axis=0) - 0.5
    return th, uu, D


def _f_uv(x, P, s0):
    u, v, t = x
    u = min(max(u, 0.0), 1.0)
    v = min(max(v, 0.0), 1.0)
    t = min(max(t, 0.0), np.pi / 2)
    ct, st = np.cos(t), np.sin(t)
    w = ct + st
    cx = w / 2 + (s0 - w) * u
    cy = w / 2 + (s0 - w) * v
    return -uncov_point(P, s0, cx, cy, t)


def _d_batch(P, s0, X):
    """d for a batch of configs X (K,3) in (u,v,theta) coordinates (clipped to the domain)."""
    u = np.clip(X[:, 0], 0.0, 1.0)
    v = np.clip(X[:, 1], 0.0, 1.0)
    t = np.clip(X[:, 2], 0.0, np.pi / 2)
    ct, st = np.cos(t), np.sin(t)
    w = ct + st
    cx = w / 2 + (s0 - w) * u
    cy = w / 2 + (s0 - w) * v
    dx = P[None, :, 0] - cx[:, None]
    dy = P[None, :, 1] - cy[:, None]
    uu = ct[:, None] * dx + st[:, None] * dy
    vv = -st[:, None] * dx + ct[:, None] * dy
    cheb = np.maximum(np.abs(uu), np.abs(vv)).min(axis=1)
    return cheb - 0.5, cx, cy, t


def refine_batch(P, s0, X0, h0, iters=80, hmin=1e-8):
    """Batched compass search maximising d over (u,v,theta) from starts X0 (K,3); h0 initial steps (3,)."""
    X = X0.copy()
    f, *_ = _d_batch(P, s0, X)
    h = np.tile(np.asarray(h0, float), (len(X), 1))
    dirs = np.array([[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]], float)
    for _ in range(iters):
        improved = np.zeros(len(X), bool)
        bestf = f.copy()
        bestX = X.copy()
        for dvec in dirs:
            Xt = X + h * dvec
            ft, *_ = _d_batch(P, s0, Xt)
            better = ft > bestf + 1e-15
            bestf = np.where(better, ft, bestf)
            bestX = np.where(better[:, None], Xt, bestX)
            improved |= better
        X, f = bestX, bestf
        h[~improved] *= 0.5
        if h.max() < hmin:
            break
    return X, f


def _boundary_candidates(P, s0, nth, nb, K, window):
    """Local maxima of d on the boundary of the centre domain (4 edges), fine grid in (position, theta).
    Returns (u,v,theta) starts.  Holes typically touch the container edge, and the 3-D grid misses them."""
    th = np.linspace(0.0, np.pi / 2, nth)
    pos = np.linspace(0.0, 1.0, nb)
    TH, PO = np.meshgrid(th, pos, indexing="ij")
    Xs = []
    for edge in range(4):
        if edge == 0:
            U, V = np.zeros_like(PO), PO
        elif edge == 1:
            U, V = np.ones_like(PO), PO
        elif edge == 2:
            U, V = PO, np.zeros_like(PO)
        else:
            U, V = PO, np.ones_like(PO)
        X = np.stack([U.ravel(), V.ravel(), TH.ravel()], axis=1)
        f, *_ = _d_batch(P, s0, X)
        f = f.reshape(TH.shape)
        mf = ndimage.maximum_filter(f, size=3, mode="nearest")
        mask = (f >= mf) & (f >= f.max() - window)
        ii = np.argwhere(mask)
        vals = f[mask]
        order = np.argsort(-vals)[:K]
        for j in order:
            a, b = ii[j]
            Xs.append([U[a, b], V[a, b], TH[a, b]])
    return np.array(Xs).reshape(-1, 3)


def worst_configs(P, s0, nth=64, nc=80, K=40, window=0.08, refine=True, dedup=1e-4, polish=0,
                  nb=200, nth_b=181, Kb=16):
    """Local maxima of d(c,theta) over the domain.  Returns list of (cx,cy,theta,d), sorted by d desc.
    Coarse grid + 3-D local maximum filter + batched compass-search refinement (+ optional NM polish
    of the top `polish` configs)."""
    th, uu, D = uncov_grid(P, s0, nth, nc)
    gmax = D.max()
    mf = ndimage.maximum_filter(D, size=3, mode="nearest")
    mask = (D >= mf) & (D >= gmax - window)
    idx = np.argwhere(mask)
    vals = D[mask]
    order = np.argsort(-vals)[:K]
    X0 = np.array([[uu[idx[j][1]], uu[idx[j][2]], th[idx[j][0]]] for j in order]).reshape(-1, 3)
    if nb > 0:
        X0 = np.vstack([X0, _boundary_candidates(P, s0, nth_b, nb, Kb, window)])
    if refine and len(X0):
        h0 = (0.5 / (nc - 1), 0.5 / (nc - 1), 0.5 * (np.pi / 2) / (nth - 1))
        X, f = refine_batch(P, s0, X0, h0)
    else:
        X = X0
        f, *_ = _d_batch(P, s0, X)
    out = []
    for j in range(len(X)):
        x0 = X[j]
        val = f[j]
        if j < polish:
            res = minimize(_f_uv, x0, args=(P, s0), method="Nelder-Mead",
                           options=dict(xatol=1e-10, fatol=1e-13, maxiter=800,
                                        initial_simplex=_simplex(x0, 1e-4, 1e-4)))
            if -res.fun > val:
                x0, val = res.x, -res.fun
        u, v, t = min(max(x0[0], 0), 1), min(max(x0[1], 0), 1), min(max(x0[2], 0), np.pi / 2)
        ct, st = np.cos(t), np.sin(t)
        w = ct + st
        cx = w / 2 + (s0 - w) * u
        cy = w / 2 + (s0 - w) * v
        out.append((cx, cy, t, val))
    out.sort(key=lambda r: -r[3])
    kept = []
    for r in out:
        if all(abs(r[0] - q[0]) + abs(r[1] - q[1]) + abs(r[2] - q[2]) > dedup for q in kept):
            kept.append(r)
    return kept


def _simplex(x0, du, dt):
    S = np.tile(x0, (4, 1))
    S[1, 0] += du if x0[0] < 0.5 else -du
    S[2, 1] += du if x0[1] < 0.5 else -du
    S[3, 2] += dt if x0[2] < np.pi / 4 else -dt
    return S


def max_uncov(P, s0, nth=64, nc=80, K=20):
    wc = worst_configs(P, s0, nth, nc, K)
    return wc[0][3], wc[0]


# ----------------------------------------------------------------------------------------
# linear parametrisations  P.flatten() = A z + b
# ----------------------------------------------------------------------------------------

class Param:
    """P (n x 2) = reshape(A z + b).  spec = list of orbit tags for group 'none','C2','axes','diag'.
    Tags (all groups): 'g' generic point.
    axes: 'g' -> 4 pts (x,y),(s-x,y),(x,s-y),(s-x,s-y); 'v' -> 2 pts (s/2,y),(s/2,s-y);
          'h' -> 2 pts (x,s/2),(s-x,s/2); 'c' -> centre.
    diag: 'g' -> 4 pts (x,y),(y,x),(s-x,s-y),(s-y,s-x)   [reflections in both diagonals]
          'd' -> 2 pts (x,x),(s-x,s-x); 'a' -> 2 pts (x,s-x),(s-x,x); 'c' -> centre
    C2:   'g' -> 2 pts (x,y),(s-x,s-y); 'c'
    D4:   'g' -> 8 pts; 'x' -> 4 pts on axes (x,s/2),(s-x,s/2),(s/2,x),(s/2,s-x);
          'd' -> 4 pts on diagonals (x,x),(s-x,s-x),(x,s-x),(s-x,x); 'c'
    none: 'g' -> 1 pt.
    """

    def __init__(self, group, spec, s0):
        self.group, self.spec, self.s0 = group, list(spec), s0
        rows = []  # each row: (coeff dict over z-index, const)
        self.orbits = []  # (tag, first param index, first row index)
        k = 0
        s = s0
        for tag in self.spec:
            self.orbits.append((tag, k, len(rows)))
            if group == "none":
                rows += [({k: 1}, 0), ({k + 1: 1}, 0)]; k += 2
            elif group == "C2":
                if tag == "g":
                    rows += [({k: 1}, 0), ({k + 1: 1}, 0), ({k: -1}, s), ({k + 1: -1}, s)]; k += 2
                elif tag == "c":
                    rows += [({}, s / 2), ({}, s / 2)]
            elif group == "axes":
                if tag == "g":
                    x, y = k, k + 1
                    rows += [({x: 1}, 0), ({y: 1}, 0), ({x: -1}, s), ({y: 1}, 0),
                             ({x: 1}, 0), ({y: -1}, s), ({x: -1}, s), ({y: -1}, s)]; k += 2
                elif tag == "v":
                    rows += [({}, s / 2), ({k: 1}, 0), ({}, s / 2), ({k: -1}, s)]; k += 1
                elif tag == "h":
                    rows += [({k: 1}, 0), ({}, s / 2), ({k: -1}, s), ({}, s / 2)]; k += 1
                elif tag == "c":
                    rows += [({}, s / 2), ({}, s / 2)]
            elif group == "diag":
                if tag == "g":
                    x, y = k, k + 1
                    rows += [({x: 1}, 0), ({y: 1}, 0), ({y: 1}, 0), ({x: 1}, 0),
                             ({x: -1}, s), ({y: -1}, s), ({y: -1}, s), ({x: -1}, s)]; k += 2
                elif tag == "d":
                    rows += [({k: 1}, 0), ({k: 1}, 0), ({k: -1}, s), ({k: -1}, s)]; k += 1
                elif tag == "a":
                    rows += [({k: 1}, 0), ({k: -1}, s), ({k: -1}, s), ({k: 1}, 0)]; k += 1
                elif tag == "c":
                    rows += [({}, s / 2), ({}, s / 2)]
            elif group == "D4":
                if tag == "g":
                    x, y = k, k + 1
                    for (ax, bx, ay, by) in [(1, 0, 1, 0), (-1, s, 1, 0), (1, 0, -1, s), (-1, s, -1, s)]:
                        rows += [({x: ax}, bx), ({y: ay}, by)]
                        rows += [({y: ay}, by), ({x: ax}, bx)]
                    k += 2
                elif tag == "x":
                    rows += [({k: 1}, 0), ({}, s / 2), ({k: -1}, s), ({}, s / 2),
                             ({}, s / 2), ({k: 1}, 0), ({}, s / 2), ({k: -1}, s)]; k += 1
                elif tag == "d":
                    rows += [({k: 1}, 0), ({k: 1}, 0), ({k: -1}, s), ({k: -1}, s),
                             ({k: 1}, 0), ({k: -1}, s), ({k: -1}, s), ({k: 1}, 0)]; k += 1
                elif tag == "c":
                    rows += [({}, s / 2), ({}, s / 2)]
            else:
                raise ValueError(group)
        self.k = k
        self.n = len(rows) // 2
        A = np.zeros((2 * self.n, k))
        b = np.zeros(2 * self.n)
        for i, (coef, const) in enumerate(rows):
            for j, c in coef.items():
                A[i, j] += c
            b[i] = const
        self.A, self.b = A, b

    def P(self, z):
        return (self.A @ z + self.b).reshape(self.n, 2)

    def random_z(self, rng, margin=0.5):
        """random parameters with all points inside [margin, s0-margin]^2 (approx)."""
        z = np.zeros(self.k)
        s = self.s0
        j = 0
        for tag in self.spec:
            npar = self._npar(tag)
            for _ in range(npar):
                z[j] = rng.uniform(margin, s - margin) if self.group != "none" else rng.uniform(margin, s - margin)
                j += 1
        return z

    def _npar(self, tag):
        if self.group == "none":
            return 2
        return {"g": 2, "v": 1, "h": 1, "c": 0, "d": 1, "a": 1, "x": 1}[tag]

    def z_from_P(self, P):
        """least squares fit of z to a point set (used for warm starts across s0)."""
        z, *_ = np.linalg.lstsq(self.A, P.flatten() - self.b, rcond=None)
        return z

    def rescale(self, new_s0):
        """same spec, new s0; parameters z are rescaled about the centre."""
        return Param(self.group, self.spec, new_s0)


# ----------------------------------------------------------------------------------------
# SLP minimiser of max d over P (trust region, cutting-plane set of critical configs)
# ----------------------------------------------------------------------------------------

def _config_matrix(configs, P):
    """For configs (list of (cx,cy,th,*)), return arrays cx,cy,ct,st and assigned point index."""
    C = np.array([[c[0], c[1], c[2]] for c in configs])
    ct, st = np.cos(C[:, 2]), np.sin(C[:, 2])
    dx = P[None, :, 0] - C[:, 0:1]
    dy = P[None, :, 1] - C[:, 1:2]
    u = ct[:, None] * dx + st[:, None] * dy
    v = -st[:, None] * dx + ct[:, None] * dy
    cheb = np.maximum(np.abs(u), np.abs(v))
    assign = cheb.argmin(axis=1)
    return C[:, 0], C[:, 1], ct, st, assign, cheb.min(axis=1) - 0.5


def slp(param, z0, s0, iters=200, rho0=0.05, rho_min=1e-7, tol=1e-9, nth=64, nc=80, K=40,
        keep=3000, verbose=False, target=None, tr_lin=True):
    """Minimise g(z) = max_{c,theta} d over z (P = param.P(z)).  Returns (z, g, configs).
    Uses cutting-plane critical configs + LP model with fixed point assignment + trust region."""
    z = np.array(z0, float)
    P = param.P(z)
    crit = worst_configs(P, s0, nth, nc, K)
    g = crit[0][3]
    rho = rho0
    n2, k = param.A.shape
    lo_bounds_P = np.zeros(n2)
    hi_bounds_P = np.full(n2, s0)
    hist = []
    for it in range(iters):
        if target is not None and g <= target:
            break
        # assign + build LP:  variables (z, t);  minimise t
        cx, cy, ct, st, assign, dvals = _config_matrix(crit, P)
        # rows of A for x and y of assigned point:
        Ax = param.A[2 * assign]      # (m,k)
        Ay = param.A[2 * assign + 1]
        bx = param.b[2 * assign]
        by = param.b[2 * assign + 1]
        # u = ct*(px-cx) + st*(py-cy) = (ct*Ax + st*Ay) z + ct*(bx-cx) + st*(by-cy)
        Au = ct[:, None] * Ax + st[:, None] * Ay
        cu = ct * (bx - cx) + st * (by - cy)
        Av = -st[:, None] * Ax + ct[:, None] * Ay
        cv = -st * (bx - cx) + ct * (by - cy)
        m = len(crit)
        # constraints:  u - t <= 1/2 - cu ;  -u - t <= 1/2 + cu ; same for v
        A_ub = np.vstack([np.hstack([Au, -np.ones((m, 1))]),
                          np.hstack([-Au, -np.ones((m, 1))]),
                          np.hstack([Av, -np.ones((m, 1))]),
                          np.hstack([-Av, -np.ones((m, 1))])])
        b_ub = np.concatenate([0.5 - cu, 0.5 + cu, 0.5 - cv, 0.5 + cv])
        # points inside container:  0 <= A z + b <= s0
        A_ub = np.vstack([A_ub, np.hstack([param.A, np.zeros((n2, 1))]), np.hstack([-param.A, np.zeros((n2, 1))])])
        b_ub = np.concatenate([b_ub, hi_bounds_P - param.b, param.b - lo_bounds_P])
        c = np.zeros(k + 1); c[-1] = 1.0
        bounds = [(zi - rho, zi + rho) for zi in z] + [(None, None)]
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")
        if res.status != 0:
            if verbose:
                print("LP fail", res.message)
            rho *= 0.5
            if rho < rho_min:
                break
            continue
        z_new = res.x[:k]
        pred = res.x[-1]
        P_new = param.P(z_new)
        new_crit = worst_configs(P_new, s0, nth, nc, K)
        g_new = new_crit[0][3]
        # merge critical sets
        crit_all = crit + new_crit
        # re-evaluate all stored configs at P_new, keep the most critical `keep`
        _, _, _, _, _, dv = _config_matrix(crit_all, P_new)
        order = np.argsort(-dv)
        crit_all = [crit_all[i] for i in order[:keep]]
        hist.append((it, g, g_new, pred, rho))
        if verbose:
            print(f"it {it:3d} g={g:.6f} -> {g_new:.6f} pred={pred:.6f} rho={rho:.2e} m={m}")
        if g_new < g - 1e-12:
            # accept
            ratio = (g - g_new) / max(g - pred, 1e-15)
            z, P, g = z_new, P_new, g_new
            crit = crit_all
            if ratio > 0.5:
                rho = min(rho * 1.6, 0.5)
            elif ratio < 0.1:
                rho *= 0.7
        else:
            # reject, but keep the new configs (they are informative), shrink
            crit = crit_all
            rho *= 0.4
            if rho < rho_min:
                break
    return z, g, crit, hist


def solve_at_s0(param, z0, s0, **kw):
    z, g, crit, hist = slp(param, z0, s0, **kw)
    return z, g, crit


def find_max_s0(group, spec, z_init, s0_init, m_target=0.0, s_lo=None, s_hi=None,
                tol_s=1e-5, verbose=False, slp_kw=None):
    """Largest s0 with min_P max d <= -m_target, by continuation + bisection.
    Returns (s0_best, z_best, g_best, param_best)."""
    slp_kw = slp_kw or {}
    param = Param(group, spec, s0_init)
    z = np.array(z_init, float)
    z, g, _ = solve_at_s0(param, z, s0_init, **slp_kw)
    feas = g <= -m_target
    if verbose:
        print(f"s0={s0_init:.6f} g={g:.6f} feas={feas}")
    # expand / shrink to bracket
    step = 0.05
    if feas:
        lo, zlo, glo = s0_init, z.copy(), g
        hi = None
        while hi is None:
            s_try = lo + step
            p2 = Param(group, spec, s_try)
            z_try = _transfer(param, z if hi is None else zlo, p2)
            z2, g2, _ = solve_at_s0(p2, z_try, s_try, **slp_kw)
            if verbose:
                print(f"s0={s_try:.6f} g={g2:.6f}")
            if g2 <= -m_target:
                lo, zlo, glo, param = s_try, z2, g2, p2
                step *= 1.5
            else:
                hi, zhi = s_try, z2
    else:
        hi, zhi = s0_init, z.copy()
        lo = None
        while lo is None:
            s_try = hi - step
            p2 = Param(group, spec, s_try)
            z_try = _transfer(param, zhi, p2)
            z2, g2, _ = solve_at_s0(p2, z_try, s_try, **slp_kw)
            if verbose:
                print(f"s0={s_try:.6f} g={g2:.6f}")
            if g2 <= -m_target:
                lo, zlo, glo = s_try, z2, g2
                param = p2
            else:
                hi, zhi = s_try, z2
                step *= 1.5
                param = p2
    # bisection
    plo = Param(group, spec, lo)
    while hi - lo > tol_s:
        mid = 0.5 * (lo + hi)
        pm = Param(group, spec, mid)
        z_try = _transfer(plo, zlo, pm)
        zm, gm, _ = solve_at_s0(pm, z_try, mid, **slp_kw)
        if verbose:
            print(f"  bisect s0={mid:.6f} g={gm:.6f}")
        if gm <= -m_target:
            lo, zlo, glo, plo = mid, zm, gm, pm
        else:
            hi = mid
    return lo, zlo, glo, plo


def _transfer(p_from, z, p_to):
    """Move parameters to a new s0 by scaling the point set about the centre."""
    P = p_from.P(z)
    P2 = (P - p_from.s0 / 2) * (p_to.s0 / p_from.s0) + p_to.s0 / 2
    return p_to.z_from_P(P2)


# ----------------------------------------------------------------------------------------
# geometry helpers
# ----------------------------------------------------------------------------------------

def square_corners(cx, cy, th):
    ct, st = np.cos(th), np.sin(th)
    R = np.array([[ct, -st], [st, ct]])
    loc = np.array([[-0.5, -0.5], [0.5, -0.5], [0.5, 0.5], [-0.5, 0.5], [-0.5, -0.5]])
    return loc @ R.T + np.array([cx, cy])


# ----------------------------------------------------------------------------------------
# orbit manipulation and basin hopping
# ----------------------------------------------------------------------------------------

def _set_orbit(param, z, oi, target):
    """Set the parameters of orbit oi so that the orbit contains (approximately) the target point."""
    tag, k0, r0 = param.orbits[oi]
    s = param.s0
    tx, ty = target
    z = z.copy()
    g = param.group
    if g == "none" or tag == "g":
        z[k0], z[k0 + 1] = tx, ty
    elif tag == "c":
        pass
    elif g == "axes":
        if tag == "v":
            z[k0] = ty
        elif tag == "h":
            z[k0] = tx
    elif g == "diag":
        if tag == "d":
            z[k0] = 0.5 * (tx + ty)
        elif tag == "a":
            z[k0] = 0.5 * (tx + s - ty)
    elif g == "D4":
        if tag == "x":
            z[k0] = tx if abs(tx - s / 2) >= abs(ty - s / 2) else ty
        elif tag == "d":
            # nearer diagonal
            if abs(tx - ty) <= abs(tx + ty - s):
                z[k0] = 0.5 * (tx + ty)
            else:
                z[k0] = 0.5 * (tx + s - ty)
    elif g == "C2":
        z[k0], z[k0 + 1] = tx, ty
    return z


def orbit_points(param, oi):
    tag, k0, r0 = param.orbits[oi]
    npts = {"none": {"g": 1}, "C2": {"g": 2, "c": 1}, "axes": {"g": 4, "v": 2, "h": 2, "c": 1},
            "diag": {"g": 4, "d": 2, "a": 2, "c": 1}, "D4": {"g": 8, "x": 4, "d": 4, "c": 1}}[param.group][tag]
    return list(range(r0 // 2, r0 // 2 + npts))


def basin_hop(param, z, s0, n_kicks=30, rng=None, verbose=False, slp_kw=None, patience=8):
    """Kick heuristic: move the least useful orbit onto the worst square, re-polish with SLP."""
    rng = rng or np.random.default_rng()
    slp_kw = dict(slp_kw or {})
    z, g, crit, _ = slp(param, z, s0, **slp_kw)
    best_z, best_g = z.copy(), g
    fails = 0
    for kick in range(n_kicks):
        P = param.P(best_z)
        wc = worst_configs(P, s0, nth=48, nc=60, K=10)
        # target: one of the top few worst squares
        tgt = wc[min(rng.integers(0, min(3, len(wc))), len(wc) - 1)]
        # usefulness of each orbit
        use = []
        for oi in range(len(param.orbits)):
            if param.orbits[oi][0] == "c":
                use.append(np.inf); continue
            keep = [i for i in range(param.n) if i not in orbit_points(param, oi)]
            if not keep:
                use.append(np.inf); continue
            g_wo = worst_configs(P[keep], s0, nth=32, nc=40, K=3, refine=False)[0][3]
            use.append(g_wo)
        order = np.argsort(use)
        cand = [o for o in order[:3] if np.isfinite(use[o])]
        oi = cand[rng.integers(0, len(cand))]
        z_try = _set_orbit(param, best_z, oi, (tgt[0], tgt[1]))
        # small jitter to break ties
        z_try = z_try + rng.normal(0, 0.01, size=z_try.shape)
        z2, g2, _, _ = slp(param, z_try, s0, **slp_kw)
        if verbose:
            print(f"  kick {kick}: orbit {oi} -> ({tgt[0]:.3f},{tgt[1]:.3f})  g {best_g:.5f} -> {g2:.5f}")
        if g2 < best_g - 1e-9:
            best_z, best_g = z2, g2
            fails = 0
        else:
            fails += 1
            if fails >= patience:
                break
    return best_z, best_g
