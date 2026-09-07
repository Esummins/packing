r"""lock103.py -- A103: the first-order LOCK test (Lemma ROT + Corollary 2 of NOCRIT-SEL, single-square
form) on every strictly K0-BLOCKED packing on disk plus Trump.

For every intruder Q of every corner c (depth d_c(Q) > MEET_TOL) the question is whether there is a
rigid motion y = (v_x, v_y, w) of Q ALONE that STRICTLY opens every active contact row of Q (squares at
SAT gap < CONTACT_TOL, walls at distance < CONTACT_TOL) and STRICTLY decreases d_c(Q) at first order.
If such a y exists the packing is not Psi-minimal at its side (Lemma ROT of docs/proofs/noroom.md:
z + eps*y is a packing at the same side with smaller Psi).  Gordan's alternative: no such y exists iff
the virtual corner row(s) of Q together with its contact rows admit a non-trivial non-negative
self-stress -- Q is HELD.

Depth derivative (Lemma ROT-GRAD): mu_c(Q) = min_{p in Q} max(p_x, p_y); its right-derivative along y is
    min over the extreme points p of the argmin set S_c(Q) of  D_p(y),
    D_p(y) = pdot_x (p_x > p_y),  pdot_y (p_y > p_x),  max(pdot_x, pdot_y) (p on the diagonal),
    pdot = v + w * J (p - c),  J = rotation by +90 deg.
Depth decreases iff the derivative of mu is > 0, i.e. D_p(y) > 0 for EVERY extreme point p; a diagonal
point contributes a disjunction, so the test enumerates the 2^(#diagonal points) branches, each an LP
    max t  s.t.  a_k . y >= t (contact rows),  grad_p . y >= t (chosen branch per extreme point),
                 |y|_inf <= 1,
and Q is UNHELD iff some branch has t* > TSTRICT, confirmed by a finite motion (eps = 1e-6): the moved
square is interior-disjoint from everything (tol 1e-11) and the depth really drops.

Pure geometry, one process, BLAS pinned; ~1 minute for the corpus.  Writes only under
attempts/A103-noroom/{results,logs}.  Usage: python lock103.py [all|<name>|trump]
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import itertools
import json
import math
import time
from decimal import Decimal
from fractions import Fraction

import numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
A103 = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(A103))
ATT = os.path.join(ROOT, 'attempts')
A87R = os.path.join(ATT, 'A87-drain-flow', 'results')
RES = os.path.join(A103, 'results')
LOGS = os.path.join(A103, 'logs')
os.makedirs(RES, exist_ok=True)
os.makedirs(LOGS, exist_ok=True)

CONTACT_TOL = 1e-7       # A102's contact bar
MEET_TOL = 1e-9          # A102's exact meet bar (any intrusion counts)
ARG_TOL = 1e-9           # a candidate point attains the argmin if within this of mu
DIAG_TOL = 1e-9
TSTRICT = 1e-7           # LP strictness needed to call a direction strictly opening
EPS_MOVE = 1e-6          # finite-motion confirmation step
CORNERS = ('BL', 'BR', 'TR', 'TL')
FSGN = {'BL': (1.0, 1.0), 'BR': (-1.0, 1.0), 'TR': (-1.0, -1.0), 'TL': (1.0, -1.0)}

T0 = time.time()
_fh = open(os.path.join(LOGS, 'lock103.log'), 'a', encoding='utf-8')


def log(*a):
    m = ' '.join(str(v) for v in a)
    print(m, flush=True)
    _fh.write('[%7.1f] %s\n' % (time.time() - T0, m))
    _fh.flush()


# ============================================================ geometry (A102 conventions)

def verts(cx, cy, th):
    c, s_ = math.cos(th), math.sin(th)
    return [(cx + 0.5 * (dx * c - dy * s_), cy + 0.5 * (dx * s_ + dy * c))
            for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def sep(p, q):
    best = -9.0
    for poly_ in (p, q):
        for i in range(4):
            a, b = poly_[i], poly_[(i + 1) % 4]
            ex, ey = b[0] - a[0], b[1] - a[1]
            n = math.hypot(ex, ey)
            ax, ay = -ey / n, ex / n
            pp = [x * ax + y * ay for x, y in p]
            qq = [x * ax + y * ay for x, y in q]
            v = max(min(qq) - max(pp), min(pp) - max(qq))
            if v > best:
                best = v
    return best


def wall_gap(p, s):
    return min(min(x for x, y in p), min(y for x, y in p),
               s - max(x for x, y in p), s - max(y for x, y in p))


def worst_gap_one(poses, i, newpose, s):
    p = verts(*newpose)
    worst = wall_gap(p, s)
    for j, q in enumerate(poses):
        if j == i:
            continue
        g = sep(p, verts(*q))
        if g < worst:
            worst = g
    return worst


def frame_map(cn, s):
    """Corner frame: container point -> corner-frame point (corner at the origin, container in the
    positive quadrant); the map is an isometry of the form p -> (sx*(px-ox), sy*(py-oy))."""
    ox, oy = (0.0, 0.0) if cn == 'BL' else (s, 0.0) if cn == 'BR' else \
        (s, s) if cn == 'TR' else (0.0, s)
    sx, sy = FSGN[cn]
    return lambda p: (sx * (p[0] - ox), sy * (p[1] - oy)), (sx, sy)


def argmin_data(sq, cn, s):
    """mu_c(Q), depth, and the extreme points of the argmin set S_c(Q), in the CORNER frame."""
    fm, _ = frame_map(cn, s)
    W = [fm(v) for v in verts(*sq)]
    cand = list(W)
    for k in range(4):
        a, b = W[k], W[(k + 1) % 4]
        d = (b[0] - a[0]) - (b[1] - a[1])
        if abs(d) > 1e-14:
            t = (a[1] - a[0]) / d
            if -1e-12 <= t <= 1 + 1e-12:
                t = min(1.0, max(0.0, t))
                cand.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
    vals = [max(p[0], p[1]) for p in cand]
    mu = min(vals)
    ext = []
    for p, v in zip(cand, vals):
        if v <= mu + ARG_TOL and not any(abs(p[0] - q[0]) < 1e-9 and abs(p[1] - q[1]) < 1e-9
                                         for q in ext):
            ext.append(p)
    return mu, max(0.0, 1.0 - mu), ext, W


def corner_depth(sq, cn, s):
    return argmin_data(sq, cn, s)[1]


def meeters(poses, s, cn, tol=MEET_TOL):
    out = [(i, corner_depth(q, cn, s)) for i, q in enumerate(poses)]
    return sorted([(i, d) for i, d in out if d > tol], key=lambda t: -t[1])


# ============================================================ contacts (A102's contacts_of)

def _edge_normal_out(a, b, owner_centre):
    ex, ey = b[0] - a[0], b[1] - a[1]
    n = math.hypot(ex, ey)
    nx, ny = -ey / n, ex / n
    mx, my = (a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0
    if (mx - owner_centre[0]) * nx + (my - owner_centre[1]) * ny < 0:
        nx, ny = -nx, -ny
    return nx, ny


def contacts_of(poses, i, s, tol=CONTACT_TOL):
    P = poses[i]
    A = verts(*P)
    out = []
    for j, q in enumerate(poses):
        if j == i:
            continue
        B = verts(*q)
        if sep(A, B) >= tol:
            continue
        pairs = []
        for (V, E, own, sign) in ((A, B, q, +1.0), (B, A, P, -1.0)):
            for v in V:
                for k in range(4):
                    a, b = E[k], E[(k + 1) % 4]
                    ex, ey = b[0] - a[0], b[1] - a[1]
                    L = ex * ex + ey * ey
                    t = max(0.0, min(1.0, ((v[0] - a[0]) * ex + (v[1] - a[1]) * ey) / L))
                    fx, fy = a[0] + t * ex, a[1] + t * ey
                    d = math.hypot(v[0] - fx, v[1] - fy)
                    if d < tol:
                        nx, ny = _edge_normal_out(a, b, (own[0], own[1]))
                        pairs.append(((v[0] + fx) / 2.0, (v[1] + fy) / 2.0,
                                      sign * nx, sign * ny, d))
        for (px, py, fx, fy, d) in pairs:
            dup = False
            for c in out:
                if (abs(c['point'][0] - px) < 1e-6 and abs(c['point'][1] - py) < 1e-6
                        and c['F'][0] * fx + c['F'][1] * fy > 1.0 - 1e-6):
                    dup = True
                    break
            if not dup:
                out.append({'with': 'square %d' % j, 'j': j, 'point': (px, py),
                            'F': (fx, fy), 'dist': d, 'gap': sep(A, B)})
    walls = (('left wall', min(x for x, y in A), (1.0, 0.0), lambda v: v[0] - 0.0),
             ('bottom wall', min(y for x, y in A), (0.0, 1.0), lambda v: v[1] - 0.0),
             ('right wall', s - max(x for x, y in A), (-1.0, 0.0), lambda v: s - v[0]),
             ('top wall', s - max(y for x, y in A), (0.0, -1.0), lambda v: s - v[1]))
    for name, gap, nrm, dfn in walls:
        if gap < tol:
            for v in A:
                if dfn(v) < tol:
                    out.append({'with': name, 'j': None, 'point': (v[0], v[1]),
                                'F': nrm, 'dist': dfn(v), 'gap': gap})
    return out


# ============================================================ the lock test

def virtual_rows(sq, cn, s):
    """The virtual corner rows of Q: for each extreme point p of S_c(Q) (corner frame) the row(s)
    grad(mu) in CONTAINER (v_x, v_y, w) coordinates: a list of (p_container, [rows]) with one row
    off the diagonal and two rows (the disjunction) on it."""
    mu, d, ext, _ = argmin_data(sq, cn, s)
    fm, (sx, sy) = frame_map(cn, s)
    cx, cy = sq[0], sq[1]
    c_f = fm((cx, cy))
    out = []
    for p in ext:
        rx, ry = p[0] - c_f[0], p[1] - c_f[1]       # corner-frame offset of p from the centre
        # velocity of p in the corner frame under (v, w) given in container coordinates:
        # container velocity of p = v + w J (p - c); the frame map has linear part diag(sx, sy),
        # so pdot_f = (sx v_x, sy v_y) + w * (sx * (-(ry_c)), sy * (rx_c)) with (rx_c, ry_c) the
        # container offset = (sx rx, sy ry).  Hence pdot_f = (sx v_x - w sx sy ry, sy v_y + w sy sx rx).
        gx = (sx, 0.0, -sx * sy * ry)      # d/d(v,w) of pdot_f,x
        gy = (0.0, sy, sx * sy * rx)       # d/d(v,w) of pdot_f,y
        if abs(p[0] - p[1]) < DIAG_TOL:
            rows = [gx, gy]
            kind = 'diagonal'
        elif p[0] > p[1]:
            rows = [gx]
            kind = 'X'
        else:
            rows = [gy]
            kind = 'Y'
        out.append({'p_frame': p, 'kind': kind, 'rows': rows})
    return mu, d, out


def lp_strict(A_rows, G_rows):
    """max t s.t. a.y >= t for contact rows, g.y >= t for the chosen virtual rows, |y|<=1."""
    rows = list(A_rows) + list(G_rows)
    if not rows:
        return 1.0, np.zeros(3)
    # variables (y0, y1, y2, t); minimise -t
    A_ub = []
    b_ub = []
    for r in rows:
        A_ub.append([-r[0], -r[1], -r[2], 1.0])     # t - r.y <= 0
        b_ub.append(0.0)
    res = linprog(c=[0, 0, 0, -1.0], A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                  bounds=[(-1, 1), (-1, 1), (-1, 1), (None, 1.0)], method='highs')
    if res.status != 0:
        return -1.0, np.zeros(3)
    return float(-res.fun), np.array(res.x[:3])


def test_intruder(poses, s, cn, i):
    P = poses[i]
    C = contacts_of(poses, i, s)
    A_rows = []
    for c in C:
        rx, ry = c['point'][0] - P[0], c['point'][1] - P[1]
        A_rows.append((c['F'][0], c['F'][1], rx * c['F'][1] - ry * c['F'][0]))
    mu, d, vr = virtual_rows(P, cn, s)
    rec = {'square': i, 'corner': cn, 'depth': d, 'tilt_deg': math.degrees(P[2]) % 90.0,
           'n_contacts': len(C),
           'contacts': [{'with': c['with'], 'point': [round(v, 9) for v in c['point']],
                         'F': [round(v, 9) for v in c['F']],
                         'torque': round(A_rows[k][2], 9)} for k, c in enumerate(C)],
           'argmin_kind': [v['kind'] for v in vr],
           'argmin_points_frame': [[round(v, 9) for v in x['p_frame']] for x in vr]}
    # branches
    choices = [x['rows'] for x in vr]
    best = None
    for combo in itertools.product(*[range(len(ch)) for ch in choices]):
        G = [choices[k][j] for k, j in enumerate(combo)]
        t, y = lp_strict(A_rows, G)
        if best is None or t > best[0]:
            best = (t, y, combo)
    t, y, combo = best
    rec['lp_t'] = float(t)
    rec['lp_dir'] = [float(v) for v in y]
    unheld = t > TSTRICT
    conf = None
    # smallest INACTIVE gap (pairs and walls at gap >= CONTACT_TOL): a strictly opening first-order
    # motion is feasible for travel below this / (max rate 2.5)
    A = verts(*P)
    gmin = 9.0
    for j, q in enumerate(poses):
        if j == i:
            continue
        g = sep(A, verts(*q))
        if g >= CONTACT_TOL and g < gmin:
            gmin = g
    for g in (min(x for x, y in A), min(y for x, y in A), s - max(x for x, y in A),
              s - max(y for x, y in A)):
        if g >= CONTACT_TOL and g < gmin:
            gmin = g
    rec['min_inactive_gap'] = float('%.3e' % gmin)
    if unheld:
        eps = min(EPS_MOVE, gmin / 10.0)
        newpose = (P[0] + eps * y[0], P[1] + eps * y[1], P[2] + eps * y[2])
        wg = worst_gap_one(poses, i, newpose, s)
        d1 = corner_depth(newpose, cn, s)
        expected = min(d, 0.5 * t * eps)
        conf = {'eps': eps, 'worst_gap_after': float('%.3e' % wg), 'depth_after': d1,
                'depth_drop': d - d1, 'expected_drop_ge': expected}
        ok = wg >= -1e-12 and (d - d1) >= 0.99 * expected
        conf['confirmed'] = bool(ok)
        if not ok:
            unheld = False
            rec['note'] = 'LP direction not confirmed by finite motion (nonsmooth/degenerate)'
        else:
            # ROOM: travel along y until the first collision (geometric growth + 50 bisections)
            lo, hi = 0.0, eps
            while hi < 2.0:
                newpose = (P[0] + hi * y[0], P[1] + hi * y[1], P[2] + hi * y[2])
                if worst_gap_one(poses, i, newpose, s) < -1e-11:
                    break
                lo, hi = hi, hi * 2.0
            if hi >= 2.0:
                lo = hi
            else:
                for _ in range(50):
                    mid = 0.5 * (lo + hi)
                    newpose = (P[0] + mid * y[0], P[1] + mid * y[1], P[2] + mid * y[2])
                    if worst_gap_one(poses, i, newpose, s) < -1e-11:
                        hi = mid
                    else:
                        lo = mid
            endpose = (P[0] + lo * y[0], P[1] + lo * y[1], P[2] + lo * y[2])
            dend = corner_depth(endpose, cn, s)
            conf['travel_max'] = lo
            conf['depth_at_travel_max'] = dend
            conf['exits_cell'] = bool(dend <= MEET_TOL)
            conf['retraction_fraction'] = float((d - dend) / d) if d > 0 else None
    rec['confirm'] = conf
    rec['held'] = not unheld
    # sub-tests for the PI's torque rule: pure rotation only, pure translation only
    sub = {}
    for name, mask in (('rotation', (0, 0, 1)), ('translation', (1, 1, 0))):
        bestm = -1.0
        for combo in itertools.product(*[range(len(ch)) for ch in choices]):
            G = [choices[k][j] for k, j in enumerate(combo)]
            rows = [tuple(r[k] * mask[k] for k in range(3)) for r in A_rows]
            Gm = [tuple(g[k] * mask[k] for k in range(3)) for g in G]
            tm, ym = lp_strict(rows, Gm)
            # the masked LP allows y outside the mask too but those coordinates are multiplied by 0
            bestm = max(bestm, tm)
        sub[name] = float(bestm)
    rec['sub_t'] = sub
    rec['free_by'] = ('rotation' if sub['rotation'] > TSTRICT else
                      'translation' if sub['translation'] > TSTRICT else
                      'screw' if unheld else None)
    return rec


def test_packing(name, poses, s):
    rows = []
    for cn in CORNERS:
        M = meeters(poses, s, cn)
        for (i, d) in M:
            r = test_intruder(poses, s, cn, i)
            r['is_second_meeter'] = bool((i, d) == min(M, key=lambda t: t[1]))
            r['n_meeters'] = len(M)
            rows.append(r)
    held = [r for r in rows if r['held']]
    unheld = [r for r in rows if not r['held']]
    out = {'packing': name, 'side': s, 'n_intruders': len(rows), 'n_held': len(held),
           'n_unheld': len(unheld),
           'meet_counts': {cn: len(meeters(poses, s, cn)) for cn in CORNERS},
           'K0_BLOCKED': all(len(meeters(poses, s, cn)) >= 2 for cn in CORNERS),
           'all_held': not unheld,
           'unheld': [{'corner': r['corner'], 'square': r['square'], 'depth': r['depth'],
                       'second': r['is_second_meeter'], 'lp_t': r['lp_t'], 'free_by': r['free_by'],
                       'tilt_deg': round(r['tilt_deg'], 4)} for r in unheld],
           'rows': rows}
    return out


# ============================================================ corpus (A102's loader, verbatim)

def load_corpus():
    C = []
    d = json.load(open(os.path.join(A87R, 'k0dir2_87.records.json')))
    for k, v in sorted(d['floors'].items()):
        if not v.get('poses'):
            continue
        s = float(Fraction(v['container_side_exact']))
        P = [(float(Fraction(p['cx_exact'])), float(Fraction(p['cy_exact'])),
              float(Fraction(p['theta_exact']))) for p in v['poses']]
        C.append({'name': 'floor_%s_%s' % (k, v['tag']), 'side': s, 'poses': P})
    dd = json.load(open(os.path.join(A87R, 'k0dir87.json')))
    rec = dd['record_K0_BLOCKED_packing']
    z = [Fraction(a) for a in rec['z']]
    C.append({'name': 'record_%s' % rec['tag'], 'side': float(z[33]),
              'poses': [(float(z[3 * i]), float(z[3 * i + 1]), float(z[3 * i + 2]))
                        for i in range(11)]})
    for i, line in enumerate(open(os.path.join(A87R, 'k0dir87.polish.jsonl'))):
        r = json.loads(line)
        if not r.get('exact_K0_BLOCKED') or not r.get('z_polished'):
            continue
        z = [Fraction(a) for a in r['z_polished']]
        C.append({'name': 'polish%02d_%s' % (i, r['tag']), 'side': float(z[33]),
                  'poses': [(float(z[3 * j]), float(z[3 * j + 1]), float(z[3 * j + 2]))
                            for j in range(11)]})
    df = json.load(open(os.path.join(A87R, 'd2front87.json')))
    src_list = [('own_side_anchored', df['own_side_anchored'])]
    src_list += [('cap' + k, v) for k, v in sorted(df['per_cap_anchored'].items())]
    seen = set()
    n = 0
    for src, v in src_list:
        if not v.get('anchored_only'):
            continue
        for c in v.get('candidates', []):
            key = tuple(c['z'])
            if key in seen:
                continue
            seen.add(key)
            z = [Fraction(a) for a in c['z']]
            C.append({'name': 'anchored%d_%s' % (n, c['tag']), 'side': float(z[33]),
                      'poses': [(float(z[3 * j]), float(z[3 * j + 1]),
                                 float(z[3 * j + 2])) for j in range(11)]})
            n += 1
    t = json.load(open(os.path.join(ATT, 'A03-upper-reconstruct', 'trump11_exact.json')))
    C.append({'name': 'TRUMP_canary',
              'side': float(Fraction(Decimal(t['s']))),
              'poses': [(float(Fraction(Decimal(q['cx']))), float(Fraction(Decimal(q['cy']))),
                         float(Fraction(Decimal(q['theta'])))) for q in t['squares']]})
    return C


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    C = load_corpus()
    if which == 'trump':
        C = [c for c in C if c['name'] == 'TRUMP_canary']
    elif which != 'all':
        C = [c for c in C if c['name'] == which]
    outs = []
    jl = open(os.path.join(RES, 'lock103.jsonl'), 'w', encoding='utf-8')
    for c in C:
        t0 = time.time()
        o = test_packing(c['name'], c['poses'], c['side'])
        outs.append(o)
        jl.write(json.dumps(o) + '\n')
        jl.flush()
        log('%-28s side %.7f  blocked %s  intruders %d  held %d  unheld %d  [%.1fs]' % (
            c['name'], c['side'], o['K0_BLOCKED'], o['n_intruders'], o['n_held'], o['n_unheld'],
            time.time() - t0))
        for u in o['unheld']:
            log('    UNHELD %s sq%d depth %.3e second=%s lp_t %.3e free_by %s tilt %.4f' % (
                u['corner'], u['square'], u['depth'], u['second'], u['lp_t'], u['free_by'],
                u['tilt_deg']))
    summ = {
        'meet_bar': MEET_TOL, 'contact_bar': CONTACT_TOL, 'lp_strict': TSTRICT,
        'packings': len(outs),
        'blocked_all_held': [o['packing'] for o in outs if o['K0_BLOCKED'] and o['all_held']],
        'blocked_with_unheld': [o['packing'] for o in outs if o['K0_BLOCKED'] and not o['all_held']],
        'per_packing': [{'packing': o['packing'], 'side': o['side'], 'K0_BLOCKED': o['K0_BLOCKED'],
                         'n_intruders': o['n_intruders'], 'n_unheld': o['n_unheld'],
                         'unheld_second_meeters': sum(1 for u in o['unheld'] if u['second']),
                         'unheld_first_meeters': sum(1 for u in o['unheld'] if not u['second']),
                         'unheld': o['unheld']} for o in outs],
        'free_by_census': {},
        'trump': next((o for o in outs if o['packing'] == 'TRUMP_canary'), None) and {
            'n_intruders': [o for o in outs if o['packing'] == 'TRUMP_canary'][0]['n_intruders'],
            'all_held': [o for o in outs if o['packing'] == 'TRUMP_canary'][0]['all_held']},
    }
    for o in outs:
        for u in o['unheld']:
            k = u['free_by'] or 'none'
            summ['free_by_census'][k] = summ['free_by_census'].get(k, 0) + 1
    json.dump(summ, open(os.path.join(RES, 'lock103.json'), 'w', encoding='utf-8'), indent=1)
    log('summary:', json.dumps({k: v for k, v in summ.items() if k != 'per_packing'}))


if __name__ == '__main__':
    main()
