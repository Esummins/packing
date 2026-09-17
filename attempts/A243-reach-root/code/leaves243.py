"""A243 -- the REACH SUMMARY of a corner crowd and the three closed-form leaves examined (notes/reach243.md).

Everything here is an EVALUATION of the summary from poses, the type-F closed forms of A239 (re-implemented, checked
against geom239.reach in test243.py), and the WITNESSES that show none of R1 / R2 / R3 is an inequality valid over a
summary cell: the off-wall holder (R1), the fibre of a cell (R3's cores).  Corner frame: the corner at the origin,
u along the floor (v = 0), v up the wall (u = 0); a pose is (cu, cv, theta) with theta in RADIANS.  No lab library is
imported here; test243.py wraps geom239 read-only for the cross-checks.
"""
import math
import random

from shapely.geometry import Polygon, box

SQ2 = math.sqrt(2.0)
DEG = math.pi / 180.0
SHAT = 3.8770835900228


def w_of(t):
    return abs(math.cos(t)) + abs(math.sin(t))


def verts(pose):
    cu, cv, t = pose
    c, s = math.cos(t), math.sin(t)
    return [(cu + a * c - b * s, cv + a * s + b * c) for a, b in ((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5))]


def poly(pose):
    return Polygon(verts(pose))


def in_quadrant(pose):
    return all(u >= -1e-12 and v >= -1e-12 for u, v in verts(pose))


def max_u(pose):
    return max(u for u, _ in verts(pose))


def max_v(pose):
    return max(v for _, v in verts(pose))


def mu(pose):
    """min over the body of max(u, v) (A233's mu_c): at a vertex or where an edge crosses the diagonal u = v."""
    V = verts(pose)
    best = min(max(u, v) for u, v in V)
    for i in range(4):
        (u0, v0), (u1, v1) = V[i], V[(i + 1) % 4]
        d0, d1 = u0 - v0, u1 - v1
        if d0 * d1 < 0:
            t = d0 / (d0 - d1)
            best = min(best, u0 + t * (u1 - u0))
    return best


def depth(pose):
    return max(0.0, 1.0 - mu(pose))


def meets_box(pose):
    return mu(pose) < 1.0 - 1e-12


def disjoint(p, q, tol=1e-12):
    d = max(abs(p[0] - q[0]), abs(p[1] - q[1]))
    if d < 1 / SQ2 - 1e-12:                                              # Lemma A1 (sideband.md): centres >= 1/sqrt 2 apart
        return False
    if d > SQ2:                                                          # bodies within 1/sqrt 2 of their centres
        return True
    return poly(p).intersection(poly(q)).area <= tol


def summary(A, B):
    """the label-free reach summary of the crowd {A, B}: (reach_u, reach_v, deeper depth, shallower depth)."""
    dA, dB = depth(A), depth(B)
    return (max(max_u(A), max_u(B)), max(max_v(A), max_v(B)), max(dA, dB), min(dA, dB))


# ---------------------------------------------------------------- the type-F closed forms (A239 s.1, s.3; A237 s.1)
def reach_F(theta_deg, delta):
    """R(theta, delta) = cos + sin + delta - (delta - sin) tan: two mode-(a) type-F crowds span a wall of side s in
    contact iff R >= s - 2 (A239 Lemma REACH).  An EVALUATION of the crowd's reaches, not a cell inequality."""
    t = theta_deg * DEG
    return math.cos(t) + math.sin(t) + delta - (delta - math.sin(t)) * math.tan(t)


def lever_delta(theta_deg):
    """A239 Proposition LEVER: torque balance of the partner under wall + corner-on-edge + top-vertex contacts needs
    delta = sin theta + cos^3 theta.  Valid for that contact structure only."""
    t = theta_deg * DEG
    return math.sin(t) + math.cos(t) ** 3


def tiltmin_ok(theta_deg, delta):
    """A237 Lemma TILT-MIN (a): sin theta <= delta < 1 for a flat wall meeter at offset delta and a tilted partner."""
    return math.sin(theta_deg * DEG) <= delta < 1.0


def pair_F(theta_deg, delta, eta=0.0):
    """the mode-(a) type-F crowd: A = [delta, 1 + delta] x [0, 1] flat on the floor; B of tilt theta with its leftmost
    vertex eta off the wall and its lower edge eta above A's corner (delta, 1) (A237 family, A239 window_pair)."""
    t = theta_deg * DEG
    xv = math.sin(t) + eta
    yv = 1.0 - (delta - xv) * math.tan(t) + eta
    A = (delta + 0.5, 0.5, 0.0)
    B = (xv + (math.cos(t) - math.sin(t)) / 2, yv + (math.sin(t) + math.cos(t)) / 2, t)
    return A, B


def theta_star(s, margin=0.02):
    """least tilt (0.01 deg grid) at which the least-offset type-F crowd (delta = sin theta + margin) spans side s."""
    for k in range(1, 9000):
        th = k / 100.0
        if reach_F(th, math.sin(th * DEG) + margin) >= s - 2:
            return th
    return None


# ---------------------------------------------------------------- R1's missing lemma: an off-wall along-wall holder
def holder_witness(delta=0.36, phi_deg=135.0):
    """A flat floor meeter A = [delta, 1+delta] x [0, 1] and a square C one of whose EDGES (direction angle phi)
    passes through A's top-right corner p = (1 + delta, 1), C on the side n_in = (sin phi, -cos phi) of that edge.
    The contact row is A's vertex on C's edge, so the force of C on A is along C's outward edge normal -n_in =
    (-sin phi, cos phi): for phi in (90, 180) it has F_u < 0 AND F_v < 0 -- Lemma HOLD's along-wall holder --
    while C's lowest vertex is strictly above the floor: the holder is not a wall member.
    Returns (A, C, force_dir, overlap_area, y_low)."""
    t = phi_deg * DEG
    p = (1.0 + delta, 1.0)
    e = (math.cos(t), math.sin(t))
    n_in = (math.sin(t), -math.cos(t))
    C = (p[0] + 0.25 * e[0] + 0.5 * n_in[0], p[1] + 0.25 * e[1] + 0.5 * n_in[1], t)
    A = (delta + 0.5, 0.5, 0.0)
    force_dir = (-n_in[0], -n_in[1])
    overlap = poly(A).intersection(poly(C)).area
    y_low = min(v for _, v in verts(C))
    return A, C, force_dir, overlap, y_low


# ---------------------------------------------------------------- R3: the fibre of a summary cell and its cores
def _pose_from_floor(t, umax, y0):
    """the square of tilt t whose rightmost vertex is at u = umax and lowest vertex at height y0."""
    c, s = math.cos(t), math.sin(t)
    ulow = umax - c                                                      # lowest vertex (ulow, y0); rightmost (umax, y0 + s)
    return (ulow + (c - s) / 2, y0 + (s + c) / 2, t)


def _pose_from_wall(t, vmax, x0):
    """the square of tilt t whose topmost vertex is at v = vmax and leftmost vertex at abscissa x0 (mirror of above)."""
    cu, cv, tt = _pose_from_floor(t, vmax, x0)
    return (cv, cu, -tt)


def _in_cell(S, cell):
    return all(lo - 1e-12 <= x <= hi + 1e-12 for x, (lo, hi) in zip(S, cell))


def sample_fibre(cell, n, seed=0, tries=400000):
    """crowds {A, B} in the closed quadrant, interior-disjoint, both meeting the box, whose summary lies in the CELL
    ((ru_lo, ru_hi), (rv_lo, rv_hi), (d1_lo, d1_hi), (d2_lo, d2_hi)).  Three families, each a SUBSET of the fibre
    (so the intersection of their bodies is an OUTER bound on the fibre's core): (i) type-F crowds pair_F(theta, delta,
    eta); (ii) the same partner with the floor meeter TILTED by phi at the same floor reach 1 + delta; (iii) the same
    partner with the flat floor meeter LIFTED by y0 (a floating flat meeter).  Returns (pairs, acceptance)."""
    rng = random.Random(seed)
    (ru0, ru1), (rv0, rv1), (d10, d11), (d20, d21) = cell
    out = []
    for k in range(tries):
        if len(out) >= n:
            break
        th = rng.uniform(0.5, 89.5)
        delta = rng.uniform(max(math.sin(th * DEG), ru0 - 1.0), min(1.0, ru1 - 1.0))
        if delta < math.sin(th * DEG):
            continue
        A, B = pair_F(th, delta, rng.uniform(0.0, 0.3))
        fam = k % 3
        if fam == 1:
            A = _pose_from_floor(rng.uniform(0, math.pi / 2), 1.0 + delta, 0.0)
        elif fam == 2:
            A = (A[0], A[1] + rng.uniform(0.0, 0.5), 0.0)
        if not (in_quadrant(A) and in_quadrant(B) and meets_box(A) and meets_box(B)):
            continue
        if not _in_cell(summary(A, B), cell):
            continue
        if not disjoint(A, B):
            continue
        out.append((A, B))
    return out, (len(out) / max(1, k + 1))


def core_outer(pairs, role):
    """intersection of the bodies of role 'deep' (the deeper meeter) or 'shallow' over the sampled fibre: an OUTER
    bound on A172's core K' (the true core is the intersection over the whole fibre, a subset)."""
    P = None
    for A, B in pairs:
        dA, dB = depth(A), depth(B)
        Q = (A if dA >= dB else B) if role == 'deep' else (B if dA >= dB else A)
        P = poly(Q) if P is None else P.intersection(poly(Q))
        if P.is_empty or P.area < 1e-12:
            return P
    return P


def cell_around(A, B, h):
    """the summary cell of half-width h (reaches) and h (depths) around the crowd's summary."""
    ru, rv, d1, d2 = summary(A, B)
    return ((ru - h, ru + h), (rv - h, rv + h), (max(0, d1 - h), min(1, d1 + h)), (max(0, d2 - h), min(1, d2 + h)))


def three_free_witness(obstacles, S, n=3, samples=3000, seed=0):
    """n pairwise interior-disjoint unit squares (random centres and tilts, greedy) inside [0, S]^2 avoiding every
    obstacle polygon: a witness that the no-room leaf (m = n) cannot fire on a pocket containing the container minus
    these obstacles.  Returns the chosen squares (fewer than n = inconclusive)."""
    rng = random.Random(seed)
    obs = [o for o in obstacles if o is not None and not o.is_empty and o.area > 0]
    cont = box(0, 0, S, S)
    chosen = []
    for _ in range(samples):
        t = rng.choice((0.0, math.pi / 4, rng.uniform(0, math.pi / 2)))
        hw = w_of(t) / 2
        q = poly((rng.uniform(hw, S - hw), rng.uniform(hw, S - hw), t))
        if q.difference(cont).area > 1e-12 or any(q.intersection(o).area > 1e-12 for o in obs):
            continue
        if all(q.intersection(c).area <= 1e-12 for c in chosen):
            chosen.append(q)
            if len(chosen) == n:
                break
    return chosen


def random_crowds(n, seed=0, tries=2000000):
    """random corner crowds: two poses with centres in LOCALITY's box [1/2, 1 + 1/sqrt 2)^2 and tilts in [0, 90),
    both in the quadrant and meeting the open box, interior-disjoint."""
    rng = random.Random(seed)
    out = []
    for _ in range(tries):
        if len(out) >= n:
            break
        A = (rng.uniform(0.5, 1.7071), rng.uniform(0.5, 1.7071), rng.uniform(0, math.pi / 2))
        B = (rng.uniform(0.5, 1.7071), rng.uniform(0.5, 1.7071), rng.uniform(0, math.pi / 2))
        if in_quadrant(A) and in_quadrant(B) and meets_box(A) and meets_box(B) and disjoint(A, B):
            out.append((A, B))
    return out


def grid_count(g, dims, quotient=8):
    return g ** dims / quotient
