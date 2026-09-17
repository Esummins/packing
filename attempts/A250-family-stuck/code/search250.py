"""A250 driver: minimise the side s over 11 unit squares subject to the FAMILY rows (every disjoint
family Pi of border cells with |Pi| <= kmax met by >= |Pi| + 1 distinct squares to depth >= delta),
or scan the residual at a ladder of fixed sides.

    python search250.py --tag main --mode descent  --maxfam 3 --seeds a244 --n 300
    python search250.py --tag res  --mode residual --maxfam 3 --sides 3.82,3.877084,3.95,4.0,4.3
    python search250.py --tag ctrl --mode descent  --maxfam 1 --seeds a217 --n 60   # ~4.00001

One JSON line per job to results/fam250_<tag>.jsonl; resumable (rids already present are skipped);
`logs/STOP` stops after the current job; the results file is committed every --commit jobs with an
explicit pathspec.  Every job that reaches the target is verified exactly by verify250.
"""
import argparse
import json
import math
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts/A244-twelve-stuck/code'))
sys.path.insert(0, HERE)

import cells244 as C          # noqa: E402
import feas244 as A           # noqa: E402
import fast250 as F           # noqa: E402
import fam250 as FM           # noqa: E402
import verify250 as V         # noqa: E402
from search244 import a217_seeds, belownormal       # noqa: E402

A.F = F                       # A244's phase_a / phase_b / polish, driven by the family penalty


def a244_seeds():
    """A244's certified twelve-stuck packings (sides 4.000010 .. 4.5) as descent starts."""
    p = os.path.join(ROOT, 'attempts/A244-twelve-stuck/results/twelve244.jsonl')
    out = []
    for line in open(p):
        r = json.loads(line)
        if 'z' in r:
            out.append((r.get('rid', '?'), np.array(r['z'], float)))
    out.sort(key=lambda t: t[1][33])
    return out


def commit(paths, msg):
    try:
        subprocess.run(['git', 'commit', '-q', '-m', msg, '--'] + list(paths), cwd=ROOT,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    except Exception as e:                                        # noqa
        print('commit failed: %r' % (e,), flush=True)


def residual(z, rows, delta):
    gw, gp, d2 = F.worst(z, rows, delta)
    short = 0.0 if d2 == float('inf') else delta - d2
    return max(-gw, -gp, short, 0.0), (gw, gp, d2)


def report(z, rows, delta):
    st = C.stuck_report(z)
    fr = FM.family_report(st['meeters'], float(z[F.S_IDX]), kmax=12)
    r, det = residual(z, rows, delta)
    return {'residual': r, 'min_wall_gap': det[0], 'min_pair_gap': det[1], 'worst_row_depth': det[2],
            'twelve_stuck_float': st['twelve_stuck'], 'meeters': st['meeters'],
            'min_excess_float': fr['min_excess'], 'argmin_float': fr['argmin'],
            'family_stuck_float': fr['family_stuck'], 'n_violating_float': fr['n_violating']}


def do_descent(z0, rows, delta, rng, a):
    z, ok = A.phase_a(z0.copy(), rows, delta, rng, tries=5, smax=a.smax)
    if not ok:
        return z, None, False
    z, s = A.phase_b(z, rows, delta, rng, step0=a.step0, tol=a.tol, retries=2)
    return z, s, True


def do_residual(z0, rows, delta, s, rng, inner=4):
    z = np.array(z0, float)
    lam = s / float(z[F.S_IDX])
    z[0:33:3] *= lam
    z[1:33:3] *= lam
    z[F.S_IDX] = s
    best = None
    for k in range(inner):
        start = z if k == 0 else A.jitter(z, rng, 0.05 * k, 4.0 * k)
        start[F.S_IDX] = s
        w, f = A.polish(start, rows, delta)
        r, _ = residual(w, rows, delta)
        if best is None or r < best[0]:
            best = (r, w)
        if r == 0.0:
            break
    return best[1], best[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tag', required=True)
    ap.add_argument('--mode', default='descent', choices=('descent', 'residual'))
    ap.add_argument('--maxfam', type=int, default=3)
    ap.add_argument('--seeds', default='a244')
    ap.add_argument('--n', type=int, default=200)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--deltas', default='0.01,0.001')
    ap.add_argument('--sides', default='3.82,3.877084,3.92,3.96,3.999,4.0,4.1,4.3,4.6')
    ap.add_argument('--S', type=float, default=4.3)
    ap.add_argument('--smax', type=float, default=7.0)
    ap.add_argument('--step0', type=float, default=0.05)
    ap.add_argument('--tol', type=float, default=1e-6)
    ap.add_argument('--wall', type=float, default=1e9)
    ap.add_argument('--tilt', type=float, default=0.0)
    ap.add_argument('--commit', type=int, default=20)
    ap.add_argument('--rowside', default='below4', choices=('below4', 'auto'),
                    help='below4 = the 1295/254 families disjoint at s < 4, a NECESSARY condition '
                         'at every side in [3, 5); auto = the families disjoint at the job side')
    a = ap.parse_args()
    belownormal()
    F.TILT_MIN = math.radians(a.tilt) if a.tilt > 0 else 0.0
    deltas = [float(x) for x in a.deltas.split(',')]
    sides = [float(x) for x in a.sides.split(',')]
    out = os.path.join(ATT, 'results', 'fam250_%s.jsonl' % a.tag)
    rel = os.path.relpath(out, ROOT).replace('\\', '/')
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
    pool = {'a244': a244_seeds, 'a217': a217_seeds}.get(a.seeds, lambda: None)()
    t0, best, nrun, since = time.time(), float('inf'), 0, 0
    for k in range(a.n):
        if os.path.exists(stop):
            print('STOP', flush=True)
            break
        if time.time() - t0 > a.wall:
            print('wall reached', flush=True)
            break
        if pool is not None:
            nm, zz = pool[(a.seed + k) % len(pool)]
            name, z0 = '%s:%s' % (a.seeds, nm), zz.copy()
        else:
            name = '%s_%d_%04d' % (a.seeds, a.seed, k)
            z0 = A.STARTS[a.seeds](rng, a.S)
        jobs = [(d, None) for d in deltas] if a.mode == 'descent' else [
            (d, s) for d in deltas for s in sides]
        for delta, side in jobs:
            rid = '%s|k%d|d%g%s' % (name, a.maxfam, delta, '' if side is None else '|s%g' % side)
            if rid in done:
                continue
            nrun += 1
            since += 1
            ts = time.time()
            rs = 3.9 if a.rowside == 'below4' else (a.S if side is None else side)
            rows = F.rows_for_side(rs, a.maxfam)
            rec = {'rid': rid, 'mode': a.mode, 'maxfam': a.maxfam, 'delta': delta, 'side': side,
                   'seed_family': a.seeds, 'seed_name': name, 'n_rows': len(rows),
                   'rowside': a.rowside,
                   'tilt_floor_deg': a.tilt}
            try:
                if a.mode == 'descent':
                    z, s, ok = do_descent(z0, rows, delta, rng, a)
                    rec['phase_a'] = ok
                else:
                    z, r = do_residual(z0, rows, delta, side, rng)
                    s, ok = float(z[F.S_IDX]), (r == 0.0)
                rec.update(report(z, rows, delta))
                rec['s'] = float(s) if s is not None else float(z[F.S_IDX])
                rec['z'] = [float(v) for v in z]
                rec['target_met'] = bool(ok and rec['residual'] == 0.0)
                if rec['target_met']:
                    c = V.certify_z(z)
                    rec['cert'] = {k2: v for k2, v in c.items()
                                   if k2 not in ('sure_meeters', 'witness_families')}
                    rec['cert_witness'] = c['witness_families'][:3]
                    if c['FAMILY_STUCK'] and c['s_cert'] < best:
                        best = c['s_cert']
            except Exception as e:                                # noqa
                rec['error'] = repr(e)
            rec['secs'] = round(time.time() - ts, 2)
            fh.write(json.dumps(rec) + '\n')
            fh.flush()
            print('%-40s s %9.6f res %.3e exc %s cert %s best %.6f %5.1fs' % (
                rid[-40:], rec.get('s', float('nan')), rec.get('residual', float('nan')),
                rec.get('min_excess_float'), rec.get('cert', {}).get('FAMILY_STUCK'), best,
                rec['secs']), flush=True)
            if since >= a.commit:
                since = 0
                commit([rel], 'A250: %s rows (%s, %d jobs)' % (a.tag, a.mode, nrun))
    commit([rel], 'A250: %s rows (%s, %d jobs, final)' % (a.tag, a.mode, nrun))
    print('done %d jobs, best certified FAMILY-STUCK %.6f, %.0fs' % (nrun, best, time.time() - t0),
          flush=True)


if __name__ == '__main__':
    main()
