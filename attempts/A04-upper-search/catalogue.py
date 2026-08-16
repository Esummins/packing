"""
Merge res_*.jsonl -> results.jsonl ; cluster into distinct local optima -> local_optima.json ;
draw the best few -> best_*.png.   usage: python catalogue.py [nplot]
"""
import json, glob, sys, math
import numpy as np

RECORD = 3.877083590022814  # exact octic root (Trump / Gensane-Ryckelynck)


def load_all():
    recs = []
    for f in sorted(glob.glob('res_*.jsonl')):
        for line in open(f):
            try:
                r = json.loads(line)
            except Exception:
                continue
            r['file'] = f
            recs.append(r)
    return recs


def key_of(r, ds=1e-5):
    # cluster key: s rounded, plus number of (near-)upright squares and angle multiset rounded to 1 deg
    a = r['angles']
    ups = sum(1 for v in a if v < 0.5 or v > 89.5)
    tilt = tuple(sorted(int(round(v)) for v in a if 0.5 <= v <= 89.5))
    return (round(r['s'] / ds) * ds, ups, tilt)


def contacts(x, tol=1e-6):
    """count active contacts (pair or wall) at tolerance tol; used to flag rigidity."""
    import pack11 as P
    x = np.array(x)
    ov = P.sat_min_overlap(x)
    cv = P.container_viol(x)
    return int(np.sum(ov > -tol)), int(np.sum(cv > -tol))


def main():
    nplot = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    recs = load_all()
    with open('results.jsonl', 'w') as f:
        for r in recs:
            f.write(json.dumps(r) + '\n')
    print('total records', len(recs))
    by_method = {}
    for r in recs:
        m = r['method']
        by_method.setdefault(m, []).append(r['s'])
    for m, v in sorted(by_method.items()):
        v = np.array(v)
        print('%-12s n=%6d best=%.7f median=%.4f  frac<3.95: %.3f  frac<3.8771: %.4f' %
              (m, len(v), v.min(), np.median(v), np.mean(v < 3.95), np.mean(v < 3.8771)))
    # cluster
    clusters = {}
    for r in recs:
        k = key_of(r)
        if k not in clusters or r['s'] < clusters[k]['s']:
            cnt = clusters.get(k, {}).get('count', 0)
            clusters[k] = dict(r); clusters[k]['count'] = cnt
        clusters[k]['count'] += 1
    # merge clusters with same s (1e-6) -> non-rigid families
    bys = {}
    for k, c in clusters.items():
        sk = round(c['s'], 6)
        bys.setdefault(sk, []).append(c)
    out = []
    for sk in sorted(bys):
        cs = sorted(bys[sk], key=lambda c: c['s'])
        best = cs[0]
        npair, nwall = contacts(best['x'])
        c, th = np.array(best['x'][:22]).reshape(11, 2), np.array(best['x'][22:33])
        out.append(dict(s=best['s'], s_raw=best.get('s_raw'), n_variants=len(cs),
                        count=sum(c_['count'] for c_ in cs), angles_deg=best['angles'],
                        n_upright=sum(1 for v in best['angles'] if v < 0.5 or v > 89.5),
                        n_pair_contacts=npair, n_wall_contacts=nwall,
                        methods=sorted(set(c_['method'] for c_ in cs)),
                        centres=[[round(v, 9) for v in row] for row in c.tolist()],
                        thetas_rad=[round(v, 10) for v in th.tolist()],
                        ovmax=best['ovmax'], cvmax=best['cvmax']))
    json.dump(dict(record_known=RECORD, n_records=len(recs), n_distinct=len(out), optima=out),
              open('local_optima.json', 'w'), indent=1)
    print('distinct local optima (s to 1e-6):', len(out), ' with s<3.95:', sum(1 for o in out if o['s'] < 3.95),
          ' with s<3.90:', sum(1 for o in out if o['s'] < 3.90))
    print('\nbest 25:')
    for o in out[:25]:
        print('%.7f  cnt=%4d  up=%2d  contacts=%2d+%2d  angles=%s  %s' % (
            o['s'], o['count'], o['n_upright'], o['n_pair_contacts'], o['n_wall_contacts'],
            [a for a in o['angles_deg'] if 0.5 <= a <= 89.5], o['methods']))
    hits = [r for r in recs if abs(r['s'] - RECORD) < 1e-6]
    print('\nrecords within 1e-6 of the exact record:', len(hits), ' strictly below record-1e-9:',
          sum(1 for r in recs if r['s'] < RECORD - 1e-9))
    # ---- structural families: n_upright + canonical tilt multiset (angles folded to [0,45], rounded to 5 deg)
    def fam_key(r):
        a = r['angles']
        ups = sum(1 for v in a if v < 0.5 or v > 89.5)
        tilt = tuple(sorted(int(round(min(v, 90 - v) / 5.0)) * 5 for v in a if 0.5 <= v <= 89.5))
        return (ups, tilt)
    fams = {}
    for r in recs:
        k = fam_key(r)
        f = fams.setdefault(k, dict(n_upright=k[0], tilt_pattern_deg=list(k[1]), count=0, s_min=9, s_values=set(),
                                    methods=set(), best=None))
        f['count'] += 1; f['s_values'].add(round(r['s'], 4)); f['methods'].add(r['method'])
        if r['s'] < f['s_min']:
            f['s_min'] = r['s']; f['best'] = r
    fl = []
    for k, f in fams.items():
        b = f['best']
        npair, nwall = contacts(b['x'])
        fl.append(dict(n_upright=f['n_upright'], tilt_pattern_deg=f['tilt_pattern_deg'], count=f['count'],
                       s_min=f['s_min'], n_distinct_s_1e4=len(f['s_values']), methods=sorted(f['methods']),
                       best_angles_deg=b['angles'], n_pair_contacts=npair, n_wall_contacts=nwall,
                       best_x=b['x']))
    fl.sort(key=lambda f: f['s_min'])
    json.dump(dict(record_exact=RECORD, n_records=len(recs), n_families=len(fl), families=fl),
              open('families_catalogue.json', 'w'), indent=1)
    print('\nstructural families (n_upright, tilt multiset to 5 deg):', len(fl),
          ' with s_min<3.95:', sum(1 for f in fl if f['s_min'] < 3.95))
    print('%-10s %-5s %-4s %-3s %-5s %-6s %s' % ('s_min', 'cnt', 'ns', 'up', 'ctc', 'meth', 'tilt pattern / best angles'))
    for f in fl:
        if f['s_min'] < 3.95:
            print('%.7f %5d %4d %3d %2d+%2d %-6s %s  best=%s' % (
                f['s_min'], f['count'], f['n_distinct_s_1e4'], f['n_upright'], f['n_pair_contacts'],
                f['n_wall_contacts'], ','.join(m[:4] for m in f['methods']), f['tilt_pattern_deg'],
                [round(min(a, 90 - a), 1) for a in f['best_angles_deg'] if 0.5 <= a <= 89.5]))
    # plots
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.patches import Polygon
        fig, axes = plt.subplots(2, (nplot + 1) // 2, figsize=(4 * ((nplot + 1) // 2), 8))
        axes = axes.ravel()
        for ax, o in zip(axes, out[:nplot]):
            s = o['s']
            ax.add_patch(Polygon([[0, 0], [s, 0], [s, s], [0, s]], fill=False, lw=1.5))
            for (cx, cy), th in zip(o['centres'], o['thetas_rad']):
                u = np.array([math.cos(th), math.sin(th)]) / 2; v = np.array([-math.sin(th), math.cos(th)]) / 2
                cc = np.array([cx, cy])
                P_ = [cc + u + v, cc + u - v, cc - u - v, cc - u + v]
                tilted = 0.5 <= (math.degrees(th) % 90) <= 89.5
                ax.add_patch(Polygon(P_, fc='tab:blue' if tilted else 'tan', ec='k', alpha=0.8))
            ax.set_xlim(-0.1, s + 0.1); ax.set_ylim(-0.1, s + 0.1); ax.set_aspect('equal')
            ax.set_title('s=%.6f (x%d)' % (s, o['count']), fontsize=9); ax.axis('off')
        plt.tight_layout(); plt.savefig('best_optima.png', dpi=110)
        print('wrote best_optima.png')
    except Exception as e:
        print('plot failed', e)


if __name__ == '__main__':
    main()
