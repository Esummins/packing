"""A234 -- witnesses and their Fritz-John stress, n-general.  Every witness becomes a dict (name, cls, n, z, rows, A,
lam, meeters) with z = (cx, cy, theta) * n + (s,), rows the active rows (wall / edge / tiltbound / crowd, A217's
conventions), A the row-gradient matrix (m, 3n+1) and lam a bounded feasible FJ multiplier (lam0 = 1) or None.
n = 11 witnesses go through A219's rows219 (external rows kept); other n through the n-general model below (walls +
pair rows on every tied axis).  Row k's force on square i is lam_k A[k, 3i:3i+2], its torque about c_i lam_k A[k, 3i+2].
"""
import json
import math
import os
import sys

import numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
for a in ('A219-wall-torque', 'A217-torque-probe'):
    sys.path.insert(0, os.path.join(HERE, '..', '..', a, 'code'))
import geom217 as G           # noqa: E402
import rows219 as R           # noqa: E402
import collect217 as K        # noqa: E402

ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
WIT = os.path.join(ROOT, 'attempts', 'A217-torque-probe', 'results', 'witnesses217.jsonl')
TRUMP = os.path.join(ROOT, 'certs', 'trump11_certificate_tight.json')
S07 = os.path.join(ROOT, 'attempts', 'A108-s07-certify', 'results', 'exact.json')
S02 = os.path.join(ROOT, 'attempts', 'A110-grain-flood', 'results', 'sweep_S02.json')
SURVEY = os.path.join(ROOT, 'attempts', 'A226-one-flush', 'results', 'survey226.jsonl')
WALLS = ('x=0', 'y=0', 'x=s', 'y=s')
HALF = np.array([(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)])
NHAT = np.array([(0.0, -1.0), (1.0, 0.0), (0.0, 1.0), (-1.0, 0.0)])
LP_CAP = 1e4


def set_priority():
    try:
        import ctypes
        k = ctypes.windll.kernel32
        h = ctypes.c_void_p(-1)
        k.SetPriorityClass(h, 0x4000)
        k.SetProcessAffinityMask(h, ctypes.c_size_t(0xFFFF))
    except Exception:
        pass


# ---------------------------------------------------------------- n-general geometry
def unpack(z):
    n = (len(z) - 1) // 3
    c = np.asarray(z, float)[:3 * n].reshape(n, 3)
    return c[:, 0], c[:, 1], c[:, 2], float(z[-1]), n


def verts(z):
    cx, cy, th, s, n = unpack(z)
    co, si = np.cos(th)[:, None], np.sin(th)[:, None]
    return np.stack([cx[:, None] + co * HALF[None, :, 0] - si * HALF[None, :, 1],
                     cy[:, None] + si * HALF[None, :, 0] + co * HALF[None, :, 1]], -1)


def normals(z):
    cx, cy, th, s, n = unpack(z)
    co, si = np.cos(th)[:, None], np.sin(th)[:, None]
    return np.stack([co * NHAT[None, :, 0] - si * NHAT[None, :, 1], si * NHAT[None, :, 0] + co * NHAT[None, :, 1]], -1)


def jrot(v):
    return np.array([-v[1], v[0]])


def row_grad(z, r):
    """gradient (3n+1,) of one wall / edge row (A219's formulas, n-general)."""
    cx, cy, th, s, n = unpack(z)
    q, c = verts(z), np.stack([cx, cy], -1)
    g = np.zeros(3 * n + 1)
    if r['kind'] == 'wall':
        i, k = r['i'], r['corner']
        d = jrot(q[i, k] - c[i])
        a = 0 if r['wall'] in ('x=0', 'x=s') else 1
        far = r['wall'] in ('x=s', 'y=s')
        sg = -1.0 if far else 1.0
        g[3 * i + a] = sg
        g[3 * i + 2] = sg * d[a]
        if far:
            g[-1] = 1.0
        return g
    p, k, o, e = r['i'], r['corner'], r['j'], r['edge']
    nn = normals(z)[o, e]
    rr = q[p, k] - c[o]
    g[3 * p:3 * p + 2] = nn
    g[3 * p + 2] = nn @ jrot(q[p, k] - c[p])
    g[3 * o:3 * o + 2] = -nn
    g[3 * o + 2] = jrot(nn) @ rr
    return g


def active_rows_general(z, tol=1e-6):
    cx, cy, th, s, n = unpack(z)
    q, nrm, c = verts(z), normals(z), np.stack([cx, cy], -1)
    rows = []
    for i in range(n):
        for k in range(4):
            for w, val in enumerate((q[i, k, 0], q[i, k, 1], s - q[i, k, 0], s - q[i, k, 1])):
                if abs(val) <= tol:
                    rows.append({'kind': 'wall', 'i': i, 'corner': k, 'wall': WALLS[w]})
    for i in range(n):
        for j in range(i + 1, n):
            if np.abs(c[i] - c[j]).max() > math.sqrt(2) + tol:
                continue
            best, proj = -1e9, {}
            for o, p in ((i, j), (j, i)):
                for e in range(4):
                    pr = (q[p] - c[o]) @ nrm[o, e] - 0.5
                    proj[(o, e, p)] = pr
                    best = max(best, pr.min())
            if abs(best) > tol:
                continue
            for (o, e, p), pr in proj.items():
                if abs(pr.min()) <= tol:
                    for k in range(4):
                        if abs(pr[k]) <= tol:
                            rows.append({'kind': 'edge', 'i': p, 'corner': k, 'j': o, 'edge': e, 'on_segment': True})
    return rows


def e_s(nv):
    e = np.zeros(nv)
    e[-1] = 1.0
    return e


EPS = 1e-6          # slack on the stationarity equation: coordinates of the exact/record packings are 1e-8 accurate


def _lp(A, cost):
    """min cost . lam over {lam >= 0, |A^T lam - e_s|_inf <= EPS, lam <= cap}; the slack absorbs the 1e-8 coordinate
    noise of the exact and record packings (their NNLS residual is ~1e-9, HiGHS refuses the exact equality)."""
    m, nv = A.shape
    Aeq = np.hstack([A.T, np.eye(nv)])
    bounds = [(0, LP_CAP)] * m + [(-EPS, EPS)] * nv
    r = linprog(np.concatenate([cost, np.zeros(nv)]), A_eq=Aeq, b_eq=e_s(nv), bounds=bounds, method='highs')
    return (np.asarray(r.x)[:m], float(r.fun)) if r.success else (None, None)


def feasible(A):
    """bounded (L1-minimal) lam >= 0 with A^T lam = e_s up to EPS, else None."""
    if A.shape[0] == 0:
        return None
    return _lp(A, np.ones(A.shape[0]))[0]


def lp_range(A, cvec):
    """[min, max] of cvec . lam over the multiplier polytope (EPS slack); None if infeasible."""
    out = []
    for sg in (1.0, -1.0):
        x, v = _lp(A, sg * cvec)
        if x is None:
            return None
        out.append(sg * v)
    return out


# ---------------------------------------------------------------- witnesses
def meeters_general(z, size=1.0, tol=1e-9):
    cx, cy, th, s, n = unpack(z)
    q, nrm = verts(z), normals(z)
    out = {}
    for cn in G.CORNER_NAMES:
        M, t, _ = G.corner_frame(cn, s)
        box = np.array([(0, 0), (size, 0), (size, size), (0, size)], float)
        lst = []
        for i in range(n):
            qf, nf = q[i] @ M.T + t, nrm[i] @ M.T
            cf = M @ np.array([cx[i], cy[i]]) + t
            if qf[:, 0].max() <= tol or qf[:, 0].min() >= size - tol or qf[:, 1].max() <= tol or qf[:, 1].min() >= size - tol:
                continue
            if any((nf[e] @ (box - cf).T).min() >= 0.5 - tol for e in range(4)):
                continue
            lst.append(i)
        out[cn] = lst
    return out


def build(name, cls, z, rows=None, A=None, tol=1e-6, meeters=None):
    z = np.asarray(z, float)
    n = (len(z) - 1) // 3
    if rows is None:
        rows = active_rows_general(z, tol)
        A = np.array([row_grad(z, r) for r in rows]) if rows else np.zeros((0, 3 * n + 1))
    if meeters is None:
        meeters = meeters_general(z)
    return {'name': name, 'cls': cls, 'n': n, 'z': z, 'rows': rows, 'A': A, 'lam': feasible(A), 'meeters': meeters}


def from_w217(w, tol=1e-7):
    rows, z = R.witness_rows(w, tol)
    _, A, _ = R.system(z, rows)
    return build(w['wid'], w['cls'], z, rows, A, meeters=w['meeters'])


def w11(name, cls, z, tol=1e-6):
    z = G.wrap_theta(np.asarray(z, float))
    w = {'wid': name, 'cls': cls, 'z': z.tolist(), 'tmin_deg': None, 'crowd_delta': None,
         'meeters': {cn: G.corner_meeters(z, cn) for cn in G.CORNER_NAMES}}
    return from_w217(w, tol)


def a217_witnesses():
    return [from_w217(json.loads(l)) for l in open(WIT, encoding='utf-8')]


def genuine_fj():
    """A217's deduplicated free FJ points (SETTLED / K0FREE / BOXK0: no external row active)."""
    K.RES = os.path.dirname(WIT)
    out = []
    for r in K.load_witnesses():
        if r['cls'] in ('SETTLED', 'K0FREE', 'BOXK0'):
            r['wid'] = 'fj_' + r['rid'].replace('|', '_')
            out.append(from_w217(r))
    return out


def trump():
    from fractions import Fraction as F
    d = json.load(open(TRUMP, encoding='utf-8'))
    z = []
    for q in d['squares']:
        z += [float(F(q['cx'])), float(F(q['cy'])), 2 * math.atan(float(F(q['t'])))]
    return w11('trump', 'TRUMP', z + [float(F(d['side']))])


def s07():
    d = json.load(open(S07, encoding='utf-8'))
    z = [v for q in d['configuration'] for v in (q['cx_float'], q['cy_float'], math.radians(q['tilt_deg']))]
    return w11('s07', 'S07', z + [d['s_exact']['float']])


def s02():
    d = json.load(open(S02, encoding='utf-8'))['polish']
    return w11('s02', 'S02', [v for p in d['cfg'] for v in p] + [d['s']])


def survey():
    out = []
    for l in open(SURVEY, encoding='utf-8'):
        w = json.loads(l)
        if w['label'] == 'trump_cert':
            continue
        z = np.array([v for p in w['squares'] for v in p] + [w['side']], float)
        for i in range(w['n']):
            z[3 * i + 2] = z[3 * i + 2] % (math.pi / 2)
        out.append(w11(w['label'], 'RECORD', z) if w['n'] == 11 else build(w['label'], 'RECORD', z, tol=1e-6))
    return out
