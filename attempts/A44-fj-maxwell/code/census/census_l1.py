"""A44 census, Level 1: A43-H1's wall-edge-resolved decoration fan-out re-run with the
A44 branch decomposition of the Maxwell row count.

Per decorated structure the census knows m = E + F exactly (A44 theory.md, Fact 0 conventions):
  E = Ess + Esw   (square-square edges + square-wall edges; a contact is ONE edge)
  F = nf  + nwf   (flush square-square edges + wall-flush square-wall edges; 2 rows each)
  m = E + F,  N = 3k + 1,  chi := m - (3k+1) = sig - d   (L8, proved)

Columns produced per (graph, wall-mask), each an exact integer count of decorations weighted by
the acyclic-orientation multiplicity (identical bookkeeping to A43 level1_h1.fanout_we):
  tot            all tilt-feasible decorations            [= A43 we_surv,     REGRESSION]
  m_ge_3k1       m >= 3k+1  (chi >= 0)  RIGID-POSSIBLE    [= A43 we_surv_N4,  REGRESSION]
  m_ge_3k        m >= 3k    (chi >= -1)  C* column        [NEW]
  m_eq_3k        m == 3k    (chi == -1)                   [NEW]
  flex           m <  3k+1  (chi <= -1)  FLEX-ONLY        [= tot - m_ge_3k1, derived]
  chi_hist       full histogram of chi                    [NEW]
plus the same under A43's `nozero` restriction (no zero-pinned tilt class).

Sampling protocol is inherited verbatim from A43 code/h1/level1_h1.py::main -- same level0
samples, same numpy default_rng(7), same cap 160 (k<=6) / 40 (k=7), same budget 22, same
per-graph weight main/nsample.  Nothing in A43 or A31 is written.
"""
import os, sys, json, math, time, itertools
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
A43 = os.path.join(ROOT, 'attempts', 'A43-spine-census')
A43H1 = os.path.join(A43, 'code', 'h1')
A43RES = os.path.join(A43, 'results', 'h1')
OUT = os.path.join(ROOT, 'attempts', 'A44-fj-maxwell', 'results')
sys.path.insert(0, A43H1)

import lib0 as L                                    # noqa: E402  (A43, unmodified)
from level1_ao import acyclic_orientations          # noqa: E402  (A43, unmodified)


def fanout_we_branch(k, gmask, wm, budget=None):
    """A43 level1_h1.fanout_we with the A44 chi-decomposition added.

    The enumeration, the phi=0/phi!=0 consistency constraint, the class contraction and the
    acyclic-orientation multiplicity `mult * ao` are byte-for-byte the A43 logic; only the
    accumulators below `v = mult * ao` are new.
    """
    adj, ss_edges = L.mask_to_adj(gmask, k)
    Ess = len(ss_edges)
    wedges = [(i, b) for i in range(k) for b in range(4) if (wm[i] >> b) & 1]
    Esw = len(wedges)
    if budget is not None and Ess + Esw > budget:
        return None
    gauge_menu = 20 ** Ess * 2 ** Esw
    E = Ess + Esw
    N = 3 * k + 1
    tot = tot_ge1 = tot_ge0 = tot_eq0 = 0            # ge1: m>=3k+1 ; ge0: m>=3k ; eq0: m==3k
    ntot = nge1 = nge0 = neq0 = 0                    # same under the nozero restriction
    chi_hist = {}
    chi_hist_nz = {}
    for fl in range(1 << Ess):
        parent = list(range(k))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        nf = 0
        for e, (i, j) in enumerate(ss_edges):
            if (fl >> e) & 1:
                nf += 1
                a, b = find(i), find(j)
                if a != b:
                    parent[a] = b
        rest = [(i, j) for e, (i, j) in enumerate(ss_edges) if not ((fl >> e) & 1)]
        if any(find(i) == find(j) for i, j in rest):
            continue
        cls = sorted(set(find(i) for i in range(k)))
        cid = {c: t for t, c in enumerate(cls)}
        mult = (4 ** nf) * (8 ** (Ess - nf))
        for ws in range(1 << Esw):
            nwf = bin(ws).count('1')
            pinned = set()
            corner_cls = set()
            for t, (i, b) in enumerate(wedges):
                if (ws >> t) & 1:
                    pinned.add(find(i))
                else:
                    corner_cls.add(find(i))
            if pinned & corner_cls:
                continue
            if pinned:
                remap = {}
                nxt = 0
                for c in cls:
                    if c in pinned:
                        continue
                    remap[cid[c]] = nxt
                    nxt += 1
                zpos = nxt
                nn = nxt + 1
                for c in pinned:
                    remap[cid[c]] = zpos
            else:
                remap = {t: t for t in range(len(cls))}
                zpos = None
                nn = len(cls)
            bad = False
            qe = set()
            for i, j in rest:
                u, v = remap[cid[find(i)]], remap[cid[find(j)]]
                if u == v:
                    bad = True
                    break
                qe.add((min(u, v), max(u, v)))
            if bad:
                continue
            if zpos is None:
                ao = acyclic_orientations(nn, qe)
            else:
                rm = {}
                t = 0
                for x in range(nn):
                    if x == zpos:
                        continue
                    rm[x] = t
                    t += 1
                qe2 = [(rm[a], rm[b]) for a, b in qe if a != zpos and b != zpos]
                ao = acyclic_orientations(nn - 1, qe2)
            v = mult * ao
            if not v:
                continue
            m = E + nf + nwf
            chi = m - N
            nozero = (zpos is None)
            tot += v
            chi_hist[chi] = chi_hist.get(chi, 0) + v
            if nozero:
                ntot += v
                chi_hist_nz[chi] = chi_hist_nz.get(chi, 0) + v
            if chi >= 0:
                tot_ge1 += v
                if nozero:
                    nge1 += v
            if chi >= -1:
                tot_ge0 += v
                if nozero:
                    nge0 += v
            if chi == -1:
                tot_eq0 += v
                if nozero:
                    neq0 += v
    f = (lambda a, b: (a / b) if b else 0.0)
    return dict(
        Ess=Ess, Esw=Esw, E=E, N=N, gauge_menu=gauge_menu,
        tot=tot, m_ge_3k1=tot_ge1, m_ge_3k=tot_ge0, m_eq_3k=tot_eq0, flex=tot - tot_ge1,
        tot_nozero=ntot, nozero_m_ge_3k1=nge1, nozero_m_ge_3k=nge0, nozero_m_eq_3k=neq0,
        nozero_flex=ntot - nge1,
        chi_hist={str(a): b for a, b in sorted(chi_hist.items())},
        chi_hist_nozero={str(a): b for a, b in sorted(chi_hist_nz.items())},
        frac_m_ge_3k1=f(tot_ge1, tot), frac_m_ge_3k=f(tot_ge0, tot),
        frac_m_eq_3k=f(tot_eq0, tot), frac_flex=f(tot - tot_ge1, tot),
        frac_nozero=f(ntot, tot),
        frac_nozero_m_ge_3k1=f(nge1, tot), frac_nozero_m_ge_3k=f(nge0, tot),
        frac_chi_eq_m1_of_flex=f(tot_eq0, tot - tot_ge1))


def load_items(k, cap, rng_seed=7):
    """A43 level1_h1.main sampling, verbatim."""
    p = os.path.join(A43RES, 'level0_k%d.json' % k)
    if not os.path.exists(p):
        return None
    d = json.load(open(p))
    items = []
    for s in d['samples']:
        w = s['main'] / max(1, s['nsample'])
        for wmv in s['w']:
            items.append((s['gmask'], tuple(wmv), w))
    rng = np.random.default_rng(rng_seed)
    cap_k = cap if k <= 6 else max(30, cap // 4)
    if len(items) > cap_k:
        idx = rng.choice(len(items), cap_k, replace=False)
        items = [items[i] for i in idx]
    return items


def main():
    ks = [int(x) for x in sys.argv[1:]] or [3, 4, 5, 6, 7]
    cap = int(os.environ.get('A43_L1_CAP', '160'))
    budget = int(os.environ.get('A43_L1_BUDGET', '22'))
    A43L1 = json.load(open(os.path.join(A43RES, 'level1.json')))
    report = {'protocol': dict(
        source='A43 attempts/A43-spine-census/code/h1/level1_h1.py sampling protocol, inherited',
        seed=7, cap='%d (k<=6) / %d (k=7)' % (cap, max(30, cap // 4)), budget=budget,
        weight='per-A-rep MAIN survivors main/nsample, from A43 results/h1/level0_k*.json')}
    reg = {'per_row_tot_mismatch': 0, 'per_row_m_ge_3k1_mismatch': 0,
           'per_row_nozero_mismatch': 0, 'per_row_nozero_n4_mismatch': 0, 'rows_compared': 0,
           'weighted_frac_N4_mismatch': []}
    for k in ks:
        items = load_items(k, cap)
        if not items:
            continue
        a43rows = A43L1.get('k%d' % k, {}).get('rows', [])
        a43idx = {}
        for i, r in enumerate(a43rows):
            a43idx.setdefault((r['gmask'], tuple(r['w'])), []).append(i)
        rows = []
        t0 = time.time()
        for gmask, wmv, w in items:
            we = fanout_we_branch(k, gmask, wmv, budget)
            if we is None:
                rows.append(dict(gmask=gmask, w=list(wmv), weight=w, we=None))
                print('k=%d gmask=%d w=%s SKIPPED (budget)' % (k, gmask, list(wmv)), flush=True)
                continue
            key = (gmask, tuple(wmv))
            if key in a43idx and a43idx[key]:
                a = a43rows[a43idx[key].pop(0)]['we']
                reg['rows_compared'] += 1
                reg['per_row_tot_mismatch'] += int(a['we_surv'] != we['tot'])
                reg['per_row_m_ge_3k1_mismatch'] += int(a['we_surv_N4'] != we['m_ge_3k1'])
                reg['per_row_nozero_mismatch'] += int(a['we_surv_nozero'] != we['tot_nozero'])
                reg['per_row_nozero_n4_mismatch'] += int(
                    a['we_surv_nozero_N4'] != we['nozero_m_ge_3k1'])
            rows.append(dict(gmask=gmask, w=list(wmv), weight=w, we=we))
            print('k=%d gmask=%d E=%d(%d+%d) tot=%.4e  ge3k1=%.4f ge3k=%.4f eq3k=%.4f flex=%.4f'
                  % (k, gmask, we['E'], we['Ess'], we['Esw'], we['tot'], we['frac_m_ge_3k1'],
                     we['frac_m_ge_3k'], we['frac_m_eq_3k'], we['frac_flex']), flush=True)
        ok = [i for i, r in enumerate(rows) if r['we'] is not None]
        wts = np.array([rows[i]['weight'] for i in ok], dtype=float)
        wts /= wts.sum()

        def wavg(key):
            return float((wts * np.array([rows[i]['we'][key] for i in ok])).sum())

        def wmed(key):
            return float(np.median([rows[i]['we'][key] for i in ok]))
        # aggregate chi histogram, graph-weighted (weights are MAIN orbit counts)
        agg = {}
        for i in ok:
            for c, v in rows[i]['we']['chi_hist'].items():
                agg[int(c)] = agg.get(int(c), 0.0) + rows[i]['weight'] * v
        tot_agg = sum(agg.values())
        entry = dict(
            n_graphs=len(rows), n_we=len(ok), seconds=round(time.time() - t0, 1),
            frac_m_ge_3k1_weighted=wavg('frac_m_ge_3k1'),
            frac_m_ge_3k_weighted=wavg('frac_m_ge_3k'),
            frac_m_eq_3k_weighted=wavg('frac_m_eq_3k'),
            frac_flex_weighted=wavg('frac_flex'),
            frac_nozero_weighted=wavg('frac_nozero'),
            frac_nozero_m_ge_3k1_weighted=wavg('frac_nozero_m_ge_3k1'),
            frac_nozero_m_ge_3k_weighted=wavg('frac_nozero_m_ge_3k'),
            frac_chi_eq_m1_of_flex_weighted=wavg('frac_chi_eq_m1_of_flex'),
            frac_m_ge_3k1_median=wmed('frac_m_ge_3k1'),
            frac_m_ge_3k_median=wmed('frac_m_ge_3k'),
            frac_flex_median=wmed('frac_flex'),
            chi_hist_orbit_weighted={str(c): agg[c] / tot_agg for c in sorted(agg)},
            chi_min=min(agg), chi_max=max(agg),
            rows=rows)
        a43k = A43L1.get('k%d' % k)
        if a43k:
            entry['A43_N4_frac_weighted'] = a43k['N4_frac_weighted']
            entry['A43_N3_frac_nozero_weighted'] = a43k['N3_frac_nozero_weighted']
            d1 = abs(entry['frac_m_ge_3k1_weighted'] - a43k['N4_frac_weighted'])
            d2 = abs(entry['frac_nozero_weighted'] - a43k['N3_frac_nozero_weighted'])
            entry['regression_abs_diff_N4_frac'] = d1
            entry['regression_abs_diff_N3_frac'] = d2
            reg['weighted_frac_N4_mismatch'].append(d1)
        report['k%d' % k] = entry
        print('--- k=%d ge3k1=%.6f ge3k=%.6f eq3k=%.6f flex=%.6f  (A43 N4=%.6f)'
              % (k, entry['frac_m_ge_3k1_weighted'], entry['frac_m_ge_3k_weighted'],
                 entry['frac_m_eq_3k_weighted'], entry['frac_flex_weighted'],
                 a43k['N4_frac_weighted'] if a43k else float('nan')), flush=True)
    reg['max_weighted_frac_N4_abs_diff'] = (max(reg['weighted_frac_N4_mismatch'])
                                            if reg['weighted_frac_N4_mismatch'] else None)
    reg['PASS'] = (reg['per_row_tot_mismatch'] == 0 and reg['per_row_m_ge_3k1_mismatch'] == 0
                   and reg['per_row_nozero_mismatch'] == 0
                   and reg['per_row_nozero_n4_mismatch'] == 0
                   # weighted fractions are floats: exact integer columns are the real test,
                   # the weighted mean can differ from A43's in the last ulp (summation order)
                   and (reg['max_weighted_frac_N4_abs_diff'] or 0.0) < 1e-14)
    report['regression_vs_A43_level1'] = reg
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, 'census_l1.json'), 'w') as fh:
        json.dump(report, fh, indent=1)
    print(json.dumps(reg, indent=1))
    print('wrote results/census_l1.json')


if __name__ == '__main__':
    main()
