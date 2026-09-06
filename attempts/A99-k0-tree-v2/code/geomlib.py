"""A59 leg (b) geometry: the trump5 residual polygon R(s), its 16 anchor elements,
certified centre boxes, per-element capacity caps, and the pairwise tables.

Everything here is a SOUND over-approximation: a box/table entry may admit
configurations that do not exist, but never excludes a realizable one.

s-window  I = [SLO, S0]  with  S0 = 969271/250000 = 3.877084,  SLO = 3.82.
All element positions are AFFINE in s, so the union of a box over a
sub-interval [a,b] of I is the interval hull of its values at a and b.
"""
import math

SQRT2 = math.sqrt(2.0)
HALF = SQRT2 / 2.0                     # circumradius of a unit square
S0 = 969271.0 / 250000.0               # 3.877084
SLO = 3.82
EPS = 1e-9                             # only ever used in the KEEP direction
NSUB = 8                               # s sub-intervals

# tangential separation of two centres on a common segment element:
# normal coords both in [1/2, sqrt2/2] => normal spread <= sqrt2/2 - 1/2,
# centres >= 1 apart  =>  tangential separation >= sqrt(1 - (sqrt2/2-1/2)^2)
TSEP = math.sqrt(1.0 - (HALF - 0.5) ** 2)   # 0.978318...

# ---------------------------------------------------------------- elements
# kind 'v': vertical segment  x = pos(s),  y in [tlo(s), thi(s)]
# kind 'h': horizontal segment y = pos(s), x in [tlo(s), thi(s)]
# side = +1 : free side is the increasing-normal side, -1 : decreasing
# kind 'p': exposed pin corner at (px(s), py(s))
# every affine expression is a pair (a, b) meaning a + b*s
ELEMS = [
    dict(n='A0',  kind='v', pos=(0, 0),  tlo=(2, 0),  thi=(0, 1),  side=+1),
    dict(n='A1',  kind='h', pos=(0, 0),  tlo=(2, 0),  thi=(-1, 1), side=+1),
    dict(n='A2',  kind='v', pos=(0, 1),  tlo=(1, 0),  thi=(-1, 1), side=-1),
    dict(n='A3',  kind='h', pos=(0, 1),  tlo=(0, 0),  thi=(-1, 1), side=-1),
    dict(n='A4',  kind='h', pos=(2, 0),  tlo=(0, 0),  thi=(1, 0),  side=+1),
    dict(n='A5',  kind='v', pos=(1, 0),  tlo=(1, 0),  thi=(2, 0),  side=+1),
    dict(n='A6',  kind='h', pos=(1, 0),  tlo=(1, 0),  thi=(2, 0),  side=+1),
    dict(n='A7',  kind='v', pos=(2, 0),  tlo=(0, 0),  thi=(1, 0),  side=+1),
    dict(n='A8',  kind='v', pos=(-1, 1), tlo=(0, 0),  thi=(1, 0),  side=-1),
    dict(n='A9',  kind='h', pos=(1, 0),  tlo=(-1, 1), thi=(0, 1),  side=+1),
    dict(n='A10', kind='v', pos=(-1, 1), tlo=(-1, 1), thi=(0, 1),  side=-1),
    dict(n='A11', kind='h', pos=(-1, 1), tlo=(-1, 1), thi=(0, 1),  side=-1),
    dict(n='C1',  kind='p', px=(1, 0),   py=(2, 0)),
    dict(n='C2',  kind='p', px=(2, 0),   py=(1, 0)),
    dict(n='C3',  kind='p', px=(-1, 1),  py=(1, 0)),
    dict(n='C4',  kind='p', px=(-1, 1),  py=(-1, 1)),
]
NAMES = [e['n'] for e in ELEMS]
NE = 16
IDX = {n: i for i, n in enumerate(NAMES)}

# boundary-cycle order (theory.md section 0)
CYCLE = [IDX[n] for n in ['A0', 'A3', 'A10', 'C4', 'A11', 'A2', 'A9', 'C3',
                          'A8', 'A1', 'A7', 'C2', 'A6', 'A5', 'C1', 'A4']]
CPOS = [0] * NE
for _p, _e in enumerate(CYCLE):
    CPOS[_e] = _p

# segments that end at an exposed pin corner (used by the contact-attribution rule)
CORNER_ENDPOINTS = {           # element -> list of (corner index)
    IDX['A4']: [IDX['C1']], IDX['A5']: [IDX['C1']],
    IDX['A6']: [IDX['C2']], IDX['A7']: [IDX['C2']],
    IDX['A8']: [IDX['C3']], IDX['A9']: [IDX['C3']],
    IDX['A10']: [IDX['C4']], IDX['A11']: [IDX['C4']],
}


def _rng(expr, a, b):
    v1 = expr[0] + expr[1] * a
    v2 = expr[0] + expr[1] * b
    return (min(v1, v2), max(v1, v2))


CORE = ((0.5, S0 - 0.5), (0.5, S0 - 0.5))


def _isect(b1, b2):
    return ((max(b1[0][0], b2[0][0]), min(b1[0][1], b2[0][1])),
            (max(b1[1][0], b2[1][0]), min(b1[1][1], b2[1][1])))


def empty(b):
    return b[0][0] > b[0][1] + EPS or b[1][0] > b[1][1] + EPS


def centre_box(i, a, b):
    """Certified centre box of a unit square touching element i, for s in [a,b].

    Segment: the contact point q lies on the element and lies in the square, so
    |c-q| <= sqrt2/2; the square lies on the free side of the element's line and
    touches it, so the normal distance |c_n - pos| is the square's half-width in
    that direction, in [1/2, sqrt2/2].  Then the tangential offset satisfies
    |c_t - q_t|^2 <= (sqrt2/2)^2 - (1/2)^2 = 1/4, i.e. |c_t - q_t| <= 1/2.
    Corner: q = C lies on the square's boundary, so |c - C| in [1/2, sqrt2/2];
    the box is the bounding box of that annulus.
    """
    e = ELEMS[i]
    if e['kind'] == 'p':
        px = _rng(e['px'], a, b)
        py = _rng(e['py'], a, b)
        box = ((px[0] - HALF, px[1] + HALF), (py[0] - HALF, py[1] + HALF))
        return _isect(box, CORE)
    p = _rng(e['pos'], a, b)
    tl = _rng(e['tlo'], a, b)
    th = _rng(e['thi'], a, b)
    if e['side'] > 0:
        nr = (p[0] + 0.5, p[1] + HALF)
    else:
        nr = (p[0] - HALF, p[1] - 0.5)
    tr = (tl[0] - 0.5, th[1] + 0.5)
    box = (nr, tr) if e['kind'] == 'v' else (tr, nr)
    return _isect(box, CORE)


def elem_rect(i, a, b):
    """Bounding rectangle of the element's own point set for s in [a,b]."""
    e = ELEMS[i]
    if e['kind'] == 'p':
        return (_rng(e['px'], a, b), _rng(e['py'], a, b))
    p = _rng(e['pos'], a, b)
    tl = _rng(e['tlo'], a, b)
    th = _rng(e['thi'], a, b)
    t = (tl[0], th[1])
    return (p, t) if e['kind'] == 'v' else (t, p)


def pin_positions(a, b):
    """Candidate positions of the five pin centres for s in [a,b].
    Moving pins: |c - P(s)|^2 is convex in s, so the max over s is attained at an
    endpoint -- two endpoint positions suffice for the 'definitely infeasible' test.
    """
    return [[(0.5, 0.5)], [(1.5, 0.5)], [(0.5, 1.5)],
            [(a - 0.5, 0.5), (b - 0.5, 0.5)],
            [(a - 0.5, a - 0.5), (b - 0.5, b - 0.5)]]


# ---------------------------------------------------------------- rect metrics
def rect_min_dist(b1, b2):
    dx = max(0.0, b1[0][0] - b2[0][1], b2[0][0] - b1[0][1])
    dy = max(0.0, b1[1][0] - b2[1][1], b2[1][0] - b1[1][1])
    return math.hypot(dx, dy)


def rect_max_dist(b1, b2):
    dx = max(b1[0][1] - b2[0][0], b2[0][1] - b1[0][0])
    dy = max(b1[1][1] - b2[1][0], b2[1][1] - b1[1][0])
    return math.hypot(dx, dy)


def pt_max_dist(b, p):
    dx = max(abs(b[0][0] - p[0]), abs(b[0][1] - p[0]))
    dy = max(abs(b[1][0] - p[1]), abs(b[1][1] - p[1]))
    return math.hypot(dx, dy)


def hull(b1, b2):
    return ((min(b1[0][0], b2[0][0]), max(b1[0][1], b2[0][1])),
            (min(b1[1][0], b2[1][0]), max(b1[1][1], b2[1][1])))


# ---------------------------------------------------------------- sub-intervals
def subintervals(n=NSUB):
    return [(SLO + (S0 - SLO) * k / n, SLO + (S0 - SLO) * (k + 1) / n)
            for k in range(n)]


class Geometry(object):
    def __init__(self, nsub=NSUB):
        self.subs = subintervals(nsub)
        self.cbox = [[centre_box(i, a, b) for i in range(NE)] for a, b in self.subs]
        self.erect = [[elem_rect(i, a, b) for i in range(NE)] for a, b in self.subs]
        self.pins = [pin_positions(a, b) for a, b in self.subs]
        self.caps = self._caps()

    # -------- capacity caps (see census_report.md, filter 5 proof)
    def _caps(self):
        caps = []
        for i in range(NE):
            if ELEMS[i]['kind'] == 'p':
                caps.append(3)          # proved: 90-degree angular separation in a
                continue                # 180-degree admissible arc => at most 3
            best = 0
            for k, (a, b) in enumerate(self.subs):
                bx = self.cbox[k][i]
                if empty(bx):
                    continue
                span = (bx[1][1] - bx[1][0]) if ELEMS[i]['kind'] == 'v' \
                    else (bx[0][1] - bx[0][0])
                best = max(best, 1 + int(math.floor(span / TSEP + 1e-12)))
            caps.append(max(best, 0))
        return caps

    # -------- per-mask feasibility
    def mask_box(self, bits):
        """(feasible, box) : box = hull over the s sub-intervals in which the mask
        is not provably infeasible.  Returns (False, None) if provably infeasible
        for every sub-interval (hence for the realized s, whatever it is)."""
        acc = None
        for k in range(len(self.subs)):
            bx = CORE
            ok = True
            for i in range(NE):
                if (bits >> i) & 1:
                    bx = _isect(bx, self.cbox[k][i])
                    if empty(bx):
                        ok = False
                        break
            if not ok:
                continue
            # pin exclusion: infeasible only if EVERY point of the box is within
            # distance < 1 of the pin for EVERY admissible pin position
            for pos in self.pins[k]:
                if max(pt_max_dist(bx, p) for p in pos) < 1.0 - EPS:
                    ok = False
                    break
            if not ok:
                continue
            # two contact points lie in one unit square (diameter sqrt2)
            els = [i for i in range(NE) if (bits >> i) & 1]
            for ii in range(len(els)):
                for jj in range(ii + 1, len(els)):
                    if rect_min_dist(self.erect[k][els[ii]],
                                     self.erect[k][els[jj]]) > SQRT2 + EPS:
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                continue
            acc = bx if acc is None else hull(acc, bx)
        return (acc is not None), acc


def interleaves(bits1, bits2):
    """True if the two anchor-element sets alternate around the boundary cycle.
    Then the two squares' contact arcs must cross inside the (simply connected)
    residual polygon => the structure is non-planar with the cycle as outer face.
    """
    s = sorted(CPOS[i] for i in range(NE) if (bits1 >> i) & 1)
    t = sorted(CPOS[i] for i in range(NE) if (bits2 >> i) & 1)
    if len(s) < 2 or len(t) < 2:
        return False
    ts = set(t)
    for ai in range(len(s)):
        for ci in range(ai + 1, len(s)):
            pa, pc = s[ai], s[ci]
            in1 = in2 = False
            for q in ts:
                if q == pa or q == pc:
                    continue
                if pa < q < pc:
                    in1 = True
                else:
                    in2 = True
            if in1 and in2:
                return True
    return False
