r"""geom130.py -- A130: A128's coupled128.py COPIED (not imported; A128 is read-only) with its write paths moved to A130.
Original docstring follows.

coupled128.py -- A128: coupled moves at the selected minimiser, decided EXACTLY on neighbourhoods.

For a packing z (11 unit squares, side m) and a box B = {|z'_i - z_i| <= r for every pose coordinate,
|m' - m| <= r}, the menu of docs/proofs/drain_sel.md is decided by interval arithmetic (mpmath.iv, outward
rounded) on the whole box:

  ROT       single-square screw y = (v, w) of an intruder Q (Lemma ROT of noroom.md, box form);
  CLUSTER   rigid screw of a set C of squares containing Q (the retreat clusters of NOCRIT-SEL, the contact
            neighbourhoods, every connected contact subset of size <= 4);
  EXCHANGE  remove the two possible meeters of a corner, place the slot square and a re-fit Q0 (Lemma
            EXPOSE of exchange_lemma.md, box form): a k >= 1 packing at the SAME side for every z' in B;
  TWO-WALL  the hook identities / one-wall bounds of lockfree.md sect 3 evaluated on the box, and the
            trivial extent bound;
  SUPPLY    the row count of a held intruder (Lemma SUPPLY of drain_sel.md).

The certificate of a move (Lemma BOX-MOVE, drain_sel.md sect T2.0): for every axis k of every pair (member,
outsider) that can be the separating axis somewhere on B, the derivative of the axis separation along the
motion is > 0 on B; every possibly active wall row of a member has derivative > 0; the depth of Q at its
corner has right-derivative of mu > 0 (min over the candidate argmin points on B); every other
(member, corner) depth that can be positive on B is nonincreasing.  Then for EVERY packing z' in B at which
Q intrudes c there is eps0 > 0 with z'_eps a packing at the same side and Psi^(w)(z'_eps) < Psi^(w)(z') for
every positive weight vector w -- so B contains no Psi^(w)-minimiser at which Q intrudes c.

The search for y is a 6+1-variable LP with INTERVAL coefficients (robust form: y = y+ - y-, coefficient
lo on y+, hi on y-); the certificate is an independent interval evaluation of the chosen y on the box
padded by 1e-6 with v perturbed by the screw's own drift.  Every certificate is then re-sampled: >= 10^4
configurations drawn uniformly in the box, every certified row's derivative evaluated in floating point,
hits = rows below their certified bound (must be 0).

Pure geometry; one process; BLAS pinned; BelowNormal priority; tiny linprogs only (as lock103/lockw105).
Writes only under attempts/A128-coupled-moves/{results,logs}.  Usage:
    python coupled128.py [all | <sample name> ...] [--radii 1e-3,3e-4,1e-4,1e-5,1e-6] [--nsamp 10000]
"""
from __future__ import annotations
import os, sys, json, math, time, itertools
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = "1"
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
try:
    import ctypes
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)  # BELOW_NORMAL
except Exception:
    pass
from fractions import Fraction
from decimal import Decimal
import numpy as np
from scipy.optimize import linprog, minimize
from mpmath import iv

iv.prec = 64
PI = iv.pi

HERE = os.path.dirname(os.path.abspath(__file__))
A130 = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(A130))
A128 = os.path.join(ROOT, 'attempts', 'A128-coupled-moves')
ATT = os.path.join(ROOT, 'attempts')
RES = os.path.join(A130, 'results'); LOGS = os.path.join(A130, 'logs')
os.makedirs(RES, exist_ok=True); os.makedirs(LOGS, exist_ok=True)

SHAT = 3.877083590022814
CONTACT_TOL = 1e-7      # A102/A103 contact bar (point tests)
MEET_TOL = 1e-9         # exact meet bar
BAR = 1e-7              # an axis with separation lower bound <= BAR on the box is treated as possibly active
CORNERS = ('BL', 'BR', 'TR', 'TL')
# frame: (sx, sy, ox is m?, oy is m?)   p_f = (sx (p_x - ox), sy (p_y - oy))
FR = {'BL': (1, 1, 0, 0), 'BR': (-1, 1, 1, 0), 'TR': (-1, -1, 1, 1), 'TL': (1, -1, 0, 1)}
T0 = time.time()
_fh = open(os.path.join(LOGS, 'geom130.log'), 'a', encoding='utf-8')


def log(*a):
    m = ' '.join(str(v) for v in a)
    print(m, flush=True)
    _fh.write('[%8.1f] %s\n' % (time.time() - T0, m)); _fh.flush()


# ============================================================================ intervals
def I(a, b=None):
    return iv.mpf([a, a if b is None else b])


def lo(x):
    return 0.0 if x.a == 0 else math.nextafter(float(x.a), -math.inf)


def hi(x):
    return 0.0 if x.b == 0 else math.nextafter(float(x.b), math.inf)


def imin(x, y):
    return iv.mpf([min(x.a, y.a), min(x.b, y.b)])


def imax(x, y):
    return iv.mpf([max(x.a, y.a), max(x.b, y.b)])


def hull(xs):
    return iv.mpf([min(x.a for x in xs), max(x.b for x in xs)])


def signs(x):
    """Admissible values of sgn(x) over an interval, both at a zero (one-sided derivatives of |x|)."""
    s = []
    if x.b >= 0:
        s.append(1.0)
    if x.a <= 0:
        s.append(-1.0)
    return s


def hderiv(cD, sD):
    """Hull of the branch derivatives of (|cos D| + |sin D|)/2 with respect to D."""
    return hull([(-sc * sD + ss * cD) / 2 for sc in signs(cD) for ss in signs(sD)])


class SqBox:
    """A unit square whose pose ranges over a box: centre in [cx +- r], tilt in [th +- r] (radians)."""

    def __init__(self, cx, cy, th, r, exact_axis=False, th_int=None, cr=None):
        cr = r if cr is None else cr
        self.c = (I(cx - cr, cx + cr), I(cy - cr, cy + cr))
        self.th = I(th - r, th + r) if th_int is None else I(th_int[0], th_int[1])
        if exact_axis and r == 0 and th_int is None and abs(th) < 1e-15:
            self.cs, self.sn = I(1), I(0)
        elif exact_axis and r == 0 and abs(th - math.pi / 2) < 1e-15:
            self.cs, self.sn = I(0), I(1)
        else:
            self.cs, self.sn = iv.cos(self.th), iv.sin(self.th)
        cs, sn = self.cs, self.sn
        self.V = [(self.c[0] + (dx * cs - dy * sn) / 2, self.c[1] + (dx * sn + dy * cs) / 2)
                  for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        self.N = [(sn, -cs), (cs, sn), (-sn, cs), (-cs, -sn)]      # outward normals of edges 0..3
        self.h = (abs(cs) + abs(sn)) / 2                             # half-extent along the axes
        self.H = hderiv(cs, sn)                                       # d h / d theta (hull)


def pair_axis(A, B, k, mover_is_A):
    """Separation along the outward normal of edge k of A against B, and the coefficients (c_vx, c_vy, c_w)
    of its derivative along a screw (v, w) about the origin applied to A (mover_is_A) or to B."""
    n = A.N[k]
    d = (B.c[0] - A.c[0], B.c[1] - A.c[1])
    D = A.th - B.th + (k - 1) * PI / 2
    cD, sD = iv.cos(D), iv.sin(D)
    h = (abs(cD) + abs(sD)) / 2
    sep = n[0] * d[0] + n[1] * d[1] - I(0.5) - h
    H = hderiv(cD, sD)
    if mover_is_A:
        Jn = (-n[1], n[0]); JcA = (-A.c[1], A.c[0])
        coef = (-n[0], -n[1], Jn[0] * d[0] + Jn[1] * d[1] - (n[0] * JcA[0] + n[1] * JcA[1]) - H)
    else:
        JcB = (-B.c[1], B.c[0])
        coef = (n[0], n[1], n[0] * JcB[0] + n[1] * JcB[1] + H)
    return sep, coef


def wall_rows(A, m):
    """(sep, coef, name) for the four wall rows of A (A the mover)."""
    return [(A.c[0] - A.h, (I(1), I(0), -A.c[1] - A.H), 'left'),
            (A.c[1] - A.h, (I(0), I(1), A.c[0] - A.H), 'bottom'),
            (m - A.c[0] - A.h, (I(-1), I(0), A.c[1] - A.H), 'right'),
            (m - A.c[1] - A.h, (I(0), I(-1), -A.c[0] - A.H), 'top')]


def depth_cands(A, cn, m):
    """mu_c(Q) enclosure on the box and the candidate argmin points with the coefficient rows of their
    branch derivatives (sect T2.0 of drain_sel.md).  Returns ((mu_lo, mu_hi), [(value, rows, tag)])."""
    sx, sy, fx, fy = FR[cn]
    ox = m if fx else I(0); oy = m if fy else I(0)
    cf = (sx * (A.c[0] - ox), sy * (A.c[1] - oy))
    cands = []
    for k in range(4):
        p = A.V[k]
        pf = (sx * (p[0] - ox), sy * (p[1] - oy))
        val = imax(pf[0], pf[1])
        rx = (I(sx), I(0), -sx * p[1], 'V%dx' % k); ry = (I(0), I(sy), sy * p[0], 'V%dy' % k)
        if pf[0].a > pf[1].b:
            rows = [rx]
        elif pf[1].a > pf[0].b:
            rows = [ry]
        else:
            rows = [rx, ry]
        cands.append((val, rows, 'V%d' % k))
    for k in range(4):
        n = A.N[k]
        nf = (-sx * n[0], -sy * n[1])
        if not (nf[0].a > 0 and nf[1].a > 0):
            continue
        S_ = nf[0] + nf[1]
        mu = (cf[0] * nf[0] + cf[1] * nf[1] - I(0.5)) / S_
        a = A.V[k]; b = A.V[(k + 1) % 4]
        af = (sx * (a[0] - ox), sy * (a[1] - oy)); bf = (sx * (b[0] - ox), sy * (b[1] - oy))
        den = (bf[0] - af[0]) - (bf[1] - af[1])
        if not (den.a <= 0 <= den.b):
            t = (af[1] - af[0]) / den
            if t.b < 0 or t.a > 1:
                continue
        w = sx * sy
        cw = (-sx * A.c[1] * nf[0] + sy * A.c[0] * nf[1] + w * (cf[1] * nf[0] - cf[0] * nf[1])
              - mu * w * (nf[0] - nf[1])) / S_
        cands.append((mu, [(sx * nf[0] / S_, sy * nf[1] / S_, cw, 'E%d' % k)], 'E%d' % k))
    mu_hi = min(c[0].b for c in cands); mu_lo = min(c[0].a for c in cands)
    thr = min(mu_hi, iv.mpf(1))
    active = [c for c in cands if c[0].a <= thr]
    return (lo(mu_lo), hi(mu_hi)), active


# ============================================================================ float geometry (point tests, A102/A103 conventions)
def verts(cx, cy, th):
    c, s_ = math.cos(th), math.sin(th)
    return [(cx + 0.5 * (dx * c - dy * s_), cy + 0.5 * (dx * s_ + dy * c))
            for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def sep(p, q):
    best = -9.0
    for poly_ in (p, q):
        for i in range(4):
            a, b = poly_[i], poly_[(i + 1) % 4]
            ex, ey = b[0] - a[0], b[1] - a[1]; n = math.hypot(ex, ey)
            ax, ay = -ey / n, ex / n
            pp = [x * ax + y * ay for x, y in p]; qq = [x * ax + y * ay for x, y in q]
            v = max(min(qq) - max(pp), min(pp) - max(qq))
            if v > best:
                best = v
    return best


def wall_gap(p, s):
    return min(min(x for x, y in p), min(y for x, y in p), s - max(x for x, y in p), s - max(y for x, y in p))


def frame_pt(cn, s):
    sx, sy, fx, fy = FR[cn]
    ox, oy = (s if fx else 0.0), (s if fy else 0.0)
    return (lambda p: (sx * (p[0] - ox), sy * (p[1] - oy))), (sx, sy, ox, oy)


def argmin_data(sq, cn, s):
    fm, _ = frame_pt(cn, s)
    W = [fm(v) for v in verts(*sq)]
    cand = list(W)
    for k in range(4):
        a, b = W[k], W[(k + 1) % 4]
        d = (b[0] - a[0]) - (b[1] - a[1])
        if abs(d) > 1e-14:
            t = (a[1] - a[0]) / d
            if -1e-12 <= t <= 1 + 1e-12:
                t = min(1.0, max(0.0, t)); cand.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
    vals = [max(p[0], p[1]) for p in cand]
    mu = min(vals)
    ext = []
    for p, v in zip(cand, vals):
        if v <= mu + 1e-9 and not any(abs(p[0] - q[0]) < 1e-9 and abs(p[1] - q[1]) < 1e-9 for q in ext):
            ext.append(p)
    return mu, max(0.0, 1.0 - mu), ext, W


def corner_depth(sq, cn, s):
    return argmin_data(sq, cn, s)[1]


def meeters(poses, s, cn, tol=MEET_TOL):
    out = [(i, corner_depth(q, cn, s)) for i, q in enumerate(poses)]
    return sorted([(i, d) for i, d in out if d > tol], key=lambda t: -t[1])


def _edge_normal_out(a, b, oc):
    ex, ey = b[0] - a[0], b[1] - a[1]; n = math.hypot(ex, ey); nx, ny = -ey / n, ex / n
    mx, my = (a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0
    if (mx - oc[0]) * nx + (my - oc[1]) * ny < 0:
        nx, ny = -nx, -ny
    return nx, ny


def contacts_of(poses, i, s, tol=CONTACT_TOL):
    """A102's contact list of square i: force F on i (unit), point, gap, and the row kind."""
    P = poses[i]; A = verts(*P); out = []
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
                    a, b = E[k], E[(k + 1) % 4]; ex, ey = b[0] - a[0], b[1] - a[1]; L = ex * ex + ey * ey
                    t = max(0.0, min(1.0, ((v[0] - a[0]) * ex + (v[1] - a[1]) * ey) / L))
                    fx, fy = a[0] + t * ex, a[1] + t * ey; d = math.hypot(v[0] - fx, v[1] - fy)
                    if d < tol:
                        nx, ny = _edge_normal_out(a, b, (own[0], own[1]))
                        pairs.append(((v[0] + fx) / 2.0, (v[1] + fy) / 2.0, sign * nx, sign * ny, d))
        for (px, py, fx, fy, d) in pairs:
            if not any(abs(c['point'][0] - px) < 1e-6 and abs(c['point'][1] - py) < 1e-6
                       and c['F'][0] * fx + c['F'][1] * fy > 1.0 - 1e-6 for c in out):
                out.append({'with': 'square %d' % j, 'j': j, 'point': (px, py), 'F': (fx, fy), 'gap': sep(A, B)})
    walls = (('left wall', min(x for x, y in A), (1.0, 0.0), lambda v: v[0]),
             ('bottom wall', min(y for x, y in A), (0.0, 1.0), lambda v: v[1]),
             ('right wall', s - max(x for x, y in A), (-1.0, 0.0), lambda v: s - v[0]),
             ('top wall', s - max(y for x, y in A), (0.0, -1.0), lambda v: s - v[1]))
    for name, gap, nrm, dfn in walls:
        if gap < tol:
            for v in A:
                if dfn(v) < tol:
                    out.append({'with': name, 'j': None, 'point': (v[0], v[1]), 'F': nrm, 'gap': gap})
    return out


# ============================================================================ the box certificate
class BoxGeom:
    """All interval rows of a packing at radius r, cached: pair-axis rows for both movers, wall rows, depths."""

    def __init__(self, poses, m, r, exact_axis=True, tilt_override=None, cr=None):
        self.r = r
        self.m = I(m - r, m + r)
        tilt_override = tilt_override or {}
        self.S = [SqBox(cx, cy, th, r, exact_axis, tilt_override.get(i), cr) for i, (cx, cy, th) in enumerate(poses)]
        n = len(poses)
        self.pair = {}      # (a, b) -> list of 8 (sep, coef_if_a_moves, coef_if_b_moves, tag)
        for a in range(n):
            for b in range(a + 1, n):
                rows = []
                for (own, oth, k) in [(a, b, kk) for kk in range(4)] + [(b, a, kk) for kk in range(4)]:
                    A, B = self.S[own], self.S[oth]
                    s1, ca = pair_axis(A, B, k, True)      # owner moves
                    s2, cb = pair_axis(A, B, k, False)     # other moves
                    if own == a:
                        rows.append((s1, ca, cb, 'ax%d of %d vs %d' % (k, own, oth)))
                    else:
                        rows.append((s1, cb, ca, 'ax%d of %d vs %d' % (k, own, oth)))
                self.pair[(a, b)] = rows
        self.walls = [wall_rows(self.S[i], self.m) for i in range(n)]
        self.depth = {}
        for i in range(n):
            for cn in CORNERS:
                self.depth[(i, cn)] = depth_cands(self.S[i], cn, self.m)

    def pair_rows(self, a, b):
        """Rows of the pair (a, b) with a the mover: (sep, coef, tag)."""
        if a < b:
            return [(s, ca, t) for (s, ca, cb, t) in self.pair[(a, b)]]
        return [(s, cb, t) for (s, ca, cb, t) in self.pair[(b, a)]]

    def possible_meeters(self, cn):
        return [i for i in range(len(self.S)) if self.depth[(i, cn)][0][0] < 1.0]


def assemble(G, C, Q, cn, bar=BAR):
    """Rows for the cluster C (set) retreating Q from corner cn.  Returns (strict, weak, safe_note) where
    each row is (coef, tag); or None with a reason if a pair is doubly-unsafe (cannot be separated)."""
    n = len(G.S)
    strict, weak = [], []
    for a in sorted(C):
        for b in range(n):
            if b in C:
                continue
            rows = G.pair_rows(a, b)
            if any(s.a > bar for (s, _, _) in rows):
                continue                                   # some axis keeps a positive margin on the box
            for (s, coef, tag) in rows:
                if s.b >= -1e-9:                            # this axis can be the separating one somewhere on B (1e-9: float contact noise)
                    strict.append((coef, tag))
        for (s, coef, name) in G.walls[a]:
            if s.a > bar:
                continue
            strict.append((coef, '%s wall of %d' % (name, a)))
    for i in sorted(C):
        for c2 in CORNERS:
            (mlo, mhi), act = G.depth[(i, c2)]
            if mlo >= 1.0:
                continue
            for (val, rows, tag) in act:
                for coef in rows:
                    (strict if (i == Q and c2 == cn) else weak).append((coef[:3], 'depth %s of %d %s' % (c2, i, coef[3])))
    return strict, weak


def robust_lp(strict, weak):
    """max t s.t. sum_j (lo_j y+_j - hi_j y-_j) >= t (strict) / >= 0 (weak); y+, y- in [0,1]."""
    if not strict:
        return -1.0, np.zeros(3)
    A_ub, b_ub = [], []
    for coef, _ in strict:
        A_ub.append([-lo(coef[j]) for j in range(3)] + [hi(coef[j]) for j in range(3)] + [1.0]); b_ub.append(0.0)
    for coef, _ in weak:
        A_ub.append([-lo(coef[j]) for j in range(3)] + [hi(coef[j]) for j in range(3)] + [0.0]); b_ub.append(0.0)
    res = linprog(c=[0] * 6 + [-1.0], A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                  bounds=[(0, 1)] * 6 + [(None, 1.0)], method='highs')
    if res.status != 0:
        return -1.0, np.zeros(3)
    y = np.array(res.x[:3]) - np.array(res.x[3:6])
    return float(-res.fun), y


def evaluate(strict, weak, y, drift=0.0):
    """Interval evaluation of every row at the screw y (v perturbed by +-drift): returns
    (min strict lower bound, min weak lower bound, worst strict tag, worst weak tag)."""
    yi = [I(y[0] - drift, y[0] + drift), I(y[1] - drift, y[1] + drift), I(y[2])]
    ms, ws, mt, wt = math.inf, math.inf, None, None
    bounds = []
    for coef, tag in strict:
        v = lo(coef[0] * yi[0] + coef[1] * yi[1] + coef[2] * yi[2])
        bounds.append((tag, v))
        if v < ms:
            ms, mt = v, tag
    for coef, tag in weak:
        v = lo(coef[0] * yi[0] + coef[1] * yi[1] + coef[2] * yi[2])
        if v < ws:
            ws, wt = v, tag
    return ms, ws, mt, wt, bounds


# ============================================================================ clusters
def press_closure(poses, s, Q, e, tol=CONTACT_TOL):
    """NOCRIT-SEL's retreat cluster C_e(Q): the forward closure of 'N presses a member against e'."""
    C = {Q}; changed = True
    while changed:
        changed = False
        for M in list(C):
            for c in contacts_of(poses, M, s, tol):
                N = c['j']
                if N is None or N in C:
                    continue
                if c['F'][0] * e[0] + c['F'][1] * e[1] < -1e-9:
                    C.add(N); changed = True
    return frozenset(C)


def cluster_menu(poses, s, Q, gc=5e-3, maxsize=4, cap=80):
    """Candidate clusters containing Q: singleton, the four retreat closures, contact neighbourhoods,
    connected contact subsets of size <= maxsize (contact graph at gap < gc)."""
    n = len(poses); V = [verts(*p) for p in poses]
    adj = {i: set() for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            if sep(V[i], V[j]) < gc:
                adj[i].add(j); adj[j].add(i)
    out = [frozenset([Q])]
    for e in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        out.append(press_closure(poses, s, Q, e))
    out.append(frozenset([Q]) | frozenset(adj[Q]))
    comp, front = {Q}, [Q]
    while front:
        x = front.pop(); [(comp.add(y), front.append(y)) for y in adj[x] if y not in comp]
    out.append(frozenset(comp))
    seen = set(out); grow = [frozenset([Q])]
    while grow and len(seen) < cap + 6:
        nxt = []
        for C in grow:
            if len(C) >= maxsize:
                continue
            for x in C:
                for y in adj[x]:
                    if y not in C:
                        D = C | {y}
                        if D not in seen:
                            seen.add(D); nxt.append(D); out.append(D)
        grow = nxt
    uniq, res = set(), []
    for C in out:
        if C not in uniq and len(C) < n:
            uniq.add(C); res.append(C)
    return res


# ============================================================================ sampled confirmation (floats, numpy)
def float_rows(z, mvec, r, C, Q, cn, y, strict_tags, nsamp, rng):
    """Draw nsamp poses in the box; evaluate every certified strict row's derivative in floats against the
    row's certified lower bound.  Returns (drawn, tested, hits, min (derivative - bound) seen)."""
    z = np.asarray(z); n = len(z)
    Z = z[None, :, :] + rng.uniform(-r, r, size=(nsamp, n, 3))
    M = mvec + rng.uniform(-r, r, size=nsamp)
    cs, sn = np.cos(Z[:, :, 2]), np.sin(Z[:, :, 2])
    vx, vy, w = y
    hits, worst = 0, math.inf
    for tag, bound in strict_tags:
        parts = tag.split()
        if parts[0].startswith('ax'):
            k = int(parts[0][2:]); own = int(parts[2]); oth = int(parts[4])
            A_c, A_th = Z[:, own, :2], Z[:, own, 2]; B_c, B_th = Z[:, oth, :2], Z[:, oth, 2]
            n0 = [(0, -1), (1, 0), (0, 1), (-1, 0)][k]
            nx = n0[0] * np.cos(A_th) - n0[1] * np.sin(A_th); ny = n0[0] * np.sin(A_th) + n0[1] * np.cos(A_th)
            D = A_th - B_th + (k - 1) * np.pi / 2
            cD, sD = np.cos(D), np.sin(D)
            Hd = (-np.sign(cD) * sD + np.sign(sD) * cD) / 2
            d = B_c - A_c
            if own in C:      # A moves
                Jn_d = -ny * d[:, 0] + nx * d[:, 1]
                n_JcA = nx * (-A_c[:, 1]) + ny * A_c[:, 0]
                der = -nx * vx - ny * vy + w * (Jn_d - n_JcA - Hd)
            else:             # B moves
                n_JcB = nx * (-B_c[:, 1]) + ny * B_c[:, 0]
                der = nx * vx + ny * vy + w * (n_JcB + Hd)
        elif parts[1] == 'wall':
            name = parts[0]; i = int(parts[3])
            c = Z[:, i, :2]; th = Z[:, i, 2]
            Hd = (-np.sign(np.cos(th)) * np.sin(th) + np.sign(np.sin(th)) * np.cos(th)) / 2
            if name == 'left':
                der = vx + w * (-c[:, 1] - Hd)
            elif name == 'bottom':
                der = vy + w * (c[:, 0] - Hd)
            elif name == 'right':
                der = -vx + w * (c[:, 1] - Hd)
            else:
                der = -vy + w * (-c[:, 0] - Hd)
        elif parts[0] == 'depth':
            c2 = parts[1]; i = int(parts[3]); ctag = parts[4]
            sx, sy, fx, fy = FR[c2]
            ox = M if fx else 0.0; oy = M if fy else 0.0
            c = Z[:, i, :2]; th = Z[:, i, 2]
            if ctag.startswith('V'):
                kk = int(ctag[1:2]); dx, dy = ((-1, -1), (1, -1), (1, 1), (-1, 1))[kk]
                px = c[:, 0] + 0.5 * (dx * np.cos(th) - dy * np.sin(th)); py = c[:, 1] + 0.5 * (dx * np.sin(th) + dy * np.cos(th))
                dx_ = sx * vx - sx * w * py; dy_ = sy * vy + sy * w * px
                der = dx_ if ctag.endswith('x') else dy_
            else:
                kk = int(ctag[1:]); n0 = [(0, -1), (1, 0), (0, 1), (-1, 0)][kk]
                nx = n0[0] * np.cos(th) - n0[1] * np.sin(th); ny = n0[0] * np.sin(th) + n0[1] * np.cos(th)
                nfx, nfy = -sx * nx, -sy * ny
                S_ = nfx + nfy
                cfx, cfy = sx * (c[:, 0] - ox), sy * (c[:, 1] - oy)
                mu = (cfx * nfx + cfy * nfy - 0.5) / S_
                wf = sx * sy
                der = (sx * nfx * vx + sy * nfy * vy + w * (-sx * c[:, 1] * nfx + sy * c[:, 0] * nfy
                       + wf * (cfy * nfx - cfx * nfy) - mu * wf * (nfx - nfy))) / S_
        else:
            continue
        worst = min(worst, float((der - bound).min()))
        hits += int((der < bound - 1e-9).sum())
    return nsamp, nsamp, hits, worst


# ============================================================================ the moves, per intruder
def certify_cluster(G_lp, G_ver, C, Q, cn):
    strict, weak = assemble(G_lp, C, Q, cn)
    t, y = robust_lp(strict, weak)
    if t <= 1e-10:
        return {'lp_t': t, 'certified': False}
    strict2, weak2 = assemble(G_ver, C, Q, cn)
    drift = 1e-6 * abs(y[2]) * math.hypot(y[0], y[1])
    ms, ws, mt, wt, bounds = evaluate(strict2, weak2, y, drift)
    ok = ms > 0 and ws >= 0
    return {'lp_t': t, 'y': [float(v) for v in y], 'certified': bool(ok), 'min_strict': ms, 'min_weak': ws,
            'worst_strict': mt, 'worst_weak': wt, 'n_strict': len(strict2), 'n_weak': len(weak2),
            'strict_tags': bounds}


def run_moves(name, poses, m, radii, nsamp, rng, extra_note=''):
    n = len(poses)
    log('=== %s side %.9f' % (name, m))
    V = [verts(*p) for p in poses]
    wg = min(min(sep(V[i], V[j]) for i in range(n) for j in range(i + 1, n)), min(wall_gap(v, m) for v in V))
    meet = {cn: meeters(poses, m, cn) for cn in CORNERS}
    log('  worst gap at the point %.2e ; meeters %s' % (wg, {k: [(i, round(d, 5)) for i, d in v] for k, v in meet.items()}))
    geoms = {}

    def G(r, ver=False):
        key = (r, ver)
        if key not in geoms:
            geoms[key] = BoxGeom(poses, m, r + (1e-6 if ver else 0.0))
        return geoms[key]

    out = {'packing': name, 'side': m, 'worst_gap_point': wg, 'note': extra_note,
           'meeters': {k: [(i, d) for i, d in v] for k, v in meet.items()},
           'K0_BLOCKED_point': all(len(v) >= 2 for v in meet.values()), 'intruders': [], 'exchange': {}, 'twowall': {}}
    for cn in CORNERS:
        # test every square that can meet the corner somewhere on the largest box: the point intruders and
        # the TANGENT squares (mu_c = 1 at the point, mu_c < 1 somewhere on B)
        subjects = list(meet[cn])
        for i in G(radii[0]).possible_meeters(cn):
            if i not in [q for q, _ in meet[cn]]:
                subjects.append((i, 0.0))
        for (Q, d) in subjects:
            rec = {'corner': cn, 'square': Q, 'depth': d, 'tilt_deg': math.degrees(poses[Q][2]) % 90.0,
                   'is_second_meeter': bool(d > 0 and (Q, d) == min(meet[cn], key=lambda t: t[1])),
                   'tangent_only': bool(d == 0.0)}
            # --- point tests: exact first order at r = 0 (the exact contact set; a direction may be blocked
            # after 1e-9 by a parallel-edge kink, noroom.md sect 2.2 remark (2)) and at r = 1e-8 (kinks within
            # 1e-8 count both branches: lock103's operational 'held' semantics)
            Gx = G(0.0); G8 = G(1e-8)
            sx0 = certify_cluster(Gx, Gx, frozenset([Q]), Q, cn)
            single0 = certify_cluster(G8, G8, frozenset([Q]), Q, cn)
            rec['ROT_point'] = {'held': not single0['certified'], 'lp_t': single0['lp_t'],
                                'held_exact_r0': not sx0['certified'], 'lp_t_exact_r0': sx0['lp_t']}
            clusters = cluster_menu(poses, m, Q)
            rec['n_clusters'] = len(clusters)
            best_cluster0 = None
            for C in clusters:
                if len(C) == 1:
                    continue
                c0 = certify_cluster(G8, G8, C, Q, cn)
                if c0['certified'] and (best_cluster0 is None or c0['lp_t'] > best_cluster0[1]):
                    best_cluster0 = (sorted(C), c0['lp_t'])
            rec['CLUSTER_point'] = {'held': best_cluster0 is None, 'best': best_cluster0}
            # --- box tests, largest radius first
            rec['ROT_box'] = {'certified_radius': None}
            rec['CLUSTER_box'] = {'certified_radius': None}
            for r in radii:
                Gl, Gv = G(r), G(r, True)
                if rec['ROT_box']['certified_radius'] is None:
                    c1 = certify_cluster(Gl, Gv, frozenset([Q]), Q, cn)
                    if c1['certified']:
                        dr, te, hits, worst = float_rows(poses, m, r, {Q}, Q, cn, c1['y'], c1['strict_tags'], nsamp, rng)
                        rec['ROT_box'] = {'certified_radius': r, 'y': c1['y'], 'lp_t': c1['lp_t'], 'min_strict': c1['min_strict'],
                                          'min_weak': c1['min_weak'], 'n_strict': c1['n_strict'], 'n_weak': c1['n_weak'],
                                          'sample': {'drawn': dr, 'tested': te, 'hits': hits, 'min_derivative_seen': worst}}
                    else:
                        rec['ROT_box'].setdefault('fail', {})[str(r)] = {'lp_t': c1['lp_t'], 'min_strict': c1.get('min_strict'),
                                                                        'worst': c1.get('worst_strict'), 'min_weak': c1.get('min_weak'),
                                                                        'worst_weak': c1.get('worst_weak')}
                if rec['CLUSTER_box']['certified_radius'] is None:
                    bestc = None
                    for C in clusters:
                        if len(C) == 1:
                            continue
                        cc = certify_cluster(Gl, Gv, C, Q, cn)
                        if cc['certified'] and (bestc is None or cc['min_strict'] > bestc[1]['min_strict']):
                            bestc = (C, cc)
                    if bestc is not None:
                        C, cc = bestc
                        dr, te, hits, worst = float_rows(poses, m, r, set(C), Q, cn, cc['y'], cc['strict_tags'], nsamp, rng)
                        rec['CLUSTER_box'] = {'certified_radius': r, 'cluster': sorted(C), 'y': cc['y'], 'lp_t': cc['lp_t'],
                                              'min_strict': cc['min_strict'], 'min_weak': cc['min_weak'],
                                              'n_strict': cc['n_strict'], 'n_weak': cc['n_weak'],
                                              'sample': {'drawn': dr, 'tested': te, 'hits': hits, 'min_derivative_seen': worst}}
                if rec['ROT_box']['certified_radius'] is not None and rec['CLUSTER_box']['certified_radius'] is not None:
                    break
            rec['SUPPLY'] = supply_count(poses, m, Q, cn)
            out['intruders'].append(rec)
            log('  %s sq%d d=%.3e%s tilt %.3f | ROT point %s (exact r0 %s) | CLUSTER point %s | ROT box r=%s | CLUSTER box r=%s %s | rows %s' % (
                cn, Q, d, ' (tangent)' if rec['tangent_only'] else '', rec['tilt_deg'], 'HELD' if rec['ROT_point']['held'] else 'unheld', 'held' if rec['ROT_point']['held_exact_r0'] else 'unheld',
                'HELD' if rec['CLUSTER_point']['held'] else ('unheld %s' % (best_cluster0[0],)),
                rec['ROT_box']['certified_radius'], rec['CLUSTER_box']['certified_radius'],
                rec['CLUSTER_box'].get('cluster', ''), (rec['SUPPLY']['sq_rows'], rec['SUPPLY']['wall_rows'], rec['SUPPLY']['mode'])))
        # --- exchange at this corner
        out['exchange'][cn] = exchange_box(poses, m, cn, radii, G, nsamp, rng)
        ex = out['exchange'][cn]
        log('  EXCHANGE %s: %s' % (cn, {k: ex[k] for k in ex if k not in ('Q0',)}))
        out['twowall'][cn] = twowall(poses, m, cn, radii[0])
    out['extent_bound'] = extent_bound(poses, m, radii[0])
    return out


# ============================================================================ SUPPLY (row count) and hold mode
def cone_certificate(A_rows, G_rows):
    nA, nG = len(A_rows), len(G_rows); rows = list(A_rows) + list(G_rows)
    for mode in ('pushed', 'wedged'):
        nn = nA + nG if mode == 'pushed' else nA
        if nn == 0:
            continue
        A_eq = [[rows[k][d] for k in range(nn)] for d in range(3)]
        A_eq.append([0.0] * nA + [1.0] * nG if mode == 'pushed' else [1.0] * nA)
        res = linprog(c=[0.0] * nn, A_eq=np.array(A_eq), b_eq=[0, 0, 0, 1.0], bounds=[(0, None)] * nn, method='highs')
        if res.status == 0:
            return mode
    return 'none'


def supply_count(poses, m, Q, cn):
    """Rows available to hold Q at the point: square rows, wall rows, and the certificate mode."""
    P = poses[Q]; C = contacts_of(poses, Q, m)
    A_rows = [(c['F'][0], c['F'][1], (c['point'][0] - P[0]) * c['F'][1] - (c['point'][1] - P[1]) * c['F'][0]) for c in C]
    mu, d, ext, _ = argmin_data(P, cn, m)
    fm, (sx, sy, ox, oy) = frame_pt(cn, m)
    cf = fm((P[0], P[1]))
    G = []
    for p in ext:
        rx, ry = p[0] - cf[0], p[1] - cf[1]
        gx = (sx, 0.0, -sx * sy * ry); gy = (0.0, sy, sx * sy * rx)
        if abs(p[0] - p[1]) < 1e-9:
            G.append(gx); G.append(gy)
        elif p[0] > p[1]:
            G.append(gx)
        else:
            G.append(gy)
    sq = sum(1 for c in C if c['j'] is not None); wl = len(C) - sq
    mode = cone_certificate(A_rows, G)
    return {'sq_rows': sq, 'wall_rows': wl, 'sq_neighbours': len(set(c['j'] for c in C if c['j'] is not None)),
            'mode': mode, 'rank': int(np.linalg.matrix_rank(np.array(A_rows))) if A_rows else 0}


# ============================================================================ EXCHANGE (Lemma EXPOSE, box form)
def frame_to_container(cn, m, u, v, phi):
    sx, sy, fx, fy = FR[cn]
    ox = m if fx else 0.0; oy = m if fy else 0.0
    return (ox + sx * u, oy + sy * v, sx * sy * phi)


def exchange_box(poses, m, cn, radii, G, nsamp, rng):
    """At corner cn: possible meeters on the box; if exactly two, search a re-fit Q0 (frame pose) with the slot
    square S placed, certified on the box."""
    res = {}
    r0 = radii[0]
    pm = G(r0).possible_meeters(cn)
    res['possible_meeters_box'] = pm
    res['meeters_point'] = [i for i, d in meeters(poses, m, cn)]
    if len(pm) <= 1:
        res['verdict'] = 'K0-FREE on the box (<= 1 possible meeter): teleport, no exchange needed'
        return res
    if len(pm) >= 3:
        res['verdict'] = 'not applicable (%d possible meeters on the box)' % len(pm)
        return res
    A, Qi = pm
    untouched = [j for j in range(len(poses)) if j not in (A, Qi)]
    fm, (sx, sy, ox, oy) = frame_pt(cn, m)
    U = [verts(*poses[j]) for j in untouched]

    def f(x):   # frame pose (u, v, phi) -> min separation from untouched squares, slot square, container
        u, v, phi = x
        cpose = frame_to_container(cn, m, u, v, phi)
        P = verts(*cpose)
        val = min(sep(P, Uj) for Uj in U)
        val = min(val, wall_gap(P, m))
        muq = argmin_data(cpose, cn, m)[0]
        val = min(val, muq - 1.0)
        return val

    starts = []
    for j in (A, Qi):
        pf = fm((poses[j][0], poses[j][1])); starts.append((pf[0], pf[1], (sx * sy * poses[j][2]) % (math.pi / 2)))
    for i in range(3):
        for j in range(3):
            if i + j > 0:
                starts.append((i + 0.5, j + 0.5, 0.0))
    for _ in range(12):
        starts.append((rng.uniform(0.5, 3.0), rng.uniform(0.5, 3.0), rng.uniform(0, math.pi / 2)))
    best = None
    for s0 in starts:
        try:
            r_ = minimize(lambda x: -f(x), np.array(s0), method='Nelder-Mead', options={'xatol': 1e-9, 'fatol': 1e-12, 'maxiter': 600})
            val = -r_.fun; x = r_.x
        except Exception:
            continue
        if best is None or val > best[0]:
            best = (val, [float(t) for t in x])
    res['best_refit_margin_point'] = best[0] if best else None
    res['Q0_frame'] = best[1] if best else None
    if best is None or best[0] <= 0:
        res['verdict'] = 'no re-fit with positive margin at the point'
        return res
    # certify on the box: Q0 fixed in the FRAME (moves with the corner as m' varies)
    u, v, phi = best[1]
    cert_r = None
    for r in radii:
        Gb = G(r)
        mI = Gb.m
        sxI = I(sx); syI = I(sy)
        oxI = mI if ox else I(0); oyI = mI if oy else I(0)
        Q0 = SqBox(0, 0, sx * sy * phi, 0)
        Q0.c = (oxI + sxI * u, oyI + syI * v)
        cs, sn = Q0.cs, Q0.sn
        Q0.V = [(Q0.c[0] + (dx * cs - dy * sn) / 2, Q0.c[1] + (dx * sn + dy * cs) / 2) for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        ok = True
        # container
        for (px, py) in Q0.V:
            if not (px.a >= 0 and py.a >= 0 and (mI - px).a >= 0 and (mI - py).a >= 0):
                ok = False
        # slot square: mu_c(Q0) >= 1 exactly (frame pose is fixed)
        (mlo, mhi), _ = depth_cands(Q0, cn, mI)
        if mlo < 1.0 - 1e-15:
            ok = False
        worst = math.inf
        for j in untouched:
            Uj = Gb.S[j]
            best_ax = -math.inf
            for k in range(4):
                s1, _ = pair_axis(Q0, Uj, k, True); best_ax = max(best_ax, lo(s1))
                s2, _ = pair_axis(Uj, Q0, k, True); best_ax = max(best_ax, lo(s2))
            worst = min(worst, best_ax)
        if worst < 0:
            ok = False
        if ok:
            cert_r = r; res['box_margin'] = worst
            break
    res['certified_radius'] = cert_r
    if cert_r is not None:
        # sampled confirmation: untouched squares drawn in the box never overlap Q0
        z = np.asarray(poses); Z = z[None] + rng.uniform(-cert_r, cert_r, size=(nsamp, len(poses), 3))
        M = m + rng.uniform(-cert_r, cert_r, size=nsamp)
        hits = 0
        for t in range(nsamp):
            cpose = frame_to_container(cn, M[t], u, v, phi); P = verts(*cpose)
            if any(sep(P, verts(*Z[t, j])) < 0 for j in untouched) or wall_gap(P, M[t]) < 0 or argmin_data(cpose, cn, M[t])[0] < 1 - 1e-12:
                hits += 1
        res['sample'] = {'drawn': nsamp, 'tested': nsamp, 'hits': hits}
        res['verdict'] = 'EXCHANGE certified on the box r=%g: every packing in B yields a k>=1 packing at the same side' % cert_r
    else:
        res['verdict'] = 'not certified on any box (point margin %.3e)' % best[0]
    return res


# ============================================================================ TWO-WALL (hook family on the box) and the extent bound
def twowall(poses, m, cn, r):
    """Hook detection at corner cn (lockfree.md sect 3.1) with the formula evaluated on the box, plus the
    wall's two-hook bound when the opposite corner of the same wall is a hook too."""
    fm, (sx, sy, ox, oy) = frame_pt(cn, m)
    M = meeters(poses, m, cn)
    hooks = []
    for (N, dN) in M:
        pN = poses[N]
        if min(abs((pN[2] % (math.pi / 2)) - t) for t in (0.0, math.pi / 2)) > 1e-6:
            continue
        W = [fm(v) for v in verts(*pN)]
        for wall in ('u', 'v'):
            if wall == 'u':
                if min(w[0] for w in W) > 1e-6:
                    continue
                vmin = min(w[1] for w in W)
                if not (1e-9 < vmin < 1):
                    continue
                eps = 1.0 - vmin; P = (1.0, vmin)
            else:
                if min(w[1] for w in W) > 1e-6:
                    continue
                umin = min(w[0] for w in W)
                if not (1e-9 < umin < 1):
                    continue
                eps = 1.0 - umin; P = (umin, 1.0)
            for (T, dT) in M:
                if T == N:
                    continue
                WT = [fm(v) for v in verts(*poses[T])]
                floor = min(w[1] for w in WT) if wall == 'u' else min(w[0] for w in WT)
                if floor > 1e-6:
                    continue
                # which edge of T carries P
                for k in range(4):
                    a, b = WT[k], WT[(k + 1) % 4]
                    ex, ey = b[0] - a[0], b[1] - a[1]; L = ex * ex + ey * ey
                    t = max(0.0, min(1.0, ((P[0] - a[0]) * ex + (P[1] - a[1]) * ey) / L))
                    fx, fy = a[0] + t * ex, a[1] + t * ey
                    if math.hypot(P[0] - fx, P[1] - fy) < 1e-6:
                        slope = math.degrees(math.atan2(abs(ey), abs(ex))) if wall == 'u' else math.degrees(math.atan2(abs(ex), abs(ey)))
                        kind = 'alpha' if slope < 45 else 'beta'
                        th = math.radians(slope if kind == 'alpha' else 90 - slope)
                        vlow = min(WT, key=lambda w: w[1] if wall == 'u' else w[0])
                        vx_actual = vlow[0] if wall == 'u' else vlow[1]
                        if kind == 'alpha':
                            vx_formula = 1 + math.tan(th / 2) + (math.cos(th) / math.sin(th)) * eps if th > 1e-12 else float('inf')
                            depthT = None
                        else:
                            vx_formula = 1 + (1 - math.sin(th)) / math.cos(th) + (math.sin(th) / math.cos(th)) * eps
                            depthT = (math.sin(th) / math.cos(th)) * (1 - math.sin(th) - eps)
                        # box evaluation of the formula: eps and theta ranging over +- r (the nick's pose and T's tilt)
                        e_i = I(eps - r, eps + r); t_i = I(th - r, th + r)
                        if kind == 'alpha':
                            vf_i = 1 + iv.tan(t_i / 2) + iv.cos(t_i) / iv.sin(t_i) * e_i
                        else:
                            vf_i = 1 + (1 - iv.sin(t_i)) / iv.cos(t_i) + iv.sin(t_i) / iv.cos(t_i) * e_i
                        hooks.append({'nick': N, 'carrier': T, 'wall': wall, 'kind': kind, 'theta_deg': math.degrees(th), 'eps': eps,
                                      'v_x_actual': vx_actual, 'v_x_formula': vx_formula, 'identity_residual': vx_actual - vx_formula,
                                      'v_x_formula_box': [lo(vf_i), hi(vf_i)], 'carrier_depth_formula': depthT, 'carrier_depth_actual': dT})
    return {'hooks': hooks, 'n_meeters': len(M)}


def extent_bound(poses, m, r):
    """The trivial box inequality m' >= extent of any wall-to-wall union: interval lower bound of the x- and
    y-extent of the whole packing (every packing in B has side >= this)."""
    Gb = BoxGeom(poses, m, r)
    xs = [v[0] for S in Gb.S for v in S.V]; ys = [v[1] for S in Gb.S for v in S.V]
    xmax = max(xs, key=lambda x: x.a); xmin = min(xs, key=lambda x: x.b); ymax = max(ys, key=lambda x: x.a); ymin = min(ys, key=lambda x: x.b)
    ext_x = lo(xmax - xmin); ext_y = lo(ymax - ymin)
    return {'x_extent_lo': ext_x, 'y_extent_lo': ext_y, 'side_lower_bound_on_box': max(ext_x, ext_y),
            'excludes_W': max(ext_x, ext_y) > SHAT}


# ============================================================================ the sample
def snap_tilt(th):
    """Tilt mod pi/2 (a symmetry of the square); a tilt within 1e-12 of the axis is taken as EXACTLY 0."""
    t = th % (math.pi / 2)
    if t < 1e-7 or t > math.pi / 2 - 1e-7:
        return 0.0
    return t


def cell_pose(cn, s, i, j):
    sx, sy, fx, fy = FR[cn]
    ox = s if fx else 0.0; oy = s if fy else 0.0
    return (ox + sx * (i + 0.5), oy + sy * (j + 0.5), 0.0)


def load_sample():
    S = []
    t = json.load(open(os.path.join(ATT, 'A03-upper-reconstruct', 'trump11_exact.json')))
    S.append({'name': 'TRUMP_canary', 'side': float(Fraction(Decimal(t['s']))),
              'poses': [(float(Fraction(Decimal(q['cx']))), float(Fraction(Decimal(q['cy']))), float(Fraction(Decimal(q['theta'])))) for q in t['squares']],
              'note': 'A03 exact data; also the near-packing of cell l1_153 (a Trump-image cell); must be HELD under every move'})
    a = json.load(open(os.path.join(ATT, 'A104-grid-lock', 'results', 'a104_summary.json')))
    for key, nm in (('m_lock_record', 'lock_4.000237'), ('m_lock_certified_record', 'lock_4.001525')):
        v = a[key]
        S.append({'name': nm, 'side': float(v['side']), 'poses': [tuple(float(x) for x in p) for p in v['poses']],
                  'note': 'A104 fully-held boundary packing (%s), exact-certified disjoint' % v['tag']})
    sh = json.load(open(os.path.join(ATT, 'A107-shadow-gallery', 'results', 'shadows_k0.json')))
    cells = {'K01': 'l1_071, l2_p65_101', 'K02': '-', 'K03': 'l2_p65_111', 'K04': 'l1_104', 'K05': 'l2_p74_001', 'K06': 'l1_159', 'K20': 'l2_p114_001', 'K26': 's3_far'}
    import re
    for e in sh:
        if e['id'] not in cells:
            continue
        s = float(e['s']); poses = []
        for nm in e['slots']:
            mm = re.match(r'([A-Z]{2})\((\d),(\d)\)', nm); poses.append(cell_pose(mm.group(1), s, int(mm.group(2)), int(mm.group(3))))
        for (cx, cy, th) in e['free']:
            poses.append((float(cx), float(cy), float(th) % (math.pi / 2)))
        S.append({'name': e['id'], 'side': s, 'poses': poses, 'note': 'A107 k0 shadow (LP support minimised); converged-alive cells: %s' % cells[e['id']]})
    # the fractional converged-alive cells with no A107 shadow: near-packings built by nearpack128.py
    npf = os.path.join(A128, 'results', 'nearpack128.json')
    if os.path.exists(npf):
        for cell, v in json.load(open(npf)).items():
            if v.get('poses'):
                S.append({'name': 'cell_' + cell, 'side': float(v['side']), 'poses': [tuple(p) for p in v['poses']], 'note': v['note']})
    # extras: the two sub-4 strictly K0-BLOCKED corpus packings (A87 exact poses), A103's loader
    A87R = os.path.join(ATT, 'A87-drain-flow', 'results')
    d = json.load(open(os.path.join(A87R, 'k0dir2_87.records.json')))
    for k, v in sorted(d['floors'].items()):
        if not v.get('poses') or k != '1e-03':
            continue
        S.append({'name': 'extra_floor1e-3_%s' % v['tag'], 'side': float(Fraction(v['container_side_exact'])),
                  'poses': [(float(Fraction(p['cx_exact'])), float(Fraction(p['cy_exact'])), float(Fraction(p['theta_exact']))) for p in v['poses']],
                  'note': 'extra row: the 3.9907 strictly K0-BLOCKED record (A87), locked left wall (A105)'})
    dd = json.load(open(os.path.join(A87R, 'k0dir87.json'))); rec = dd['record_K0_BLOCKED_packing']; z = [Fraction(x) for x in rec['z']]
    S.append({'name': 'extra_record_%s' % rec['tag'], 'side': float(z[33]),
              'poses': [(float(z[3 * i]), float(z[3 * i + 1]), float(z[3 * i + 2])) for i in range(11)],
              'note': 'extra row: the 3.98548 record (A87), held bottom wall (A105)'})
    return S


def main():
    args = sys.argv[1:]
    radii = [1e-3, 3e-4, 1e-4, 1e-5, 1e-6]
    nsamp = 10000
    names = []
    i = 0
    while i < len(args):
        if args[i] == '--radii':
            radii = [float(x) for x in args[i + 1].split(',')]; i += 2
        elif args[i] == '--nsamp':
            nsamp = int(args[i + 1]); i += 2
        else:
            names.append(args[i]); i += 1
    S = load_sample()
    if names and names != ['all']:
        S = [s for s in S if s['name'] in names]
    for s in S:
        s['poses'] = [(cx, cy, snap_tilt(th)) for (cx, cy, th) in s['poses']]
    rng = np.random.default_rng(128)
    outs = []
    jl = open(os.path.join(RES, 'moves_geom130.jsonl'), 'a', encoding='utf-8')
    for s in S:
        t0 = time.time()
        o = run_moves(s['name'], s['poses'], s['side'], radii, nsamp, rng, s.get('note', ''))
        o['seconds'] = time.time() - t0; o['radii'] = radii; o['nsamp'] = nsamp
        outs.append(o); jl.write(json.dumps(o) + '\n'); jl.flush()
        log('  [%s done in %.0f s]' % (s['name'], o['seconds']))
    log('all done')


if __name__ == '__main__':
    main()
