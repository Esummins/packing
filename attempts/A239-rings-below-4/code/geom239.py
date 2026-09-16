"""A239 geometry (n-general): the wedged square of Lemma WEDGED-SEAL and its numeric checks, the along-wall REACH of
a corner crowd (docs/notes rings_below_4.md s.1), the ring builders (A226's crowd ring; the window family ring(S, theta,
delta, eta) of A237 with eta = 0 for real contacts; the JUTTING third member resting on two wall squares), and the
region-search helpers (A222's exact free-centre space).  Poses are (cx, cy, theta) in a y-up frame, container [0, S]^2.
"""
import math
import os
import sys

import numpy as np
from scipy.optimize import minimize
from shapely.geometry import Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
for a in ('A236-ring-capacity', 'A226-one-flush', 'A222-ring-swap', 'A217-torque-probe', 'A237-pocket-waste'):
    sys.path.insert(0, os.path.join(HERE, '..', '..', a, 'code'))
import band236 as BD                                                       # noqa: E402
import crowd226 as C226                                                    # noqa: E402
import region222 as RG                                                     # noqa: E402
import geom237 as G237                                                     # noqa: E402

CORNERS = BD.CORNERS
DEG = math.pi / 180.0


def set_priority():
    try:
        import ctypes
        k = ctypes.windll.kernel32
        h = ctypes.c_void_p(-1)
        k.SetPriorityClass(h, 0x4000)
        k.SetProcessAffinityMask(h, ctypes.c_size_t(0xFFFF))
    except Exception:
        pass


def w_of(a):
    return abs(math.cos(a)) + abs(math.sin(a))


# ---------------------------------------------------------------- Lemma WEDGED-SEAL (docs/proofs/wedged_seal.md)
def wedged_square(theta_deg):
    """the unit square with one vertex on the floor (sin th, 0) and one on the wall (0, cos th): centre (w/2, w/2),
    tilt theta -- the PRESSED square of sideband.md Cor. B1."""
    th = theta_deg * DEG
    w = w_of(th)
    return (w / 2, w / 2, th)


def wedge_regions(theta_deg):
    """(sealed triangle, floor wedge inside the box, wall wedge inside the box) as vertex lists."""
    th = theta_deg * DEG
    b, l = math.cos(th), math.sin(th)
    tri = [(0.0, 0.0), (l, 0.0), (0.0, b)]
    Tf = [(l, 0.0), (1.0, 0.0), (1.0, (1 - l) * math.tan(th))]
    Tw = [(0.0, b), (0.0, 1.0), ((1 - b) / math.tan(th), 1.0)]
    return tri, Tf, Tw


def f_alpha(theta_deg, alpha_deg):
    """min u of a unit square in the wedge under the line through R at angle alpha (wedged_seal.md s.2, step 6):
    u_A + cos^2 alpha / sin alpha with u_A = sin th + cos th - sin th cot alpha."""
    th, al = theta_deg * DEG, alpha_deg * DEG
    return math.sin(th) + math.cos(th) - math.sin(th) / math.tan(al) + math.cos(al) ** 2 / math.sin(al)


def b0star(phi_deg, zeta_deg):
    """Lemma B0* (k0_count.md s.1): w(phi) + (cos z - sin z) w(phi + z) - 2 cos^2 z >= 0."""
    p, z = phi_deg * DEG, zeta_deg * DEG
    return w_of(p) + (math.cos(z) - math.sin(z)) * w_of(p + z) - 2 * math.cos(z) ** 2


def random_meeter(rng, size=1.0):
    """a random unit square in the closed quadrant whose interior meets the open box (0, size)^2."""
    while True:
        th = rng.uniform(0, math.pi / 2)
        h = w_of(th) / 2
        p = (rng.uniform(h, size + 1.0), rng.uniform(h, size + 1.0), th)
        if BD.meets_corner(p, 100.0, 'BL', size):
            return p


def second_meeter_search(theta_deg, trials, seed=0):
    """Monte-Carlo: unit squares in the quadrant meeting the box that are interior-disjoint from the wedged square
    (expected: none).  Returns (count found, min SAT overlap seen, i.e. the largest -gap)."""
    rng = np.random.default_rng(seed)
    Q = wedged_square(theta_deg)
    found, worst = 0, -1e9
    for _ in range(trials):
        p = random_meeter(rng)
        g = BD.sep(p, Q)
        worst = max(worst, g)
        if g >= -1e-9:
            found += 1
    return found, worst


# ---------------------------------------------------------------- the REACH of a corner crowd (flat + tilted, TILT-MIN type)
def reach(theta_deg, delta):
    """R(theta, delta) = w(theta) + delta - (delta - sin theta) tan theta: the two crowds' reach along a wall beyond
    their corner boxes when the crowd is a flat meeter at offset delta and a mode-(a) partner of tilt theta; a wall of
    side s is spanned (k = 0 contact) iff 2 + R >= s; the gap for a third member is s - 2 - R."""
    th = theta_deg * DEG
    return math.cos(th) + math.sin(th) + delta - (delta - math.sin(th)) * math.tan(th)


def theta_star(s, delta_of=lambda th: math.sin(th * DEG) + 0.02):
    """least tilt (deg, 0.01 grid) at which the least-offset crowd bridges side s with k = 0; None if never."""
    for k in range(1, 9000):
        th = k / 100.0
        if reach(th, delta_of(th)) >= s - 2:
            return th
    return None


# ---------------------------------------------------------------- ring builders
def ring226(S, eps):
    """A226's eight-square crowd ring (alternating floor / wall variants); pattern 2 2 2 2, no contacts but the walls."""
    out = []
    for c, var in zip(CORNERS, ('floor', 'wall', 'floor', 'wall')):
        A, B = C226.crowd_pair(eps, var)
        out.append(C226.to_container(c, S, *A))
        out.append(C226.to_container(c, S, *B))
    return out


def window_pair(theta_deg, delta, eta=0.0):
    """BL-frame poses of A (flat, floor, offset delta) and B (tilt theta, leftmost vertex eta off the wall, lowest
    vertex eta above A's corner line): A237's mode-(a) crowd; eta = 0 gives the contacts wall-B and A-B."""
    th = theta_deg * DEG
    xv = math.sin(th) + eta
    yv = 1.0 - (delta - xv) * math.tan(th) + eta
    A = (delta + 0.5, 0.5, 0.0)
    cB = (xv + (math.cos(th) - math.sin(th)) / 2, yv + (math.sin(th) + math.cos(th)) / 2)
    return A, (cB[0], cB[1], th)


def window_ring(S, theta_deg, delta=None, eta=0.0, margin=0.02):
    """the alternating window ring (A237 family237.ring with explicit delta and eta); returns (poses, delta)."""
    if delta is None:
        delta = math.sin(theta_deg * DEG) + margin
    out = []
    for c, var in zip(CORNERS, ('floor', 'wall', 'floor', 'wall')):
        A, B = window_pair(theta_deg, delta, eta)
        if var == 'wall':
            A, B = (A[1], A[0], 0.0), (B[1], B[0], -B[2])
        out.append(C226.to_container(c, S, *A))
        out.append(C226.to_container(c, S, *B))
    return out, delta


def jut_member(neigh, S, phi_deg, x0, y0, sense=1.0):
    """a unit square of tilt phi resting on the squares `neigh` (list of poses), as LOW (sense = +1) or as HIGH
    (sense = -1) as possible: optimise sense * cy over (cx, cy) subject to SAT gaps >= 0 against every neighbour and
    the container.  Returns the pose and its gaps to the neighbours."""
    phi = phi_deg * DEG
    h = w_of(phi) / 2

    def cons(x):
        p = (x[0], x[1], phi)
        return np.array([BD.sep(p, q) for q in neigh] + [x[0] - h, S - h - x[0], x[1] - h, S - h - x[1]])

    best = None
    for dx in (0.0, -0.2, 0.2, -0.4, 0.4):
        r = minimize(lambda x: sense * x[1], np.array([x0 + dx, y0]), method='SLSQP',
                     constraints=[{'type': 'ineq', 'fun': cons}], options={'maxiter': 500, 'ftol': 1e-14})
        if cons(r.x).min() >= -1e-9 and (best is None or sense * r.x[1] < sense * best[1]):
            best = r.x
    if best is None:
        return None, None
    p = (float(best[0]), float(best[1]), phi)
    return p, [BD.sep(p, q) for q in neigh]


def jutting_ring(S, theta_deg, phi_deg=45.0, eta=0.0, margin=0.02):
    """pattern 3 2 3 2: the window ring plus a jutting member on the floor (as low as it goes above the gap
    between BL's flat A and BR's floor-lying B') and one on the ceiling (as high as it goes, avoiding the first);
    indices: ring 0..7 (A, B per corner in order BL BR TR TL), 8 = floor jut, 9 = ceiling jut."""
    R, delta = window_ring(S, theta_deg, None, eta, margin)
    A_bl, B_br = R[0], R[3]
    xr, xl = min(BD.verts(B_br)[:, 0]), max(BD.verts(A_bl)[:, 0])
    M, gM = jut_member(R, S, phi_deg, 0.5 * (xl + xr), 1.6, +1.0)
    info = {'delta': delta, 'gap': float(xr - xl), 'reach': reach(theta_deg, delta)}
    if M is None:
        return R, dict(info, jut_ok=False)
    M2, gM2 = jut_member(R + [M], S, phi_deg, S - 0.5 * (xl + xr), S - 1.6, -1.0)
    if M2 is None:
        return R + [M], dict(info, jut_ok=False, jut_gaps=[float(g) for g in gM])
    info.update({'jut_ok': True, 'jut_gaps': [float(g) for g in gM], 'jut2_gaps': [float(g) for g in gM2],
                 'jut_top': float(BD.verts(M)[:, 1].max()), 'jut_bottom': float(BD.verts(M)[:, 1].min()),
                 'jut2_bottom': float(BD.verts(M2)[:, 1].min()),
                 'jut_touches': [i for i, g in enumerate(gM) if abs(g) <= 1e-7],
                 'jut2_touches': [i for i, g in enumerate(gM2) if abs(g) <= 1e-7]})
    return R + [M, M2], info


# ---------------------------------------------------------------- region search (A222, n-general parts)
def thetas(step=5.0):
    return [math.radians(t) for t in np.arange(0.0, 90.0, step)]


def capacity(members, S, kmax=3, beam=3):
    """largest k <= kmax for which A222's greedy placer packs k unit squares into the pocket (exact SAT check)."""
    k_found, poses = 0, []
    for k in range(1, kmax + 1):
        got = RG.greedy(list(members), S, k, thetas(5.0), beam)
        if got is None:
            got = RG.greedy(list(members), S, k, thetas(1.0), beam)
        if got is None:
            break
        ok, gap, wall = BD.check_packing(list(members) + got, S)
        if not ok:
            break
        k_found, poses = k, got
    return k_found, poses


def touchable(members, S, idx, step=1.0, tol=1e-6):
    """can SOME unit square inside the pocket touch member idx?  (over a tilt grid: the free-centre region of that
    tilt reaches the boundary of member (+) Q_theta.)  Returns (bool, least distance, best tilt deg)."""
    best = (1e9, None)
    m = members[idx]
    for t in np.arange(0.0, 90.0, step):
        th = math.radians(t)
        reg = RG.cspace(list(members), S, th)
        if reg.is_empty:
            continue
        mk = G237.minkowski_convex(G237.sq_verts(*m), G237.sq_verts(0.0, 0.0, th))
        d = reg.distance(mk)
        if d < best[0]:
            best = (d, float(t))
    return best[0] <= tol, float(best[0]), best[1]


def pocket_polygon(members, S):
    return G237.pocket(list(members), S)
