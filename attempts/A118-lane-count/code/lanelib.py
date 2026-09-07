"""A118 LANE-COUNT: the geometry of "how many non-pin squares can reach a usable cell".

Everything here is a SOUND OVER-approximation of the reachable set R(C) and therefore a sound
UPPER bound on LANE(C) = the maximum number of pairwise interior-disjoint unit squares whose
poses lie in R(C).  A LANE <= 1 verdict is the kill; LANE >= 2 verdicts carry two explicit
witness poses.

Conventions (docs/proofs/slot_crowds.md, docs/proofs/k0_route.md):
  * cell (corner c, offsets i, j): the closed unit cell at c's slot (i, j);
  * corner frame  u = x or s-x,  v = y or s-y;  slot frame  x' = u - i,  y' = v - j;
  * depth functional  mu_p(Q) = min_{q in Q} max(x'(q), y'(q));
    "Q meets the closed slot box"  <=>  mu_p(Q) <= 1  (with Lemma CONT).
  * the licensed family is F_p(a_w) = {Q admissible : mu_p(Q) <= a_w}; a_w is the dilation pad
    (Lemma B-YES-S), computed per campaign in lane.py.

R(C) := { poses (cx, cy, theta) : Q(c,theta) subset [0,s]^2,
                                  mu_p(Q) <= a_w,
                                  int Q disjoint from every hypothesis core }.

Sound because every non-pin square of the (dilated) family that meets the cell is admissible,
lies in F_p(a_w) and is interior-disjoint from every core (the cores are contained in the
squares that realise them, and a free square is a DIFFERENT square from every core-realiser --
A57's node semantics, guarded by pinguard).
"""
import math

import numpy as np

SQ2 = math.sqrt(2.0)
S0 = 969271.0 / 250000.0            # 3.877084
SHAT = 3.877083590022814
WLO = 3.82                          # window floor


# ------------------------------------------------------------------ cells and frames
def frame(corner, i, j, s):
    """(sx, vx, sy, vy) with x' = sx*(x - vx), y' = sy*(y - vy)."""
    if corner == "BL":
        return (1.0, float(i), 1.0, float(j))
    if corner == "BR":
        return (-1.0, s - i, 1.0, float(j))
    if corner == "TR":
        return (-1.0, s - i, -1.0, s - j)
    if corner == "TL":
        return (1.0, float(i), -1.0, s - j)
    raise ValueError(corner)


def cell_centre(corner, i, j, s):
    sx, vx, sy, vy = frame(corner, i, j, s)
    return (vx + sx * 0.5, vy + sy * 0.5)


def parse_cell(name):
    """'BL(1,0)' -> ('BL', 1, 0)"""
    c = name[:2]
    i, j = name[3:-1].split(",")
    return c, int(i), int(j)


# ------------------------------------------------------------------ mu_p, vectorised
def mu_many(C, TH, fr):
    """mu_p(Q(c, theta)) for centres C (m,2) and tilts TH (m,) in RADIANS.

    max(x', y') is convex piecewise linear on the square, so its minimum over the square is
    attained at a vertex or where x' = y' on an edge.  Both are evaluated exactly.
    """
    sx, vx, sy, vy = fr
    C = np.asarray(C, float).reshape(-1, 2)
    TH = np.asarray(TH, float).reshape(-1)
    co, si = np.cos(TH), np.sin(TH)
    # the four vertices
    VX = np.empty((len(TH), 4)); VY = np.empty((len(TH), 4))
    for k, (dx, dy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        px = C[:, 0] + 0.5 * (dx * co - dy * si)
        py = C[:, 1] + 0.5 * (dx * si + dy * co)
        VX[:, k] = sx * (px - vx)
        VY[:, k] = sy * (py - vy)
    best = np.max(np.stack([VX, VY], 0), axis=0).min(axis=1)
    # edge crossings of x' = y'
    D = VX - VY
    for k in range(4):
        l = (k + 1) % 4
        d0, d1 = D[:, k], D[:, l]
        den = d0 - d1
        with np.errstate(divide="ignore", invalid="ignore"):
            t = np.where(np.abs(den) > 1e-15, d0 / den, -1.0)
        ok = (t >= 0.0) & (t <= 1.0) & (np.abs(den) > 1e-15)
        val = VX[:, k] + t * (VX[:, l] - VX[:, k])
        best = np.where(ok, np.minimum(best, val), best)
    return best


def mu_lower_box(b, fr):
    """A sound LOWER bound on mu_p over every pose in the parameter box b.

    x'(q) >= sx*(cx - vx) - h(theta), h(theta) = (|cos|+|sin|)/2 <= sqrt(2)/2, so
    mu_p(Q) >= max(sx*(cx-vx), sy*(cy-vy)) - h_max(theta-range).
    """
    hmax = 0.5 * max_cs(b.th0, b.th1)
    if b.x1 - b.x0 < 0 or b.y1 - b.y0 < 0:
        return 1e9
    sx, vx, sy, vy = fr
    ax = min(sx * (b.x0 - vx), sx * (b.x1 - vx))     # min over the x-range of sx*(cx-vx)
    ay = min(sy * (b.y0 - vy), sy * (b.y1 - vy))
    # min over the centre box of max(ax_term, ay_term) is attained at the corner minimising both
    return max(ax, ay) - hmax


def _cs(deg):
    r = math.radians(deg)
    return abs(math.cos(r)) + abs(math.sin(r))


def max_cs(d0, d1):
    """max of |cos|+|sin| over [d0, d1] degrees (endpoints and every 45 deg mod 90)."""
    best = max(_cs(d0), _cs(d1))
    k = math.floor(d0 / 90.0)
    while k * 90.0 + 45.0 <= d1 + 1e-12:
        c = k * 90.0 + 45.0
        if c >= d0 - 1e-12:
            best = max(best, _cs(c))
        k += 1
    return best


def min_cs(d0, d1):
    """min of |cos|+|sin| over [d0, d1] degrees (unimodal on any 90-window: endpoints, plus
    0/90 multiples inside the range)."""
    best = min(_cs(d0), _cs(d1))
    k = math.ceil(d0 / 90.0)
    while k * 90.0 <= d1 + 1e-12:
        best = min(best, _cs(k * 90.0))
        k += 1
    return best


# ------------------------------------------------------------------ tight core (A96 T5')
def tight_a(b, theta_m_deg):
    """A96 core96.tight_a: the tight common-inscribed half-side of box b at core tilt theta_m."""
    h = max(0.5 * (b.x1 - b.x0), 0.5 * (b.y1 - b.y0))
    Mc = max_cs(b.th0, b.th1)
    phi0, phi1 = b.th0 - theta_m_deg, b.th1 - theta_m_deg
    lo, hi = min(phi0, phi1), max(phi0, phi1)
    Mt = max(_cs(lo), _cs(hi))
    if lo <= 0.0 <= hi:
        Mt = max(Mt, 1.0)
    return (0.5 - h * Mc) / Mt


class Sq:
    """a rotated square: centre (x, y), tilt th (radians), half-side a."""
    __slots__ = ("x", "y", "th", "a")

    def __init__(self, x, y, th, a):
        self.x, self.y, self.th, self.a = float(x), float(y), float(th), float(a)


def tight_core_of_box(b, margin=1e-9):
    """A96's tight core of an A57 Box, as a Sq; None if empty.  Half-side asserted <= 1/2."""
    tm = 0.5 * (b.th0 + b.th1)
    a = tight_a(b, tm) - margin
    if a <= 0:
        return None
    assert a <= 0.5 + 1e-12, "core half-side > 1/2"
    return Sq(0.5 * (b.x0 + b.x1), 0.5 * (b.y0 + b.y1), math.radians(tm), a)


# ------------------------------------------------------------------ SAT overlap
def sq_gap(A, B):
    """separating-axis gap between two rotated squares (>0 disjoint, <0 overlapping interiors)."""
    best = -1e9
    for (P, Q) in ((A, B), (B, A)):
        c, s = math.cos(P.th), math.sin(P.th)
        oc, os_ = math.cos(Q.th), math.sin(Q.th)
        for ax, ay in ((c, s), (-s, c)):
            d = abs((Q.x - P.x) * ax + (Q.y - P.y) * ay)
            sup = Q.a * (abs(ax * oc + ay * os_) + abs(-ax * os_ + ay * oc))
            best = max(best, d - P.a - sup)
    return best


def gap_pose_vs_core(C, TH, K):
    """vectorised SAT gap between unit squares at (C, TH radians) and a fixed core Sq K."""
    C = np.asarray(C, float).reshape(-1, 2)
    TH = np.asarray(TH, float).reshape(-1)
    co, si = np.cos(TH), np.sin(TH)
    kc, ks = math.cos(K.th), math.sin(K.th)
    dx = K.x - C[:, 0]; dy = K.y - C[:, 1]
    best = np.full(len(TH), -1e9)
    # axes of the unit square
    for ax, ay in ((co, si), (-si, co)):
        d = np.abs(dx * ax + dy * ay)
        sup = K.a * (np.abs(ax * kc + ay * ks) + np.abs(-ax * ks + ay * kc))
        best = np.maximum(best, d - 0.5 - sup)
    # axes of the core
    for ax, ay in ((kc, ks), (-ks, kc)):
        d = np.abs(dx * ax + dy * ay)
        sup = 0.5 * (np.abs(ax * co + ay * si) + np.abs(-ax * si + ay * co))
        best = np.maximum(best, d - K.a - sup)
    return best


def pair_gaps(C, TH):
    """full pairwise SAT gap matrix for unit squares at (C, TH radians)."""
    C = np.asarray(C, float).reshape(-1, 2)
    TH = np.asarray(TH, float).reshape(-1)
    n = len(TH)
    co, si = np.cos(TH), np.sin(TH)
    dx = C[None, :, 0] - C[:, None, 0]
    dy = C[None, :, 1] - C[:, None, 1]
    best = np.full((n, n), -1e9)
    for (axc, ays, other) in ((co, si, 1), (-si, co, 1)):
        ax = axc[:, None]; ay = ays[:, None]
        d = np.abs(dx * ax + dy * ay)
        sup = 0.5 * (np.abs(ax * co[None, :] + ay * si[None, :])
                     + np.abs(-ax * si[None, :] + ay * co[None, :]))
        best = np.maximum(best, d - 0.5 - sup)
    for (axc, ays) in ((co, si), (-si, co)):
        ax = axc[None, :]; ay = ays[None, :]
        d = np.abs(dx * ax + dy * ay)
        sup = 0.5 * (np.abs(ax * co[:, None] + ay * si[:, None])
                     + np.abs(-ax * si[:, None] + ay * co[:, None]))
        best = np.maximum(best, d - 0.5 - sup)
    return best


# ------------------------------------------------------------------ R(C) membership
def cell_square(fr):
    """The cell itself, as a Sq: the unit cell [i, i+1] x [j, j+1] of the corner frame."""
    sx, vx, sy, vy = fr
    return Sq(vx + sx * 0.5, vy + sy * 0.5, 0.0, 0.5)


def centre_window(fr, a_w, s):
    """Bounding rectangle of the centres of poses that MEET the cell: |cx - cellx| <= 1/2 +
    h(theta) <= 1/2 + sqrt(2)/2, intersected with the container's centre domain."""
    K = cell_square(fr)
    hi = 0.5 + SQ2 / 2.0
    return (max(0.5, K.x - hi), min(s - 0.5, K.x + hi),
            max(0.5, K.y - hi), min(s - 0.5, K.y + hi))


def box_always_misses_cell(b, fr, eps=1e-12):
    """True if EVERY pose in b gives a square disjoint (open interiors) from the cell -- a sound
    prune.  A single separating axis certified over the whole box suffices; the cell's own two
    normals are the axis-aligned ones, and the moving square's normals are bounded as in
    box_always_hits_core."""
    K = cell_square(fr)
    hmax = 0.5 * max_cs(b.th0, b.th1)
    if (b.x0 - hmax >= K.x + 0.5 - eps or b.x1 + hmax <= K.x - 0.5 + eps
            or b.y0 - hmax >= K.y + 0.5 - eps or b.y1 + hmax <= K.y - 0.5 + eps):
        return True
    return False


def cont_frames(fr, rho):
    """The two shifted frames whose mu >= 0 expresses Lemma CONT (Q avoids R_p), with an outward
    margin rho for the dilation drift.

    R_p^rho = {x' < -rho, y' < 1-rho} u {y' < -rho, x' < 1-rho}; "Q misses R_p^rho" is
    min_Q max(x'+rho, y'-1+rho) >= 0 and min_Q max(y'+rho, x'-1+rho) >= 0, i.e. mu >= 0 in the
    two frames below.
    """
    sx, vx, sy, vy = fr
    f1 = (sx, vx - sx * rho, sy, vy + sy * (1.0 - rho))
    f2 = (sx, vx + sx * (1.0 - rho), sy, vy - sy * rho)
    return f1, f2


INR = 0.5 / SQ2                    # the inscribed disc of a unit square has radius 1/2, so the
                                   # point c - (sx, sy) * INR lies in Q for EVERY tilt


def mu_upper_box(b, g):
    """A sound UPPER bound on mu (in the frame g) over every pose in the box b: mu(Q) is at most
    max(x', y') at any point of Q, and c - (sx, sy)*INR is in Q at every tilt."""
    sx, vx, sy, vy = g
    ax = max(sx * (b.x0 - vx), sx * (b.x1 - vx))
    ay = max(sy * (b.y0 - vy), sy * (b.y1 - vy))
    return max(ax, ay) - INR


def box_cont_fails(b, fr, rho, eps=1e-12):
    """True if EVERY pose in b violates Lemma CONT -- a sound prune."""
    for g in cont_frames(fr, rho):
        if mu_upper_box(b, g) < -eps:
            return True
    return False


def in_R(C, TH, fr, a_w, cores, s, eps=1e-9, rho=None):
    """boolean mask: poses in R(C).  Container test uses the exact half-extent; every tolerance
    is in the KEEP direction (R(C) is only ever enlarged, which is the sound direction for an
    upper bound on LANE)."""
    C = np.asarray(C, float).reshape(-1, 2)
    TH = np.asarray(TH, float).reshape(-1)
    h = 0.5 * (np.abs(np.cos(TH)) + np.abs(np.sin(TH)))
    ok = ((C[:, 0] >= h - eps) & (C[:, 0] <= s - h + eps)
          & (C[:, 1] >= h - eps) & (C[:, 1] <= s - h + eps))
    if not ok.any():
        return ok
    # "meets the cell", open interiors: the SAT gap against the unit cell is negative
    ok &= (gap_pose_vs_core(C, TH, cell_square(fr)) < eps)
    if rho is not None:
        for g in cont_frames(fr, rho):
            if not ok.any():
                break
            ok &= (mu_many(C, TH, g) >= -eps)
    for K in cores:
        if not ok.any():
            break
        ok &= (gap_pose_vs_core(C, TH, K) >= -eps)
    return ok


# ------------------------------------------------------------------ the pair test (T5''-style)
def _max_abs_proj(D, th0, th1):
    """max over d in the interval box D = (dx0, dx1, dy0, dy1) and over the two edge normals of
    a square with tilt theta in [th0, th1] (degrees) of |n . d|.

    |n(theta) . d| is convex in d (an absolute value of a linear form), so the max over the box
    is at a corner; for a fixed corner it is R*|cos(theta - phi)|, maximised at an endpoint of
    the theta range or at theta = phi (mod 90, because BOTH normals are taken).
    """
    dx0, dx1, dy0, dy1 = D
    a0, a1 = math.radians(th0), math.radians(th1)
    best = 0.0
    for dx in (dx0, dx1):
        for dy in (dy0, dy1):
            R = math.hypot(dx, dy)
            if R == 0.0:
                continue
            phi = math.atan2(dy, dx)
            cand = [a0, a1]
            # theta = phi + k*90 deg inside [a0, a1]
            base = phi - math.pi / 2 * math.ceil((phi - a0) / (math.pi / 2))
            t = base
            while t <= a1 + 1e-15:
                if t >= a0 - 1e-15:
                    cand.append(t)
                t += math.pi / 2
            for th in cand:
                v = max(abs(dx * math.cos(th) + dy * math.sin(th)),
                        abs(-dx * math.sin(th) + dy * math.cos(th)))
                best = max(best, v)
    return best


def pair_always_overlap(b1, b2, eps=1e-12):
    """True if EVERY pose in b1 and EVERY pose in b2 give unit squares with overlapping interiors.

    A separating axis must be an edge normal of one of the two squares.  Along an edge normal n
    of square 1, the SAT gap is |n.(c2-c1)| - 1/2 - 1/2*(|cos D| + |sin D|) with D = th2 - th1
    the relative tilt; bounding |n.(c2-c1)| above by interval arithmetic and (|cos D| + |sin D|)
    below by its minimum over the relative tilt range gives a sound upper bound on the gap.  If
    the bound is negative for BOTH normal families, no separating axis exists.
    """
    D = (b2.x0 - b1.x1, b2.x1 - b1.x0, b2.y0 - b1.y1, b2.y1 - b1.y0)
    m = min_cs(b2.th0 - b1.th1, b2.th1 - b1.th0)
    lim = 0.5 + 0.5 * m
    u1 = _max_abs_proj(D, b1.th0, b1.th1)
    if u1 - lim >= -eps:
        return False
    u2 = _max_abs_proj(D, b2.th0, b2.th1)
    return (u2 - lim < -eps)


def pairs_always_overlap_matrix(boxes, eps=1e-12):
    """Vectorised, sound version of pair_always_overlap over a whole cover.

    Uses the coarser but fully vectorisable projection bound |n.d| <= |d|:
        gap <= |d|_max - 1/2 - 1/2*(min over the relative tilt range of |cos|+|sin|),
    so the pair is certified always-overlapping when the max Euclidean length of the centre
    difference over the two boxes is below that limit.  (The k = k' diagonal entry is the
    statement that two squares from the SAME box always overlap.)
    """
    n = len(boxes)
    X0 = np.array([b.x0 for b in boxes]); X1 = np.array([b.x1 for b in boxes])
    Y0 = np.array([b.y0 for b in boxes]); Y1 = np.array([b.y1 for b in boxes])
    T0 = np.array([b.th0 for b in boxes]); T1 = np.array([b.th1 for b in boxes])
    dx_lo = X0[None, :] - X1[:, None]; dx_hi = X1[None, :] - X0[:, None]
    dy_lo = Y0[None, :] - Y1[:, None]; dy_hi = Y1[None, :] - Y0[:, None]
    ax = np.maximum(np.abs(dx_lo), np.abs(dx_hi))
    ay = np.maximum(np.abs(dy_lo), np.abs(dy_hi))
    Dmax = np.hypot(ax, ay)
    # min of |cos| + |sin| over the relative tilt interval [t2lo - t1hi, t2hi - t1lo] (degrees)
    lo = T0[None, :] - T1[:, None]
    hi = T1[None, :] - T0[:, None]
    def cs(a):
        r = np.radians(a)
        return np.abs(np.cos(r)) + np.abs(np.sin(r))
    m = np.minimum(cs(lo), cs(hi))
    has90 = np.ceil(lo / 90.0) <= hi / 90.0 + 1e-12      # a multiple of 90 deg inside the range
    m = np.where(has90, 1.0, m)
    lim = 0.5 + 0.5 * m
    return (Dmax - lim) < -eps


def cross_gaps(C1, T1, C2, T2):
    """SAT gaps between every pose of set 1 and every pose of set 2 (unit squares)."""
    C1 = np.asarray(C1, float).reshape(-1, 2); T1 = np.asarray(T1, float).reshape(-1)
    C2 = np.asarray(C2, float).reshape(-1, 2); T2 = np.asarray(T2, float).reshape(-1)
    c1, s1 = np.cos(T1), np.sin(T1)
    c2, s2 = np.cos(T2), np.sin(T2)
    dx = C2[None, :, 0] - C1[:, None, 0]
    dy = C2[None, :, 1] - C1[:, None, 1]
    best = np.full(dx.shape, -1e9)
    for ax, ay in ((c1[:, None], s1[:, None]), (-s1[:, None], c1[:, None])):
        d = np.abs(dx * ax + dy * ay)
        sup = 0.5 * (np.abs(ax * c2[None, :] + ay * s2[None, :])
                     + np.abs(-ax * s2[None, :] + ay * c2[None, :]))
        best = np.maximum(best, d - 0.5 - sup)
    for ax, ay in ((c2[None, :], s2[None, :]), (-s2[None, :], c2[None, :])):
        d = np.abs(dx * ax + dy * ay)
        sup = 0.5 * (np.abs(ax * c1[:, None] + ay * s1[:, None])
                     + np.abs(-ax * s1[:, None] + ay * c1[:, None]))
        best = np.maximum(best, d - 0.5 - sup)
    return best


def box_always_hits_core(b, K, eps=1e-12):
    """T5''-style octagon/Minkowski test: True if EVERY pose in the box b gives a unit square
    whose interior meets the fixed core K (a rotated square of half-side K.a).  Sound prune."""
    thK = math.degrees(K.th)
    D = (K.x - b.x1, K.x - b.x0, K.y - b.y1, K.y - b.y0)
    m = min_cs(thK - b.th1, thK - b.th0)          # min of |cos|+|sin| over the relative tilt
    # axes of the moving square
    u1 = _max_abs_proj(D, b.th0, b.th1)
    if u1 - (0.5 + K.a * m) >= -eps:
        return False
    # the two axes of the fixed core
    u2 = _max_abs_proj(D, thK, thK)
    return (u2 - (K.a + 0.5 * m) < -eps)


def sample_R(fr, a_w, cores, s, n, rng, rho=None):
    """rejection-sample poses uniformly from the centre window x [0, 90) degrees."""
    x0, x1, y0, y1 = centre_window(fr, a_w, s)
    if x1 <= x0 or y1 <= y0:
        return np.zeros((0, 2)), np.zeros(0)
    C = np.column_stack([rng.uniform(x0, x1, n), rng.uniform(y0, y1, n)])
    TH = rng.uniform(0.0, 0.5 * math.pi, n)
    m = in_R(C, TH, fr, a_w, cores, s, rho=rho)
    return C[m], TH[m]


# ------------------------------------------------------------------ box cover of R(C)
class Bx:
    """a parameter box in A57's format (degrees for tilt)."""
    __slots__ = ("x0", "x1", "y0", "y1", "th0", "th1")

    def __init__(self, x0, x1, y0, y1, th0, th1):
        self.x0, self.x1, self.y0, self.y1 = float(x0), float(x1), float(y0), float(y1)
        self.th0, self.th1 = float(th0), float(th1)

    def to_json(self):
        return dict(x0=self.x0, x1=self.x1, y0=self.y0, y1=self.y1, th0=self.th0, th1=self.th1)

    def split(self):
        wx, wy, wt = self.x1 - self.x0, self.y1 - self.y0, (self.th1 - self.th0) / 60.0
        if wx >= wy and wx >= wt:
            m = 0.5 * (self.x0 + self.x1)
            return [Bx(self.x0, m, self.y0, self.y1, self.th0, self.th1),
                    Bx(m, self.x1, self.y0, self.y1, self.th0, self.th1)]
        if wy >= wt:
            m = 0.5 * (self.y0 + self.y1)
            return [Bx(self.x0, self.x1, self.y0, m, self.th0, self.th1),
                    Bx(self.x0, self.x1, m, self.y1, self.th0, self.th1)]
        m = 0.5 * (self.th0 + self.th1)
        return [Bx(self.x0, self.x1, self.y0, self.y1, self.th0, m),
                Bx(self.x0, self.x1, self.y0, self.y1, m, self.th1)]

    def centre_pose(self):
        return (0.5 * (self.x0 + self.x1), 0.5 * (self.y0 + self.y1),
                math.radians(0.5 * (self.th0 + self.th1)))


def box_outside_container(b, s):
    """True if EVERY pose in b puts the square outside [0, s]^2 -- sound prune."""
    hmin = 0.5 * min_cs(b.th0, b.th1)
    return (b.x1 < hmin - 1e-12 or b.y1 < hmin - 1e-12
            or b.x0 > s - hmin + 1e-12 or b.y0 > s - hmin + 1e-12)


def box_misses_cell(b, fr, a_w):
    """True if EVERY pose in b has mu_p > a_w -- sound prune."""
    return mu_lower_box(b, fr) > a_w + 1e-12


def box_hits_core(b, cores, margin=1e-9):
    """True if EVERY pose in b gives a square overlapping one of the cores -- a sound prune.

    Two independent sufficient tests, both already in the lab's TCB in kind:
      * T5 / CORE-MEET: the box's tight common-inscribed core K_B (A96) is contained in every
        square with pose in b, so K_B meeting a hypothesis core K_j forces an overlap;
      * T5'' / the octagon (box-vs-core) test: an interval bound showing no separating axis
        exists for any pose in b.
    """
    K = tight_core_of_box(b, margin)
    for c in cores:
        if K is not None and sq_gap(K, c) < 0.0:
            return True
        if box_always_hits_core(b, c):
            return True
    return False


def cover_R(fr, a_w, cores, s, nx=10, nth=6, max_boxes=20000, margin=1e-9, rho=None):
    """A sound box cover of R(C): a uniform grid over the centre window x [0, 90), with the
    three prune rules applied.  Every pose of R(C) lies in one of the returned boxes."""
    x0, x1, y0, y1 = centre_window(fr, a_w, s)
    if x1 <= x0 or y1 <= y0:
        return []
    out = []
    xs = np.linspace(x0, x1, nx + 1)
    ys = np.linspace(y0, y1, nx + 1)
    ts = np.linspace(0.0, 90.0, nth + 1)
    for a in range(nx):
        for bb in range(nx):
            for c in range(nth):
                b = Bx(xs[a], xs[a + 1], ys[bb], ys[bb + 1], ts[c], ts[c + 1])
                if box_outside_container(b, s):
                    continue
                if box_always_misses_cell(b, fr):
                    continue
                if rho is not None and box_cont_fails(b, fr, rho):
                    continue
                if box_hits_core(b, cores, margin):
                    continue
                out.append(b)
                if len(out) > max_boxes:
                    return out
    return out
