"""A244 driver: minimise the side s over 11 unit squares subject to every cell of a cell set being
met by >= 2 squares to depth >= delta (mode `twelve` = the four corner boxes AND the eight wall
slots; mode `four` = A217's corner-only control).

    python search244.py --tag T --mode twelve --seeds a217 --n 400 --seed 0 --deltas 0.01,0.001

One JSON line per (seed, delta) to results/twelve244_<tag>.jsonl; resumable (rids already present
are skipped); `touch logs/STOP` stops after the current job.  Every record that reaches the target
carries verify244's interval-arithmetic verdict at the inflated side.
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts/A217-torque-probe/code'))
sys.path.insert(0, HERE)

import cells244 as C          # noqa: E402
import fast244 as F           # noqa: E402
import feas244 as A           # noqa: E402
import verify244 as V         # noqa: E402
import stress244 as S         # noqa: E402


def belownormal():
    try:
        import ctypes
        k = ctypes.windll.kernel32
        k.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        k.SetProcessAffinityMask.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        h = ctypes.c_void_p(-1)
        k.SetPriorityClass(h, 0x00004000)
        k.SetProcessAffinityMask(h, 0xFFFF)
    except Exception as e:                                        # noqa
        print('belownormal failed: %r' % (e,), flush=True)


def a217_seeds():
    """A217's crowd runs: every FEASIBLE four-crowd, sorted by side (282 of the 1217 are already
    12-stuck; the rest are 4-stuck starts for the twelve-cell descent)."""
    p = os.path.join(ROOT, 'attempts/A217-torque-probe/results/search217_crowd0.jsonl')
    out = []
    for line in open(p):
        r = json.loads(line)
        if 'z' not in r or r.get('min_pair_gap', -9) < -1e-9 or r.get('min_wall_gap', -9) < -1e-9:
            continue
        out.append((r['rid'], np.array(r['z'], float)))
    out.sort(key=lambda t: t[1][33])
    return out


def ring_seeds():
    """A239's rings (window / contact / jutting / A226 rattler), padded to 11 squares."""
    out = []
    p = os.path.join(ROOT, 'attempts/A239-rings-below-4/results/rings239.jsonl')
    if os.path.exists(p):
        for line in open(p):
            r = json.loads(line)
            out.append((r['label'], [tuple(q) for q in r['poses']], float(r['S'])))
    return out


def pad(poses, S, rng, grow=0.45):
    z = np.zeros(F.NV)
    f = (S + grow) / S
    for i, (x, y, t) in enumerate(poses[:11]):
        z[3 * i], z[3 * i + 1], z[3 * i + 2] = x * f, y * f, t
    for i in range(len(poses), 11):
        z[3 * i] = rng.uniform(1.0, S + grow - 1.0)
        z[3 * i + 1] = rng.uniform(1.0, S + grow - 1.0)
        z[3 * i + 2] = rng.uniform(0, math.pi / 2)
    z[F.S_IDX] = S + grow
    return z


def record(rid, meta, z, s, cells, delta, want):
    rec = {'rid': rid, 'delta': delta}
    rec.update(meta)
    if z is None:
        rec['ok'] = False
        return rec
    gw, gp, d2 = F.worst(z, cells, delta)
    st = C.stuck_report(z)
    rec.update({'ok': True, 's': float(s), 'z': [float(v) for v in z],
                'min_wall_gap': gw, 'min_pair_gap': gp, 'worst_second_depth': d2,
                'tilts_deg': [float(math.degrees(z[3 * i + 2] % (math.pi / 2))) for i in range(11)],
                'n_doubly_met': st['n_doubly_met'], 'meeters': st['meeters'],
                'twelve_stuck_float': st['twelve_stuck'], 'four_stuck_float': st['four_stuck'],
                'supply': {c: [C.supply_kind(c, i, st['meeters']) for i in st['meeters'][c][:4]]
                           for c in C.SLOTS}})
    rec['target_met'] = bool(st['twelve_stuck'] if want == 'twelve' else st['four_stuck'])
    try:
        rec.update(S.analyse(z))
    except Exception as e:                                        # noqa
        rec['fj_error'] = repr(e)
    if rec['target_met']:
        cert = V.certify_z(z, need=(want,))
        rec['cert'] = {k: v for k, v in cert.items() if k != 'cells'}
        rec['cert_cells'] = {k: v['meeters'] for k, v in cert['cells'].items()}
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tag', required=True)
    ap.add_argument('--mode', default='twelve', choices=('twelve', 'four', 'slots'))
    ap.add_argument('--seeds', default='a217')
    ap.add_argument('--n', type=int, default=200)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--deltas', default='0.01,0.001')
    ap.add_argument('--S', type=float, default=4.4)
    ap.add_argument('--step0', type=float, default=0.05)
    ap.add_argument('--tol', type=float, default=1e-6)
    ap.add_argument('--wall', type=float, default=1e9)
    ap.add_argument('--tilt', type=float, default=0.0,
                    help='tilt floor in degrees applied to every square (0 = off)')
    a = ap.parse_args()
    belownormal()
    F.TILT_MIN = math.radians(a.tilt) if a.tilt > 0 else 0.0
    cells = A.CELLSETS[a.mode]
    want = 'twelve' if a.mode == 'twelve' else 'four'
    deltas = [float(x) for x in a.deltas.split(',')]
    out = os.path.join(ATT, 'results', 'twelve244_%s.jsonl' % a.tag)
    stop = os.path.join(ATT, 'logs', 'STOP')
    done = set()
    if os.path.exists(out):
        for line in open(out):
            try:
                done.add(json.loads(line)['rid'])
            except Exception:                                     # noqa
                pass
    fh = open(out, 'a')
    rng = np.random.default_rng(a.seed)
    pool = a217_seeds() if a.seeds == 'a217' else None
    rings = ring_seeds() if a.seeds == 'ring' else None
    t0 = time.time()
    best = float('inf')
    nrun = 0
    for k in range(a.n):
        if os.path.exists(stop):
            print('STOP', flush=True)
            break
        if time.time() - t0 > a.wall:
            print('wall reached', flush=True)
            break
        if pool is not None:
            nm, zz = pool[(a.seed + k) % len(pool)]
            name, z0 = 'a217:%s' % nm, zz.copy()
        elif rings is not None:
            lbl, poses, S0 = rings[k % len(rings)]
            name, z0 = 'ring:%s:%d' % (lbl, k), pad(poses, S0, rng)
        else:
            name = '%s_%d_%04d' % (a.seeds, a.seed, k)
            z0 = A.STARTS[a.seeds](rng, a.S)
        for delta in deltas:
            rid = '%s|%s|d%g%s' % (name, a.mode, delta,
                                   '' if a.tilt <= 0 else '|t%g' % a.tilt)
            if rid in done:
                continue
            nrun += 1
            ts = time.time()
            try:
                z, ok = A.phase_a(z0.copy(), cells, delta, rng, tries=5)
                if ok:
                    z, s = A.phase_b(z, cells, delta, rng, step0=a.step0, tol=a.tol, retries=2)
                    rec = record(rid, {'mode': a.mode, 'seed_family': a.seeds, 'seed_name': name,
                                       'tilt_floor_deg': a.tilt}, z, s, cells, delta, want)
                else:
                    rec = record(rid, {'mode': a.mode, 'seed_family': a.seeds, 'seed_name': name,
                                       'phase_a': False, 'worst': list(F.worst(z, cells, delta))},
                                 None, None, cells, delta, want)
            except Exception as e:                                # noqa
                rec = {'rid': rid, 'ok': False, 'error': repr(e)}
            rec['secs'] = round(time.time() - ts, 2)
            fh.write(json.dumps(rec) + '\n')
            fh.flush()
            if rec.get('cert', {}).get('PASS') and rec['cert']['s_cert'] < best:
                best = rec['cert']['s_cert']
            print('%-46s s %9.6f cells %2d cert %s best %.6f %5.1fs' % (
                rid[-46:], rec.get('s', float('nan')), rec.get('n_doubly_met', -1),
                rec.get('cert', {}).get('PASS'), best, rec['secs']), flush=True)
    print('done %d jobs, best certified %.6f, %.0fs' % (nrun, best, time.time() - t0), flush=True)


if __name__ == '__main__':
    main()
