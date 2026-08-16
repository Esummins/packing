"""
Fixed-s basin hopping ("shrink-container" search).
usage: python fsbh.py <seed> <minutes> <outfile> [start_type]
State: centres+angles at container side s_t (fixed).  Local step = L-BFGS on overlap penalty (mu=1).
If penalty ~ 0 -> feasible packing at s_t: polish with free-s penalty continuation (local optimum s*),
record it, shrink s_t below s*, continue.  Else perturb and retry (Metropolis on penalty).
"""
import sys, time, json
import numpy as np
from scipy.optimize import minimize
import pack11 as P
from pack11 import N, unpack, pack, obj_grad, penalty_solve, feasibility, canonical, \
    start_random, start_biased, start_diagonal_band
from driver import local_opt, Writer, perturb


def fixed_s_local(x, s_t, maxiter=300):
    def fg(z):
        xx = np.concatenate([z, [s_t]])
        F, g = obj_grad(xx, 1.0)
        return F - s_t, g[:-1]
    res = minimize(fg, x[:-1], jac=True, method='L-BFGS-B',
                   options=dict(maxiter=maxiter, maxcor=20, ftol=1e-16, gtol=1e-12))
    z = res.x
    z[2 * N:3 * N] = np.mod(z[2 * N:3 * N], np.pi / 2)
    return np.concatenate([z, [s_t]]), float(res.fun)


def kick(x, rng, s_t):
    c, th, s = unpack(x)
    c = c.copy(); th = th.copy()
    r = rng.random()
    if r < 0.35:
        m = 1 if rng.random() < 0.7 else 2
        for i in rng.choice(N, m, replace=False):
            c[i] = rng.uniform(0.5, s_t - 0.5, size=2)
            u = rng.random()
            th[i] = 0.0 if u < 0.35 else rng.uniform(0, np.pi / 2)
    elif r < 0.55:
        i = rng.integers(N)
        th[i] = np.mod(th[i] + rng.normal(0, 0.4), np.pi / 2)
    elif r < 0.70:
        i, j = rng.choice(N, 2, replace=False)
        c[[i, j]] = c[[j, i]]
    elif r < 0.80:
        i = rng.integers(N)
        th[i] = np.mod(np.pi / 2 - th[i], np.pi / 2)
    elif r < 0.90:
        c += rng.normal(0, 0.10, size=c.shape)
        th += rng.normal(0, 0.10, size=N)
    else:
        i = rng.integers(N)
        c[i] += rng.normal(0, 0.4, 2)
        th[i] = 0.0 if rng.random() < 0.4 else rng.uniform(0, np.pi / 2)
    return pack(c, th, s_t)


def main():
    seed, minutes, out = int(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
    start_type = sys.argv[4] if len(sys.argv) > 4 else 'mix'
    near_rec = len(sys.argv) > 5 and sys.argv[5] == 'near'
    rng = np.random.default_rng(seed)
    W = Writer(out)
    t_end = time.time() + 60 * minutes
    tilts = [40., 45., 30., 'two', None]
    chain = 0
    while time.time() < t_end:
        chain += 1
        s_t = rng.uniform(3.90, 3.99)
        if start_type == 'record':
            # contact-structure jiggling: start from the best known configuration found so far
            import glob
            best = None
            for f in glob.glob('res_fsbh[1-5].jsonl'):
                for line in open(f):
                    r = json.loads(line)
                    if best is None or r['s'] < best['s']:
                        best = r
            x = np.array(best['x'])
            s_t = best['s'] - rng.choice([0.0002, 0.001, 0.003, 0.006, 0.010])
            c, th, s_b = unpack(x)
            c = (c - s_b / 2) * (s_t / s_b) + s_t / 2
            x = pack(c, th, s_t)
            # structural mutation before hopping
            for _ in range(int(rng.integers(1, 4))):
                x = kick(x, rng, s_t)
        elif start_type == 'rand' or (start_type == 'mix' and rng.random() < 0.4):
            x = start_random(rng, s0=s_t)
        elif start_type == 'diag':
            x = start_diagonal_band(rng); x[-1] = s_t
        else:
            x = start_biased(rng, k=int(rng.integers(3, 9)), tilt=tilts[chain % 5], s0=s_t)
        x, pen = fixed_s_local(x, s_t)
        fails = 0; T = 2e-4
        nfeas = 0
        maxfails = 300 if start_type == 'record' else 120
        while fails < maxfails and time.time() < t_end:
            if pen < 1e-11:
                # feasible at s_t: polish freely
                xs, s_strict, s_raw, ov, cv = local_opt(x, deep=True)
                W.write(xs, s_strict, s_raw, ov, cv, 'fsbh' if start_type != 'record' else 'fsbh-rec', dict(chain=chain, s_t=s_t))
                nfeas += 1
                s_t = min(s_t, s_strict) - rng.uniform(0.001, 0.008)
                x = xs.copy(); x[-1] = s_t
                # rescale centres into new container
                c, th, s = unpack(x)
                c = (c - s_strict / 2) * (s_t / s_strict) + s_t / 2
                x = pack(c, th, s_t)
                x, pen = fixed_s_local(x, s_t)
                fails = 0
                continue
            xp = kick(x, rng, s_t)
            xp, penp = fixed_s_local(xp, s_t)
            if near_rec and penp < 3e-4 and rng.random() < 0.5:
                # near-feasible: relax freely to a nearby local optimum and record it (catalogue breadth)
                xs, s_strict, s_raw, ov, cv = local_opt(xp, deep=True)
                W.write(xs, s_strict, s_raw, ov, cv, 'fsbh-near', dict(chain=chain, s_t=s_t))
            if penp < pen - 1e-14 or rng.random() < np.exp(-(penp - pen) / T):
                if penp < pen - 1e-14:
                    fails = 0
                else:
                    fails += 1
                x, pen = xp, penp
            else:
                fails += 1
        # chain end
        if nfeas == 0:
            # record the infeasible best as a free local optimum anyway (gives catalogue coverage)
            xs, s_strict, s_raw, ov, cv = local_opt(x, deep=True)
            W.write(xs, s_strict, s_raw, ov, cv, 'fsbh-relax' if start_type != 'record' else 'fsbh-rec-relax', dict(chain=chain, s_t=s_t))
    print('done fsbh', W.n, 'records, best', W.best)


if __name__ == '__main__':
    main()
