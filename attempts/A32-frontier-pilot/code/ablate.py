"""A32 ablation: rerun the mode-G tree with one cascade stage disabled at a time."""
import os
import sys
import json
import time
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.normpath(os.path.join(HERE, '..', 'results'))
STATE = os.path.normpath(os.path.join(HERE, '..', 'state'))
ABL = os.path.join(STATE, 'ablate')

STAGES = ['none', 'M2_wallcap3', 'M4_euler', 'X1_L1ext', 'X2_eulerbudget',
          'M5_metric', 'M5b_triangle', 'M5_metric,M5b_triangle', 'M6_planar',
          'M5_metric,M5b_triangle,M6_planar']


def run(K, off, workers):
    env = dict(os.environ)
    env['A32_WALLCAP'] = '3'
    env['A32_DISABLE'] = '' if off == 'none' else off
    env['A32_STATE'] = ABL
    t0 = time.time()
    p = subprocess.run([sys.executable, 'bb.py', str(K), '--workers', str(workers),
                        '--no-resume'], cwd=HERE, env=env,
                       capture_output=True, text=True)
    el = time.time() - t0
    d = json.load(open(os.path.join(RES, 'bb_K%d.json' % K)))
    lv = {int(a): b for a, b in d['levels'].items()}
    vis = 0
    for k, v in lv.items():
        for t, s in v.get('sub', {}).items():
            vis += s['visited']
    return dict(disabled=off, frontier={k: v['frontier'] for k, v in sorted(lv.items())},
                closed=d['close']['closed'], main=d['close']['main'],
                partial_nodes_visited=vis, seconds=round(el, 1))


def main():
    K = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    rows = os.environ.get('A32_ABL_ROWS')
    stages = rows.split('|') if rows else STAGES
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    out = []
    keep = os.path.join(RES, 'bb_K%d.json' % K)
    bak = keep + '.keep'
    if os.path.exists(keep):
        shutil.copy(keep, bak)
    for s in stages:
        r = run(K, s, w)
        out.append(r)
        print('  ablate %-16s frontier[%d]=%-8d main=%-7d nodes=%-10d %.1fs'
              % (s, K, r['frontier'][K], r['main'], r['partial_nodes_visited'],
                 r['seconds']), flush=True)
        json.dump(out, open(os.path.join(RES, 'ablation_K%d.json' % K), 'w'),
                  indent=1)
    if os.path.exists(bak):
        shutil.move(bak, keep)


if __name__ == '__main__':
    main()
