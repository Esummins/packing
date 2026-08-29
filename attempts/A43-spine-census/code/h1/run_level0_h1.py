"""A43-H1 Level 0: A31's exhaustive orbit enumeration + the 2026 theorem-library filters.

The A31 code path (cum[0..7], marg, soft[0..4], branch, Ehist, samples) is byte-for-byte the
same computation, so `--baseline` reproduces attempts/A31-structure-count/results/level0_k*.json
EXACTLY.  Everything new is ADDITIVE:

  R11  (NEW HARD row)  = R10 & N1   per-wall <= 3   [EXACT; A31 soft bit 16 promoted]
  R12  (NEW HARD row)  = R11 & N5 & N6              [EXACT; both measured to be inert]
  columns on MAIN / MAIN&N1 / MAIN' :
    N2  all-wall (every square has a nonzero wall mask)   EXACT-EXISTENTIAL (hard only at k=11)
    N4  2E >= 3k+1                                        CONDITIONAL (Maxwell, unproved)
    N7a square-square subgraph contains a 4-cycle          APPROX proxy
  MAIN' = MAIN & N1 & N5 & N6 is the composed EXACT count.
"""
import os, sys, math, json, time, itertools
import numpy as np
import lib0 as L

CHUNK = 1_500_000
SAMPLE_PER_AREP = 40

RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'results', 'h1')

# ------------------------------------------------------------------ N5/N6 mask tables (global)
N5DEAD = np.zeros(16, dtype=bool)          # wall mask -> W1-dead
N6BAD = np.zeros((16, 16), dtype=bool)     # mask pair -> W2-dead
FIELD_INFO = {}


def load_field_tables():
    global FIELD_INFO
    import field_h1 as FH
    f = FH.field()
    gp = os.path.join(RES, 'mlow_grid_a39.npz')
    M, meta = FH.load_grid(gp) if os.path.exists(gp) else (None, None)
    mm = FH.mask_mlow(L.ALLOWED, M, meta, f)
    thr1, thr2 = float(f.thr1), float(f.thr2)
    for m in L.ALLOWED:
        if mm[m]['mlow_certified'] > thr1:
            N5DEAD[m] = True
    for a in L.ALLOWED:
        for b in L.ALLOWED:
            if mm[a]['mlow_certified'] + mm[b]['mlow_certified'] > thr2:
                N6BAD[a, b] = True
    FIELD_INFO = dict(field=FH.pick_field()[1], cert=os.path.relpath(f.path, FH.REPO),
                      n_atoms=f.n, d4_defects=f.d4_defects,
                      total=str(f.total), eta_cert=str(f.eta), eta_float=float(f.eta),
                      thr1_exact=str(f.thr1), thr1_float=thr1,
                      thr2_exact=str(f.thr2), thr2_float=thr2,
                      grid=meta, per_mask=mm,
                      n5_dead_masks=[int(m) for m in L.ALLOWED if N5DEAD[m]],
                      n6_dead_pairs=[[int(a), int(b)] for a in L.ALLOWED for b in L.ALLOWED
                                     if N6BAD[a, b]])
    return FIELD_INFO


def has_4cycle(adj, k):
    """True iff the square-square graph contains a 4-cycle (4 distinct vertices, cyclically
    adjacent).  N7 APPROX proxy."""
    for a in range(k):
        for b in range(k):
            if b == a or not ((adj[a] >> b) & 1):
                continue
            for c in range(k):
                if c in (a, b) or not ((adj[b] >> c) & 1):
                    continue
                for d in range(k):
                    if d in (a, b, c):
                        continue
                    if ((adj[c] >> d) & 1) and ((adj[d] >> a) & 1):
                        return True
    return False


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
    """A31 semantics verbatim, plus the new EXACT/EXISTENTIAL/CONDITIONAL columns."""
    degA, edges, D, comps, eA = ctx
    n = W.shape[0]
    pop = np.asarray(L.POP, dtype=np.uint8)
    wdeg = np.zeros(n, dtype=np.int16)
    for i in range(k):
        wdeg += pop[W[:, i]]
    E = eA + wdeg
    f = np.zeros(n, dtype=np.uint16)
    if max(degA) <= 12:
        f |= 1
    f |= np.where(E <= 3 * k + 2, 2, 0).astype(np.uint16)
    ok = np.ones(n, dtype=bool)
    for i in range(k):
        for j in range(i + 1, k):
            tab = L.OKTAB[D[i][j]]
            ok &= tab[W[:, i].astype(np.int32) * 16 + W[:, j]]
    f |= np.where(ok, 4, 0).astype(np.uint16)
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
    float_any = np.zeros(n, dtype=bool)
    span = np.zeros(n, dtype=bool)
    for c in range(nc):
        float_any |= (CW[:, c] == 0)
        span |= ((CW[:, c] & 5) == 5) | ((CW[:, c] & 10) == 10)
    f |= np.where(~float_any, 8, 0).astype(np.uint16)
    f |= np.where(span, 16, 0).astype(np.uint16)
    allw = np.zeros(n, dtype=np.uint8)
    for i in range(k):
        allw |= W[:, i]
    f |= np.where(((allw & 5) == 5) | ((allw & 10) == 10), 64, 0).astype(np.uint16)
    thin = np.zeros(n, dtype=bool)
    for i in range(k):
        thin |= (degA[i] + pop[W[:, i]]) == 2
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
    wallcap3 = np.ones(n, dtype=bool)
    for b in range(4):
        cnt = np.zeros(n, dtype=np.int16)
        for i in range(k):
            cnt += ((W[:, i] >> b) & 1).astype(np.int16)
        wallcap3 &= (cnt <= 3)
    s |= np.where(wallcap3, 16, 0).astype(np.uint8)

    # ---------------- NEW columns
    # N2 all-wall: every square has a nonzero wall mask (EXACT-EXISTENTIAL, hard at k=11 only)
    allwall = np.ones(n, dtype=bool)
    for i in range(k):
        allwall &= (W[:, i] != 0)
    # N5 W1: some square's wall-mask window is certified exempt
    n5dead = np.zeros(n, dtype=bool)
    if N5DEAD.any():
        for i in range(k):
            n5dead |= N5DEAD[W[:, i]]
    # N6 W2: some CONTACT edge / some PAIR has certified window-sum > 2 + eta
    n6dead_edge = np.zeros(n, dtype=bool)
    n6dead_pair = np.zeros(n, dtype=bool)
    if N6BAD.any():
        for (i, j) in edges:
            n6dead_edge |= N6BAD[W[:, i], W[:, j]]
        for i in range(k):
            for j in range(i + 1, k):
                n6dead_pair |= N6BAD[W[:, i], W[:, j]]
    return f, s, thin, E, wallcap3, allwall, n5dead, n6dead_edge, n6dead_pair


def run_arep(args):
    k, gmask, aut, want_sample, a_planar = args
    adj, edges = L.mask_to_adj(gmask, k)
    degA = [bin(adj[i]).count("1") for i in range(k)]
    D = L.hop_matrix(adj, k)
    comps = L.components(adj, k)
    eA = len(edges)
    ctx = (degA, edges, D, comps, eA)
    cyc4 = has_4cycle(adj, k)
    per = [[m for m in L.ALLOWED if L.POP[m] >= 2 - degA[i]] for i in range(k)]
    N = 1
    for p in per:
        N *= len(p)
    NEW = ['main_N1', 'main_N5dead', 'main_N6dead_edge', 'main_N6dead_pair',
           'mainprime', 'mainprime_nonthin', 'main_allwall', 'main_N1_allwall',
           'mainprime_allwall', 'main_4cyc', 'main_N1_4cyc', 'mainprime_4cyc',
           'main_N4', 'main_N1_N4', 'mainprime_N4', 'mainprime_N4_nonthin',
           'main_N1_nonthin']
    res = dict(k=k, gmask=gmask, eA=eA, aut=len(aut), N=N,
               cum=[0] * 10, marg=[0] * 8, branch=dict(main=0, thin_main=0,
               selfstress_float=0, lam0=0, both=0), soft=[0] * 5,
               soft_and=0, planar_calls=0, sample=[], Ehist={},
               main_wallcap3_nonthin=0, cyc4=bool(cyc4),
               new={t: 0 for t in NEW})
    if N == 0:
        return res
    lo = 0
    rng = np.random.default_rng(1234 + gmask)
    while lo < N:
        hi = min(N, lo + CHUNK)
        W = build_W(per, lo, hi)
        cand = canonical_rows(W, aut, k)
        if cand.size:
            Wc = W[cand]
            (f, s, thin, E, wallcap3, allwall, n5dead,
             n6de, n6dp) = eval_filters(Wc, k, ctx)
            res['cum'][0] += Wc.shape[0]
            m = (f & 1) != 0
            res['cum'][1] += int(m.sum())
            m &= (f & 2) != 0
            res['cum'][2] += int(m.sum())
            m &= (f & 4) != 0
            res['cum'][3] += int(m.sum())
            base = m.copy()
            m2 = base & ((f & 8) != 0)
            res['cum'][4] += int(m2.sum())
            m3 = m2 & ((f & 16) != 0)
            res['cum'][5] += int(m3.sum())
            idx = np.nonzero(base)[0] if a_planar else np.zeros(0, dtype=np.int64)
            res['planar_calls'] += idx.size
            pl = np.zeros(Wc.shape[0], dtype=bool)
            pl_nc = np.zeros(Wc.shape[0], dtype=bool)
            for t in idx:
                wm = tuple(int(x) for x in Wc[t])
                pl[t] = L.is_planar(k, tuple(edges), wm, True)
                pl_nc[t] = L.is_planar(k, tuple(edges), wm, False)
            m4 = m3 & pl
            res['cum'][6] += int(m4.sum())
            m5 = m4 & ((f & 64) != 0)
            res['cum'][7] += int(m5.sum())
            # NEW hard rows on the cumulative ladder
            m6 = m5 & wallcap3
            res['cum'][8] += int(m6.sum())                      # R11 = + N1
            m7 = m6 & ~n5dead & ~n6de
            res['cum'][9] += int(m7.sum())                      # R12 = + N5 + N6
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
            if main.any():
                vals, cts = np.unique(E[main], return_counts=True)
                for v, c in zip(vals, cts):
                    res['Ehist'][int(v)] = res['Ehist'].get(int(v), 0) + int(c)
            nb = int(base.sum())
            res['marg'][3] += nb
            res['marg'][4] += int((base & nofloat).sum())
            res['marg'][5] += int((base & spanb).sum())
            res['marg'][6] += int((base & pl).sum())
            res['marg'][7] += int((base & pl_nc).sum())
            # ---- NEW column aggregation (all measured on MAIN)
            mN1 = main & wallcap3
            mprime = mN1 & ~n5dead & ~n6de
            n4 = ((s >> 0) & 1).astype(bool)
            nw = res['new']
            nw['main_N1'] += int(mN1.sum())
            nw['main_N1_nonthin'] += int((mN1 & ~thin).sum())
            nw['main_N5dead'] += int((main & n5dead).sum())
            nw['main_N6dead_edge'] += int((main & n6de).sum())
            nw['main_N6dead_pair'] += int((main & n6dp).sum())
            nw['mainprime'] += int(mprime.sum())
            nw['mainprime_nonthin'] += int((mprime & ~thin).sum())
            nw['main_allwall'] += int((main & allwall).sum())
            nw['main_N1_allwall'] += int((mN1 & allwall).sum())
            nw['mainprime_allwall'] += int((mprime & allwall).sum())
            if cyc4:
                nw['main_4cyc'] += int(main.sum())
                nw['main_N1_4cyc'] += int(mN1.sum())
                nw['mainprime_4cyc'] += int(mprime.sum())
            nw['main_N4'] += int((main & n4).sum())
            nw['main_N1_N4'] += int((mN1 & n4).sum())
            nw['mainprime_N4'] += int((mprime & n4).sum())
            nw['mainprime_N4_nonthin'] += int((mprime & n4 & ~thin).sum())
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
    ks = [int(x) for x in sys.argv[1:] if x.isdigit()] or [3, 4, 5, 6]
    nw = int(os.environ.get('A43_WORKERS', '3'))
    os.makedirs(RES, exist_ok=True)
    info = load_field_tables()
    with open(os.path.join(RES, 'field_info.json'), 'w') as fh:
        json.dump(info, fh, indent=1, default=str)
    print('field: %s  eta=%s  thr1=%s  N5-dead masks=%s' % (
        info['cert'], info['eta_cert'], info['thr1_exact'], info['n5_dead_masks']), flush=True)
    for k in ks:
        t0 = time.time()
        reps = L.graph_reps(k)
        planar_reps = [(g, aut) for g, aut in reps if L.planar_graph(g, k)]
        pset = set(g for g, _ in planar_reps)
        jobs = [(k, g, aut, True, g in pset) for g, aut in reps]
        if nw > 1:
            import multiprocessing as mp
            with mp.Pool(nw, initializer=load_field_tables) as pool:
                out = pool.map(run_arep, jobs, chunksize=1)
        else:
            out = [run_arep(j) for j in jobs]
        NEWK = list(out[0]['new'].keys())
        agg = dict(k=k, n_areps=len(reps), n_areps_planar=len(planar_reps),
                   cum=[0] * 10, marg=[0] * 8, soft=[0] * 5, soft_and=0,
                   branch=dict(main=0, thin_main=0, selfstress_float=0,
                               lam0=0, both=0), planar_calls=0, N_total=0,
                   Ehist={}, main_wallcap3_nonthin=0,
                   new={t: 0 for t in NEWK}, n_areps_with_4cycle=0)
        samples = []
        for r in out:
            for i in range(10):
                agg['cum'][i] += r['cum'][i]
            for i in range(8):
                agg['marg'][i] += r['marg'][i]
            for i in range(5):
                agg['soft'][i] += r['soft'][i]
            agg['main_wallcap3_nonthin'] += r['main_wallcap3_nonthin']
            agg['soft_and'] += r['soft_and']
            for key in agg['branch']:
                agg['branch'][key] += r['branch'][key]
            agg['planar_calls'] += r['planar_calls']
            agg['N_total'] += r['N']
            agg['n_areps_with_4cycle'] += int(r['cyc4'])
            for t in NEWK:
                agg['new'][t] += r['new'][t]
            for v, c in r['Ehist'].items():
                agg['Ehist'][int(v)] = agg['Ehist'].get(int(v), 0) + c
            if r['sample']:
                samples.append(dict(gmask=r['gmask'], w=r['sample'],
                                    main=r['branch']['main'],
                                    nsample=len(r['sample']),
                                    cyc4=bool(r['cyc4'])))
        r0, r2 = L.burnside_rows(k)
        agg['R0_no_filter'] = r0
        agg['R2_L5b'] = r2
        agg['seconds'] = round(time.time() - t0, 1)
        agg['samples'] = samples
        with open(os.path.join(RES, 'level0_k%d.json' % k), 'w') as fh:
            json.dump(agg, fh, indent=1)
        print('k=%d R0=%d R2=%d R3=%d R10=%d R11=%d R12=%d main=%d N1=%d MAIN\'=%d allwall=%d (%.1fs)'
              % (k, r0, r2, agg['cum'][0], agg['cum'][7], agg['cum'][8], agg['cum'][9],
                 agg['branch']['main'], agg['new']['main_N1'], agg['new']['mainprime'],
                 agg['new']['main_allwall'], agg['seconds']), flush=True)


if __name__ == '__main__':
    main()
