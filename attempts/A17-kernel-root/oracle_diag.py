"""A17 — diagonal separation oracle: maximise K(x,x) over x in P_s.
Stages: (1) vectorised scan over structured grid + random placements (with admissible-boundary and
theta in {0, 45, 90} deg emphasis — the A14 blind-spot lesson) + boundary sweeps, (2) pattern-search
polish from the top candidates.  K through the factor L (KernelEval).
"""
import math
import numpy as np
from oracle_pair import KernelEval, admissible_many
from features import random_placements


def boundary_sweep(s, n_theta=181, step_c=0.02):
    """placements with the centre ON the admissible boundary (cx = w/2 etc.), all four sides."""
    out = []
    for th in np.linspace(0.0, math.pi / 2, n_theta):
        w = math.cos(th) + math.sin(th)
        lo, hi = w / 2, s - w / 2
        cs = np.arange(lo, hi + 1e-12, step_c)
        for fixed, is_x in ((lo, True), (hi, True), (lo, False), (hi, False)):
            m = len(cs)
            P = np.empty((m, 3))
            P[:, 2] = th
            if is_x:
                P[:, 0] = fixed; P[:, 1] = cs
            else:
                P[:, 0] = cs; P[:, 1] = fixed
            out.append(P)
        # corners of the admissible square
        out.append(np.array([[lo, lo, th], [lo, hi, th], [hi, lo, th], [hi, hi, th]]))
    return np.vstack(out)


def polish_diag(ke, s, x, step0=0.04, min_step=2e-4, max_eval=300):
    x = np.array(x, float)
    u = ke.u_single(x)
    best = float(u @ u)
    step = step0
    nev = 0
    from oracle_pair import _moves
    while step >= min_step and nev < max_eval:
        improved = False
        for mv in _moves():
            cand = x + mv * np.array([step, step, step * 0.6])
            cand[2] %= math.pi / 2
            # clamp to admissibility (moves toward the wall land ON the boundary)
            w = math.cos(cand[2]) + math.sin(cand[2])
            cand[0] = min(max(cand[0], w / 2), s - w / 2)
            cand[1] = min(max(cand[1], w / 2), s - w / 2)
            uc = ke.u_single(cand)
            nev += 1
            v = float(uc @ uc)
            if v > best + 1e-12:
                best = v; x = cand; u = uc
                improved = True
                break
        if not improved:
            step *= 0.5
    return best, x


def diag_oracle(ke, s, structP=None, rng=None, n_rand=40000, n_polish=60, topk=300,
                bnd_theta=121, bnd_step=0.03, log=print, extra_seeds=None):
    rng = np.random.default_rng(0) if rng is None else rng
    sets = []
    if structP is not None:
        sets.append(structP)
    if extra_seeds is not None and len(extra_seeds):
        sets.append(np.asarray(extra_seeds))
    sets.append(random_placements(s, n_rand, rng, boundary_frac=0.3))
    sets.append(boundary_sweep(s, n_theta=bnd_theta, step_c=bnd_step))
    P = np.vstack(sets)
    kv = ke.kdiag(P)
    order = np.argsort(-kv)
    log(f"    [diag] scan {len(P)} placements: max K(x,x) {kv[order[0]]:.6f}")
    cands = []
    seen = set()
    for t in order[: topk * 4]:
        key = (round(P[t, 0], 3), round(P[t, 1], 3), round(P[t, 2], 3))
        if key in seen:
            continue
        seen.add(key)
        cands.append((float(kv[t]), P[t].copy()))
        if len(cands) >= topk:
            break
    polished = []
    starts = cands[:n_polish]
    if extra_seeds is not None and len(extra_seeds):
        kv_seed = ke.kdiag(np.asarray(extra_seeds))
        o = np.argsort(-kv_seed)[: max(20, n_polish // 2)]
        starts = starts + [(float(kv_seed[t]), np.asarray(extra_seeds)[t]) for t in o]
    for v, x in starts:
        vb, xb = polish_diag(ke, s, x)
        polished.append((vb, xb))
    all_c = sorted(polished + cands, key=lambda c: -c[0])
    log(f"    [diag] best after polish: {all_c[0][0]:.6f}")
    return dict(best=all_c[0], cands=all_c[:topk])


if __name__ == "__main__":
    # calibration harness lives in calibrate.py; here a smoke test on the LP kernel at 3.84
    from features import FeatureMap, load_atoms_a07_384, structured_placements
    A, w, s = load_atoms_a07_384()
    fm = FeatureMap(A, w, s)
    M = fm.M_lp()
    wv, U = np.linalg.eigh(M)
    L = (np.sqrt(np.maximum(wv, 0.0))[:, None] * U.T)
    ke = KernelEval(fm, L)
    rng = np.random.default_rng(0)
    r = diag_oracle(ke, s, structP=structured_placements(s), rng=rng, n_rand=20000, n_polish=25)
    tau = w.sum()
    v, x = r["best"]
    print(f"LP kernel at 3.84: max K(x,x) = {v:.6f} -> min coverage {tau/(v+1):.6f} at {x}")


def coverage_seeds(fm, s, dth_deg=0.25, cstep=0.005, nseed=3000, log=print):
    """A07-style dense coverage scan: for each theta on [0,45] deg (D4 suffices), histogram the atoms
    in the rotated frame with prefix sums -> exact-at-grid coverage m(x) on a (cstep) centre grid.
    Returns the nseed lowest-coverage admissible placements (seeds for the K(x,x) polish: the tau/m
    term makes low-coverage cells the prime diagonal suspects)."""
    import numpy as np
    A = fm.A; w = fm.w
    best = []
    for th in np.arange(0.0, 45.0 + 1e-9, dth_deg) * math.pi / 180.0:
        c, sn = math.cos(th), math.sin(th)
        u = c * A[:, 0] + sn * A[:, 1]
        v = -sn * A[:, 0] + c * A[:, 1]
        # centre in rotated frame: c' = R(-th) c; admissible c in [w2, s-w2]^2 (original frame)
        w2 = (c + sn) / 2
        lo, hi = w2, s - w2
        # grid in original frame
        cx = np.arange(lo, hi + 1e-12, cstep)
        cy = np.arange(lo, hi + 1e-12, cstep)
        CX, CY = np.meshgrid(cx, cy, indexing="ij")
        a = c * CX + sn * CY      # rotated centre coords
        b = -sn * CX + c * CY
        # prefix-sum histogram of atoms in rotated frame
        u0, v0 = u.min() - 0.6, v.min() - 0.6
        iu = np.floor((u - u0) / cstep).astype(int)
        iv = np.floor((v - v0) / cstep).astype(int)
        nu, nv = iu.max() + 2, iv.max() + 2
        H = np.zeros((nu + 1, nv + 1))
        np.add.at(H, (iu + 1, iv + 1), w)
        S = H.cumsum(0).cumsum(1)
        # window [a-.5, a+.5] x [b-.5, b+.5], midpoint rounding (ranking heuristic; exact re-check follows)
        i1 = np.clip(np.round((a - 0.5 - u0) / cstep).astype(int), 0, nu)
        i2 = np.clip(np.round((a + 0.5 - u0) / cstep).astype(int) + 1, 0, nu)
        j1 = np.clip(np.round((b - 0.5 - v0) / cstep).astype(int), 0, nv)
        j2 = np.clip(np.round((b + 0.5 - v0) / cstep).astype(int) + 1, 0, nv)
        cov = S[i2, j2] - S[i1, j2] - S[i2, j1] + S[i1, j1]
        k = min(60, cov.size)
        flat = np.argpartition(cov.ravel(), k)[:k]
        for t in flat:
            best.append((float(cov.ravel()[t]), float(CX.ravel()[t]), float(CY.ravel()[t]), float(th)))
    best.sort()
    best = best[:nseed]
    log(f"    [covscan] {len(best)} low-coverage seeds, lowest approx cov {best[0][0]:.4f} at "
        f"({best[0][1]:.3f},{best[0][2]:.3f},{math.degrees(best[0][3]):.2f}deg)")
    return np.array([[cx, cy, th] for _, cx, cy, th in best])


def polish_coverage(fm, s, x, step0=0.03, min_step=1e-4, max_eval=400):
    """pattern search MINIMISING coverage m(x) (exact, via patterns)."""
    from oracle_pair import _moves
    x = np.array(x, float)
    best = float(fm.coverage(x[None])[0])
    step = step0
    nev = 0
    while step >= min_step and nev < max_eval:
        improved = False
        for mv in _moves():
            cand = x + mv * np.array([step, step, step * 0.6])
            cand[2] %= math.pi / 2
            w2 = (math.cos(cand[2]) + math.sin(cand[2])) / 2
            cand[0] = min(max(cand[0], w2), s - w2)
            cand[1] = min(max(cand[1], w2), s - w2)
            v = float(fm.coverage(cand[None])[0])
            nev += 1
            if v < best - 1e-12:
                best = v; x = cand; improved = True
                break
        if not improved:
            step *= 0.5
    return best, x


def low_coverage_placements(fm, s, dth_deg=0.25, cstep=0.005, n_polish=250, log=print):
    """dense scan + exact re-rank + coverage pattern search: the low-m(x) suspects for the diagonal."""
    seeds = coverage_seeds(fm, s, dth_deg=dth_deg, cstep=cstep, nseed=4000, log=log)
    cov = fm.coverage(seeds)
    order = np.argsort(cov)
    out = []
    seen = set()
    for t in order:
        key = (round(seeds[t, 0], 2), round(seeds[t, 1], 2), round(seeds[t, 2], 2))
        if key in seen:
            continue
        seen.add(key)
        out.append(seeds[t])
        if len(out) >= n_polish:
            break
    res = []
    for x in out:
        v, xb = polish_coverage(fm, s, x)
        res.append((v, xb))
    res.sort(key=lambda r: r[0])
    log(f"    [covscan] exact min coverage after polish: {res[0][0]:.6f} at {res[0][1]}")
    return np.array([xb for _, xb in res]), np.array([v for v, _ in res])
