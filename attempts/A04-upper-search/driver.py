"""
Search driver.  usage:  python driver.py <method> <seed> <minutes> <outfile>
methods: rand | biased | bh | diag | bhrec
Each local optimisation result is appended to <outfile> (JSON lines) immediately.
"""
import sys, time, json, os
import numpy as np
from scipy.optimize import minimize
import pack11 as P
from pack11 import N, unpack, pack, penalty_solve, feasibility, pair_overlaps, canonical, \
    start_random, start_biased, start_diagonal_band, sat_min_overlap, container_viol

RECORD = 3.877084


def local_opt(x0, deep=True):
    """penalty continuation + high-mu refinement + attempted SLSQP polish + inflation to strict feasibility.
    Returns (x_strict, s_strict, s_raw, ovmax, cvmax)."""
    x = penalty_solve(x0)
    x = penalty_solve(x, mus=(1e7, 1e8), maxiter=1000)
    if deep:
        xs = try_slsqp(x)
        if xs is not None:
            x = xs
    ovmax, cvmax = feasibility(x)
    # inflate: scale centres about container centre so that all overlaps close
    c, th, s = unpack(x)
    eps = max(ovmax, 0.0) * 1.05 + 1e-12
    cc = (c - s / 2) * (1 + eps) + s / 2
    xs = pack(cc, th, s)
    # now fix container: shift so it fits, s = bounding extent
    e = P.H * (np.abs(np.cos(th)) + np.abs(np.sin(th)))
    lo = (cc - e[:, None]).min(axis=0); hi = (cc + e[:, None]).max(axis=0)
    cc = cc - lo
    s_strict = float(max(hi - lo)) + 1e-12
    xs = pack(cc, th, s_strict)
    ov2, cv2 = feasibility(xs)
    return xs, s_strict, float(s), ov2, cv2


def try_slsqp(x, thresh=2e-3, maxiter=300):
    ov, _ = pair_overlaps(x)
    kfix = np.argmin(ov, axis=1); ovm = ov.min(axis=1)
    act = np.nonzero(ovm > -thresh)[0]
    if len(act) == 0:
        return None
    fpair = lambda x, k=kfix, act=act: P._pair_con_fixed(x, k)[0][act]
    jpair = lambda x, k=kfix, act=act: P._pair_con_fixed(x, k)[1][act]
    cons = [dict(type='ineq', fun=fpair, jac=jpair),
            dict(type='ineq', fun=lambda x: P._cont_con(x)[0], jac=lambda x: P._cont_con(x)[1])]
    try:
        res = minimize(lambda x: x[3 * N], x, jac=lambda x: np.eye(3 * N + 1)[3 * N],
                       constraints=cons, method='SLSQP', options=dict(maxiter=maxiter, ftol=1e-15))
    except Exception:
        return None
    xn = res.x.copy()
    xn[2 * N:3 * N] = np.mod(xn[2 * N:3 * N], np.pi / 2)
    ovn, cvn = feasibility(xn)
    if ovn < 1e-8 and cvn < 1e-8 and xn[3 * N] <= x[3 * N] + 1e-10:
        return xn
    return None


class Writer:
    def __init__(self, path):
        self.f = open(path, 'a', buffering=1)
        self.n = 0
        self.best = 99.0

    def write(self, xs, s_strict, s_raw, ov, cv, method, extra=None):
        c, th, s = unpack(xs)
        _, angs = canonical(xs)
        rec = dict(s=s_strict, s_raw=s_raw, ovmax=ov, cvmax=cv, method=method, angles=angs,
                   x=[round(v, 12) for v in xs.tolist()], t=time.time())
        if extra:
            rec.update(extra)
        self.f.write(json.dumps(rec) + '\n')
        self.n += 1
        if s_strict < self.best:
            self.best = s_strict
            print('[%s] new best %.7f  angles %s' % (method, s_strict, angs), flush=True)
            if s_strict < RECORD:
                with open('CANDIDATE_%s_%d.json' % (method, int(time.time())), 'w') as g:
                    json.dump(rec, g)
                print('!!!!! CANDIDATE BELOW RECORD', s_strict, flush=True)


# ---------------- perturbations for basin hopping -----------------
def perturb(x, rng, structural=False):
    c, th, s = unpack(x)
    c = c.copy(); th = th.copy()
    r = rng.random()
    if r < 0.30:      # relocate 1-2 squares randomly
        m = 1 if rng.random() < 0.6 else 2
        for i in rng.choice(N, m, replace=False):
            c[i] = rng.uniform(0.6, s - 0.6, size=2)
            th[i] = rng.uniform(0, np.pi / 2) if rng.random() < 0.7 else 0.0
    elif r < 0.50:    # rotate one square by random amount
        i = rng.integers(N)
        th[i] = np.mod(th[i] + rng.normal(0, 0.5), np.pi / 2)
    elif r < 0.65:    # swap two squares (position swap keeps angles) -> effectively swaps angles
        i, j = rng.choice(N, 2, replace=False)
        c[[i, j]] = c[[j, i]]
    elif r < 0.75:    # mirror one tilted square's angle
        i = rng.integers(N)
        th[i] = np.mod(np.pi / 2 - th[i], np.pi / 2)
    elif r < 0.85:    # rotate all tilted squares by delta
        tilted = (np.mod(np.degrees(th), 90) > 3) & (np.mod(np.degrees(th), 90) < 87)
        th[tilted] = np.mod(th[tilted] + rng.normal(0, 0.15), np.pi / 2)
    elif r < 0.93:    # jiggle everything
        c += rng.normal(0, 0.12, size=c.shape)
        th += rng.normal(0, 0.12, size=N)
    else:             # make a tilted square upright or vice versa
        i = rng.integers(N)
        if np.mod(np.degrees(th[i]), 90) < 3 or np.mod(np.degrees(th[i]), 90) > 87:
            th[i] = np.radians(rng.uniform(15, 75))
        else:
            th[i] = 0.0
    return pack(c, th, s + 0.05)


def bh_chain(x0, rng, W, method, hops=60, T=0.02, deep=True):
    xs, s_strict, s_raw, ov, cv = local_opt(x0, deep)
    W.write(xs, s_strict, s_raw, ov, cv, method, dict(hop=0))
    xcur, scur = xs, s_strict
    xbest, sbest = xs, s_strict
    for h in range(hops):
        xp = perturb(xcur, rng)
        xs, s_strict, s_raw, ov, cv = local_opt(xp, deep)
        W.write(xs, s_strict, s_raw, ov, cv, method, dict(hop=h + 1))
        if s_strict < scur - 1e-9 or rng.random() < np.exp(-(s_strict - scur) / T):
            xcur, scur = xs, s_strict
        if s_strict < sbest:
            xbest, sbest = xs, s_strict
    return xbest, sbest


def main():
    method, seed, minutes, out = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
    rng = np.random.default_rng(seed)
    W = Writer(out)
    t_end = time.time() + 60 * minutes
    tilts = [40., 45., 30., 'two', None, 40., None]
    it = 0
    while time.time() < t_end:
        it += 1
        if method == 'rand':
            x0 = start_random(rng)
            W.write(*local_opt(x0), method)
        elif method == 'biased':
            k = int(rng.integers(4, 9)); tilt = tilts[it % len(tilts)]
            x0 = start_biased(rng, k=k, tilt=tilt)
            W.write(*local_opt(x0), method, dict(k=k, tilt=str(tilt)))
        elif method == 'bh':
            if rng.random() < 0.5:
                x0 = start_random(rng)
            else:
                x0 = start_biased(rng, tilt=tilts[it % len(tilts)])
            bh_chain(x0, rng, W, method, hops=int(rng.integers(30, 80)), T=0.02)
        elif method == 'diag':
            x0 = start_diagonal_band(rng)
            bh_chain(x0, rng, W, method, hops=int(rng.integers(20, 60)), T=0.015)
        elif method == 'bhlong':
            x0 = start_biased(rng, tilt=tilts[it % len(tilts)])
            bh_chain(x0, rng, W, method, hops=250, T=0.03)
        elif method == 'bhrec':
            # start from best known configuration in a given file and hop from it
            best = None
            for line in open(sys.argv[5]):
                r = json.loads(line)
                if best is None or r['s'] < best['s']:
                    best = r
            x0 = np.array(best['x'])
            bh_chain(x0, rng, W, method, hops=200, T=0.01)
    print('done', method, W.n, 'records, best', W.best)


if __name__ == '__main__':
    main()
