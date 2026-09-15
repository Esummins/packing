"""A223 the CLICK: every tilted square rotates toward its nearest axis alignment ('+' -> 0, '-' -> 90, flat stay),
the grains of one handedness rotating together; at each tilt step the side is minimised over the centres at
FIXED tilts by the alternating LP (the separating-axis polyhedron P(S, theta) of Lemma GRAIN-LP; the selection S
re-chosen at the LP's solution until stable).  Three variants per witness:
  A 'click' : the witness's contact pairs keep their separating axis (the lean contact SLIDES on its edge),
              non-touching pairs re-selected; BLOCKED at the first step where P(S, theta) is empty;
  B 'free'  : every pair re-selected at every step (a fixed-tilt local minimum, warm-started);
  C 'core'  : as A on the loaded squares only (rattlers removed), the rattlers re-fitted flat at the end.
    python click223.py [--only RID] [--resume] [--steps 20]    -> results/click223.jsonl (one row per witness)
"""
import json
import math
import os
import subprocess
import sys
import time

import numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A222-ring-swap', 'code'))
import grains223 as GR        # noqa: E402
import geom217 as G           # noqa: E402
import region222 as RG        # noqa: E402

ATT = os.path.abspath(os.path.join(HERE, '..'))
REPO = os.path.abspath(os.path.join(ATT, '..', '..'))
OUT = os.path.join(ATT, 'results', 'click223.jsonl')
TOL = 1e-7
S_MAX = 9.0


def schedule(th0, t, sense=None):
    """tilts at click parameter t in [0, 1]; sense: dict diamond index -> +1 (to 0) / -1 (to 90)."""
    th = np.array(th0, float) % (math.pi / 2)
    out = th.copy()
    for i in range(len(th)):
        h = GR.handedness(th[i])
        if h == 'F':
            out[i] = 0.0 if th[i] < math.pi / 4 else math.pi / 2
        elif h == '+' or (h == 'D' and (sense or {}).get(i, 1) > 0):
            out[i] = th[i] * (1 - t)
        else:
            out[i] = math.pi / 2 - (math.pi / 2 - th[i]) * (1 - t)
    return out


def compose(c, th, s, idx):
    z = np.zeros(G.NV)
    for a, i in enumerate(idx):
        z[3 * i:3 * i + 3] = (c[2 * a], c[2 * a + 1], th[a])
    z[G.S_IDX] = s; return z


def wfun(n, th):
    return abs(n[0] * math.cos(th) + n[1] * math.sin(th)) + abs(-n[0] * math.sin(th) + n[1] * math.cos(th))


def lp(th, sel, idx, seed):
    """min s over centres at tilts th (per idx member) with selection sel {(a,b) local: (o,e)}; rows affine.
    Returns (c, s) or None if infeasible."""
    m = len(idx)
    nv = 2 * m + 1
    A, b = [], []
    for a in range(m):
        w = (abs(math.cos(th[a])) + abs(math.sin(th[a]))) / 2
        for k in range(2):
            r = np.zeros(nv); r[2 * a + k] = -1.0; A.append(r); b.append(-w)            # c >= w
            r = np.zeros(nv); r[2 * a + k] = 1.0; r[-1] = -1.0; A.append(r); b.append(-w)  # c - s <= -w
    for (a, bb), (o, e) in sel.items():
        p = bb if o == a else a
        n = G.NHAT[e]
        co, si = math.cos(th[o]), math.sin(th[o])
        n = np.array([co * n[0] - si * n[1], si * n[0] + co * n[1]])
        rhs = (1 + wfun(n, th[p])) / 2
        r = np.zeros(nv)
        r[2 * p:2 * p + 2] = -n
        r[2 * o:2 * o + 2] = n
        A.append(r); b.append(-rhs)                                                       # n.(c_p - c_o) >= rhs
    cost = np.zeros(nv); cost[-1] = 1.0
    res = linprog(cost, A_ub=np.array(A), b_ub=np.array(b), bounds=[(0, S_MAX)] * (nv - 1) + [(1, S_MAX)], method='highs')
    return (res.x[:-1], float(res.x[-1])) if res.success else None


def select(c, th, idx, fixed):
    """best separating axis per local pair at centres c, tilts th; pairs in `fixed` keep their axis."""
    z = compose(c, th, S_MAX, idx)
    tab = G.sat_table(z)
    sel, gaps = {}, {}
    m = len(idx)
    for a in range(m):
        for bb in range(a + 1, m):
            i, j = idx[a], idx[bb]
            t = tab[(i, j)]
            if (a, bb) in fixed:
                o, e = fixed[(a, bb)]
                oi = 0 if o == a else 1
                sel[(a, bb)] = (o, e)
                gaps[(a, bb)] = float(t[oi, e].min())
                continue
            mm = t.min(axis=2)
            oi, e = np.unravel_index(np.argmax(mm), mm.shape)
            sel[(a, bb)] = (a if oi == 0 else bb, int(e))
            gaps[(a, bb)] = float(mm[oi, e])
    return sel, gaps


def fixed_tilt_min(c0, th, idx, fixed, iters=8):
    """alternating LP: returns (c, s, sel, iterations) or (None, None, sel0, k) if P(S, theta) is empty."""
    c, best = np.array(c0, float), None
    sel, _ = select(c, th, idx, fixed)
    for k in range(iters):
        r = lp(th, sel, idx, c)
        if r is None:
            return (None, None, sel, k) if best is None else best + (k,)
        c, s = r
        if best is None or s < best[1] - 1e-10:
            best = (c, s, sel)
        sel2, _ = select(c, th, idx, fixed)
        if sel2 == sel:
            break
        sel = sel2
    return best + (k + 1,)


def blockers(c, th_prev, th_new, idx):
    """pairs whose gap turns negative when the tilts advance at the previous centres (attribution only)."""
    z = compose(c, th_new, S_MAX, idx)
    gaps = G.pair_gaps(z)
    out = []
    for (i, j), g in gaps.items():
        if i in idx and j in idx and g < -1e-9:
            out.append([int(i), int(j), round(float(g), 5)])
    return sorted(out, key=lambda x: x[2])[:6]


def path(z0, idx, contacts_fixed, steps, sense=None, keep_all=False):
    """the click on the squares idx; contacts_fixed: keep the t=0 axis of every touching pair (variant A/C)."""
    cx, cy, th0, s0 = G.unpack(z0)
    th_all = np.array(th0) % (math.pi / 2)
    c = np.array([v for i in idx for v in (cx[i], cy[i])])
    thl0 = th_all[idx]
    fixed = {}
    if contacts_fixed:
        sel0, gaps0 = select(c, thl0, idx, {})
        fixed = {pr: sel0[pr] for pr, g in gaps0.items() if g <= TOL}
    rec = {'t': [], 's': [], 'blocked_at': None, 'blockers': None, 'contacts_kept': [], 'frames': {}}
    sched = []
    for k in range(steps + 1):
        t = k / steps
        thl = schedule(th_all, t, sense)[idx]
        sched.append(thl)
        cc, s, sel, it = fixed_tilt_min(c, thl, idx, fixed)
        if cc is None:
            rec['blocked_at'] = t
            rec['blockers'] = blockers(c, sched[-2] if k else thl, thl, idx)
            break
        # which fixed contacts are still closed (gap <= 1e-6) at this step
        _, gaps = select(cc, thl, idx, fixed)
        kept = sum(1 for pr in fixed if gaps[pr] <= 1e-6)
        rec['contacts_kept'].append(kept)
        rec['t'].append(round(t, 4)); rec['s'].append(round(s, 7))
        c = cc
        if keep_all or k in (0, steps // 2, steps):
            rec['frames'][str(round(t, 4))] = [float(v) for v in compose(c, thl, s, idx)]
    rec['n_fixed_contacts'] = len(fixed)
    rec['s_end'] = rec['s'][-1] if rec['s'] else None
    rec['s_max'] = max(rec['s']) if rec['s'] else None
    ups = [rec['s'][k + 1] - rec['s'][k] for k in range(len(rec['s']) - 1)]
    rec['max_uptick'] = round(max(ups), 7) if ups else 0.0
    rec['monotone'] = bool(all(u <= 1e-7 for u in ups))
    rec['z_end'] = [float(v) for v in compose(c, sched[len(rec['s']) - 1], rec['s'][-1], idx)] if rec['s'] else None
    return rec


def refit(z_core, idx, rattlers):        # the removed rattlers placed flat into the clicked core's free space
    s = float(z_core[G.S_IDX])
    fixed = [tuple(float(v) for v in z_core[3 * i:3 * i + 3]) for i in idx]
    r = RG.place(fixed, s, len(rattlers), thetas=[0.0], restarts=8)
    return {'found': bool(r['found']), 'method': r.get('method'), 'k': len(rattlers)}


def run_witness(w, steps):
    t0 = time.time()
    g = GR.grains(w)
    z0 = np.array(w['z'], float)
    cx, cy, th, s = G.unpack(z0)
    allidx = list(range(G.N))
    dia = [i for i in allidx if g['hand'][i] == 'D']
    senses = [None] if not dia else [{i: +1 for i in dia}, {i: -1 for i in dia}]
    out = {'wid': w['wid'], 'rid': w['rid'], 'cls': w['cls'], 's0': float(s), 'hand': g['hand'],
           'grains': [(x['hand'], x['members']) for x in g['grains']], 'n_lean': g['n_lean'],
           'rattlers': g['rattlers'], 'diamonds': dia}
    best = None
    for sn in senses:
        A = path(z0, allidx, True, steps, sn)
        if best is None or (A['blocked_at'] is None and best[0]['blocked_at'] is not None) or \
           (A['blocked_at'] == best[0]['blocked_at'] and (A['s_max'] or 9) < (best[0]['s_max'] or 9)):
            best = (A, sn)
    out['A'], sense = best
    out['diamond_sense'] = sense
    out['B'] = path(z0, allidx, False, steps, sense)
    core = [i for i in allidx if i not in g['rattlers']]
    if g['rattlers'] and len(core) >= 2:
        C = path(z0, core, True, steps, sense)
        if C['blocked_at'] is None and C['z_end'] is not None:
            C['refit'] = refit(np.array(C['z_end']), core, g['rattlers'])
        out['C'] = C
    for k in ('B', 'C'):
        if k in out:
            out[k].pop('z_end', None)
            out[k].pop('frames', None)
    out['secs'] = round(time.time() - t0, 1)
    return out


def commit(path_, msg):
    try:
        subprocess.run(['git', 'add', path_], cwd=REPO, check=False)
        subprocess.run(['git', 'commit', '-q', '-m', msg + '\n\nCo-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>',
                        '--', path_], cwd=REPO, check=False, capture_output=True)
    except Exception as e:  # noqa: BLE001
        print('commit failed', e, flush=True)


def main():
    only = sys.argv[sys.argv.index('--only') + 1] if '--only' in sys.argv else None
    steps = int(sys.argv[sys.argv.index('--steps') + 1]) if '--steps' in sys.argv else 20
    done = set()
    if '--resume' in sys.argv and os.path.exists(OUT):
        done = {json.loads(l)['wid'] for l in open(OUT, encoding='utf-8')}
    n = 0
    for w in GR.four_crowds():
        if (only and w['rid'] != only) or w['wid'] in done:
            continue
        rec = run_witness(w, steps)
        with open(OUT, 'a', encoding='utf-8') as f:
            f.write(json.dumps(rec) + '\n')
        n += 1
        print(w['wid'], 'A:', rec['A']['s'][:1], '->', rec['A']['s_end'], 'blocked', rec['A']['blocked_at'],
              'mono', rec['A']['monotone'], '| B:', rec['B']['s_end'], rec['B']['monotone'], rec['secs'], 's', flush=True)
        if n % 10 == 0 or only:
            commit(os.path.relpath(OUT, REPO).replace('\\', '/'), 'A223 click: %s' % w['wid'])
    commit(os.path.relpath(OUT, REPO).replace('\\', '/'), 'A223 click: final rows')


if __name__ == '__main__':
    main()
