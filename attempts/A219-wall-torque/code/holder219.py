"""A219 task 2 (second half): add ONE interior holder square at the best pose and see whether 11 squares
ever balance.  Per four-crowd witness: the meeter M that ring219's minimal external load pulls hardest and
the pull direction d; the holder R = a rattler (no loaded row) that is no meeter, else the least-loaded
non-meeter; every pose of holderpose219 priced by the free FJ residual (minimal external load); then the
DRAIN from the best pose: A217's local optimiser (a) free (no tilt floor, no crowd rows) and (b) with the
witness's four-crowd designation forced (crowd rows, delta) -- does a genuine FJ point with four doubly-met
open corners appear (crowd rows unloaded, n2 = 4, free residual < 1e-8)?
    python holder219.py [--drain-crowd N]   (resumable: witnesses already in results/holder219.jsonl skipped;
                                              one commit per row)
Resume block:  cd C:/Users/esumm/code/packing; export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1
    nohup python attempts/A219-wall-torque/code/holder219.py > attempts/A219-wall-torque/logs/holder219.log 2>&1 &
"""
import json
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rows219 as R                    # noqa: E402
import ring219 as RING                 # noqa: E402
import holderpose219 as HP             # noqa: E402
import geom217 as G                    # noqa: E402
import opt217 as O                     # noqa: E402
import crowd217 as C                   # noqa: E402

ATT = RING.ATT
REPO = os.path.abspath(os.path.join(ATT, '..', '..'))
OUT = os.path.join(ATT, 'results', 'holder219.jsonl')
RING_OUT = os.path.join(ATT, 'results', 'ring219.jsonl')
S_HAT = 3.877084


def belownormal():
    try:
        import ctypes
        k = ctypes.windll.kernel32
        k.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        k.SetPriorityClass(ctypes.c_void_p(-1), 0x00004000)
    except Exception as e:
        print('belownormal failed: %r' % (e,), flush=True)


def commit(path, msg):
    rel = os.path.relpath(path, REPO).replace('\\', '/')
    subprocess.run(['git', 'add', '--', rel], cwd=REPO, capture_output=True)
    subprocess.run(['git', 'commit', '-q', '-m', msg, '--', rel], cwd=REPO, capture_output=True)


def targets(ring_row, z, nmax=3):
    """(M, d, kind) candidates: the nmax meeters carrying the largest external load; d = the external force
    direction, and for a torque a push at each vertex v producing its sign (d ~ sign(tau) J(v-c) - 1.5 (v-c),
    which makes v the rearmost vertex of M in direction d)."""
    per = ring_row['force_torque']['per_square']
    ranked = sorted(((float(np.linalg.norm(d['F'])) + abs(d['tau']) / 0.7, int(i)) for i, d in per.items() if d['meeter']), reverse=True)
    out = []
    for _, M in ranked[:nmax]:
        F = np.array(per[str(M)]['F'])
        tau = per[str(M)]['tau']
        if np.linalg.norm(F) > 1e-6:
            out.append((M, F / np.linalg.norm(F), 'force'))
        if abs(tau) > 1e-6:
            c = z[3 * M:3 * M + 2]
            for v in G.corners(z)[M]:
                d = np.sign(tau) * R.jrot(v - c) - 1.5 * (v - c)
                out.append((M, d / np.linalg.norm(d), 'torque'))
    return out


def choose_holders(w, z, rows, lam):
    meeters = set(sum(w['meeters'].values(), []))
    load = {i: 0.0 for i in range(G.N)}
    for k, r in enumerate(rows):
        if lam[k] > 1e-6:
            load[r['i']] += lam[k]
            if r['kind'] == 'edge':
                load[r['j']] += lam[k]
    cands = sorted((load[i], i) for i in range(G.N) if i not in meeters)
    return [i for _, i in cands[:2]], {i: load[i] for i in range(G.N)}


def drain(z0, extra=None, max_outer=25):
    t0 = time.time()
    z, hist = O.local_opt(z0, tmin=None, max_outer=max_outer, extra=extra)
    res, lam, rws = O.fj_residual(z)
    out = {'s': float(z[G.S_IDX]), 'n2': HP.doubly_met_open(z), 'n_settled': sum(G.settled(z, c) is not None for c in G.CORNER_NAMES),
           'fj_res_free': float(res), 'outer_iters': len(hist), 't_s': round(time.time() - t0, 1),
           'meeters': {c: G.corner_meeters(z, c) for c in G.CORNER_NAMES}, 'z': [float(v) for v in z],
           'min_pair_gap': float(min(G.pair_gaps(z).values())), 'min_wall_gap': float(G.wall_rows(z)[0].min())}
    return out


def run_scan(z, holders, tg, out):
    best, n_poses = None, 0
    for h in holders:
        others = [o_ for o_ in holders if o_ != h]
        slot = {o_: HP.slots(z, o_, ignore=[h]) for o_ in others}
        for M, d, kind in tg:
            for z2, desc in HP.poses(z, M, h, d, ignore=others):
                for o_ in others:                            # the other free square gets out of the way
                    z2 = HP.relocate(z2, o_, slot[o_]) if z2 is not None else None
                if z2 is None:
                    continue
                n_poses += 1
                ev = HP.evaluate(z2)
                if best is None or ev['objective'] < best['objective']:
                    best = dict(ev, holder=h, target=M, target_kind=kind, pose=desc, z=[float(v) for v in z2])
    out['n_poses'] = n_poses
    out['_best'] = best
    return best


def run_one(w, ring_row, do_drain):
    rows, z = R.witness_rows(w)
    _, A, _ = R.system(z, rows)
    lam, lam0 = R.feasible(A)
    tg = targets(ring_row, z)
    out = {'wid': w['wid'], 'cls': w['cls'], 'rid': w['rid'], 's0': float(z[G.S_IDX]),
           'objective_no_holder': ring_row['force_torque']['objective'],
           'targets': [(M, kind, [float(v) for v in d]) for M, d, kind in tg]}
    if not tg:
        out['note'] = 'no external load on any meeter'
        return out
    holders, load = choose_holders(w, z, rows, lam if lam is not None else np.zeros(len(rows)))
    out['holders_tried'] = holders
    out['holder_loads'] = {h: load[h] for h in holders}
    best = None
    n_poses = 0
    z_orig = z
    for dil in (1.0, 1.15):                               # no room at the witness side: dilate uniformly
        z = z_orig.copy()
        z[:33:3] *= dil
        z[1:33:3] *= dil
        z[G.S_IDX] *= dil
        out['dilation'] = dil
        if run_scan(z, holders, tg, out) is not None:
            break
    best = out.pop('_best', None)
    n_poses = out.get('n_poses', 0)
    if best is None:
        out['note'] = 'no feasible pose'
        if do_drain:
            out['drain_free'] = drain(z_orig)
            for key in ('drain_free',):
                out[key]['four_crowd_FJ'] = bool(out[key]['n2'] == 4 and out[key]['fj_res_free'] < 1e-8)
                out[key]['below_s_hat'] = bool(out[key]['s'] <= S_HAT + 1e-9)
        return out
    out['best_pose'] = {k: v for k, v in best.items() if k != 'z'}
    out['best_pose']['objective_drop'] = ring_row['force_torque']['objective'] - best['objective']
    if do_drain:
        zb = np.array(best['z'])
        out['drain_free'] = drain(zb)
        desq = {cn: [int(i) for i in w['designated'][cn]] for cn in G.CORNER_NAMES} if w.get('designated') else C.designate_fixed(z)
        delta = w.get('crowd_delta') or 0.02
        out['drain_crowd'] = drain(zb, extra=C.make_extra_fixed(desq, delta))
        zc = np.array(out['drain_crowd']['z'])
        labels, Jc = C.active_crowd_fixed(zc, desq, delta)
        res_c, lam_c, rows_c = O.fj_residual(zc, extra_active=(labels, Jc))
        out['drain_crowd']['crowd_rows_active'] = len(labels)
        out['drain_crowd']['crowd_lam_sum'] = float(sum(l for r, l in zip(rows_c, lam_c) if r['kind'] == 'crowd'))
        out['drain_crowd']['fj_res_with_crowd'] = float(res_c)
        for key in ('drain_free', 'drain_crowd'):
            dd = out[key]
            dd['four_crowd_FJ'] = bool(dd['n2'] == 4 and dd['fj_res_free'] < 1e-8)
            dd['below_s_hat'] = bool(dd['s'] <= S_HAT + 1e-9)
    return out


def main():
    belownormal()
    n_drain_crowd = int(sys.argv[sys.argv.index('--drain-crowd') + 1]) if '--drain-crowd' in sys.argv else 40
    done = set()
    if os.path.exists(OUT):
        for l in open(OUT, encoding='utf-8'):
            done.add(json.loads(l)['wid'])
    ring = {}
    for l in open(RING_OUT, encoding='utf-8'):
        o = json.loads(l)
        ring[o['wid']] = o
    ws = RING.four_crowds()
    crowd_drain = {w['wid'] for w in sorted([w for w in ws if w['cls'] == 'CROWD'], key=lambda w: w['s'])[:n_drain_crowd]}
    t0 = time.time()
    for w in ws:
        if w['wid'] in done:
            continue
        do_drain = w['cls'] == 'HELD' or w['wid'] in crowd_drain
        o = run_one(w, ring[w['wid']], do_drain)
        o['t_total_s'] = round(time.time() - t0, 1)
        with open(OUT, 'a', encoding='utf-8') as f:
            f.write(json.dumps(o, default=float) + '\n')
        commit(OUT, 'A219 holder: %s %s' % (w['wid'], 'drain' if do_drain else 'pose-scan'))
        print(w['wid'], w['cls'], 'poses', o.get('n_poses'), 'obj', o.get('objective_no_holder'), '->',
              o.get('best_pose', {}).get('objective'), 'drain', {k: (o[k]['s'], o[k]['n2'], o[k]['fj_res_free']) for k in ('drain_free', 'drain_crowd') if k in o},
              '%.0f s' % (time.time() - t0), flush=True)


if __name__ == '__main__':
    main()
