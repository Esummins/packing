"""A235 contact census + two-selection test over every stressed witness we have: A217's 486 witnesses (HELD 184,
CROWD 185, and the SETTLED / K0FREE / BOXK0 kept there), the 883 genuine free FJ points, Trump, S02, S07 and the
21 survey records n = 5..55.  Writes results/census235.jsonl (one line per witness) and prints the summary.
    python census235.py [--only NAME]
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vv235 as V             # noqa: E402
import stress234 as ST        # noqa: E402

OUT = os.path.join(V.ATT, 'results', 'census235.jsonl')


def witnesses():
    for l in open(ST.WIT, encoding='utf-8'):
        raw = json.loads(l)
        w = ST.from_w217(raw)
        w['rid'] = raw['rid']
        yield w
    yield from ST.genuine_fj()
    yield ST.trump()
    yield ST.s02()
    yield ST.s07()
    yield from ST.survey()


def main():
    ST.set_priority()
    only = sys.argv[sys.argv.index('--only') + 1] if '--only' in sys.argv else None
    t0 = time.time()
    res = []
    with open(OUT if only is None else os.devnull, 'w', encoding='utf-8') as f:
        for w in witnesses():
            if only is not None and only not in w['name'] and only not in w.get('rid', ''):
                continue
            o, _ = V.analyse(w)
            o['t_s'] = round(time.time() - t0, 1)
            res.append(o)
            f.write(json.dumps(o, default=float) + '\n')
            if only is not None:
                print(json.dumps(o, indent=1, default=float))
    print('%d witnesses, %.0f s' % (len(res), time.time() - t0))
    groups = [('SETTLED',), ('K0FREE',), ('BOXK0',), ('HELD',), ('CROWD',), ('TRUMP', 'S02', 'S07'), ('RECORD',)]
    print('%-16s %5s %5s | %6s %6s %6s %6s %6s | %5s %5s %5s %5s %5s | %5s' % (
        'class', 'n', 'stat', 'VE', 'PAR', 'PARpt', 'VVtlt', 'ld-VV', 'wVV', 'wLd', 'wLdbl', 'wNec', 'wTot', 'EXCL1'))
    for g in groups:
        rs = [o for o in res if o['cls'] in g]
        if not rs:
            continue
        c = lambda key: sum(v for o in rs for k, v in o['contacts'].items() if k.startswith(key))
        print('%-16s %5d %5d | %6d %6d %6d %6d %6d | %5d %5d %5d %5d %5d | %5d' % (
            '+'.join(g), len(rs), sum(o['stationary'] for o in rs), c('VE/loaded'), c('PAR/loaded'), c('PAR-point/loaded'),
            sum(o['n_vv'] for o in rs), c('VV/loaded'),
            sum(o['n_vv'] > 0 for o in rs), sum(o['n_vv_loaded_l1'] > 0 for o in rs), sum(o['n_vv_loadable'] > 0 for o in rs),
            sum(any(e['necessarily_loaded'] for e in o['vv']) for o in rs),
            sum(o['n_vv'] > 0 and not o['vv_free_stress'] for o in rs),
            sum(any(e['loadable'] and e['first_order'] == 'EXCL-1' for e in o['vv']) for o in rs)))
    print('columns: loaded contacts by type (VE, PAR flush, PAR corner-point, tilted VV count, tilted VV loaded in the L1 stress);'
          ' witnesses with a tilted VV / loaded (L1) / loadable (polytope max > 0) / necessarily loaded (min > 0) /'
          ' with NO stress unloading every tilted VV at once (wTot) / loadable AND excluded at first order by the two-selection test')
    lv = [(o['name'], o['cls'], e) for o in res for e in o['vv'] if e['loadable']]
    print('loadable tilted VV contacts: %d; first-order: %s' % (len(lv), {k: sum(e['first_order'] == k for _, _, e in lv)
                                                                     for k in ('EXCL-1', 'PASS-1', 'PASS-1(self-stress)')}))
    for name, cls, e in lv:
        if e['first_order'] != 'EXCL-1':
            print('  PASS-1: %s %s pair %s tilt-gap %.1f deg lam(A,B)_l1 = (%.3g, %.3g) range %s sel_A %s sel_B %s' % (
                name, cls, e['pair'], e['tilt_gap_deg'], e['lam_A_l1'], e['lam_B_l1'], e['load_range'], e['sel_A'], e['sel_B']))


if __name__ == '__main__':
    main()
