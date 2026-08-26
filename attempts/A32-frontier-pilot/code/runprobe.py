"""A32 driver for cascade stages 4-6 (sampled, cost/benefit measurement)."""
import os
import sys
import json
import math
import time
import random

import core as C
import t3probe as P

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.normpath(os.path.join(HERE, '..', 'results'))
STATE = os.path.normpath(os.path.join(HERE, '..', 'state'))


def sample_nodes(K, level, n, seed=0, main_only=False):
    p = os.path.join(STATE, 'K%d_level%d.json' % (K, level))
    if not os.path.exists(p):
        return []
    masks = json.load(open(p))['masks']
    rnd = random.Random(seed)
    if main_only:
        keep = []
        for m in masks:
            adj, wm = C.decode(level, m)
            if C.close_checks(level, adj, wm)['main']:
                keep.append(m)
        masks = keep
    if len(masks) > n:
        masks = rnd.sample(masks, n)
    return [(m,) + C.decode(level, m) for m in masks]


def main():
    out = {'stage4': [], 'stage5': [], 'stage6': [], 'tilt_variants': []}
    budget = float(os.environ.get('A32_PROBE_SECONDS', '900'))
    t_start = time.time()
    # --- stage 4 on structure-derived cells, across K and depth
    for K, lvl, nn in ((4, 4, 8), (5, 5, 8), (6, 4, 4), (6, 5, 4), (6, 6, 6)):
        for m, adj, wm in sample_nodes(K, lvl, nn, seed=K * 10 + lvl,
                                       main_only=(lvl == K)):
            if time.time() - t_start > budget:
                break
            r = P.probe_node(lvl, wm)
            r.update(K=K, level=lvl, mask=m,
                     E=sum(bin(a).count('1') for a in adj) // 2
                     + sum(C.POP[x] for x in wm))
            out['stage4'].append(r)
            print('  stage4 K=%d lvl=%d rows=%d pairs=%d farkas=%s %.2fs'
                  % (K, lvl, r['nrows'], r['straddling_pairs'],
                     r['farkas_verified'], r.get('t_farkas', 0)), flush=True)
    # --- tilt-class refinement: does pinning tilts (mode-D information) help?
    for m, adj, wm in sample_nodes(5, 5, 6, seed=77, main_only=True):
        if time.time() - t_start > budget * 1.5:
            break
        for tag, tilt in (('free', None),
                          ('zero_class', [(0.0, 1e-9)] * 5),
                          ('narrow_10deg', [(0.0, math.radians(10))] * 5)):
            r = P.probe_node(5, wm, tilt=tilt)
            r.update(variant=tag, mask=m)
            out['tilt_variants'].append(r)
            print('  tilt %s rows=%d farkas=%s kill=%s' %
                  (tag, r['nrows'], r['farkas_verified'], r['stage4a_kill']),
                  flush=True)
    # --- stage 5 (case-LP stub) and stage 6 (FJ) on ~10 leaves each
    for m, adj, wm in sample_nodes(5, 5, 10, seed=5, main_only=True):
        r = P.probe_node(5, wm, do_lp=True)
        out['stage5'].append({a: b for a, b in r.items() if a.startswith('t_')
                              or a in ('stage5_lp_feasible', 'nrows')})
        print('  stage5 rows=%d feas=%s %.2fs' % (r['nrows'],
              r.get('stage5_lp_feasible'), r.get('t_stage5_lp', 0)), flush=True)
    for m, adj, wm in sample_nodes(5, 5, 10, seed=6, main_only=True):
        ss = [(i, j) for i in range(5) for j in range(i + 1, 5)
              if (adj[i] >> j) & 1]
        sw = [(i, b) for i in range(5) for b in range(4) if (wm[i] >> b) & 1]
        r = P.probe_node(5, wm, do_fj=(ss, sw))
        out['stage6'].append({a: b for a, b in r.items() if a.startswith('t_')
                              or a.startswith('stage6') or a == 'nrows'})
        print('  stage6 active_rows=%d excluded=%s %.3fs'
              % (r.get('stage6_active_rows', 0), r.get('stage6_fj_excluded'),
                 r.get('t_stage6_fj', 0)), flush=True)
    json.dump(out, open(os.path.join(RES, 'probe.json'), 'w'), indent=1)
    print('done, %.1fs' % (time.time() - t_start))


if __name__ == '__main__':
    main()
