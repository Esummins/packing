"""A222 exchange searches on the ring rand_0_0569|t20 and every HELD / CROWD four-crowd of A217 (193):
  corner   -- CORNER-SWAP per corner c: X = M(c), settle S_c, place |M(c)| - 1 squares in U(X) \\ int S_c;
  wall     -- per wall (c, c'): X = M(c) u M(c'), settle both, place |X| - 2;
  ring4    -- X = the eight meeters, settle all four corners, place 4;
  ring1    -- X = the eight meeters, settle ONE corner c (each c), place 7;
  ring4x   -- X = meeters + every non-meeter meeting a window-perimeter cell (the intruders), settle all four,
              place |X| - 4.
Every placement is checked exactly on the composed 11-square configuration (region222.exact_check).
    python swap222.py [--only RID] [--resume]      -> results/swap222.jsonl (one row per witness, committed per row)
"""
import json
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import raise222 as R          # noqa: E402
import region222 as RG        # noqa: E402
import cells222 as C          # noqa: E402
import geom217 as G           # noqa: E402

ATT = os.path.abspath(os.path.join(HERE, '..'))
OUT = os.path.join(ATT, 'results', 'swap222.jsonl')
REPO = os.path.abspath(os.path.join(ATT, '..', '..'))
WALLS = [('BL', 'BR'), ('BR', 'TR'), ('TR', 'TL'), ('TL', 'BL')]


def poses(z):
    return [tuple(float(v) for v in z[3 * i:3 * i + 3]) for i in range(G.N)]


def intruders(z, X):
    """non-X squares meeting a window-perimeter cell (the squares a ring swap must also move)."""
    s = float(z[G.S_IDX])
    out = set()
    for (c, i, j) in C.window_family(s):
        box = C.cell_box(c, i, j, s)
        for q in range(G.N):
            if q not in X and C.square_meets_box(z, q, box):
                out.add(q)
    return sorted(out)


def hull_intruders(z, X):
    """non-X squares whose interior meets the convex hull of the X squares (what blocks a local swap)."""
    from shapely.geometry import Polygon, MultiPoint
    sq = poses(z)
    hull = MultiPoint([p for i in X for p in RG.sq_verts(*sq[i])]).convex_hull
    out = []
    for q in range(G.N):
        if q in X:
            continue
        P = Polygon(RG.sq_verts(*sq[q]))
        if P.intersection(hull).area > 1e-9:
            out.append(q)
    return out


def run_witness(w, quick=False):
    z = np.array(w['z'], float)
    s = float(z[G.S_IDX])
    sq = poses(z)
    M = {c: sorted(int(i) for i in w['meeters'][c]) for c in C.CORNERS}
    ring = sorted(set(sum(M.values(), [])))
    rec = {'wid': w['wid'], 'rid': w['rid'], 'cls': w['cls'], 's': s, 'meeters': M, 'ring': ring, 'searches': {}}
    t0 = time.time()

    def do(name, X, settle, k, seeds=()):
        fixed = [sq[i] for i in range(G.N) if i not in X] + [RG.slot_pose(c, s) for c in settle]
        t1 = time.time()
        r = RG.place(fixed, s, k, restarts=6 if quick else 12, seeds=seeds)
        r['X'] = list(X)
        r['settled'] = list(settle)
        r['secs'] = round(time.time() - t1, 2)
        r['hull_intruders'] = hull_intruders(z, X)
        if r['found']:
            zz = RG.compose(fixed, [tuple(p) for p in r['poses']], s)
            r['z_swapped'] = [float(v) for v in zz]
        rec['searches'][name] = r
        return r

    for c in C.CORNERS:
        do('corner_' + c, M[c], [c], len(M[c]) - 1)
    for (a, b) in WALLS:
        X = sorted(set(M[a] + M[b]))
        do('wall_%s%s' % (a, b), X, [a, b], len(X) - 2)
    # ring seeds: drop one meeter per corner (16 ways), keep the rest at their old poses (they overlap the
    # settled squares only; the polish pushes them into the bands)
    import itertools
    drops = [set(ch) for ch in itertools.product(*[M[c] for c in C.CORNERS])]
    seeds4 = [[sq[i] for i in ring if i not in d] for d in drops]
    do('ring4', ring, list(C.CORNERS), len(ring) - 4, seeds=seeds4)
    for c in C.CORNERS:
        cs = rec['searches']['corner_' + c]
        if cs['found']:      # the corner swap keeps the other six meeters: it IS a ring1 placement
            rec['searches']['ring1_' + c] = {'found': True, 'method': 'implied by corner_' + c, 'k': len(ring) - 1,
                                             'X': ring, 'settled': [c], 'secs': 0.0, 'hull_intruders': cs['hull_intruders']}
            continue
        seeds1 = [[sq[i] for i in ring if i != d] for d in M[c]]
        do('ring1_' + c, ring, [c], len(ring) - 1, seeds=seeds1)
    ext = sorted(set(ring) | set(intruders(z, ring)))
    rec['intruders'] = [q for q in ext if q not in ring]
    seedsx = [[sq[i] for i in ext if i not in d] for d in drops]
    do('ring4x', ext, list(C.CORNERS), len(ext) - 4, seeds=seedsx)
    rec['secs'] = round(time.time() - t0, 1)
    rec['summary'] = {'corners_swappable': [c for c in C.CORNERS if rec['searches']['corner_' + c]['found']],
                      'walls_swappable': [a + b for (a, b) in WALLS if rec['searches']['wall_%s%s' % (a, b)]['found']],
                      'ring4': rec['searches']['ring4']['found'],
                      'ring1': [c for c in C.CORNERS if rec['searches']['ring1_' + c]['found']],
                      'ring4x': rec['searches']['ring4x']['found']}
    return rec


def commit(path, msg):
    try:
        subprocess.run(['git', 'add', path], cwd=REPO, check=False)
        subprocess.run(['git', 'commit', '-q', '-m', msg + '\n\nCo-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>',
                        '--', path], cwd=REPO, check=False, capture_output=True)
    except Exception as e:  # noqa: BLE001
        print('commit failed', e, flush=True)


def main():
    only = None
    if '--only' in sys.argv:
        only = sys.argv[sys.argv.index('--only') + 1]
    ws = [w for w in R.load(True) if w['n2'] == 4 and w['cls'] in ('HELD', 'CROWD')]
    ws.sort(key=lambda w: (w['rid'] != 'rand_0_0569|t20', w['wid']))       # the ring first
    done = set()
    if '--resume' in sys.argv and os.path.exists(OUT):
        done = {json.loads(l)['wid'] for l in open(OUT, encoding='utf-8')}
    for w in ws:
        if only and w['rid'] != only:
            continue
        if w['wid'] in done:
            continue
        rec = run_witness(w, quick='--quick' in sys.argv)
        with open(OUT, 'a', encoding='utf-8') as f:
            f.write(json.dumps(rec) + '\n')
        print(w['wid'], rec['summary'], rec['secs'], flush=True)
        commit(os.path.relpath(OUT, REPO).replace('\\', '/'), 'A222 swap: %s' % w['wid'])


if __name__ == '__main__':
    main()
