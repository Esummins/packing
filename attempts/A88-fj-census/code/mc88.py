"""A88 Monte-Carlo layer for k_H = 11.

The FACTORABLE measure (uniform on {(mask tuple, edge set) : all pairs coexist,
every edge is in the touching window}) is sampled EXACTLY in the mask direction
and by an importance-tilted Bernoulli in the edge direction:

  * masks: the marginal is  P(m) proportional to 2^{T(m)} * [all pairs coexist],
    and both T(m) and the coexistence predicate depend on the mask COUNT VECTOR
    only (verified in selftest88: coexistence fails exactly for two squares with
    the SAME corner mask, and the touching window fails exactly for a pair whose
    masks jointly carry two OPPOSITE walls).  So the exact marginal is a discrete
    distribution on the 75582 - (corner-repeat) count vectors; we sample it
    exactly and then permute.  sum over count vectors of W = Z (asserted against
    the Burnside identity term).
  * edges: each touchable pair is included with probability q; the importance
    weight of a draw is  2^{-T} / (q^{|E|} (1-q)^{T-|E|}).

Hence  p = |F0 & factorable| / |factorable|  is estimated without bias by the
mean of  1_{F0} * weight, and the Level-0 census estimate is Z * p (labelled)
or (Burnside UB) * p (orbits, with the orbit-weight caveat).
"""
import os
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
import itertools
import json
import math
import sys
import time

import numpy as np

import a88lib as A

K = 11
PAIRS = [(i, j) for i in range(K) for j in range(i + 1, K)]
NPAIR = len(PAIRS)
PI = np.array([p[0] for p in PAIRS])
PJ = np.array([p[1] for p in PAIRS])


# ------------------------------------------------------- exact mask marginal
def mask_count_table():
    """All count vectors n over the 9 ALLOWED masks with sum 11 and every corner
    mask used at most once, with weight multinomial(11;n) * 2^{T(n)}."""
    T = A.TOUCH.astype(np.int64)
    corner = [A.MIDX[m] for m in A.CORNER_MASKS]
    vecs = []
    wts = []
    Ts = []
    fact = [math.factorial(i) for i in range(12)]

    def rec(pos, rem, cur):
        if pos == 8:
            cur.append(rem)
            c = tuple(cur)
            cur.pop()
            for q in corner:
                if c[q] > 1:
                    return
            t = 0
            for a in range(9):
                if c[a] >= 2:
                    t += (c[a] * (c[a] - 1) // 2) * int(T[a, a])
                for b in range(a + 1, 9):
                    t += c[a] * c[b] * int(T[a, b])
            m = fact[11]
            for x in c:
                m //= fact[x]
            vecs.append(c)
            wts.append(m * (1 << t))
            Ts.append(t)
            return
        lim = rem
        if pos in corner:
            lim = min(rem, 1)
        for v in range(lim + 1):
            cur.append(v)
            rec(pos + 1, rem - v, cur)
            cur.pop()
    rec(0, 11, [])
    return np.array(vecs, dtype=np.int64), wts, np.array(Ts, dtype=np.int64)


class MaskSampler:
    def __init__(self):
        self.vecs, self.wts, self.Ts = mask_count_table()
        self.Z = sum(self.wts)
        w = np.array([float(x) for x in self.wts])
        self.p = w / w.sum()
        self.cum = np.cumsum(self.p)

    def draw(self, n, rng):
        idx = np.searchsorted(self.cum, rng.random(n))
        idx = np.clip(idx, 0, len(self.p) - 1)
        V = self.vecs[idx]                                   # (n,9) counts
        C = np.cumsum(V, axis=1)                             # (n,9)
        srt = (C[:, None, :] <= np.arange(K)[None, :, None]).sum(2)   # (n,K)
        order = np.argsort(rng.random((n, K)), axis=1)
        out = np.empty((n, K), dtype=np.int64)
        np.put_along_axis(out, order, srt, axis=1)
        return out, self.Ts[idx]


# ------------------------------------------------------- vectorised filters
POPD = np.array([A.POP[m] for m in A.ALLOWED], dtype=np.int64)
BITD = np.array([[(m >> b) & 1 for b in range(4)] for m in A.ALLOWED],
                dtype=np.int64)
RAWD = np.array(A.ALLOWED, dtype=np.int64)
TOUCH_P = A.TOUCH


def cheap_flags(M, E):
    """M (B,11) dense mask indices, E (B,55) bool edge indicator.
    Returns dict of boolean arrays for the vectorisable F0 filters."""
    B = M.shape[0]
    deg = np.zeros((B, K), dtype=np.int64)
    for q in range(NPAIR):
        deg[:, PI[q]] += E[:, q]
        deg[:, PJ[q]] += E[:, q]
    wdeg = POPD[M]
    Ess = E.sum(1)
    Esw = wdeg.sum(1)
    Etot = Ess + Esw
    out = {}
    out['L1_deg2'] = ((deg + wdeg) >= 2).all(1)
    out['L5d_deg12'] = (deg <= 12).all(1)
    out['L4a_euler'] = Etot <= 3 * K + 2
    wcnt = np.zeros((B, 4), dtype=np.int64)
    for b in range(4):
        wcnt[:, b] = BITD[M, b].sum(1)
    out['N1_wallcap3'] = (wcnt <= 3).all(1)
    anyw = wcnt > 0
    out['L7'] = (anyw[:, 0] & anyw[:, 2]) | (anyw[:, 1] & anyw[:, 3])
    return out, Ess, Esw, deg


def slow_flags(mrow, erow):
    """L5(a) hop, L3, L6, L4(b) planarity for ONE sample."""
    wm = [int(RAWD[a]) for a in mrow]
    edges = [PAIRS[q] for q in np.nonzero(erow)[0]]
    f = A.f0_flags(K, edges, wm)
    return f, edges, wm


# ------------------------------------------------------------------ driver
STAGES = ['L1_deg2', 'L5d_deg12', 'L4a_euler', 'L5a_metric', 'L3_nofloat',
          'L6_span', 'L7', 'N1_wallcap3', 'L4b_planar']
QMIX = np.array([0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.42, 0.50])


def run(nsamp, seed, want_survivors=True, log=print, batch=20000):
    """Multiple-importance-sampling (balance heuristic) over the edge-inclusion
    probability q in QMIX.  Proposal density of an edge set given the touchable
    set of size T:  mix(e) = mean_q q^e (1-q)^{T-e};  target density 2^{-T}."""
    ms = MaskSampler()
    rng = np.random.default_rng(seed)
    ln2 = math.log(2.0)
    ns = len(STAGES)
    cum_w = [0.0] * (ns + 1)
    cum_w2 = [0.0] * (ns + 1)
    cnt = [0] * (ns + 1)
    survivors = []
    surv_w = []
    n_planar_calls = 0
    done = 0
    t0 = time.time()
    lq = np.log(QMIX)
    l1q = np.log(1.0 - QMIX)
    while done < nsamp:
        b = min(batch, nsamp - done)
        M, _ = ms.draw(b, rng)
        TP = TOUCH_P[M[:, PI], M[:, PJ]]                  # (b,55) bool
        qi = rng.integers(0, len(QMIX), size=b)
        E = (rng.random((b, NPAIR)) < QMIX[qi][:, None]) & TP
        nE = E.sum(1)
        Tc = TP.sum(1)
        # balance-heuristic mixture density
        lg = nE[:, None] * lq[None, :] + (Tc - nE)[:, None] * l1q[None, :]
        mx = lg.max(1)
        logmix = mx + np.log(np.exp(lg - mx[:, None]).mean(1))
        w = np.exp(-Tc * ln2 - logmix)
        cf, Ess, Esw, deg = cheap_flags(M, E)
        cum_w[0] += float(w.sum())
        cum_w2[0] += float((w * w).sum())
        cnt[0] += b
        alive = np.ones(b, dtype=bool)
        for si, nm in enumerate(['L1_deg2', 'L5d_deg12', 'L4a_euler']):
            alive &= cf[nm]
            cum_w[si + 1] += float(w[alive].sum())
            cum_w2[si + 1] += float((w[alive] ** 2).sum())
            cnt[si + 1] += int(alive.sum())
        for t in np.nonzero(alive)[0]:
            wm = [int(RAWD[a]) for a in M[t]]
            edges = [PAIRS[qq] for qq in np.nonzero(E[t])[0]]
            f = A.f0_flags(K, edges, wm, skip_planar=True)
            ok = True
            for si, nm in enumerate(STAGES[3:-1], start=4):
                if not f[nm]:
                    ok = False
                    break
                cum_w[si] += float(w[t])
                cum_w2[si] += float(w[t] ** 2)
                cnt[si] += 1
            if not ok:
                continue
            n_planar_calls += 1
            if not A.is_planar_struct(K, edges, wm):
                continue
            cum_w[ns] += float(w[t])
            cum_w2[ns] += float(w[t] ** 2)
            cnt[ns] += 1
            if want_survivors:
                survivors.append((wm, edges))
                surv_w.append(float(w[t]))
        done += b
        if done % 200000 == 0:
            log('   %d / %d samples, %.1fs, survivors %d, planar calls %d'
                % (done, nsamp, time.time() - t0, cnt[-1], n_planar_calls))
    res = dict(n=nsamp, seed=seed, Z=str(ms.Z), qmix=QMIX.tolist(),
               stage_names=['factorable'] + STAGES,
               stage_counts=cnt,
               stage_rate=[c / nsamp for c in cum_w],
               stage_sigma=[math.sqrt(max(c2 / nsamp - (c / nsamp) ** 2, 0.0)
                                      / nsamp) for c, c2 in zip(cum_w, cum_w2)],
               n_planar_calls=n_planar_calls,
               seconds=round(time.time() - t0, 1))
    if surv_w:
        sw = np.array(surv_w)
        res['ess_survivors'] = float(sw.sum() ** 2 / (sw ** 2).sum())
    return res, survivors, surv_w, ms


# ---------------------------------------------------------------- run2
# Second, better-conditioned proposal used for the production estimate AND for
# the exactly-uniform D5 sample:
#   * masks exactly from the target marginal;
#   * the edge COUNT e uniform on {0..cap}, cap = min(T, 3k+2-Esw)  (so every
#     draw already satisfies the Euler bound, which F0 requires anyway), then a
#     uniform e-subset of the touchable pairs.
#   Importance weight  w = (cap+1) * C(T,e) * 2^{-T}  <= WCAP.
#   Accepting a draw with probability w / WCAP gives draws that are EXACTLY
#   uniform on the factorable set intersected with the Euler bound, hence
#   exactly uniform on any subset of it (in particular on the F0 survivors).
WCAP = 4.0
_LOGC = {}


def logcomb_row(T):
    v = _LOGC.get(T)
    if v is None:
        v = np.array([math.lgamma(T + 1) - math.lgamma(e + 1)
                      - math.lgamma(T - e + 1) for e in range(T + 1)])
        _LOGC[T] = v
    return v


def run2(nsamp, seed, want_uniform=0, log=print, batch=20000,
         k0_filters=False, rng=None):
    ms = MaskSampler()
    if rng is None:
        rng = np.random.default_rng(seed)
    ln2 = math.log(2.0)
    ns = len(STAGES)
    cum_w = [0.0] * (ns + 1)
    cum_w2 = [0.0] * (ns + 1)
    cnt = [0] * (ns + 1)
    surv = []
    surv_w = []
    uni = []
    k02_w = 0.0
    k02_n = 0
    done = 0
    t0 = time.time()
    wmax_seen = 0.0
    while done < nsamp:
        b = min(batch, nsamp - done)
        M, _ = ms.draw(b, rng)
        TP = TOUCH_P[M[:, PI], M[:, PJ]]
        Tc = TP.sum(1)
        Esw = POPD[M].sum(1)
        cap = np.minimum(Tc, 3 * K + 2 - Esw)
        good = cap >= 0
        e = np.zeros(b, dtype=np.int64)
        e[good] = (rng.random(good.sum()) * (cap[good] + 1)).astype(np.int64)
        R = rng.random((b, NPAIR))
        R[~TP] = 2.0
        order = np.argsort(R, axis=1)
        rank = np.empty_like(order)
        np.put_along_axis(rank, order, np.arange(NPAIR)[None, :], axis=1)
        E = (rank < e[:, None]) & TP
        lw = np.zeros(b)
        for t in np.nonzero(good)[0]:
            lw[t] = (math.log(cap[t] + 1) + logcomb_row(int(Tc[t]))[int(e[t])]
                     - Tc[t] * ln2)
        w = np.where(good, np.exp(lw), 0.0)
        wmax_seen = max(wmax_seen, float(w.max()))
        cf, Ess, Esw2, deg = cheap_flags(M, E)
        cum_w[0] += float(w.sum())
        cum_w2[0] += float((w * w).sum())
        cnt[0] += b
        alive = good.copy()
        for si, nm in enumerate(['L1_deg2', 'L5d_deg12', 'L4a_euler']):
            alive &= cf[nm]
            cum_w[si + 1] += float(w[alive].sum())
            cum_w2[si + 1] += float((w[alive] ** 2).sum())
            cnt[si + 1] += int(alive.sum())
        for t in np.nonzero(alive)[0]:
            wm = [int(RAWD[a]) for a in M[t]]
            edges = [PAIRS[qq] for qq in np.nonzero(E[t])[0]]
            f = A.f0_flags(K, edges, wm, skip_planar=True)
            ok = True
            for si, nm in enumerate(STAGES[3:-1], start=4):
                if not f[nm]:
                    ok = False
                    break
                cum_w[si] += float(w[t])
                cum_w2[si] += float(w[t] ** 2)
                cnt[si] += 1
            if not ok:
                continue
            if not A.is_planar_struct(K, edges, wm):
                continue
            cum_w[ns] += float(w[t])
            cum_w2[ns] += float(w[t] ** 2)
            cnt[ns] += 1
            surv.append((wm, edges))
            surv_w.append(float(w[t]))
            if k0_filters:
                ok2, _ = A.k0_2(K, edges, wm)
                k02_n += int(ok2)
                k02_w += float(w[t]) * int(ok2)
            if want_uniform and rng.random() * WCAP < w[t]:
                uni.append((wm, edges))
        done += b
        if done % 200000 == 0:
            log('   run2 %d / %d, %.1fs, F0 survivors %d, uniform %d'
                % (done, nsamp, time.time() - t0, cnt[-1], len(uni)))
    res = dict(n=nsamp, seed=seed, Z=str(ms.Z), proposal='uniform-edge-count',
               stage_names=['factorable&euler'] + STAGES,
               stage_counts=cnt,
               stage_rate=[c / nsamp for c in cum_w],
               stage_sigma=[math.sqrt(max(c2 / nsamp - (c / nsamp) ** 2, 0.0)
                                      / nsamp) for c, c2 in zip(cum_w, cum_w2)],
               wmax_seen=wmax_seen, WCAP=WCAP,
               n_uniform=len(uni), seconds=round(time.time() - t0, 1))
    if surv_w:
        sw = np.array(surv_w)
        res['ess_survivors'] = float(sw.sum() ** 2 / (sw ** 2).sum())
    if k0_filters and cum_w[ns] > 0:
        res['K0_2_rate_weighted'] = k02_w / cum_w[ns]
        res['K0_2_count'] = k02_n
    return res, surv, surv_w, uni, ms


# ---------------------------------------------------------------- run3
# PLAIN uniform sampling of the factorable set (each touchable pair an
# independent fair coin, masks from the exact marginal).  Weight identically 1,
# so the F0 pass rate is a plain Bernoulli estimate and every F0 survivor found
# is an EXACTLY UNIFORM draw from the labelled F0 census.
RUN3_STAGES = ['L1_deg2', 'L5d_deg12', 'L4a_euler', 'N1_wallcap3', 'L7',
               'L5a_metric', 'L3_nofloat', 'L6_span', 'L4b_planar']


def run3(nsamp, seed, log=print, batch=50000, k0_2=True, tlimit=None):
    ms = MaskSampler()
    rng = np.random.default_rng(seed)
    ns = len(RUN3_STAGES)
    cnt = [0] * (ns + 1)
    surv = []
    n_k02 = 0
    done = 0
    t0 = time.time()
    while done < nsamp:
        b = min(batch, nsamp - done)
        M, _ = ms.draw(b, rng)
        TP = TOUCH_P[M[:, PI], M[:, PJ]]
        E = (rng.random((b, NPAIR)) < 0.5) & TP
        cf, Ess, Esw, deg = cheap_flags(M, E)
        cnt[0] += b
        alive = np.ones(b, dtype=bool)
        for si, nm in enumerate(RUN3_STAGES[:5]):
            alive &= cf[nm]
            cnt[si + 1] += int(alive.sum())
        for t in np.nonzero(alive)[0]:
            wm = [int(RAWD[a]) for a in M[t]]
            edges = [PAIRS[qq] for qq in np.nonzero(E[t])[0]]
            f = A.f0_flags(K, edges, wm, skip_planar=True)
            ok = True
            for si, nm in enumerate(RUN3_STAGES[5:-1], start=6):
                if not f[nm]:
                    ok = False
                    break
                cnt[si] += 1
            if not ok:
                continue
            if not A.is_planar_struct(K, edges, wm):
                continue
            cnt[ns] += 1
            rec = dict(wm=wm, edges=[list(x) for x in edges])
            if k0_2:
                ok2, _ = A.k0_2(K, edges, wm)
                rec['k0_2'] = bool(ok2)
                n_k02 += int(ok2)
            surv.append(rec)
        done += b
        if done % 500000 == 0:
            log('   run3 %d / %d, %.1fs, F0 survivors %d'
                % (done, nsamp, time.time() - t0, cnt[-1]))
        if tlimit and time.time() - t0 > tlimit:
            log('   run3 time limit hit at %d samples' % done)
            break
    n = done
    p = cnt[ns] / n
    res = dict(n=n, seed=seed, Z=str(ms.Z), proposal='plain uniform (q=1/2)',
               stage_names=['factorable'] + RUN3_STAGES,
               stage_counts=cnt,
               stage_rate=[c / n for c in cnt],
               F0_rate=p, F0_rate_sigma=math.sqrt(max(p * (1 - p), 1e-30) / n),
               K0_2_count=n_k02,
               K0_2_rate=(n_k02 / cnt[ns]) if cnt[ns] else None,
               seconds=round(time.time() - t0, 1))
    return res, surv, ms


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200000
    res, _, _, ms = run(n, 20260902)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
