"""A43-H1 Level 2: the A31 extrapolation machinery (3 models, k=7 holdout) recomputed for the
composed EXACT series, the non-thin series, and the CONDITIONAL variants, plus the k = 11 join
statement for the two EXACT-EXISTENTIAL filters N2 and N3.
"""
import os, json, math, sys
import numpy as np

RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'results', 'h1')


def fits(ks, ys):
    ks = np.array(ks, dtype=float)
    ly = np.log(np.array(ys, dtype=float))
    out = {}
    b, a = np.polyfit(ks, ly, 1)
    out['M1_exp'] = (lambda k, a=a, b=b: math.exp(a + b * k),
                     'log N = %.4f + %.4f k' % (a, b))
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
    L0 = {}
    for k in range(3, 12):
        p = os.path.join(RES, 'level0_k%d.json' % k)
        if os.path.exists(p):
            L0[k] = json.load(open(p))
    L1 = json.load(open(os.path.join(RES, 'level1.json')))
    ks = sorted(L0)
    rep = {'ks': ks, 'series': {}, 'fits': {}, 'holdout': {}, 'projection': {}}

    S = {}
    S['main_A31'] = [L0[k]['branch']['main'] for k in ks]
    S['main_nonthin_A31'] = [L0[k]['branch']['main'] - L0[k]['branch']['thin_main'] for k in ks]
    S['MAINprime_exact'] = [L0[k]['new']['mainprime'] for k in ks]
    S['MAINprime_nonthin'] = [L0[k]['new']['mainprime_nonthin'] for k in ks]
    S['MAINprime_N4_conditional'] = [L0[k]['new']['mainprime_N4'] for k in ks]
    S['MAINprime_N4_nonthin_conditional'] = [L0[k]['new']['mainprime_N4_nonthin'] for k in ks]
    rep['series'] = {n: dict(zip(ks, v)) for n, v in S.items()}

    for nm, ys in S.items():
        if min(ys) <= 0:
            continue
        Fa = fits(ks, ys)
        rep['fits'][nm] = {n: f[1] for n, f in Fa.items()}
        rep['projection'][nm] = {n: {kk: f[0](kk) for kk in range(max(ks) + 1, 12)}
                                 for n, f in Fa.items()}
        if len(ks) >= 4:
            Fh = fits(ks[:-1], ys[:-1])
            rep['holdout'][nm] = {n: dict(predicted=f[0](ks[-1]), actual=ys[-1],
                                          ratio=f[0](ks[-1]) / ys[-1]) for n, f in Fh.items()}

    # ---------------- decoration fan-out (A31 model, refit on this run's Level-1 numbers)
    kk = sorted(int(x[1:]) for x in L1)
    Ess = np.array([np.average([r['Ess'] for r in L1['k%d' % k]['rows']],
                               weights=[r['weight'] for r in L1['k%d' % k]['rows']])
                    for k in kk])
    Esw = np.array([np.average([r['Esw'] for r in L1['k%d' % k]['rows']],
                               weights=[r['weight'] for r in L1['k%d' % k]['rows']])
                    for k in kk])
    surv = np.array([L1['k%d' % k]['gauge_surv_geomean_weighted'] for k in kk])
    a1, b1 = np.polyfit(kk, Ess, 1)[::-1]
    a2, b2 = np.polyfit(kk, Esw, 1)[::-1]
    menu = Ess * math.log(20) + Esw * math.log(2)
    keep = np.log(surv) - menu
    ak, bk = np.polyfit(kk, keep, 1)[::-1]

    def fan(k):
        return math.exp((a1 + b1 * k) * math.log(20) + (a2 + b2 * k) * math.log(2) + ak + bk * k)

    n3 = np.array([L1['k%d' % k]['N3_frac_nozero_weighted'] for k in kk])
    n4 = np.array([L1['k%d' % k]['N4_frac_weighted'] for k in kk])
    n7 = np.array([L1['k%d' % k]['N7d_frac_weighted'] for k in kk])
    c3, d3 = np.polyfit(kk, n3, 1)[::-1]
    b4, a4 = np.polyfit(kk, np.log(n4), 1)
    rep['fits']['fanout'] = dict(
        Ess='%.4f + %.4f k' % (a1, b1), Esw='%.4f + %.4f k' % (a2, b2),
        log_keep_fraction='%.4f + %.4f k' % (ak, bk),
        measured_surv={k: float(surv[i]) for i, k in enumerate(kk)},
        N3_frac_nozero={k: float(n3[i]) for i, k in enumerate(kk)},
        N3_fit='%.4f + %.4f k (linear)' % (c3, d3),
        N4_frac={k: float(n4[i]) for i, k in enumerate(kk)},
        N4_fit='log frac = %.4f + %.4f k' % (a4, b4),
        N7d_frac={k: float(n7[i]) for i, k in enumerate(kk)})
    rep['projection']['fanout'] = {k: fan(k) for k in range(3, 12)}
    rep['projection']['fanout_N3_frac_k11'] = float(c3 + d3 * 11)
    rep['projection']['fanout_N4_frac_k11'] = float(math.exp(a4 + b4 * 11))

    # ---------------- composed totals
    tot = {}
    for nm in ('main_A31', 'MAINprime_exact', 'MAINprime_nonthin',
               'MAINprime_N4_conditional', 'MAINprime_N4_nonthin_conditional'):
        if nm not in rep['projection']:
            continue
        tot[nm] = {}
        for model, pr in rep['projection'][nm].items():
            allk = {}
            for k in range(3, 12):
                m = L0[k]['new']['mainprime'] if (k in L0 and nm == 'MAINprime_exact') else None
                if k in L0:
                    m = dict(main_A31=L0[k]['branch']['main'],
                             MAINprime_exact=L0[k]['new']['mainprime'],
                             MAINprime_nonthin=L0[k]['new']['mainprime_nonthin'],
                             MAINprime_N4_conditional=L0[k]['new']['mainprime_N4'],
                             MAINprime_N4_nonthin_conditional=L0[k]['new'][
                                 'mainprime_N4_nonthin'])[nm]
                else:
                    m = pr[k]
                f = fan(k)
                if nm.endswith('conditional'):
                    f = f * (n4[kk.index(k)] if k in kk else math.exp(a4 + b4 * k))
                allk[k] = m * f
            tot[nm][model] = dict(per_k=allk, k11=allk[11], sum_all_cores=sum(allk.values()))
    rep['projection']['composed_totals'] = tot

    # ---------------- k = 11 JOIN for the EXACT-EXISTENTIAL filters
    aw = {k: L0[k]['new']['main_N1_allwall'] / max(1, L0[k]['new']['main_N1']) for k in ks}
    lk = np.array(ks, dtype=float)
    la = np.log(np.array([max(aw[k], 1e-12) for k in ks]))
    ba, aa = np.polyfit(lk, la, 1)
    rep['k11_join'] = dict(
        N2_allwall_frac_of_MAIN_N1={k: aw[k] for k in ks},
        N2_allwall_counts={k: L0[k]['new']['main_N1_allwall'] for k in ks},
        N2_fit='log frac = %.4f + %.4f k' % (aa, ba),
        N2_frac_k11_extrapolated=float(math.exp(aa + ba * 11)),
        N2_statement=(
            'At k = 11 the loaded core IS the whole packing (no rattlers), so A38.1 applies '
            'directly: a structure in which EVERY square carries a nonzero wall mask has no '
            'square with centre in Z = [11/10, 694271/250000]^2 and is DEAD.  For k < 11 the '
            'A38.1 witness may be one of the 11-k rattlers, so the column is vacuous there.  '
            'Extrapolated all-wall fraction of MAIN&N1 at k=11: %.3e -- i.e. N2 removes a '
            'vanishing share of the k=11 graph count.  Note also the exact combinatorial '
            'squeeze: with N1 (per-wall <= 3) the four walls carry at most 12 square-wall '
            'incidences, so an all-wall k=11 core has at most ONE corner square.'
            % float(math.exp(aa + ba * 11))),
        N3_frac_no_zero_class={k: float(n3[i]) for i, k in enumerate(kk)},
        N3_frac_k11_extrapolated=float(c3 + d3 * 11),
        N3_statement=(
            'A21 THM3 is existential over the 11 squares, so like N2 it bites only at k = 11.  '
            'It can bite only on decorations with NO zero-pinned tilt class (a wall-flush edge '
            'gives phi = 0 in [0,18] deg and satisfies THM3 for free).  Measured share of '
            'tilt-feasible decorations with no zero class is FLAT in k (%s), extrapolating to '
            '%.3f at k=11.  So THM3 can remove AT MOST ~%.0f%% of decorated k=11 structures, '
            'and only that subset in which the tilt system additionally FORCES all 11 tilts '
            'into (18,27)u(63,72) deg -- a condition this census does not test.'
            % ({k: round(float(n3[i]), 4) for i, k in enumerate(kk)},
               float(c3 + d3 * 11), 100 * float(c3 + d3 * 11))))

    json.dump(rep, open(os.path.join(RES, 'level2.json'), 'w'), indent=1, default=float)
    print(json.dumps({a: b for a, b in rep.items() if a != 'projection'}, indent=1,
                     default=float)[:4000])
    print('--- k11 composed:')
    for nm in tot:
        print(nm, {m: '%.3e' % tot[nm][m]['k11'] for m in tot[nm]})


if __name__ == '__main__':
    main()
