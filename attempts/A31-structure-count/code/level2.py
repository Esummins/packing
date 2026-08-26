"""A31 Level 2: fit the Level-0 growth in k, project to k = 11, multiply by the
Level-1 decoration fan-out.  Everything here is EXTRAPOLATION, not a bound."""
import os, sys, json, math
import numpy as np


def load(outdir):
    L0, L1 = {}, {}
    for k in range(2, 12):
        p = os.path.join(outdir, 'level0_k%d.json' % k)
        if os.path.exists(p):
            L0[k] = json.load(open(p))
    p = os.path.join(outdir, 'level1.json')
    if os.path.exists(p):
        L1 = json.load(open(p))
    return L0, L1


def fits(ks, ys):
    """ys = counts.  Returns dict of model -> callable(k)."""
    ks = np.array(ks, dtype=float)
    ly = np.log(np.array(ys, dtype=float))
    out = {}
    # M1 pure exponential
    b, a = np.polyfit(ks, ly, 1)
    out['M1_exp'] = (lambda k, a=a, b=b: math.exp(a + b * k), 'log N = %.4f + %.4f k' % (a, b))
    # M2 quadratic in log (super-exponential)
    c, b, a = np.polyfit(ks, ly, 2)
    out['M2_logquad'] = (lambda k, a=a, b=b, c=c: math.exp(a + b * k + c * k * k),
                         'log N = %.4f + %.4f k + %.4f k^2' % (a, b, c))
    # M3 ratio linear in k:  N(k)/N(k-1) = alpha + beta k
    r = np.array([ys[i] / ys[i - 1] for i in range(1, len(ys))], dtype=float)
    rk = ks[1:]
    beta, alpha = np.polyfit(rk, r, 1)

    def m3(k, alpha=alpha, beta=beta, k0=ks[-1], y0=ys[-1]):
        v = float(y0)
        for t in range(int(k0) + 1, int(k) + 1):
            v *= (alpha + beta * t)
        return v
    out['M3_ratio_lin'] = (m3, 'N(k)/N(k-1) = %.4f + %.4f k' % (alpha, beta))
    return out


def main():
    here = os.path.dirname(__file__)
    outdir = os.path.join(here, '..', 'results')
    L0, L1 = load(outdir)
    ks = sorted(L0)
    rep = {'level0_counts': {}, 'fits': {}, 'projection': {}, 'notes': []}
    for k in ks:
        d = L0[k]
        rep['level0_counts'][k] = dict(
            R0_none=d['R0_no_filter'], R2_L5b=d['R2_L5b'], R3_L1=d['cum'][0],
            R4_L5d=d['cum'][1], R5_L4a=d['cum'][2], R6_L5a=d['cum'][3],
            R7_L3=d['cum'][4], R8_L6=d['cum'][5], R9_L4b=d['cum'][6],
            R10_L7=d['cum'][7], main=d['branch']['main'],
            thin_main=d['branch']['thin_main'],
            selfstress=d['branch']['selfstress_float'], lam0=d['branch']['lam0'],
            soft=d['soft'])
    # ---- growth of the several survivor series
    fk = [k for k in ks if k >= 3]
    series = {'main': [L0[k]['branch']['main'] for k in fk],
              'main_non_thin': [L0[k]['branch']['main'] - L0[k]['branch']['thin_main']
                                for k in fk]}
    if all(len(L0[k]['soft']) > 4 for k in fk):
        series['main_wallcap3'] = [L0[k]['soft'][4] for k in fk]
        series['main_wallcap3_nonthin'] = [L0[k].get('main_wallcap3_nonthin', 0)
                                           for k in fk]
    rep['series'] = {n: dict(zip(fk, v)) for n, v in series.items()}
    rep['projection']['other_series'] = {}
    for nm, yy in series.items():
        if nm == 'main' or min(yy) <= 0:
            continue
        F = fits(fk, yy)
        rep['projection']['other_series'][nm] = {
            n: {kk: f[0](kk) for kk in range(max(fk) + 1, 12)} for n, f in F.items()}
        rep['fits'][nm] = {n: f[1] for n, f in F.items()}
    ys = series['main']
    if len(fk) >= 4:
        # hold out the last k as a check
        F_all = fits(fk, ys)
        F_ho = fits(fk[:-1], ys[:-1])
        rep['fits']['main'] = {n: f[1] for n, f in F_all.items()}
        rep['fits']['main_holdout'] = {n: f[1] for n, f in F_ho.items()}
        rep['fits']['holdout_check'] = {
            n: dict(predicted=f[0](fk[-1]), actual=ys[-1],
                    ratio=f[0](fk[-1]) / ys[-1]) for n, f in F_ho.items()}
        proj = {}
        for n, f in F_all.items():
            proj[n] = {kk: f[0](kk) for kk in range(max(fk) + 1, 12)}
        rep['projection']['main_level0'] = proj
    # ---- decoration fan-out model
    if L1:
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
        keep = np.log(surv) - menu                  # log of the surviving fraction
        ak, bk = np.polyfit(kk, keep, 1)[::-1]
        rep['fits']['fanout'] = dict(
            Ess='%.4f + %.4f k' % (a1, b1), Esw='%.4f + %.4f k' % (a2, b2),
            log_keep_fraction='%.4f + %.4f k' % (ak, bk),
            per_edge_weighted={k: L1['k%d' % k]['per_edge_weighted'] for k in kk},
            kill_weighted={k: L1['k%d' % k]['kill_weighted'] for k in kk},
            measured_surv={k: surv[i] for i, k in enumerate(kk)})

        def fan(k):
            e1 = a1 + b1 * k
            e2 = a2 + b2 * k
            return math.exp(e1 * math.log(20) + e2 * math.log(2) + ak + bk * k)
        rep['projection']['fanout'] = {k: fan(k) for k in range(3, 12)}
        # ---- composed total
        if 'main_level0' in rep['projection']:
            tot = {}
            for n, pr in rep['projection']['main_level0'].items():
                allk = {}
                for k in range(3, 12):
                    m = (L0[k]['branch']['main'] if k in L0 else pr[k])
                    allk[k] = m * fan(k)
                tot[n] = dict(per_k=allk, k11=allk[11],
                              sum_all_cores=sum(allk.values()))
            rep['projection']['total_structures'] = tot
    with open(os.path.join(outdir, 'level2.json'), 'w') as fh:
        json.dump(rep, fh, indent=1, default=float)
    print(json.dumps(rep, indent=1, default=float)[:6000])


if __name__ == '__main__':
    main()
