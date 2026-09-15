"""A217 witness search: local side-minimisation from (a) A85's 262 k0 optima, (b) the A37 atlas with
the corner squares perturbed, (c) random starts -- each free and with the tilt box (no settled corner).
    python search217.py --seeds cp85|atlas|random --tag T [--n N --seed K --wall SEC]
Appends one JSON line per run to results/search217_<tag>.jsonl.  Resumable: runs already in the
file (by run id) are skipped.
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geom217 as G
import opt217 as O
import crowd217 as C

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
TMINS = (None, math.radians(3), math.radians(10), math.radians(20))


def belownormal():
    try:
        import ctypes
        k = ctypes.windll.kernel32
        k.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        k.SetProcessAffinityMask.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        k.GetPriorityClass.argtypes = [ctypes.c_void_p]
        h = ctypes.c_void_p(-1)
        k.SetPriorityClass(h, 0x00004000)
        k.SetProcessAffinityMask(h, 0xFFFF)
        print('priority class %d (16384 = BelowNormal)' % k.GetPriorityClass(h), flush=True)
    except Exception as e:
        print('belownormal failed: %r' % (e,), flush=True)


def load_cp85():
    c = json.load(open(os.path.join(ROOT, 'attempts/A85-k0-route/results/cp85_k0_search.json')))
    out = []
    for o in sorted(c['optima'], key=lambda o: o['s']):
        z = np.zeros(34)
        for i, (x, y) in enumerate(o['centres']):
            z[3 * i], z[3 * i + 1], z[3 * i + 2] = x, y, math.radians(o['tilts_deg'][i])
        z[33] = o['s']
        out.append(z)
    return out


def load_atlas():
    a = json.load(open(os.path.join(ROOT, 'attempts/A37-cp-atlas/results/atlas_final.json')))
    out = []
    for e in a['entries']:
        z = np.array([v for row in e['canonical_sig'] for v in row] + [e['s_min_float']])
        out.append((str(e['family_id']), z))
    T = json.load(open(os.path.join(ROOT, 'attempts/A03-upper-reconstruct/trump11_float.json')))
    out.append(('trump', np.concatenate([np.array(T['X']).reshape(-1), [T['s']]])))
    return out


def perturb_corners(z, rng, tilt=(3, 30), shift=0.15):
    """rotate every square meeting a corner box by a random tilt and shift it inward."""
    z = np.array(z, float)
    s = z[33]
    for c in G.CORNER_NAMES:
        for i in G.corner_meeters(z, c):
            z[3 * i + 2] += math.radians(rng.uniform(*tilt)) * rng.choice([-1, 1])
            sx, sy = G.slot_centre(c, s)
            d = np.array([s / 2 - sx, s / 2 - sy])
            z[3 * i:3 * i + 2] += rng.uniform(0, shift) * d / np.linalg.norm(d)
    z[33] += 0.4
    return O.feasible_start(z)


def run_one(z0, tmin, rid, meta, fh):
    t0 = time.time()
    try:
        z, hist = O.local_opt(z0, tmin=tmin)
        sm = O.summary(z, tmin=tmin)
    except Exception as e:                      # noqa
        sm = {'error': repr(e)}
        hist = []
    rec = {'rid': rid, 'tmin_deg': None if tmin is None else round(math.degrees(tmin), 3),
           'secs': round(time.time() - t0, 3), 'outer': len(hist), 'hist_tail': hist[-2:]}
    rec.update(meta)
    rec.update(sm)
    fh.write(json.dumps(rec) + '\n')
    fh.flush()
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seeds', required=True)
    ap.add_argument('--tag', required=True)
    ap.add_argument('--n', type=int, default=400)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--wall', type=float, default=3000)
    ap.add_argument('--S', type=float, default=4.6)
    a = ap.parse_args()
    belownormal()
    out = os.path.join(ATT, 'results', 'search217_%s.jsonl' % a.tag)
    done = set()
    if os.path.exists(out):
        for line in open(out):
            try:
                done.add(json.loads(line)['rid'])
            except Exception:
                pass
    fh = open(out, 'a')
    t_start = time.time()
    rng = np.random.default_rng(a.seed)
    n_k0 = 0
    if a.seeds == 'cp85':
        seeds = [('cp85_%03d' % k, z) for k, z in enumerate(load_cp85())]
    elif a.seeds == 'atlas':
        seeds = []
        for name, z in load_atlas():
            seeds.append(('atlas_%s_raw' % name, z))
            for r in range(3):
                seeds.append(('atlas_%s_p%d' % (name, r), perturb_corners(z, rng)))
    elif a.seeds == 'crowd':
        seeds = [('crowd_%d_%04d' % (a.seed, k), None) for k in range(a.n)]
    else:
        seeds = [('rand_%d_%04d' % (a.seed, k), None) for k in range(a.n)]
    for name, z in seeds:
        if time.time() - t_start > a.wall:
            print('wall reached', flush=True)
            break
        if z is None:
            z = O.random_start(rng, S=a.S)
        if a.seeds == 'crowd':
            for delta in (0.05, 0.02):
                rid = '%s|crowd%g' % (name, delta)
                if rid in done:
                    continue
                desq = C.designate_fixed(z)
                z1, ok = C.crowd_feasible_start(z, desq, delta)
                if not ok:
                    fh.write(json.dumps({'rid': rid, 'seed_name': name, 'crowd_delta': delta, 'crowd_feasible': False}) + '\n')
                    fh.flush()
                    print('%-28s crowd start infeasible' % rid, flush=True)
                    continue
                t0 = time.time()
                zz, hist = O.local_opt(z1, extra=C.make_extra_fixed(desq, delta))
                sm = O.summary(zz, extra_active=C.active_crowd_fixed(zz, desq, delta))
                rec = {'rid': rid, 'seed_name': name, 'crowd_delta': delta, 'crowd_feasible': True, 'tmin_deg': None,
                       'designated': {k: v for k, v in desq.items()}, 'secs': round(time.time() - t0, 3),
                       'outer': len(hist), 'hist_tail': hist[-2:]}
                rec.update(sm)
                fh.write(json.dumps(rec) + '\n')
                fh.flush()
                n2 = sum(1 for c, m in sm['meeters'].items() if len(m) >= 2)
                print('%-28s s %.6f res %.1e rows %3d crowd_active %d n2 %d gaps %.0e %.0e %.1fs' % (
                    rid, sm['s'], sm['fj_res'], sm['n_rows'], sm['n_crowd_active'], n2, sm['min_pair_gap'], sm['min_wall_gap'], rec['secs']), flush=True)
            continue
        for tmin in TMINS:
            rid = '%s|%s' % (name, 'free' if tmin is None else 't%g' % round(math.degrees(tmin), 1))
            if rid in done:
                continue
            rec = run_one(z, tmin, rid, {'seed_name': name}, fh)
            if rec.get('k0') and rec.get('fj_res', 1) < 1e-8:
                n_k0 += 1
            print('%-28s s %.6f res %.1e rows %3d settled %d tb %d k0 %s %.1fs' % (
                rid, rec.get('s', float('nan')), rec.get('fj_res', float('nan')), rec.get('n_rows', -1),
                rec.get('n_settled', -1), rec.get('n_tiltbound_active', -1), rec.get('k0'), rec['secs']), flush=True)
    print('done; k0 FJ (res<1e-8) runs: %d; %.0fs' % (n_k0, time.time() - t_start), flush=True)


if __name__ == '__main__':
    main()
