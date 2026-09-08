"""A89 / T2 shared library: corner-blocker census at a configuration.

Definitions (BRIEF T2, verbatim where stated):

  * configuration z = 34 floats/Fractions, layout (x_i, y_i, theta_i) for
    i = 0..10 at indices 3i, 3i+1, 3i+2, and z[33] = s.  theta in RADIANS.
    (Layout confirmed by reading A87 code/t3lib.py wall_row/sep_row/dom_row and
    fjpolish87.zsplit; squares are UNIT, half-extent 1/2.)
  * sigma := enclosing side = max(extent_x, extent_y) over all 44 corners.
    origin := (min corner x, min corner y).  container = [origin, origin+sigma]^2.
  * corner boxes B_c = closed unit boxes at the 4 container corners.
    "Q meets B_c"  iff  int(Q) cap int(B_c) != empty, decided by SAT on the 4
    candidate axes (2 box axes + 2 square edge normals); penetration depth
    margin = -(SAT gap).  meets iff margin > MEET_TOL.
  * tilt(Q) := dist(theta_deg, 90 Z) in [0,45].
  * FJ polytope (BRIEF): P = {lam_0 >= 0, lam >= 0, lam_0 + sum lam = 1,
    lam_0 * grad s = sum_k lam_k * grad g_k}.  row r FORCED iff min_P lam_r >
    LP_TOL, LOADABLE iff max_P lam_r > LP_TOL, LP_TOL = 1e-7 (A46 convention).
    The A46 lambda_0 = 1 form (A^T lam = e_s, 0 <= lam <= 1e6) is reported too.
"""
from __future__ import annotations

import os
for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ.setdefault(_v, '1')

import ctypes
import math
import sys
from fractions import Fraction

import numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
A89 = os.path.abspath(os.path.join(HERE, '..'))
ATT = os.path.abspath(os.path.join(A89, '..'))
REPO = os.path.abspath(os.path.join(ATT, '..'))
RESULTS = os.path.join(A89, 'results')
NOTES = os.path.join(A89, 'notes')
LOGS = os.path.join(A89, 'logs')
for _d in (RESULTS, NOTES, LOGS):
    os.makedirs(_d, exist_ok=True)

MEET_TOL = 1e-9        # interior-intersection threshold on the penetration depth
CONTACT_TOL = 1e-6     # A87 tight-end contact tolerance
LP_TOL = 1e-7          # A46 forced / loadable threshold
FLUSH_TOL = 1e-6       # two vertices on a wall  =>  flush

CORNERS = ('BL', 'BR', 'TL', 'TR')
CORNER_WALLS = {'BL': ('x=0', 'y=0'), 'BR': ('x=s', 'y=0'),
                'TL': ('x=0', 'y=s'), 'TR': ('x=s', 'y=s')}

TILT_POS = 1e-7        # BRIEF bin 1 is '0 exact (< 1e-7 deg)': a tilt below
                       # this counts as the exact-0 branch, not as positive tilt.

TILT_BINS = [('0_exact_lt_1e-7', 0.0, 1e-7),
             ('(1e-7,0.5)', 1e-7, 0.5),
             ('[0.5,1)', 0.5, 1.0),
             ('[1,1.7347)', 1.0, 1.7347),
             ('[1.7347,2)', 1.7347, 2.0),
             ('[2,5)', 2.0, 5.0),
             ('[5,10)', 5.0, 10.0),
             ('[10,20)', 10.0, 20.0),
             ('[20,30)', 20.0, 30.0),
             ('[30,40)', 30.0, 40.0),
             ('[40,45]', 40.0, 45.0 + 1e-12)]

THETA0_CANDIDATES = (0.5, 1.0, 1.7347, 2.0, 3.0, 5.0, 10.0, 20.0, 30.0)


def free_commit_mb():
    """available COMMIT in MB (MEMORYSTATUSEX.ullAvailPageFile) -- tree85 pattern."""
    try:
        class MS(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        m = MS()
        m.dwLength = ctypes.sizeof(MS)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return m.ullAvailPageFile / (1024.0 * 1024.0)
    except Exception:
        return 1e9


def tilt_bin(t):
    for name, a, b in TILT_BINS:
        if a <= t < b:
            return name
    return TILT_BINS[-1][0]


def empty_bins():
    return {name: 0 for name, _, _ in TILT_BINS}


# ------------------------------------------------------------------ geometry
def mis90(a_deg):
    """distance of a_deg to the nearest multiple of 90, in [0,45]  (A46 mis90)."""
    m = a_deg % 90.0
    return min(m, 90.0 - m)


def verts(cx, cy, th):
    c, s = math.cos(th), math.sin(th)
    return [(cx + c * u - s * v, cy + s * u + c * v)
            for (u, v) in ((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5))]


def all_verts(z):
    return [verts(float(z[3 * i]), float(z[3 * i + 1]), float(z[3 * i + 2]))
            for i in range(11)]


def bbox_sigma(z):
    """(x0, y0, sigma) with sigma = enclosing side (max extent)."""
    V = [p for q in all_verts(z) for p in q]
    xs = [p[0] for p in V]
    ys = [p[1] for p in V]
    sig = max(max(xs) - min(xs), max(ys) - min(ys))
    return min(xs), min(ys), sig


def corner_boxes(x0, y0, sig):
    x1, y1 = x0 + sig, y0 + sig
    return {'BL': (x0, y0, x0 + 1.0, y0 + 1.0),
            'BR': (x1 - 1.0, y0, x1, y0 + 1.0),
            'TL': (x0, y1 - 1.0, x0 + 1.0, y1),
            'TR': (x1 - 1.0, y1 - 1.0, x1, y1)}


def sat_gap_poly_box(Q, box):
    """max over the 4 candidate separating axes of the signed gap.

    < 0  =>  interiors intersect, penetration depth = -gap.
    """
    bx0, by0, bx1, by1 = box
    B = [(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)]
    ex = (Q[1][0] - Q[0][0], Q[1][1] - Q[0][1])
    n = math.hypot(*ex)
    e1 = (ex[0] / n, ex[1] / n)
    e2 = (-e1[1], e1[0])
    best = -float('inf')
    for ax in ((1.0, 0.0), (0.0, 1.0), e1, e2):
        pq = [ax[0] * p[0] + ax[1] * p[1] for p in Q]
        pb = [ax[0] * p[0] + ax[1] * p[1] for p in B]
        g = max(min(pb) - max(pq), min(pq) - max(pb))
        if g > best:
            best = g
    return best


def meeting(Q, box):
    """(meets, margin) -- margin = penetration depth (>0 when interiors meet)."""
    g = sat_gap_poly_box(Q, box)
    return (-g > MEET_TOL), -g


def corner_frame_centre(corner, cx, cy, x0, y0, sig):
    x1, y1 = x0 + sig, y0 + sig
    if corner == 'BL':
        return (cx - x0, cy - y0)
    if corner == 'BR':
        return (x1 - cx, cy - y0)
    if corner == 'TL':
        return (cx - x0, y1 - cy)
    return (x1 - cx, y1 - cy)


# ------------------------------------------------- contact-type classification
# verbatim in spirit from A46 code/task1_audit.py classify_pair (SAT, TOL=1e-6).
def _proj(V, n):
    return [n[0] * x + n[1] * y for (x, y) in V]


def _sat_pair(VA, VB, eA, eB):
    best = None
    for n in (eA[0], eA[1], eB[0], eB[1]):
        pa, pb = _proj(VA, n), _proj(VB, n)
        for (g, nn) in ((min(pb) - max(pa), n), (min(pa) - max(pb), (-n[0], -n[1]))):
            if best is None or g > best[0]:
                best = (g, nn)
    return best


def _axes(th):
    c, s = math.cos(th), math.sin(th)
    return ((c, s), (-s, c))


def pair_contact_type(z, i, j, tol=CONTACT_TOL):
    """-> dict(type in {FL, CE, CC, UNKNOWN}, gap, apex, ...) or None."""
    VA = verts(float(z[3 * i]), float(z[3 * i + 1]), float(z[3 * i + 2]))
    VB = verts(float(z[3 * j]), float(z[3 * j + 1]), float(z[3 * j + 2]))
    eA, eB = _axes(float(z[3 * i + 2])), _axes(float(z[3 * j + 2]))
    gap, n = _sat_pair(VA, VB, eA, eB)
    if gap >= tol:
        return None
    t = (n[1], -n[0])
    pa, pb = _proj(VA, n), _proj(VB, n)
    mA, mB = max(pa), min(pb)
    WA = [VA[k] for k in range(4) if mA - pa[k] < tol]
    WB = [VB[k] for k in range(4) if pb[k] - mB < tol]
    ta, tb = sorted(_proj(WA, t)), sorted(_proj(WB, t))
    lo, hi = max(ta[0], tb[0]), min(ta[-1], tb[-1])
    seg = hi - lo
    rel = mis90(math.degrees(float(z[3 * i + 2]) - float(z[3 * j + 2])))
    out = {'pair': [i, j], 'gap': gap, 'overlap': seg, 'nA': len(WA), 'nB': len(WB),
           'rel_mismatch_deg': rel}
    if len(WA) == 2 and len(WB) == 2 and seg > tol:
        out['type'] = 'FL'
        return out
    P = (t[0] * (lo + hi) / 2 + n[0] * (mA + mB) / 2,
         t[1] * (lo + hi) / 2 + n[1] * (mA + mB) / 2)
    out['apex'] = list(P)
    isvA = any(abs(q[0] - P[0]) < tol and abs(q[1] - P[1]) < tol for q in VA)
    isvB = any(abs(q[0] - P[0]) < tol and abs(q[1] - P[1]) < tol for q in VB)
    if isvA and isvB:
        out['type'] = 'CC'
    elif isvA:
        out['type'] = 'CE'
        out['vertex_of'] = i
        out['edge_of'] = j
    elif isvB:
        out['type'] = 'CE'
        out['vertex_of'] = j
        out['edge_of'] = i
    else:
        out['type'] = 'UNKNOWN'
    return out


def pair_type_wrt(rec, Q):
    """human label of rec relative to blocker Q."""
    if rec is None:
        return 'none'
    tp = rec['type']
    if tp != 'CE':
        return tp
    return 'CE_corner_of_Q_on_edge_of_P' if rec.get('vertex_of') == Q \
        else 'CE_corner_of_P_on_edge_of_Q'


def wall_touch(z, i, wall, s_var, tol=CONTACT_TOL):
    """(touching, n_vertices_on_wall, min_gap).  flush iff n >= 2."""
    V = verts(float(z[3 * i]), float(z[3 * i + 1]), float(z[3 * i + 2]))
    if wall == 'x=0':
        g = [p[0] for p in V]
    elif wall == 'y=0':
        g = [p[1] for p in V]
    elif wall == 'x=s':
        g = [float(s_var) - p[0] for p in V]
    else:
        g = [float(s_var) - p[1] for p in V]
    mg = min(g)
    n_on = sum(1 for v in g if abs(v) <= tol)
    return (abs(mg) <= tol), n_on, mg


# ------------------------------------------------------------------- the LP
def lam_bounds(A, want=None):
    """min / max of each lambda over the BRIEF FJ polytope.

    variables u = (lam_0, lam_1..lam_m) >= 0
      sum u = 1
      lam_0 * e_33 - A^T lam = 0
    Returns dict with lam_min, lam_max (length m), lam0_min, lam0_max, feasible.
    """
    m, nv = A.shape
    ncol = m + 1
    Aeq = np.zeros((1 + nv, ncol))
    Aeq[0, :] = 1.0
    Aeq[1:, 0] = 0.0
    Aeq[1 + 33, 0] = 1.0
    Aeq[1:, 1:] = -A.T
    beq = np.zeros(1 + nv)
    beq[0] = 1.0
    bounds = [(0.0, 1.0)] * ncol

    def solve(c):
        r = linprog(c, A_eq=Aeq, b_eq=beq, bounds=bounds, method='highs')
        return (float(r.fun), np.asarray(r.x)) if r.success else (None, None)

    f0, x0 = solve(np.zeros(ncol))
    out = {'feasible': f0 is not None, 'm': m}
    if f0 is None:
        return out
    idx = range(m) if want is None else sorted(set(want))
    lmin = [None] * m
    lmax = [None] * m
    for k in idx:
        c = np.zeros(ncol); c[k + 1] = 1.0
        v, _ = solve(c)
        lmin[k] = v
        c = np.zeros(ncol); c[k + 1] = -1.0
        v, _ = solve(c)
        lmax[k] = None if v is None else -v
    c = np.zeros(ncol); c[0] = 1.0
    out['lam0_min'], _ = solve(c)
    c = np.zeros(ncol); c[0] = -1.0
    v, _ = solve(c)
    out['lam0_max'] = None if v is None else -v
    out['lam_min'] = lmin
    out['lam_max'] = lmax
    out['lam0_zero_branch'] = bool(out['lam0_min'] is not None
                                   and out['lam0_min'] <= 1e-9)
    return out


def lam_bounds_a46(A, want=None, cap=1e6):
    """A46 / A44 lambda_0 = 1 form:  A^T lam = e_s, 0 <= lam <= cap."""
    m, nv = A.shape
    b = np.zeros(nv); b[33] = 1.0
    bounds = [(0.0, cap)] * m

    def solve(c):
        r = linprog(c, A_eq=A.T, b_eq=b, bounds=bounds, method='highs')
        return float(r.fun) if r.success else None

    f0 = solve(np.zeros(m))
    out = {'feasible': f0 is not None}
    if f0 is None:
        return out
    idx = range(m) if want is None else sorted(set(want))
    lmin = [None] * m
    lmax = [None] * m
    for k in idx:
        c = np.zeros(m); c[k] = 1.0
        lmin[k] = solve(c)
        c = np.zeros(m); c[k] = -1.0
        v = solve(c)
        lmax[k] = None if v is None else -v
    out['lam_min'] = lmin
    out['lam_max'] = lmax
    return out


def cls_from_bounds(vals_min, vals_max):
    """(forced, loadable) booleans from the incident-row multiplier bounds."""
    f = any(v is not None and v > LP_TOL for v in vals_min)
    l = any(v is not None and v > LP_TOL for v in vals_max)
    return bool(f), bool(l)


# ------------------------------------------------------------------- summary
def summarise(rows, source, extra=None):
    """The five summary tables of BRIEF T2 (1)-(4) over a list of blocker rows."""
    pts = sorted(set(r['tag'] for r in rows))
    per_point_corner = {}
    for r in rows:
        per_point_corner.setdefault(r['tag'], {c: 0 for c in CORNERS})
        per_point_corner[r['tag']][r['corner']] += 1
    dist = {}
    viol = []
    for tag, cc in per_point_corner.items():
        for c in CORNERS:
            dist[str(cc[c])] = dist.get(str(cc[c]), 0) + 1
        if any(cc[c] < 2 for c in CORNERS):
            viol.append({'tag': tag, 'per_corner': cc})

    def bins_of(sel):
        b = empty_bins()
        for r in sel:
            b[tilt_bin(r['tilt_deg'])] += 1
        return b

    loaded_f = [r for r in rows if r['loaded_forced']]
    loaded_l = [r for r in rows if r['loaded_loadable']]
    unloaded = [r for r in rows if not r['loaded_loadable']]

    def min_pos(sel):
        cand = [r for r in sel if r['tilt_deg'] > 1e-7]
        if not cand:
            return None
        r = min(cand, key=lambda x: x['tilt_deg'])
        return {'tilt_deg': r['tilt_deg'], 'tag': r['tag'], 'square': r['square'],
                'corner': r['corner'], 'theta_mod90_deg': r['theta_mod90_deg'],
                'loaded_forced': r['loaded_forced'],
                'loaded_loadable': r['loaded_loadable'],
                'contacts': r['contacts']}

    th0 = {}
    for t0 in THETA0_CANDIDATES:
        th0['%g' % t0] = {
            'loaded_loadable_in_zone': sum(1 for r in loaded_l
                                           if 1e-7 < r['tilt_deg'] < t0),
            'loaded_forced_in_zone': sum(1 for r in loaded_f
                                         if 1e-7 < r['tilt_deg'] < t0),
            'unloaded_or_rattler_in_zone': sum(1 for r in unloaded
                                               if 1e-7 < r['tilt_deg'] < t0),
            'all_in_zone': sum(1 for r in rows if 1e-7 < r['tilt_deg'] < t0)}

    sub10 = [r for r in rows if TILT_POS < r['tilt_deg'] < 10.0]
    wallview = []
    for r in sub10:
        wallview.append({'tag': r['tag'], 'square': r['square'], 'corner': r['corner'],
                         'tilt_deg': r['tilt_deg'],
                         'n_corner_walls_touched': r['n_corner_walls_touched'],
                         'corner_wall_loaded_forced': r['corner_wall_forced'],
                         'corner_wall_loaded_loadable': r['corner_wall_loadable'],
                         'is_rattler': r['is_rattler']})
    ghosts = [r for r in rows if r['near_flush_ghost']]

    out = {
        'source': source,
        'n_points': len(pts),
        'n_blockers': len(rows),
        'n_rattler_blockers': sum(1 for r in rows if r['is_rattler']),
        'n_loaded_forced': len(loaded_f),
        'n_loaded_loadable': len(loaded_l),
        'n_unloaded_with_rows': sum(1 for r in rows
                                    if not r['is_rattler'] and not r['loaded_loadable']),
        'blockers_per_point': {
            'min': min((sum(v.values()) for v in per_point_corner.values()), default=0),
            'max': max((sum(v.values()) for v in per_point_corner.values()), default=0),
            'mean': (len(rows) / len(pts)) if pts else None},
        'per_corner_count_distribution': dist,
        'n_points_violating_K0_2_ge2_per_corner': len(viol),
        'K0_2_violations': viol,
        'tilt_hist_all': bins_of(rows),
        'tilt_hist_loaded_forced': bins_of(loaded_f),
        'tilt_hist_loaded_loadable': bins_of(loaded_l),
        'tilt_hist_unloaded_or_rattler': bins_of(unloaded),
        'min_positive_tilt': {
            'loaded_forced': min_pos(loaded_f),
            'loaded_loadable': min_pos(loaded_l),
            'all_blockers': min_pos(rows)},
        'theta0_table': th0,
        'blockers_tilt_lt_10_wall_view': wallview,
        'near_flush_ghosts': {'n': len(ghosts), 'items': ghosts},
    }
    if extra:
        out.update(extra)
    return out
