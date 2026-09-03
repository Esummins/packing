"""A88 D2: Level-1 decoration statistics on uniformly sampled Level-0 survivors.

Per structure:
  * EXACT tilt-feasible decoration count (A44 census/census_l1.fanout_we_branch
    logic, copied in selftest88.exact_tilt_count) where E <= budget (22);
  * unbiased MC estimate elsewhere: draws uniform on the raw gauge-fixed menu
    20^Ess * 2^Esw, accepted by the tilt test.  Estimator
        tot_hat = menu * (accepted / drawn),  sigma from the binomial.
  * conditional pass rates of K0-1 (no slot square) and K0-3 (Lemma R ruler);
  * RIGID-POSSIBLE share chi = m - (3k+1) >= 0 vs FLEX-ONLY, with and without
    K0-1 (A44 columns).
"""
import os
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
import json
import math
import sys
import time
from collections import defaultdict

import numpy as np

import a88lib as A
from selftest88 import exact_tilt_count

K = 11
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, '..', 'results')
BUDGET = 22


def study(wm, edges, ndraw, rng):
    dec0 = A.Decoration(K, edges, wm, [('F', 0)] * len(edges),
                        {(i, b): 'CW' for i in range(K) for b in range(4)
                         if (wm[i] >> b) & 1})
    c0 = dec0.counts()
    Ess, Esw, E = c0['Ess'], c0['Esw'], c0['E']
    menu = 20 ** Ess * 2 ** Esw
    nf = 0
    n_k01 = 0
    n_k03 = 0
    n_both = 0
    n_rigid = 0
    n_rigid_k01 = 0
    chi_hist = defaultdict(int)
    chi_hist_k01 = defaultdict(int)
    for _ in range(ndraw):
        dec = A.random_decoration(K, edges, wm, rng)
        ts = dec.tilt_system()
        if not ts['feasible']:
            continue
        nf += 1
        c = dec.counts()
        chi_hist[c['chi']] += 1
        if c['chi'] >= 0:
            n_rigid += 1
        k01 = dec.k0_1()
        k03 = dec.k0_3(ts)[0]
        if k01:
            n_k01 += 1
            chi_hist_k01[c['chi']] += 1
            if c['chi'] >= 0:
                n_rigid_k01 += 1
        if k03:
            n_k03 += 1
        if k01 and k03:
            n_both += 1
    r = nf / ndraw
    row = dict(wm=wm, Ess=Ess, Esw=Esw, E=E, menu_log10=math.log10(menu),
               ndraw=ndraw, n_feasible=nf,
               tilt_rate=r, tilt_rate_sigma=math.sqrt(max(r * (1 - r), 0) / ndraw),
               tot_hat_log10=(math.log10(menu) + math.log10(r)) if r > 0 else None,
               K0_1_rate=(n_k01 / nf) if nf else None,
               K0_3_rate=(n_k03 / nf) if nf else None,
               K0_1_and_3_rate=(n_both / nf) if nf else None,
               rigid_possible_share=(n_rigid / nf) if nf else None,
               rigid_possible_share_given_K0_1=(n_rigid_k01 / n_k01)
               if n_k01 else None,
               chi_hist={str(a): b for a, b in sorted(chi_hist.items())},
               chi_hist_K0_1={str(a): b for a, b in sorted(chi_hist_k01.items())})
    return row


def add_exact(row, wm, edges):
    if True:
        ex = exact_tilt_count(K, edges, wm)
        row['exact'] = dict(tot=str(ex['tot']), m_ge_3k1=str(ex['m_ge_3k1']),
                            gauge_menu=str(ex['gauge_menu']),
                            exact_rate=ex['tot'] / ex['gauge_menu'],
                            exact_rigid_share=(ex['m_ge_3k1'] / ex['tot'])
                            if ex['tot'] else None)
    r = row['tilt_rate']
    if r > 0:
        row['exact_vs_mc_sigma'] = ((r - row['exact']['exact_rate'])
                                    / max(row['tilt_rate_sigma'], 1e-12))
    return row


def main():
    ngraph = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    ndraw = int(sys.argv[2]) if len(sys.argv) > 2 else 25000
    rng = np.random.default_rng(31415)
    surv = [json.loads(l) for l in
            open(os.path.join(RES, 'level0_survivors.jsonl'))]
    print('Level-0 uniform survivors: %d' % len(surv))
    idx = rng.permutation(len(surv))[:ngraph]
    rows = []
    picked = []
    t0 = time.time()
    for c, t in enumerate(idx):
        s = surv[int(t)]
        ed = [tuple(e) for e in s['edges']]
        rows.append(study(s['wm'], ed, ndraw, rng))
        picked.append((s['wm'], ed))
        if (c + 1) % 25 == 0:
            print('  %d / %d  (%.0fs)' % (c + 1, len(idx), time.time() - t0),
                  flush=True)
    # exact A44 decoration count on the N_EXACT smallest-E graphs (the exact
    # enumeration is 2^Ess * 2^Esw, so it is only affordable at small E)
    N_EXACT = int(os.environ.get('A88_N_EXACT', '8'))
    order = sorted(range(len(rows)), key=lambda t: rows[t]['E'])
    ne = 0
    for t in order:
        if ne >= N_EXACT or rows[t]['E'] > BUDGET:
            break
        te = time.time()
        add_exact(rows[t], picked[t][0], picked[t][1])
        rows[t]['exact_seconds'] = round(time.time() - te, 1)
        ne += 1
        print('  exact E=%d: rate %.6f vs MC %.6f (z=%.2f)  %.0fs'
              % (rows[t]['E'], rows[t]['exact']['exact_rate'],
                 rows[t]['tilt_rate'], rows[t].get('exact_vs_mc_sigma') or 0.0,
                 rows[t]['exact_seconds']), flush=True)

    def agg(key):
        v = [r[key] for r in rows if r.get(key) is not None]
        return dict(n=len(v), mean=float(np.mean(v)) if v else None,
                    median=float(np.median(v)) if v else None,
                    p05=float(np.percentile(v, 5)) if v else None,
                    p95=float(np.percentile(v, 95)) if v else None)

    lt = [r['tot_hat_log10'] for r in rows if r['tot_hat_log10'] is not None]
    ex_rows = [r for r in rows if 'exact' in r]
    ch = defaultdict(int)
    ch1 = defaultdict(int)
    for r in rows:
        for a, b in r['chi_hist'].items():
            ch[int(a)] += b
        for a, b in r['chi_hist_K0_1'].items():
            ch1[int(a)] += b
    tot_ch = sum(ch.values()) or 1
    tot_ch1 = sum(ch1.values()) or 1
    out = dict(
        n_graphs=len(rows), ndraw_per_graph=ndraw, budget_exact=BUDGET,
        E=agg('E'), Ess=agg('Ess'), Esw=agg('Esw'),
        tilt_rate=agg('tilt_rate'),
        log10_decorations_per_graph=dict(
            n=len(lt), mean=float(np.mean(lt)) if lt else None,
            median=float(np.median(lt)) if lt else None,
            p05=float(np.percentile(lt, 5)) if lt else None,
            p95=float(np.percentile(lt, 95)) if lt else None,
            max=float(np.max(lt)) if lt else None),
        K0_1_rate=agg('K0_1_rate'), K0_3_rate=agg('K0_3_rate'),
        K0_1_and_3_rate=agg('K0_1_and_3_rate'),
        rigid_possible_share=agg('rigid_possible_share'),
        rigid_possible_share_given_K0_1=agg('rigid_possible_share_given_K0_1'),
        chi_hist_pooled={str(a): ch[a] / tot_ch for a in sorted(ch)},
        chi_hist_pooled_K0_1={str(a): ch1[a] / tot_ch1 for a in sorted(ch1)},
        n_graphs_with_exact=len(ex_rows),
        exact_vs_mc=[dict(E=r['E'], exact_rate=r['exact']['exact_rate'],
                          mc_rate=r['tilt_rate'], sigma=r['tilt_rate_sigma'],
                          z=r.get('exact_vs_mc_sigma'))
                     for r in ex_rows],
        n_graphs_zero_feasible=sum(1 for r in rows if r['n_feasible'] == 0),
        seconds=round(time.time() - t0, 1),
        rows=rows)
    with open(os.path.join(RES, 'level1_88.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps({a: b for a, b in out.items() if a != 'rows'}, indent=1))


if __name__ == '__main__':
    main()
