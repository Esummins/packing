"""A91 T2 -- the FRAME as a finite object, and the necessary conditions R1-R5.

Definitions: docs/proofs/frame_census.md sections 1-2 (Lemmas F1-F6) and
attempts/A91-frame-census/notes/t2_spec.md.  Nothing here is geometry on a real
packing (that is geom91/canary91); this module is combinatorial + box tests.

Conventions
-----------
corners BL BR TR TL, walls L R B T.  Corner c has a vertical wall VW[c] and a
horizontal wall HW[c]; c's frame axes point AWAY from c:
    BL: +x,+y   BR: -x,+y   TR: -x,-y   TL: +x,-y
A home square of c has type tau in {X,Y,D}: its cardinal retreat set in c's frame
is {x}, {y}, {x,y}.  In container directions Rdir(N) = the corresponding signed
axis directions.  N DEEPENS under a container direction e iff -e in Rdir(N).
"""
from __future__ import annotations

import itertools
import math
from fractions import Fraction

SQRT2 = math.sqrt(2.0)
HALF2 = SQRT2 / 2.0
S_LO, S_HI = 3.82, 3.877084
M0 = 1.0 + 2.0 * SQRT2

CORNERS = ('BL', 'BR', 'TR', 'TL')
WALLS = ('L', 'R', 'B', 'T')
VW = {'BL': 'L', 'BR': 'R', 'TR': 'R', 'TL': 'L'}
HW = {'BL': 'B', 'BR': 'B', 'TR': 'T', 'TL': 'T'}
CWALLS = {c: (VW[c], HW[c]) for c in CORNERS}
WCORN = {'L': ('BL', 'TL'), 'R': ('BR', 'TR'),
         'B': ('BL', 'BR'), 'T': ('TL', 'TR')}
WAXIS = {'L': 'x', 'R': 'x', 'B': 'y', 'T': 'y'}
# container unit direction of corner c's frame axis a (pointing away from c)
DIRV = {}
for _c in CORNERS:
    _sx = 1 if VW[_c] == 'L' else -1
    _sy = 1 if HW[_c] == 'B' else -1
    DIRV[(_c, 'x')] = (_sx, 0)
    DIRV[(_c, 'y')] = (0, _sy)
# far wall reached by moving along (c, axis)
FARWALL = {}
for _c in CORNERS:
    FARWALL[(_c, 'x')] = 'R' if VW[_c] == 'L' else 'L'
    FARWALL[(_c, 'y')] = 'T' if HW[_c] == 'B' else 'B'
# the corner adjacent to c across the OTHER axis (its home squares are excluded
# as middles of a (c, axis) column by Lemma F4)
CROSS = {}
for _c in CORNERS:
    for _a, _o in (('x', 'y'), ('y', 'x')):
        # same far wall on the _o axis, other corner of c's own _a wall
        w = VW[_c] if _a == 'x' else HW[_c]
        CROSS[(_c, _a)] = [q for q in WCORN[w] if q != _c][0]

TAUS = ('X', 'Y', 'D')
AXES_OF = {'X': ('x',), 'Y': ('y',), 'D': ('x', 'y')}


def retreat_dirs(c, tau):
    return tuple(DIRV[(c, a)] for a in AXES_OF[tau])


def deepens_under(c, tau, e):
    """home square of c with type tau deepens under container direction e."""
    me = (-e[0], -e[1])
    return me in retreat_dirs(c, tau)


# --------------------------------------------------------------- D4 action
def _rot(p):
    return (-p[1], p[0])


D4_CORNER = []          # list of dicts corner->corner
D4_WALL = []
D4_DIR = []             # dict (dx,dy)->(dx,dy)
_CPT = {'BL': (-1, -1), 'BR': (1, -1), 'TR': (1, 1), 'TL': (-1, 1)}
_WPT = {'L': (-1, 0), 'R': (1, 0), 'B': (0, -1), 'T': (0, 1)}
_CINV = {v: k for k, v in _CPT.items()}
_WINV = {v: k for k, v in _WPT.items()}
for _k in range(4):
    for _refl in (False, True):
        def _act(p, k=_k, r=_refl):
            q = (p[0], -p[1]) if r else p
            for _ in range(k):
                q = _rot(q)
            return q
        D4_CORNER.append({c: _CINV[_act(_CPT[c])] for c in CORNERS})
        D4_WALL.append({w: _WINV[_act(_WPT[w])] for w in WALLS})
        D4_DIR.append({d: _act(d) for d in ((1, 0), (-1, 0), (0, 1), (0, -1))})


def d4_tau(g, c, tau):
    """types transform as directions: tau at c -> tau' at g(c)."""
    c2 = D4_CORNER[g][c]
    axes = set()
    for a in AXES_OF[tau]:
        d2 = D4_DIR[g][DIRV[(c, a)]]
        for a2 in ('x', 'y'):
            if DIRV[(c2, a2)] == d2:
                axes.add(a2)
    if axes == {'x'}:
        return 'X'
    if axes == {'y'}:
        return 'Y'
    return 'D'


# ================================================================== the frame
class Frame:
    """role/type/mask/terminal/column data on n squares (default 11)."""

    def __init__(self, n=11):
        self.n = n
        self.home = [None] * n          # corner or None
        self.open = [False] * n         # open intruder (home and d>0)
        self.tau = [None] * n           # for home squares
        self.mask = [frozenset() for _ in range(n)]
        self.terminal = {}              # slot -> (N, kind) kind in 'W','I'
        self.column = {}                # slot -> tuple(Q,...,Nk)
        self.ghost = {}                 # slot -> bool (2-member W column)

    # ---- derived
    def is_free(self, i):
        return self.home[i] is None

    def intruders(self, c):
        return [i for i in range(self.n) if self.home[i] == c and self.open[i]]

    def home_of(self, c):
        return [i for i in range(self.n) if self.home[i] == c]

    def pattern(self):
        return tuple(len(self.intruders(c)) for c in CORNERS)

    def slots(self):
        out = []
        for i in range(self.n):
            if self.home[i] is not None and self.open[i]:
                for a in AXES_OF[self.tau[i]]:
                    out.append((i, a))
        return out

    def edir(self, slot):
        Q, a = slot
        return DIRV[(self.home[Q], a)]

    def farwall(self, slot):
        Q, a = slot
        return FARWALL[(self.home[Q], a)]

    def wall_squares(self, w):
        return [i for i in range(self.n) if w in self.mask[i]]

    # ---- admissible terminals (Lemma F3 a/b)
    def term_candidates(self, slot):
        """list of (N, kind) admissible by F3(a) (W) and F3(b) (I)."""
        Q, a = slot
        c = self.home[Q]
        w = FARWALL[(c, a)]
        e = DIRV[(c, a)]
        out = []
        for N in range(self.n):
            if N == Q:
                continue
            if w in self.mask[N]:
                out.append((N, 'W'))
        for N in range(self.n):
            if N == Q or self.home[N] is None or self.home[N] == c:
                continue
            if self.home[N] not in WCORN[w]:
                continue
            if deepens_under(self.home[N], self.tau[N], e):
                out.append((N, 'I'))
        return out

    def middle_candidates(self, slot):
        """Lemma F4: a middle of a (W)-column is not a home square of c nor of
        CROSS(c,axis), and touches no far wall (minimality)."""
        Q, a = slot
        c = self.home[Q]
        w = FARWALL[(c, a)]
        bad = {c, CROSS[(c, a)]}
        return [N for N in range(self.n)
                if N != Q and w not in self.mask[N] and self.home[N] not in bad]

    def copy(self):
        f = Frame(self.n)
        f.home = list(self.home)
        f.open = list(self.open)
        f.tau = list(self.tau)
        f.mask = list(self.mask)
        f.terminal = dict(self.terminal)
        f.column = dict(self.column)
        f.ghost = dict(self.ghost)
        return f

    def to_dict(self):
        return {'n': self.n, 'home': self.home, 'open': self.open,
                'tau': self.tau, 'mask': [sorted(m) for m in self.mask],
                'terminal': {'%d%s' % s: list(v) for s, v in self.terminal.items()},
                'column': {'%d%s' % s: list(v) for s, v in self.column.items()},
                'ghost': {'%d%s' % s: v for s, v in self.ghost.items()}}


# ============================================================ R1 .. R5
def R1(f, wall_cap=3):
    """masks / roles (Lemma F1(iii), F2)."""
    bad = []
    for c in CORNERS:
        if len(f.intruders(c)) < 2:
            bad.append('K0BLOCKED:%s has %d open intruders' % (c, len(f.intruders(c))))
        both = [i for i in f.home_of(c) if f.mask[i] == frozenset(CWALLS[c])]
        if len(both) > 1:
            bad.append('R1d:%s has %d both-wall home squares' % (c, len(both)))
        for i in both:
            if not f.open[i]:
                bad.append('R1e:sq%d both walls at %s but not an open intruder' % (i, c))
    for i in range(f.n):
        h = f.home[i]
        if h is None:
            if len(f.mask[i]) > 1:
                bad.append('R1f:free sq%d touches %d walls' % (i, len(f.mask[i])))
        else:
            if not f.mask[i] <= frozenset(CWALLS[h]):
                bad.append('R1c:sq%d home %s mask %s' % (i, h, sorted(f.mask[i])))
    for w in WALLS:
        sq = f.wall_squares(w)
        if len(sq) > wall_cap:
            bad.append('R1a:wall %s has %d squares' % (w, len(sq)))
        fr = [i for i in sq if f.home[i] is None]
        if len(fr) > 1:
            bad.append('R1b:wall %s has %d free squares' % (w, len(fr)))
    return bad


def R2(f):
    """every slot has an admissible terminal, and the recorded one is admissible."""
    bad = []
    for s in f.slots():
        cand = f.term_candidates(s)
        if not cand:
            bad.append('R2:no admissible terminal for slot %s' % (s,))
        if s in f.terminal and tuple(f.terminal[s]) not in [tuple(x) for x in cand]:
            bad.append('R2:recorded terminal %s inadmissible for slot %s'
                       % (f.terminal[s], s))
    return bad


def R3(f, ghost_ok=False):
    """Lemma COL / F4: W-columns >= 3 members, I-columns >= 2."""
    bad = []
    for s in f.slots():
        if s not in f.terminal:
            continue
        N, kind = f.terminal[s]
        if kind == 'W':
            if not f.middle_candidates(s) and not (ghost_ok and f.ghost.get(s)):
                bad.append('R3:no admissible middle for W-slot %s' % (s,))
        if s in f.column:
            col = f.column[s]
            need = 2 if kind == 'I' else (2 if (ghost_ok and f.ghost.get(s)) else 3)
            if len(col) < need:
                bad.append('R3:column %s has %d members (need %d)'
                           % (s, len(col), need))
            if len(set(col)) != len(col):
                bad.append('R3:column %s repeats a member' % (s,))
            if col[0] != s[0] or col[-1] != N:
                bad.append('R3:column %s endpoints wrong' % (s,))
    return bad


def R4(f):
    """Lemma F3(c) mutuality.  Reported, never a kill (PLATEAU is a refinement
    that the census does NOT use)."""
    rows = []
    for s in f.slots():
        if s not in f.terminal:
            continue
        N, kind = f.terminal[s]
        if kind != 'I':
            continue
        Q, a = s
        c = f.home[Q]
        e = DIRV[(c, a)]
        cN = f.home[N]
        # the reverse slot of N
        rev = [b for b in AXES_OF[f.tau[N]] if DIRV[(cN, b)] == (-e[0], -e[1])]
        ok = bool(rev) and f.open[N]
        rows.append({'slot': s, 'N': N, 'N_open': f.open[N],
                     'rev_slot': (N, rev[0]) if rev else None,
                     'mutual_slot_exists': ok,
                     'rate_x': 1.0 if f.tau[N] in ('X', 'Y') else None,
                     'plateau_candidate': bool(
                         ok and f.tau[N] in ('X', 'Y') and f.tau[Q] in ('X', 'Y'))})
    return rows


# ---------------------------------------------------------------- R5 boxes
def cbox(f, i, m_lo=S_LO, m_hi=S_HI):
    """sound centre box [xlo,xhi] x [ylo,yhi] of square i over m in [m_lo,m_hi]."""
    xlo, xhi = 0.5, m_hi - 0.5
    ylo, yhi = 0.5, m_hi - 0.5
    m = f.mask[i]
    if 'L' in m:
        xhi = min(xhi, HALF2)
    if 'R' in m:
        xlo = max(xlo, m_lo - HALF2)
        xhi = min(xhi, m_hi - 0.5)
    if 'B' in m:
        yhi = min(yhi, HALF2)
    if 'T' in m:
        ylo = max(ylo, m_lo - HALF2)
        yhi = min(yhi, m_hi - 0.5)
    h = f.home[i]
    if h is not None:
        # home square of h: centre in h + [1/2, 1+sqrt2/2]^2 in h's frame
        U = 1.0 + HALF2
        if VW[h] == 'L':
            xhi = min(xhi, U)
        else:
            xlo = max(xlo, m_lo - U)
        if HW[h] == 'B':
            yhi = min(yhi, U)
        else:
            ylo = max(ylo, m_lo - U)
    return (xlo, xhi, ylo, yhi)


def box_ok(b):
    return b[0] <= b[1] + 1e-12 and b[2] <= b[3] + 1e-12


def _free_feasible(b, m_lo=S_LO, ngrid=12):
    """some point of box b has dist >= 1/2 from EVERY corner box [0,1]^2 of the
    container (sound necessary condition for a FREE square: mu_c > 1 for all c).
    Grid-sound: a cell is kept only if its most favourable point works."""
    xlo, xhi, ylo, yhi = b
    if not box_ok(b):
        return False
    m = m_lo
    for ix in range(ngrid):
        x0 = xlo + (xhi - xlo) * ix / ngrid
        x1 = xlo + (xhi - xlo) * (ix + 1) / ngrid
        for iy in range(ngrid):
            y0 = ylo + (yhi - ylo) * iy / ngrid
            y1 = ylo + (yhi - ylo) * (iy + 1) / ngrid
            ok = True
            for c in CORNERS:
                # in c's frame the corner box is [0,1]^2; use the cell's best point
                px = (x0, x1) if VW[c] == 'L' else (m - x1, m - x0)
                py = (y0, y1) if HW[c] == 'B' else (m - y1, m - y0)
                dx = max(0.0, px[1] - 1.0)
                dy = max(0.0, py[1] - 1.0)
                if dx * dx + dy * dy < 0.25 - 1e-12:
                    ok = False
                    break
            if ok:
                return True
    return False


def _bxdist(b1, b2):
    """(min, max) centre distance between two boxes."""
    dxmin = max(0.0, b1[0] - b2[1], b2[0] - b1[1])
    dymin = max(0.0, b1[2] - b2[3], b2[2] - b1[3])
    dxmax = max(b1[1] - b2[0], b2[1] - b1[0])
    dymax = max(b1[3] - b2[2], b2[3] - b1[2])
    return math.hypot(dxmin, dymin), math.hypot(dxmax, dymax)


def _dot_range(b1, b2, e):
    """range of (c2 - c1).e over the boxes."""
    lo = hi = 0.0
    for k, (a1, a2, c1, c2) in enumerate(((b1[0], b1[1], b2[0], b2[1]),
                                          (b1[2], b1[3], b2[2], b2[3]))):
        w = e[k]
        vals = [w * (c1 - a2), w * (c2 - a1), w * (c1 - a1), w * (c2 - a2)]
        lo += min(vals)
        hi += max(vals)
    return lo, hi


def R5(f, m_lo=S_LO, m_hi=S_HI, use_bbox_free=False):
    """box-level necessary conditions (Lemma F6 + the A88 label boxes)."""
    bad = []
    B = [cbox(f, i, m_lo, m_hi) for i in range(f.n)]
    for i in range(f.n):
        if not box_ok(B[i]):
            bad.append('R5:empty centre box for sq%d' % i)
            continue
        if f.home[i] is None:
            if use_bbox_free:
                # A88-style bounding-box variant (NOT sound; reported as a flag)
                pass
            if not _free_feasible(B[i], m_lo):
                bad.append('R5:free sq%d cannot avoid every corner box' % i)
    for s, (N, kind) in f.terminal.items():
        Q = s[0]
        if s in f.column and len(f.column[s]) == 3:
            lo, hi = _bxdist(B[Q], B[N])
            if lo > 2 * SQRT2 + 1e-12:
                bad.append('R5:3-column terminal %d too far from %d (%.4f>2sqrt2)'
                           % (N, Q, lo))
    for s, col in f.column.items():
        e = f.edir(s)
        for a, b in zip(col[:-1], col[1:]):
            lo, hi = _bxdist(B[a], B[b])
            if lo > SQRT2 + 1e-12:
                bad.append('R5:link %d->%d box distance %.4f > sqrt2' % (a, b, lo))
            dlo, dhi = _dot_range(B[a], B[b], e)
            if dhi <= -1.0 + 1e-12:
                bad.append('R5:link %d->%d cannot have (c_N-c_M).e > -1' % (a, b))
    return bad


# ------------------------------------------------------- sign consistency (L3)
def sign_consistency(f):
    """every unordered link pair carries ONE sign class sigma(M,N) in
    {-,0,+}^2 \\ {(0,0)}; N presses M against e iff n_M . e < 0 where n_M has
    signs sigma(M,N).  Returns (ok, assignment or conflict list)."""
    need = {}
    for s, col in f.column.items():
        e = f.edir(s)
        for M, N in zip(col[:-1], col[1:]):
            need.setdefault((min(M, N), max(M, N)), []).append((M, N, e))
    out = {}
    conflicts = []
    for key, reqs in need.items():
        ok = []
        for sx in (-1, 0, 1):
            for sy in (-1, 0, 1):
                if sx == 0 and sy == 0:
                    continue
                good = True
                for (M, N, e) in reqs:
                    nM = (sx, sy) if M == key[0] else (-sx, -sy)
                    if nM[0] * e[0] + nM[1] * e[1] >= 0:
                        good = False
                        break
                if good:
                    ok.append((sx, sy))
        if not ok:
            conflicts.append((key, reqs))
        else:
            out[key] = ok
    return (not conflicts), out, conflicts


# ------------------------------------------------------------- canonical form
def canon_key(f, level='L1', want_orbit=False):
    """canonical form under G = (prod_c S_{n_c} x S_f) x D4 with n_c = the OPEN
    intruders of c and f = the 11 - sum n_c non-open squares (tangency is a
    COLOUR on a free square, so S_f permutes tangent and plain free alike).
    Returns the canonical key, or (key, orbit_size) if want_orbit."""
    best = None
    seen = set()
    n = f.n
    for g in range(8):
        home2 = [None if h is None else D4_CORNER[g][h] for h in f.home]
        tau2 = [None if f.home[i] is None else d4_tau(g, f.home[i], f.tau[i])
                for i in range(n)]
        mask2 = [frozenset(D4_WALL[g][w] for w in f.mask[i]) for i in range(n)]
        classes = {}
        for i in range(n):
            classes.setdefault(
                (str(home2[i]), True) if f.open[i] else ('FREE', False),
                []).append(i)
        order = sorted(classes)
        groups = [classes[k] for k in order]
        for perms in itertools.product(*[itertools.permutations(gp) for gp in groups]):
            pos = {}
            k = 0
            for gp in perms:
                for i in gp:
                    pos[i] = k
                    k += 1
            sq = [None] * n
            for i in range(n):
                sq[pos[i]] = (str(home2[i]), f.open[i], str(tau2[i]),
                              tuple(sorted(mask2[i])))
            key = [tuple(sq)]
            if level in ('L1', 'L2', 'L3'):
                tt = []
                for (Q, a) in sorted(f.slots()):
                    a2 = a
                    if home2[Q] is not None:
                        d2 = D4_DIR[g][DIRV[(f.home[Q], a)]]
                        a2 = 'x' if DIRV[(home2[Q], 'x')] == d2 else 'y'
                    v = f.terminal.get((Q, a))
                    tt.append((pos[Q], a2, None if v is None else (pos[v[0]], v[1])))
                key.append(tuple(sorted(tt)))
            if level in ('L2', 'L3'):
                cc = []
                for (Q, a) in sorted(f.slots()):
                    col = f.column.get((Q, a))
                    a2 = a
                    if home2[Q] is not None:
                        d2 = D4_DIR[g][DIRV[(f.home[Q], a)]]
                        a2 = 'x' if DIRV[(home2[Q], 'x')] == d2 else 'y'
                    if col is None:
                        cc.append((pos[Q], a2, None))
                    elif level == 'L2':
                        cc.append((pos[Q], a2, pos[col[1]] if len(col) > 1 else None))
                    else:
                        cc.append((pos[Q], a2, tuple(pos[v] for v in col)))
                key.append(tuple(sorted(cc)))
            key = tuple(key)
            if want_orbit:
                seen.add(key)
            if best is None or key < best:
                best = key
    return (best, len(seen)) if want_orbit else best


def orbit_size(f, level='L1'):
    return canon_key(f, level, want_orbit=True)[1]
