"""A44 census, k=11 projection: A43-H1 level2_h1.py's three extrapolation models applied to the
A44 branch columns.

Models (identical to A43 code/h1/level2_h1.py::fits, which is A31's machinery):
  M1_exp        log N = a + b k                       (linear fit of log counts, k = 3..7)
  M2_logquad    log N = a + b k + c k^2
  M3_ratio_lin  N(k)/N(k-1) = alpha + beta k, marched from k = 7
Composition (identical to A43): total(k) = graphs(k) * fanout(k) * frac(k), where
  graphs(k)   = exact MAIN' orbit count for k <= 7, model projection for k = 8..11
  fanout(k)   = A43's fitted decoration multiplier exp((a1+b1 k) ln20 + (a2+b2 k) ln2 + ak+bk k)
  frac(k)     = measured Level-1 weighted column fraction for k <= 7, log-linear fit for k >= 8
Everything at k = 8..11 is an EXTRAPOLATION, not a bound (A43 gap G-A43-7 / G2).
"""
import os, sys, json, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
A43RES = os.path.join(ROOT, 'attempts', 'A43-spine-census', 'results', 'h1')
OUT = os.path.join(ROOT, 'attempts', 'A44-fj-maxwell', 'results')
KS = [3, 4, 5, 6, 7]


def fits(ks, ys):
    """verbatim A43 level2_h1.fits"""
    ks = np.array(ks, dtype=float)
    ly = np.log(np.array(ys, dtype=float))
    out = {}
    b, a = np.polyfit(ks, ly, 1)
    out['M1_exp'] = (lambda k, a=a, b=b: math.exp(a + b * k), 'log N = %.4f + %.4f k' % (a, b))
    c, b, a = np.polyfit(ks, ly, 2)
    out['M2_logquad'] = (lambda k, a=a, b=b, c=c: math.exp(a + b * k + c * k * k),
                         'log N = %.4f + %.4f k + %.4f k^2' % (a, b, c))
    r = np.array([ys[i] / ys[i - 1] for i in range(1, len(ys))], dtype=float)
    beta, alpha = np.polyfit(ks[1:], r, 1)

    def m3(k, alpha=alpha, beta=beta, k0=ks[-1], y0=ys[-1]):
        v = float(y0)
        for t in range(int(k0) + 1, int(k) + 1):
            v *= (alpha + beta * t)
        return v
    out['M3_ratio_lin'] = (m3, 'N(k)/N(k-1) = %.4f + %.4f k' % (alpha, beta))
    return out


def main():
    L0 = {k: json.load(open(os.path.join(A43RES, 'level0_k%d.json' % k))) for k in KS}
    A43L1 = json.load(open(os.path.join(A43RES, 'level1.json')))
    A43L2 = json.load(open(os.path.join(A43RES, 'level2.json')))
    C = json.load(open(os.path.join(OUT, 'census_l1.json')))
    rep = {'ks': KS, 'models': {}, 'series': {}, 'fractions': {}, 'columns': {},
           'kill_factors': {}, 'regression': {}}

    # ---- fan-out multiplier, refit exactly as A43 level2_h1 (from A43's own level1.json)
    kk = KS
    Ess = np.array([np.average([r['Ess'] for r in A43L1['k%d' % k]['rows']],
                               weights=[r['weight'] for r in A43L1['k%d' % k]['rows']])
                    for k in kk])
    Esw = np.array([np.average([r['Esw'] for r in A43L1['k%d' % k]['rows']],
                               weights=[r['weight'] for r in A43L1['k%d' % k]['rows']])
                    for k in kk])
    surv = np.array([A43L1['k%d' % k]['gauge_surv_geomean_weighted'] for k in kk])
    a1, b1 = np.polyfit(kk, Ess, 1)[::-1]
    a2, b2 = np.polyfit(kk, Esw, 1)[::-1]
    keep = np.log(surv) - (Ess * math.log(20) + Esw * math.log(2))
    ak, bk = np.polyfit(kk, keep, 1)[::-1]

    def fan(k):
        return math.exp((a1 + b1 * k) * math.log(20) + (a2 + b2 * k) * math.log(2) + ak + bk * k)
    rep['models']['fanout'] = dict(
        Ess='%.4f + %.4f k' % (a1, b1), Esw='%.4f + %.4f k' % (a2, b2),
        log_keep='%.4f + %.4f k' % (ak, bk),
        values={k: fan(k) for k in range(3, 12)})
    rep['regression']['fanout_matches_A43'] = all(
        abs(fan(k) / A43L2['projection']['fanout'][str(k)] - 1) < 1e-12 for k in range(3, 12))

    # ---- graph series (A43 Level 0, unchanged)
    S = {'MAINprime': [L0[k]['new']['mainprime'] for k in KS],
         'MAINprime_N4_L0': [L0[k]['new']['mainprime_N4'] for k in KS],
         'MAINprime_nonthin': [L0[k]['new']['mainprime_nonthin'] for k in KS]}
    rep['series'] = {n: dict(zip(KS, v)) for n, v in S.items()}
    G = {}
    for n, ys in S.items():
        F = fits(KS, ys)
        rep['models'][n] = {m: F[m][1] for m in F}
        G[n] = {m: {k: (float(ys[KS.index(k)]) if k in KS else F[m][0](k))
                    for k in range(3, 12)} for m in F}

    # ---- Level-1 column fractions: measured k=3..7, log-linear fit for k=8..11 (A43's N4 rule)
    # Two columns are FITTED (both decay log-linearly, exactly as A43 fitted its N4 column);
    # the rest are DERIVED from them so the projected shares stay internally coherent
    # (flex = 1 - ge3k1, eq3k = ge3k - ge3k1).  A naive independent log-fit of `flex` runs
    # through 1.0 before k = 11 (it is a saturating share), which is why it is derived.
    FR = {}
    for nm in ('frac_m_ge_3k1', 'frac_m_ge_3k'):
        meas = np.array([C['k%d' % k][nm + '_weighted'] for k in KS])
        b, a = np.polyfit(KS, np.log(meas), 1)
        FR[nm] = {k: (float(meas[KS.index(k)]) if k in KS else math.exp(a + b * k))
                  for k in range(3, 12)}
        rep['fractions'][nm] = dict(kind='FITTED (log-linear in k, A43 N4 rule)',
                                    measured={k: float(meas[KS.index(k)]) for k in KS},
                                    fit='log frac = %.4f + %.4f k' % (a, b),
                                    k11=FR[nm][11], per_k=FR[nm])
    FR['frac_flex'] = {k: 1.0 - FR['frac_m_ge_3k1'][k] for k in range(3, 12)}
    FR['frac_m_eq_3k'] = {k: FR['frac_m_ge_3k'][k] - FR['frac_m_ge_3k1'][k]
                          for k in range(3, 12)}
    FR['frac_chi_eq_m1_of_flex'] = {k: FR['frac_m_eq_3k'][k] / FR['frac_flex'][k]
                                    for k in range(3, 12)}
    for nm in ('frac_flex', 'frac_m_eq_3k', 'frac_chi_eq_m1_of_flex'):
        meas = {k: float(C['k%d' % k][nm + '_weighted']) for k in KS}
        rep['fractions'][nm] = dict(
            kind='DERIVED from the two fitted columns',
            measured=meas, k11=FR[nm][11], per_k=FR[nm],
            derived_matches_measured_k3to7=all(
                abs(FR[nm][k] - meas[k]) < 1e-12 for k in KS))
    for nm in ('frac_nozero_m_ge_3k1', 'frac_nozero_m_ge_3k', 'frac_nozero'):
        rep['fractions'][nm] = dict(
            kind='DIAGNOSTIC (measured only, never composed)',
            measured={k: float(C['k%d' % k][nm + '_weighted']) for k in KS})
    rep['regression']['frac_m_ge_3k1_equals_A43_N4'] = {
        k: dict(a44=FR['frac_m_ge_3k1'][k], a43=A43L1['k%d' % k]['N4_frac_weighted']) for k in KS}
    rep['regression']['frac_m_ge_3k1_k11_vs_A43_N4_k11'] = dict(
        a44=FR['frac_m_ge_3k1'][11], a43=A43L2['projection']['fanout_N4_frac_k11'])

    # ---- composed columns
    def compose(graph_series, frac=None):
        out = {}
        for m in ('M1_exp', 'M2_logquad', 'M3_ratio_lin'):
            per = {k: G[graph_series][m][k] * fan(k) * (1.0 if frac is None else FR[frac][k])
                   for k in range(3, 12)}
            out[m] = dict(per_k=per, k11=per[11], sum_all_cores=sum(per.values()))
        return out

    COLS = {
        "MAIN' baseline (R11, EXACT composed)": compose('MAINprime'),
        "MAIN' non-thin (EXACT composed)": compose('MAINprime_nonthin'),
        'C-rep m>=3k+1 [CONDITIONAL on C-rep, A44-G1]': compose('MAINprime', 'frac_m_ge_3k1'),
        'C-rep m>=3k+1, A43 replication (L0 N4 series)': compose('MAINprime_N4_L0',
                                                                 'frac_m_ge_3k1'),
        'C* m>=3k [CONDITIONAL on C*, unproved]': compose('MAINprime', 'frac_m_ge_3k'),
        'FLEX-ONLY branch m<3k+1 [EXACT split of the baseline]': compose('MAINprime',
                                                                        'frac_flex'),
        'chi = -1 slice (m = 3k exactly)': compose('MAINprime', 'frac_m_eq_3k'),
        'C-rep & non-thin [CONDITIONAL]': compose('MAINprime_nonthin', 'frac_m_ge_3k1'),
        'C* & non-thin [CONDITIONAL]': compose('MAINprime_nonthin', 'frac_m_ge_3k'),
        'FLEX-ONLY & non-thin': compose('MAINprime_nonthin', 'frac_flex'),
    }
    rep['columns'] = {n: {m: dict(k11=v[m]['k11'], sum_all_cores=v[m]['sum_all_cores'],
                                  per_k=v[m]['per_k']) for m in v} for n, v in COLS.items()}

    base = COLS["MAIN' baseline (R11, EXACT composed)"]
    for n, v in COLS.items():
        rep['kill_factors'][n] = {
            m: dict(k11=base[m]['k11'] / v[m]['k11'],
                    per_k={k: base[m]['per_k'][k] / v[m]['per_k'][k] for k in range(3, 12)})
            for m in v}

    # ---- A43 regression on the composed numbers
    ctA = A43L2['projection']['composed_totals']
    rep['regression']['baseline_k11_vs_A43_MAINprime_exact'] = {
        m: dict(a44=base[m]['k11'], a43=ctA['MAINprime_exact'][m]['k11'],
                rel=abs(base[m]['k11'] / ctA['MAINprime_exact'][m]['k11'] - 1))
        for m in base}
    crep = COLS['C-rep m>=3k+1, A43 replication (L0 N4 series)']
    rep['regression']['Crep_k11_vs_A43_MAINprime_N4_conditional'] = {
        m: dict(a44=crep[m]['k11'], a43=ctA['MAINprime_N4_conditional'][m]['k11'],
                rel=abs(crep[m]['k11'] / ctA['MAINprime_N4_conditional'][m]['k11'] - 1))
        for m in crep}
    cnt = COLS['C-rep & non-thin [CONDITIONAL]']
    rep['regression']['Crep_nonthin_k11_vs_A43_MAINprime_N4_nonthin_conditional'] = {
        m: dict(a44=cnt[m]['k11'], a43=ctA['MAINprime_N4_nonthin_conditional'][m]['k11'],
                rel=abs(cnt[m]['k11'] / ctA['MAINprime_N4_nonthin_conditional'][m]['k11'] - 1))
        for m in cnt}
    rep['regression']['PASS'] = (
        rep['regression']['fanout_matches_A43']
        and all(v['rel'] < 1e-9 for v in
                rep['regression']['baseline_k11_vs_A43_MAINprime_exact'].values())
        and all(v['rel'] < 1e-9 for v in
                rep['regression']['Crep_k11_vs_A43_MAINprime_N4_conditional'].values())
        and all(v['rel'] < 1e-9 for v in rep['regression'][
            'Crep_nonthin_k11_vs_A43_MAINprime_N4_nonthin_conditional'].values()))

    rep['notes'] = [
        'Sampling protocol inherited verbatim from A43 (seed 7, cap 160/40, budget 22); no A43 '
        'or A31 file was modified.',
        'k = 3..7 fractions are EXACT weighted means over the sampled graph set (the same sample '
        'A43 used); the k = 8..11 values are extrapolations under the fitted models, NOT bounds '
        '(A43 G-A43-7 / G2).',
        'The FLEX-ONLY column is an EXACT split of the baseline (L9 contraposition): a structure '
        'with m < 3k+1 can never be first-order rigid. The C-rep and C* columns are CONDITIONAL '
        'on unproved conjectures (A44 theory.md).',
        'The C-rep A43-replication row multiplies A43\'s Level-0 N4 graph series (mainprime_N4, '
        'which is 0.997 x mainprime) as A43 did; the headline C-rep/C* rows use the same '
        'MAINprime graph series for both so the two kill factors are directly comparable.']

    json.dump(rep, open(os.path.join(OUT, 'census.json'), 'w'), indent=1, default=float)
    print('REGRESSION', json.dumps(
        {a: b for a, b in rep['regression'].items() if a != 'frac_m_ge_3k1_equals_A43_N4'},
        indent=1, default=float))
    print('\n--- k=11 composed (3 models) and kill factor vs baseline')
    for n in COLS:
        print('%-56s %s   kill %s' % (
            n[:56], {m: '%.3e' % COLS[n][m]['k11'] for m in COLS[n]},
            {m: '%.3g' % rep['kill_factors'][n][m]['k11'] for m in COLS[n]}))
    print('\n--- per-k fractions')
    for nm in FR:
        print('%-24s %s  k11=%.4g' % (nm, {k: round(FR[nm][k], 5) for k in KS}, FR[nm][11]))
    print('\n--- chi histogram (orbit-weighted share of all decorations)')
    for k in KS:
        h = C['k%d' % k]['chi_hist_orbit_weighted']
        print('k=%d ' % k, {c: round(v, 4) for c, v in sorted(h.items(), key=lambda t: int(t[0]))
                            if v >= 5e-4})
    print('wrote results/census.json')


if __name__ == '__main__':
    main()
