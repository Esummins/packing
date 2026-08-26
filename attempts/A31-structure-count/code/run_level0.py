"""A31 Level 0 driver: exhaustive enumeration of pruned support structures, per k.

Counts orbits under S_k x D4 exactly.  Strategy:
  * enumerate square-square graphs A on k vertices up to S_k (canonical reps + Aut),
  * per A-rep, enumerate wall masks w in ALLOWED^k restricted by L1 (mixed radix),
  * keep only the lexicographically canonical w under Aut(A) x D4  -> exact orbits,
  * evaluate every remaining filter, vectorised, and aggregate the ablation table.
"""
import os, sys, math, json, time, itertools
import numpy as np
import lib0 as L

CHUNK = 1_500_000          # RAM guard: rows of the mask array per chunk
SAMPLE_PER_AREP = 40       # reservoir of MAIN survivors kept for Level 1

FBITS = ['L5d', 'L4a_euler', 'L5a_metric', 'L3_nofloat', 'L6_span',
         'L4b_planar', 'L7', 'planar_nocycle']
SBITS = ['soft_maxwell_possible', 'soft_maxwell_certain', 'soft_wallcap5',
         'soft_kiss8']


def build_W(per, lo, hi):
    k = len(per)
    n = hi - lo
    W = np.empty((n, k), dtype=np.uint8)
    r = np.arange(lo, hi, dtype=np.int64)
    rep = 1
    for i in range(k):
        s = len(per[i])
        W[:, i] = np.asarray(per[i], dtype=np.uint8)[(r // rep) % s]
        rep *= s
    return W


def canonical_rows(W, aut, k):
    """Boolean mask: w is the lex-min of its Aut(A) x D4 orbit (key = base-16 digits)."""
    pw = (np.uint64(1) << (np.uint64(4) * np.arange(k, dtype=np.uint64)))
    key = np.zeros(W.shape[0], dtype=np.uint64)
    for i in range(k):
        key += W[:, i].astype(np.uint64) * pw[i]
    cand = np.arange(W.shape[0], dtype=np.int64)
    ident = tuple(range(k))
    for p in aut:
        for d in range(8):
            if d == 0 and p == ident:
                continue
            if cand.size == 0:
                return cand
            kp = np.zeros(cand.size, dtype=np.uint64)
            tab = L.MT[d]
            for i in range(k):
                kp += tab[W[cand, i]].astype(np.uint64) * pw[p[i]]
            cand = cand[kp >= key[cand]]
    return cand


def eval_filters(W, k, ctx):
    """Returns (flags uint16 array, edge counts) for rows of W."""
    degA, edges, D, comps, eA = ctx
    n = W.shape[0]
    pop = np.asarray(L.POP, dtype=np.uint8)
    wdeg = np.zeros(n, dtype=np.int16)
    for i in range(k):
        wdeg += pop[W[:, i]]
    E = eA + wdeg                                  # total contact edges
    f = np.zeros(n, dtype=np.uint16)

    # b0 L5(d): square-square degree <= 12
    if max(degA) <= 12:
        f |= 1
    # b1 L4(a): Euler bound |E| + 4 <= 3(k+4)-6
    f |= np.where(E <= 3 * k + 2, 2, 0).astype(np.uint16)
    # b2 L5(a): metric / hop-distance consistency
    ok = np.ones(n, dtype=bool)
    for i in range(k):
        for j in range(i + 1, k):
            tab = L.OKTAB[D[i][j]]
            ok &= tab[W[:, i].astype(np.int32) * 16 + W[:, j]]
    f |= np.where(ok, 4, 0).astype(np.uint16)
    # component wall-masks, then H-components (components of A joined via shared walls)
    nc = len(comps)
    CW = np.zeros((n, nc), dtype=np.uint8)
    for c, vs in enumerate(comps):
        acc = np.zeros(n, dtype=np.uint8)
        for v in vs:
            acc |= W[:, v]
        CW[:, c] = acc
    for _ in range(nc):
        for a in range(nc):
            for b in range(a + 1, nc):
                sh = (CW[:, a] & CW[:, b]) != 0
                u = CW[:, a] | CW[:, b]
                CW[:, a] = np.where(sh, u, CW[:, a])
                CW[:, b] = np.where(sh, u, CW[:, b])
    # b3 L3: no floating component (component with no wall node)
    float_any = np.zeros(n, dtype=bool)
    span = np.zeros(n, dtype=bool)
    for c in range(nc):
        float_any |= (CW[:, c] == 0)
        span |= ((CW[:, c] & 5) == 5) | ((CW[:, c] & 10) == 10)
    f |= np.where(~float_any, 8, 0).astype(np.uint16)
    # b4 L6: some H-component joins two opposite walls
    f |= np.where(span, 16, 0).astype(np.uint16)
    # b6 L7: on some axis both walls are touched (a condition on G, see report)
    allw = np.zeros(n, dtype=np.uint8)
    for i in range(k):
        allw |= W[:, i]
    f |= np.where(((allw & 5) == 5) | ((allw & 10) == 10), 64, 0).astype(np.uint16)
    # thin branch flag (L2): some square of total degree exactly 2
    thin = np.zeros(n, dtype=bool)
    for i in range(k):
        thin |= (degA[i] + pop[W[:, i]]) == 2
    # soft columns
    s = np.zeros(n, dtype=np.uint8)
    s |= np.where(2 * E >= 3 * k + 1, 1, 0).astype(np.uint8)
    s |= np.where(E >= 3 * k + 1, 2, 0).astype(np.uint8)
    wallcap = np.ones(n, dtype=bool)
    for b in range(4):
        cnt = np.zeros(n, dtype=np.int16)
        for i in range(k):
            cnt += ((W[:, i] >> b) & 1).astype(np.int16)
        wallcap &= (cnt <= 5)
    s |= np.where(wallcap, 4, 0).astype(np.uint8)
    s |= np.where(max(degA) <= 8, 8, 0).astype(np.uint8)
    # bit 4: CERTIFIED tightening of L5(c).  Two squares on the same wall have their
    # centres within sqrt2/2 of it, so their coordinates along the wall differ by at
    # least sqrt(1 - (sqrt2/2 - 1/2)^2) = 0.97832, and the along-wall range is
    # s - 1 <= 2.8771; hence at most 3 squares touch any one wall.  Still reported as
    # SOFT because the ledger of structure_lemmas.md lists L5(c) as soft.
    wallcap3 = np.ones(n, dtype=bool)
    for b in range(4):
        cnt = np.zeros(n, dtype=np.int16)
        for i in range(k):
            cnt += ((W[:, i] >> b) & 1).astype(np.int16)
        wallcap3 &= (cnt <= 3)
    s |= np.where(wallcap3, 16, 0).astype(np.uint8)
    return f, s, thin, E


def run_arep(args):
    k, gmask, aut, want_sample, a_planar = args
    adj, edges = L.mask_to_adj(gmask, k)
    degA = [bin(adj[i]).count("1") for i in range(k)]
    D = L.hop_matrix(adj, k)
    comps = L.components(adj, k)
    eA = len(edges)
    ctx = (degA, edges, D, comps, eA)
    per = [[m for m in L.ALLOWED if L.POP[m] >= 2 - degA[i]] for i in range(k)]
    N = 1
    for p in per:
        N *= len(p)
    res = dict(k=k, gmask=gmask, eA=eA, aut=len(aut), N=N,
               cum=[0] * 8, marg=[0] * 8, branch=dict(main=0, thin_main=0,
               selfstress_float=0, lam0=0, both=0), soft=[0] * 5,
               soft_and=0, planar_calls=0, sample=[], Ehist={},
               main_wallcap3_nonthin=0)
    if N == 0:
        return res
    lo = 0
    rng = np.random.default_rng(1234 + gmask)
    seen_main = 0
    while lo < N:
        hi = min(N, lo + CHUNK)
        W = build_W(per, lo, hi)
        cand = canonical_rows(W, aut, k)
        if cand.size:
            Wc = W[cand]
            f, s, thin, E = eval_filters(Wc, k, ctx)
            res['cum'][0] += Wc.shape[0]                     # R3 = L5b + L1
            m = (f & 1) != 0
            res['cum'][1] += int(m.sum())                    # + L5d
            m &= (f & 2) != 0
            res['cum'][2] += int(m.sum())                    # + L4a
            m &= (f & 4) != 0
            res['cum'][3] += int(m.sum())                    # + L5a
            base = m.copy()                                  # metric-consistent set
            # marginal kills measured on `base` for the remaining filters
            m2 = base & ((f & 8) != 0)
            res['cum'][4] += int(m2.sum())                   # + L3
            m3 = m2 & ((f & 16) != 0)
            res['cum'][5] += int(m3.sum())                   # + L6
            # planarity: evaluate on the whole metric-consistent set (needed for the
            # main count and for both flagged branches)
            idx = np.nonzero(base)[0] if a_planar else np.zeros(0, dtype=np.int64)
            res['planar_calls'] += idx.size
            pl = np.zeros(Wc.shape[0], dtype=bool)
            pl_nc = np.zeros(Wc.shape[0], dtype=bool)
            for t in idx:
                wm = tuple(int(x) for x in Wc[t])
                pl[t] = L.is_planar(k, tuple(edges), wm, True)
                pl_nc[t] = L.is_planar(k, tuple(edges), wm, False)
            m4 = m3 & pl
            res['cum'][6] += int(m4.sum())                   # + L4b planarity
            m5 = m4 & ((f & 64) != 0)
            res['cum'][7] += int(m5.sum())                   # + L7
            # branches (all hard filters except L3/L6, plus planarity)
            hard = base & pl
            nofloat = (f & 8) != 0
            spanb = (f & 16) != 0
            main = hard & nofloat & spanb
            res['branch']['main'] += int(main.sum())
            res['branch']['thin_main'] += int((main & thin).sum())
            res['branch']['selfstress_float'] += int((hard & ~nofloat).sum())
            res['branch']['lam0'] += int((hard & nofloat & ~spanb).sum())
            res['branch']['both'] += int((hard & ~nofloat & ~spanb).sum())
            for b in range(5):
                res['soft'][b] += int((main & ((s >> b) & 1).astype(bool)).sum())
            res['soft_and'] += int((main & (s == 31)).sum())
            res['main_wallcap3_nonthin'] += int(
                (main & ~thin & ((s >> 4) & 1).astype(bool)).sum())
            # edge-count histogram over MAIN survivors (Maxwell diagnostics)
            if main.any():
                vals, cts = np.unique(E[main], return_counts=True)
                for v, c in zip(vals, cts):
                    res['Ehist'][int(v)] = res['Ehist'].get(int(v), 0) + int(c)
            # marginal (each filter alone, measured on base)
            nb = int(base.sum())
            res['marg'][3] += nb
            res['marg'][4] += int((base & nofloat).sum())
            res['marg'][5] += int((base & spanb).sum())
            res['marg'][6] += int((base & pl).sum())
            res['marg'][7] += int((base & pl_nc).sum())
            # sample of MAIN survivors
            if want_sample:
                mi = np.nonzero(main)[0]
                if mi.size:
                    take = mi if mi.size <= SAMPLE_PER_AREP else rng.choice(
                        mi, SAMPLE_PER_AREP, replace=False)
                    for t in take:
                        if len(res['sample']) < SAMPLE_PER_AREP:
                            res['sample'].append([int(x) for x in Wc[t]])
        lo = hi
    return res


def main():
    ks = [int(x) for x in sys.argv[1:]] or [3, 4, 5, 6]
    nw = int(os.environ.get('A31_WORKERS', '6'))
    outdir = os.path.join(os.path.dirname(__file__), '..', 'results')
    os.makedirs(outdir, exist_ok=True)
    for k in ks:
        t0 = time.time()
        reps = L.graph_reps(k)
        # A non-planar => every leaf fails L4b (subgraph of a planar graph is planar):
        # keep the A-rep (the weak ablation rows need it) but skip the planarity calls.
        planar_reps = [(g, aut) for g, aut in reps if L.planar_graph(g, k)]
        pset = set(g for g, _ in planar_reps)
        jobs = [(k, g, aut, True, g in pset) for g, aut in reps]
        if nw > 1:
            import multiprocessing as mp
            with mp.Pool(nw) as pool:
                out = pool.map(run_arep, jobs, chunksize=1)
        else:
            out = [run_arep(j) for j in jobs]
        agg = dict(k=k, n_areps=len(reps), n_areps_planar=len(planar_reps),
                   cum=[0] * 8, marg=[0] * 8, soft=[0] * 5, soft_and=0,
                   branch=dict(main=0, thin_main=0, selfstress_float=0,
                               lam0=0, both=0), planar_calls=0, N_total=0,
                   Ehist={}, main_wallcap3_nonthin=0)
        samples = []
        for r in out:
            for i in range(8):
                agg['cum'][i] += r['cum'][i]
                agg['marg'][i] += r['marg'][i]
            for i in range(5):
                agg['soft'][i] += r['soft'][i]
            agg['main_wallcap3_nonthin'] += r['main_wallcap3_nonthin']
            agg['soft_and'] += r['soft_and']
            for key in agg['branch']:
                agg['branch'][key] += r['branch'][key]
            agg['planar_calls'] += r['planar_calls']
            agg['N_total'] += r['N']
            for v, c in r['Ehist'].items():
                agg['Ehist'][int(v)] = agg['Ehist'].get(int(v), 0) + c
            if r['sample']:
                samples.append(dict(gmask=r['gmask'], w=r['sample'],
                                    main=r['branch']['main'],
                                    nsample=len(r['sample'])))
        r0, r2 = L.burnside_rows(k)
        agg['R0_no_filter'] = r0
        agg['R2_L5b'] = r2
        agg['seconds'] = round(time.time() - t0, 1)
        agg['samples'] = samples
        p = os.path.join(outdir, 'level0_k%d.json' % k)
        with open(p, 'w') as fh:
            json.dump(agg, fh, indent=1)
        print('k=%d  R0=%d R2=%d R3=%d ... main=%d  (%.1fs)' % (
            k, r0, r2, agg['cum'][0], agg['branch']['main'], agg['seconds']),
            flush=True)


if __name__ == '__main__':
    main()
