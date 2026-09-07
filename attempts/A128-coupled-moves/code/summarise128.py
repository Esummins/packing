"""summarise128.py -- the packing x move table of drain_sel.md T3 from results/moves128.jsonl."""
import json, os, math
HERE = os.path.dirname(os.path.abspath(__file__)); A128 = os.path.dirname(HERE)
RES = os.path.join(A128, 'results')
rows = [json.loads(l) for l in open(os.path.join(RES, 'moves128.jsonl'), encoding='utf-8') if l.strip()]
SHAT = 3.877083590022814


def fmt_r(r):
    return '-' if r is None else ('%g' % r)


out = []
out.append('# T3 table -- packing x move (A128, results/moves128.jsonl)\n')
out.append('Box radius r in every pose coordinate and in the side; certified = exact interval certificate on the box of the stated radius (largest of 1e-3, 3e-4, 1e-4, 1e-5, 1e-6 that certifies); '
           '"held" = no certificate at any radius tried (point verdict in brackets: lock103 semantics at r = 0, contact bar 1e-7). Sample = drawn -> tested -> hits for the certified rows.\n')
out.append('| packing | side | K0-BLOCKED (point) | corner sq depth | ROT box r [point] | CLUSTER box r, cluster [point] | EXCHANGE at corner | rows sq/wall, mode | sample |')
out.append('|---|---|---|---|---|---|---|---|---|')
summary = {}
for o in rows:
    nm = o['packing']; s = o['side']
    ex = o['exchange']
    first = True
    n_int = len(o['intruders']); n_rot = sum(1 for r in o['intruders'] if r['ROT_box']['certified_radius'] is not None)
    n_rot3 = sum(1 for r in o['intruders'] if (r['ROT_box']['certified_radius'] or 0) >= 1e-3)
    n_cl = sum(1 for r in o['intruders'] if r['CLUSTER_box']['certified_radius'] is not None)
    n_cl3 = sum(1 for r in o['intruders'] if (r['CLUSTER_box']['certified_radius'] or 0) >= 1e-3)
    n_any3 = sum(1 for r in o['intruders'] if max(r['ROT_box']['certified_radius'] or 0, r['CLUSTER_box']['certified_radius'] or 0) >= 1e-3)
    n_cl_only = sum(1 for r in o['intruders'] if r['ROT_box']['certified_radius'] is None and r['CLUSTER_box']['certified_radius'] is not None)
    n_ex = sum(1 for c, e in ex.items() if e.get('certified_radius') is not None)
    n_free = sum(1 for c, e in ex.items() if 'K0-FREE' in e.get('verdict', ''))
    held_all = all(r['ROT_box']['certified_radius'] is None and r['CLUSTER_box']['certified_radius'] is None for r in o['intruders'])
    # per-corner box verdict: a corner is DEAD on the box of radius r if <= 1 possible meeter, or EXCHANGE certified
    # at >= r, or exactly two possible meeters and one of them certified retreating (ROT or CLUSTER) at >= r
    corners = {}
    for cn, e in ex.items():
        pm = e.get('possible_meeters_box', [])
        subj = [r for r in o['intruders'] if r['corner'] == cn]
        best = 0.0
        if len(pm) <= 1:
            best = max(o['radii'])
        if e.get('certified_radius'):
            best = max(best, e['certified_radius'])
        if len(pm) == 2:
            for r in subj:
                for key in ('ROT_box', 'CLUSTER_box'):
                    if r[key]['certified_radius']:
                        best = max(best, r[key]['certified_radius'])
        corners[cn] = {'possible_meeters': len(pm), 'dead_radius': best or None}
    box_dead_r = max((c['dead_radius'] or 0) for c in corners.values()) or None
    summary[nm] = dict(corners=corners, box_dead_radius=box_dead_r, side=s, blocked=o['K0_BLOCKED_point'], n_int=n_int, n_rot=n_rot, n_rot3=n_rot3, n_cl=n_cl, n_cl3=n_cl3,
                       n_any3=n_any3, n_cl_only=n_cl_only, n_ex=n_ex, n_free=n_free, held_all_box=held_all,
                       held_all_point=all(r['ROT_point']['held'] and r['CLUSTER_point']['held'] for r in o['intruders']),
                       extent=o['extent_bound'], seconds=o['seconds'], hooks={c: len(v['hooks']) for c, v in o['twowall'].items()})
    for r in o['intruders']:
        cn = r['corner']
        rb, cb = r['ROT_box'], r['CLUSTER_box']
        samp = cb.get('sample') or rb.get('sample')
        stxt = '-' if samp is None else '%d -> %d -> %d' % (samp['drawn'], samp['tested'], samp['hits'])
        e = ex[cn]
        etxt = ('K0-FREE box' if 'K0-FREE' in e.get('verdict', '') else
                'certified r=%g (margin %.1e)' % (e['certified_radius'], e.get('box_margin', float('nan'))) if e.get('certified_radius') is not None else
                'n/a (%d meeters)' % len(e['possible_meeters_box']) if len(e.get('possible_meeters_box', [])) >= 3 else
                'no (point margin %.1e)' % (e.get('best_refit_margin_point') if e.get('best_refit_margin_point') is not None else float('nan')))
        sup = r['SUPPLY']
        out.append('| %s | %.6f | %s | %s sq%d %.3g (tilt %.2f) | %s [%s] | %s %s [%s] | %s | %d/%d %s | %s |' % (
            nm if first else '', s if first else 0.0, ('yes' if o['K0_BLOCKED_point'] else 'no') if first else '',
            cn, r['square'], r['depth'], r['tilt_deg'],
            fmt_r(rb['certified_radius']), 'held' if r['ROT_point']['held'] else 'unheld',
            fmt_r(cb['certified_radius']), cb.get('cluster', ''), 'held' if r['CLUSTER_point']['held'] else 'unheld %s' % (r['CLUSTER_point']['best'][0],),
            etxt, sup['sq_rows'], sup['wall_rows'], sup['mode'], stxt))
        first = False
out.append('')
out.append('## Per-packing summary\n')
out.append('| packing | side | K0-BLOCKED | subjects | ROT box >= 1e-3 / any r | CLUSTER box >= 1e-3 / any r | coupled-only | any move >= 1e-3 | EXCHANGE certified corners | K0-FREE corners (box) | held under the whole menu on every box | BOX DEAD at radius | extent bound excludes W | hooks | s |')
out.append('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for nm, v in summary.items():
    out.append('| %s | %.6f | %s | %d | %d / %d | %d / %d | %d | %d | %d | %d | %s | %s | %s (%.4f) | %s | %.0f |' % (
        nm, v['side'], 'yes' if v['blocked'] else 'no', v['n_int'], v['n_rot3'], v['n_rot'], v['n_cl3'], v['n_cl'], v['n_cl_only'], v['n_any3'],
        v['n_ex'], v['n_free'], 'YES' if v['held_all_box'] else 'no', fmt_r(v['box_dead_radius']) + ' ' + str({c: fmt_r(x['dead_radius']) for c, x in v['corners'].items() if x['dead_radius']}), 'yes' if v['extent']['excludes_W'] else 'no', v['extent']['side_lower_bound_on_box'],
        {c: h for c, h in v['hooks'].items() if h}, v['seconds']))
open(os.path.join(RES, 'table128.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
json.dump(summary, open(os.path.join(RES, 'summary128.json'), 'w'), indent=1)
print('\n'.join(out[-len(summary) - 3:]))
