"""A263 tests of the factorisation  FULL (four squares, <= 8 parameters)  =>  P2 (W, S') + WE (s1, W) + WS (S', W').
  --mode rows : A260's adversary rows (results/adv260.jsonl: hybrid rings, independent tilts) + A258's 46 corpus
                rings; per corner: FULL margin vs the three factor margins.  Soundness check: max(factors) >= FULL.
  --mode adv  : hard-feasibility adversary on ONE factor family (--fam P2 | WE | WS, --adj 1 | 0): structured starts
                (tight / loose offsets x tilt pairs incl. unequal tilts), accept-only random moves; exact SAT check of
                the final witness (free_margin) before it is written.  results/fact263_<mode>.jsonl, resumable by key.
[M] only -- the box-valid statements are cert263.py."""
import argparse
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geo263 as G                                                    # noqa: E402
H, Z, R = G.H, G.Z, G.R
DEG = G.DEG


def ring_to_x(ring, s, N):
    """hybrid coordinates (a, f1, b, fW) per wall from eight vertex arrays (sense +; else mirrored first)."""
    for mirror in (False, True):
        sq = [np.stack([s - V[:, 0], V[:, 1]], axis=1) if mirror else np.array(V, float) for V in ring]
        x, ok = [], True
        for w in range(4):
            i1, iW = N.wall_pair(sq, s, w)
            if mirror:
                pass
            row = []
            for V in (sq[i1], sq[iW]):
                P = np.array(V, float)
                for _ in range((4 - w) % 4):
                    P = np.stack([s - P[:, 1], P[:, 0]], axis=1)
                e = P[1] - P[0]
                tilt = math.atan2(e[1], e[0]) % (math.pi / 2)
                row.append((P[:, 0].min(), s - P[:, 0].max(), tilt))
            if row[0][0] > row[1][0]:
                row = row[::-1]
            x += [row[0][0], row[0][2], row[1][1], row[1][2]]
        x = np.array(x)
        Vh = H.hyb_verts(x, s)
        err = max(min(np.abs(np.sort(Vh[i], axis=0) - np.sort(np.array(q, float), axis=0)).max() for q in sq)
                  for i in range(8))
        if err < 1e-6:
            return x
    return None


def mode_rows(a):
    out = os.path.join(HERE, '..', 'results', 'fact263_rows.jsonl')
    done = {json.loads(l)['key'] for l in open(out)} if os.path.exists(out) else set()
    items = []
    for l in open(os.path.join(G.ROOT, 'attempts', 'A260-locked-wall', 'results', 'adv260.jsonl')):
        r = json.loads(l)
        items.append(('adv260:' + r['key'], r['s'], np.array(r['x'])))
    rows, N = H.corpus()
    for name, s, sq in rows:
        x = ring_to_x(sq[:8], s, N)
        if x is None:
            print('SKIP (not a sense-+ hybrid)', name, flush=True)
            continue
        items.append(('corpus:' + name, s, x))
    for key, s, x in items:
        if key in done:
            continue
        rec = dict(key=key, s=s, corners=[])
        for k in range(4):
            f, g = G.corner_of_ring(x, s, k)
            m = {kind: G.factor_margin(kind, s, f, g, a.step)[0] for kind in ('FULL', 'P2', 'WE', 'WS')}
            m['dtilt_deg'] = [(f[1] - f[3]) / DEG, (g[3] - g[1]) / DEG]
            m['e'] = [f[2], g[2]]
            rec['corners'].append(m)
        rec['full'] = max(c['FULL'] for c in rec['corners'])
        rec['fact'] = max(max(c['P2'], c['WE'], c['WS']) for c in rec['corners'])
        rec['sound'] = all(max(c['P2'], c['WE'], c['WS']) >= c['FULL'] - 1e-9 for c in rec['corners'])
        with open(out, 'a') as fh:
            fh.write(json.dumps(rec) + '\n')
        print(key[:44], 'FULL %+.4f  factors %+.4f  sound %s' % (rec['full'], rec['fact'], rec['sound']), flush=True)


def sample(rng, fam, s, adj):
    """a structured feasible start of the family."""
    for _ in range(100000):
        t = rng.choice([1.0, 3.0, 8.0, 14.5, 20.0, 27.0, 35.0, 43.0]) + rng.normal()
        d = rng.choice([0.0, 0.0, 2.0, -2.0, 6.0, -6.0, 15.0, -15.0])
        f1, fW = np.clip([t, t + d], 0.3, 44.9) * DEG
        off = rng.choice([0.999, 0.97, 0.9, 0.8, 0.65])
        e = rng.choice([0.0, 1e-3, 0.03, 0.1, 0.25]) + (0.0 if fW == f1 else 0.0)
        if fam == 'WE':
            p = np.array([off, fW, e, f1])
            if G.floor_dom(p, s, adj) >= 0:
                return p
            p[2] = e + max(0.0, -G.floor_dom(p, s, False)) + 1e-3        # open the shift until s1, W are disjoint
            if G.floor_dom(p, s, adj) >= 0:
                return p
        elif fam == 'WS':
            p = np.array([off, f1, e, fW])
            for bump in (0.0, 0.02, 0.05, 0.1, 0.2):
                p[2] = e + bump
                if G.right_dom(p, s, adj) >= 0:
                    return p
        else:
            p = np.array([off, fW, rng.choice([0.999, 0.97, 0.9, 0.8, 0.65]), f1])
            if p2_dom(p, s) >= 0:
                return p
    return None


def p2_dom(p, s):
    b, fW, a1, f1 = p
    W = H.toucher(s - b - H.w_of(fW), fW, s, 0)
    S = H.toucher(a1, f1, s, 1)
    return min(1 - b, b, 1 - a1, a1, fW, f1, 45 * DEG - fW, 45 * DEG - f1, Z.poly_gap(W, S))


def fam_margin(fam, p, s, step):
    if fam == 'WE':
        return G.factor_margin('WE', s, f=tuple(p), step=step)
    if fam == 'WS':
        return G.factor_margin('WS', s, g=tuple(p), step=step)
    return G.factor_margin('P2', s, f=(p[0], p[1], 0.0, p[1]), g=(p[2], p[3], 0.0, p[3]), step=step)


def fam_dom(fam, p, s, adj):
    return G.floor_dom(p, s, adj) if fam == 'WE' else G.right_dom(p, s, adj) if fam == 'WS' else p2_dom(p, s)


def fam_verts(fam, p, s):
    if fam == 'WE':
        return G.floor_sq(tuple(p), s)
    if fam == 'WS':
        return G.right_sq(tuple(p), s)
    return [G.floor_sq((p[0], p[1], 0.0, p[1]), s)[1], G.right_sq((p[2], p[3], 0.0, p[3]), s)[0]]


def mode_adv(a):
    s = G.SHAT if a.side == 'shat' else float(a.side)
    out = os.path.join(HERE, '..', 'results', 'fact263_adv.jsonl')
    stop = os.path.join(HERE, '..', 'logs', 'STOP')
    done = {json.loads(l)['key'] for l in open(out)} if os.path.exists(out) else set()
    scale = np.array([1.0, 0.5, 1.0, 0.5])
    for r in range(a.restarts):
        key = '%s|%s|adj%d|%d|%d' % (a.fam, a.side, a.adj, a.seed, r)
        if key in done:
            continue
        if os.path.exists(stop):
            return
        t0 = time.time()
        rng = np.random.default_rng(9000 * a.seed + r)
        x = sample(rng, a.fam, s, bool(a.adj))
        if x is None:
            continue
        fx, sig = fam_margin(a.fam, x, s, 3.0)[0], 0.03
        for it in range(a.iters):
            y = x + sig * rng.normal(size=4) * scale
            if fam_dom(a.fam, y, s, bool(a.adj)) < 0:
                sig = max(sig * 0.97, 1e-4)
                continue
            fy = fam_margin(a.fam, y, s, 3.0)[0]
            if fy >= fx:
                x, fx, sig = y, fy, min(sig * 1.3, 0.1)
            else:
                sig = max(sig * 0.93, 1e-4)
        m, pose = fam_margin(a.fam, x, s, 0.5)
        Vs = fam_verts(a.fam, x, s)
        row = dict(key=key, fam=a.fam, s=s, adj=a.adj, p=[float(v) for v in x], margin=m, pose=pose,
                   pose_free_margin=None if pose is None else R.free_margin(pose[:3], Vs, s),
                   dom=fam_dom(a.fam, x, s, bool(a.adj)), slack=-(4 - s) / 2, sec=round(time.time() - t0, 1))
        with open(out, 'a') as fh:
            fh.write(json.dumps(row) + '\n')
        print(key, 'margin %+.5f (flush %+.5f)' % (m, row['slack']), [round(float(v), 4) for v in x], flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', default='rows')
    ap.add_argument('--fam', default='WE')
    ap.add_argument('--side', default='shat')
    ap.add_argument('--adj', type=int, default=1)
    ap.add_argument('--restarts', type=int, default=6)
    ap.add_argument('--iters', type=int, default=150)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--step', type=float, default=1.0)
    a = ap.parse_args()
    Z.belownormal()
    mode_rows(a) if a.mode == 'rows' else mode_adv(a)
