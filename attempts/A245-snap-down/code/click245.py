"""A245 Lemma WALL-CLICK, tested: on every wall of every testbed configuration find the WALL PAIR (B = the
meeter of corner c touching the wall, B' = the meeter of the adjacent corner c' touching it; H-WALL), read
STACK's data (order, clearance, contact type, handedness, mutual supply), then rotate the pair JOINTLY toward
flush in `steps` steps, the side re-minimised at every step by the fixed-tilt LP
  LOCAL  -- only the pair's centres move (every other square frozen): feasible iff s_local(t) <= s0;
  GLOBAL -- every centre free (A223's variant B);
and run REDUCE (reduce245) on the original, the local end and the global end configurations.
    python click245.py [--which a244,ring,crowd] [--steps 20] [--resume]  -> results/click245.jsonl
"""
import argparse
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom245 as G          # noqa: E402
import lp245 as L            # noqa: E402
import reduce245 as R        # noqa: E402
import stack245 as S         # noqa: E402
import testbeds245 as T      # noqa: E402

RES = os.path.join(HERE, '..', 'results')
OUT = os.path.join(RES, 'click245.jsonl')
STOP = os.path.join(HERE, '..', 'logs', 'STOP')


def be_polite():
    try:
        import psutil
        p = psutil.Process()
        p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        p.cpu_affinity(list(range(16)))
    except Exception:
        pass


TOUCH_TOL = 1e-4      # A244's candidates are polished to ~1e-5 of their walls


def wall_pair(poses, s, wall, tol=None):
    tol = TOUCH_TOL if tol is None else tol
    n = len(poses)
    c, cp, names = G.wall_names(wall)
    ms = G.meeters(poses, s)
    fr = [G.to_frame(p, wall, s) for p in poses]
    touch = {i for i in range(n) if G.verts(fr[i])[:, 0].min() <= tol}
    wp = {i: G.wall_params(fr[i])[1] for i in touch}
    Bc = [i for i in ms[names[0]] if i in touch]
    Bpc = [i for i in ms[names[3]] if i in touch]
    info = {'wall': wall, 'c': c, 'cp': cp, 'm_c00': ms[names[0]], 'm_c01': ms[names[1]],
            'm_cp01': ms[names[2]], 'm_cp00': ms[names[3]], 'touch_c': Bc, 'touch_cp': Bpc, 'pair': None}
    hwall = bool(Bc and Bpc)
    if hwall:
        B, Bp = max(Bc, key=wp.get), min(Bpc, key=wp.get)
    else:                                   # H-WALL fails: fall back to the MUTUAL suppliers, if any
        Bm = [i for i in ms[names[0]] if i in ms[names[2]]]
        Bpm = [i for i in ms[names[3]] if i in ms[names[1]]]
        if not Bm or not Bpm:
            info['why'] = 'no wall-touching meeter of ' + ('c' if not Bc else "c'") + ' and no mutual pair'
            return info, fr
        B, Bp = Bm[0], Bpm[0]
    if B == Bp:
        info['why'] = 'one square meets both boxes'
        return info, fr
    gap = G.pair_gap(fr[B], fr[Bp])
    info.update({'pair': (B, Bp), 'hwall': hwall, 'A': [i for i in ms[names[0]] if i != B],
                 'Ap': [i for i in ms[names[3]] if i != Bp],
                 'mutual': bool(Bp in ms[names[1]] and B in ms[names[2]]),
                 'th': math.degrees(fr[B][2]), 'thp': math.degrees(fr[Bp][2]),
                 'hand': G.handedness(fr[B][2]) + G.handedness(fr[Bp][2]), 'gap': float(gap),
                 'contact': bool(gap <= 1e-6), 'chord_sum': G.chord(fr[B][2]) + G.chord(fr[Bp][2])})
    if hwall:
        thB, ellB = G.wall_params(fr[B])
        thP, ellP = G.wall_params(fr[Bp])
        info.update({'ell': ellB, 'ellp': ellP, 'order_ok': bool(ellB < ellP),
                     'clearance': (ellP - math.cos(thP)) - (ellB + math.sin(thB)),
                     'contact_type': S.contact_type(thB, ellB, thP, ellP, tol=1e-5) if gap <= 1e-6 else 'none',
                     'predicted': S.predicted(thB, thP), 'H': (ellP + math.sin(thP)) - (ellB - math.cos(thB))})
    return info, fr


def schedule(th, t):
    h = G.handedness(th)
    if h == 'F':
        return th
    if h == '-':
        return math.pi / 2 - (math.pi / 2 - th) * (1 - t)
    return th * (1 - t)


def click(poses, s0, pair, steps):
    n = len(poses)
    rec = {}
    for mode in ('local', 'global'):
        free = list(pair) if mode == 'local' else list(range(n))
        cur, ss, frames = list(poses), [], {}
        blocked_at, blk = None, None
        for k in range(steps + 1):
            t = k / steps
            new = [(cur[i][0], cur[i][1], schedule(poses[i][2], t) if i in pair else cur[i][2]) for i in range(n)]
            p2, s, sel, it = L.fixed_tilt_min(new, free)
            if p2 is None:
                blocked_at, blk = t, L.blockers(cur, new, pair)
                break
            cur, s = p2, s
            ss.append(round(s, 7))
            if k in (0, steps // 2, steps):
                frames[str(round(t, 3))] = ([[float(v) for v in p] for p in cur], s)
        ups = [ss[i + 1] - ss[i] for i in range(len(ss) - 1)]
        rec[mode] = {'s': ss, 's_end': ss[-1] if ss else None, 's_max': max(ss) if ss else None,
                     'blocked_at': blocked_at, 'blockers': blk,
                     'feasible_at_s0': bool(blocked_at is None and all(v <= s0 + 1e-7 for v in ss)),
                     'monotone': bool(all(u <= 1e-7 for u in ups)), 'max_uptick': round(max(ups), 7) if ups else 0.0,
                     'poses_end': [[float(v) for v in p] for p in cur] if blocked_at is None else None,
                     'frames': frames}
    return rec


def pair_extent(poses, s, wall, pair):
    fr = [G.to_frame(poses[i], wall, s) for i in pair]
    ys = [G.verts(p)[:, 1] for p in fr]
    return {'H': float(max(y.max() for y in ys) - min(y.min() for y in ys)),
            'chord_sum': float(sum(G.chord(p[2]) for p in fr)),
            'touching': int(sum(G.verts(p)[:, 0].min() <= 1e-6 for p in fr))}


def run_config(cfg, steps):
    rows = []
    for wall in G.WALLS:
        t0 = time.time()
        info, fr = wall_pair(cfg['poses'], cfg['s'], wall)
        row = {'rid': cfg['rid'], 'tag': cfg['tag'], 's0': cfg['s'], 'n': len(cfg['poses']), 'wall': wall,
               'pair_info': info, 'reduce_before': R.reduce_wall(cfg['poses'], cfg['s'], wall)}
        if info['pair'] is not None:
            pair = tuple(info['pair'])
            row['click'] = click(cfg['poses'], cfg['s'], pair, steps)
            row['extent_before'] = pair_extent(cfg['poses'], cfg['s'], wall, pair)
            for mode in ('local', 'global'):
                cm = row['click'][mode]
                if cm['poses_end'] is not None:
                    pe = [tuple(p) for p in cm['poses_end']]
                    cm['extent_end'] = pair_extent(pe, cm['s_end'], wall, pair)
                    cm['reduce_end'] = R.reduce_wall(pe, cm['s_end'], wall)
                    cm['check_end'] = G.check_packing(pe, cm['s_end'], tol=1e-7)
                cm.pop('poses_end', None)
        row['secs'] = round(time.time() - t0, 2)
        rows.append(row)
    return rows


def main():
    global TOUCH_TOL
    be_polite()
    ap = argparse.ArgumentParser()
    ap.add_argument('--which', default='a244,ring,crowd')
    ap.add_argument('--steps', type=int, default=20)
    ap.add_argument('--resume', action='store_true')
    ap.add_argument('--only', default=None)
    ap.add_argument('--tol', type=float, default=TOUCH_TOL)
    a = ap.parse_args()
    TOUCH_TOL = a.tol
    os.makedirs(RES, exist_ok=True)
    done = set()
    if a.resume and os.path.exists(OUT):
        for line in open(OUT, encoding='utf-8'):
            r = json.loads(line)
            done.add((r['rid'], r['wall']))
    cfgs = T.all_configs(tuple(a.which.split(',')))
    if a.only:
        cfgs = [c for c in cfgs if c['rid'] == a.only]
    with open(OUT, 'a', encoding='utf-8') as f:
        for k, cfg in enumerate(cfgs):
            if os.path.exists(STOP):
                print('STOP'); break
            if all((cfg['rid'], w) in done for w in G.WALLS):
                continue
            t0 = time.time()
            for row in run_config(cfg, steps=a.steps):
                if (row['rid'], row['wall']) in done:
                    continue
                f.write(json.dumps(row) + '\n'); f.flush()
            print('%3d/%d %-6s %-40s s0=%.5f  %.1fs' % (k + 1, len(cfgs), cfg['tag'], cfg['rid'], cfg['s'],
                                                        time.time() - t0), flush=True)


if __name__ == '__main__':
    main()
