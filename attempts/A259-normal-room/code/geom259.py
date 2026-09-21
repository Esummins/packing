"""A259 geometry of the NORMAL RING: a pinwheel of four common-tilt PAIRS (rows of two) of one sense.

Floor frame (wall y = 0), tilt phi in (0, 45 deg] (sense +, counter-clockwise), offset delta of the row's leftmost
point from the corner behind it (counter-clockwise order of walls: floor from BL, right wall from BR, ceiling from
TR, left wall from TL).  c = cos phi, z = sin phi, p = delta + z:
    square j (j = 0, 1): lowest vertex (p + j sec phi, 0); vertices  L + (0,0), (c, z), (c - z, c + z), (-z, c);
    row extent along the wall [delta, delta + sec + c + z]; height c + z; sawtooth top between heights c and c + z.
Wall k = the floor frame rotated k quarter turns about the container centre: (x, y) -> (s - y, x).
Parameters x = (delta_0..3, phi_0..3) (radians) + s.  A reflection flips the sense, so sense + is WLOG.

D (version A259-v0, the most generous reading of A258's BRIEF; every bound on a superset is sound):
    0 < phi_k <= 45 deg;  the eight squares inside [0, s]^2 and pairwise interior-disjoint;
    optional `boxes`: every corner box doubly met:  delta_k < 1  and  delta_k + span_k > s - 1.
"""
import math

import numpy as np

SHAT = 3.877083590022814
DEG = math.pi / 180.0


def span(phi):
    return 1.0 / math.cos(phi) + math.cos(phi) + math.sin(phi)


def rot_k(P, s, k):
    P = np.array(P, float)
    for _ in range(k % 4):
        P = np.stack([s - P[:, 1], P[:, 0]], axis=1)
    return P


def row_verts(delta, phi, s, k):
    """the two squares of wall k as 4x2 vertex arrays (counter-clockwise from the wall vertex)."""
    c, z = math.cos(phi), math.sin(phi)
    out = []
    for j in (0, 1):
        L = delta + z + j / c
        V = [(L, 0.0), (L + c, z), (L + c - z, c + z), (L - z, c)]
        out.append(rot_k(V, s, k))
    return out


def ring_verts(x, s):
    out = []
    for k in range(4):
        out += row_verts(x[k], x[4 + k], s, k)
    return out


def pose_of(V):
    ctr = V.mean(axis=0)
    e = V[1] - V[0]
    return (float(ctr[0]), float(ctr[1]), float(math.atan2(e[1], e[0])))


def ring_poses(x, s):
    return [pose_of(V) for V in ring_verts(x, s)]


def sq_verts(cx, cy, th, half=0.5):
    c, d = math.cos(th), math.sin(th)
    return np.array([(cx + c * a - d * b, cy + d * a + c * b) for a, b in
                     ((-half, -half), (half, -half), (half, half), (-half, half))])


def poly_gap(A, B):
    """signed SAT separation of two convex polygons (>= 0: interior-disjoint; the best separating-axis gap)."""
    best = -1e9
    for P, Q in ((A, B), (B, A)):
        E = np.roll(P, -1, axis=0) - P
        N = np.stack([E[:, 1], -E[:, 0]], axis=1)
        N /= np.linalg.norm(N, axis=1)[:, None]
        pp = P @ N.T
        qq = Q @ N.T
        g = np.maximum(qq.min(axis=0) - pp.max(axis=0), pp.min(axis=0) - qq.max(axis=0))
        best = max(best, float(g.max()))
    return best


def contain_margin(V, s):
    return float(min(V[:, 0].min(), V[:, 1].min(), s - V[:, 0].max(), s - V[:, 1].max()))


def ring_margin(x, s, boxes=True):
    """min of: containment, 28 pairwise SAT gaps, tilt range, and (boxes) the corner-box strictness terms.
    >= 0: x in D (closed); the box terms are reported with their own sign (strict inside D)."""
    Vs = ring_verts(x, s)
    m = min(contain_margin(V, s) for V in Vs)
    for i in range(8):
        for j in range(i):
            if i // 2 != j // 2:                                      # the two squares of a row touch edge to edge [T]
                m = min(m, poly_gap(Vs[i], Vs[j]))
    for k in range(4):
        m = min(m, x[4 + k], 45 * DEG - x[4 + k])
        if boxes:
            m = min(m, 1.0 - x[k], x[k] + span(x[4 + k]) - (s - 1.0))
    return float(m)


def c4(delta, phi):
    return np.array([delta] * 4 + [phi] * 4, float)


def delta_range_c4(phi, s):
    """closed-form delta interval of the C4 common-tilt normal ring (face-to-face corner contact, delta > z):
    lower: delta > s - 1 - span;  upper: (s - 2c - z - sec - d) c + (d - z) z >= 0  =>  d <= (.)/(c - z)."""
    c, z = math.cos(phi), math.sin(phi)
    lo = s - 1.0 - span(phi)
    hi = ((s - 2 * c - z - 1 / c) * c - z * z) / (c - z) if c > z else float('inf')
    return lo, min(hi, 1.0)


def sample_D(rng, s, n, boxes=True, phimax=45.0, tries=200000):
    """rejection sampler with conditional proposals: phi_k uniform, delta_k uniform in its own box interval."""
    out = []
    for _ in range(tries):
        phi = rng.uniform(0.2, phimax, 4) * DEG
        lo = np.array([max(0.0, s - 1.0 - span(f)) for f in phi]) if boxes else np.zeros(4)
        hi = np.array([min(1.0, s - span(f)) for f in phi])
        if np.any(hi <= lo):
            continue
        d = lo + (hi - lo) * rng.uniform(0, 1, 4) ** 1.0
        x = np.concatenate([d, phi])
        if ring_margin(x, s, boxes) >= 0:
            out.append(x)
            if len(out) >= n:
                break
    return out


def belownormal():
    try:
        import ctypes
        k = ctypes.windll.kernel32
        k.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        k.SetProcessAffinityMask.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        k.SetPriorityClass(ctypes.c_void_p(-1), 0x00004000)
        k.SetProcessAffinityMask(ctypes.c_void_p(-1), 0xFFFF)
    except Exception as e:                                             # noqa
        print('belownormal failed: %r' % (e,))
