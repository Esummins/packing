"""A253: the MINIMUM-TILT ring -- shared geometry.

The all-ADJ ring family of A251 (`family251`, 17 coordinates) carries a TILT per member: the
corner-frame parameter theta in (0, 90 deg) of a wall meeter B or a floor meeter A.  The square's
deviation from flushness is  tau := min(theta, 90 deg - theta)  in [0, 45 deg]  -- exactly A249's
`tilt_margin`, the term block 36..43 of `ring_margin(..., terms=True)` (68 terms: 28 pair gaps,
8 containments, 8 tilts, 8 deltas, 16 cell depths).  A253 asks for the SMALLEST tau at which the
ring still admits the POKER (A252: a ninth square whose corner lies in a wall's slot overlap
[0,1] x [s-2, 2]), so the objects here are

    feas(x, s)      the ring's feasibility margin with the TILT BLOCK REMOVED (at a fixed common
                    tau the eight tilt terms are all equal to tau and say nothing; the binding
                    question is whether the geometric terms survive),
    x_of(tau, sigma, deltas)        the COMMON-tilt ring: theta_i = tau or 90 deg - tau per the
                    sign pattern sigma in {0,1}^8 (member order B_BL, A_BL, B_BR, A_BR, ...),
    x_free(us, sigma, deltas)       the non-uniform ring with per-member tau_i = us[i],
    joint(z, ...)   min(feas, poker fit) -- the ring + poker margin of A252's `poke_margin`.

Nothing here is new geometry: `twotilted249.ring_margin` / `ring_polys`, `poker252.poke_margin`
and `geom248` do the work.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
for a in ('A249-type-t-chase', 'A248-corner-chase', 'A251-ring-pocket', 'A252-centre-disc',
          'A237-pocket-waste', 'A222-ring-swap'):
    p = os.path.join(ROOT, 'attempts', a, 'code')
    if p not in sys.path:
        sys.path.insert(0, p)
import twotilted249 as W                                              # noqa: E402
import geom248 as G                                                   # noqa: E402
import poker252 as PK                                                 # noqa: E402

HALF = math.pi / 2
DEG = math.pi / 180.0
NAMES = ('B_BL', 'A_BL', 'B_BR', 'A_BR', 'B_TR', 'A_TR', 'B_TL', 'A_TL')
CORNERS = ('BL', 'BR', 'TR', 'TL')
TILT0, TILT1 = 36, 44
NTERM = 68
SW = 3.877084


def term_names():
    out = ['gap_%s_%s' % (NAMES[j], NAMES[i]) for i in range(8) for j in range(i)]
    out += ['in_' + n for n in NAMES]
    out += ['tilt_' + n for n in NAMES]
    out += ['delta_' + n for n in NAMES]
    for c in CORNERS:
        out += ['box_B_' + c, 'box_A_' + c, 'slot_B_' + c, 'slot_A_' + c]
    return out


TNAMES = term_names()


def terms(x, s):
    t = W.ring_margin(list(x), s, False, True)
    return t if len(t) == NTERM else None


def feas(x, s):
    """the ring margin with the tilt block removed; -1 if a theta left (0, 90 deg)."""
    t = terms(x, s)
    if t is None:
        return -1.0
    return float(min(t[:TILT0] + t[TILT1:]))


def feas_named(x, s, k=4):
    t = terms(x, s)
    if t is None:
        return [('theta_out_of_range', -1.0)]
    r = [(TNAMES[i], t[i]) for i in range(NTERM) if not TILT0 <= i < TILT1]
    return sorted(r, key=lambda z: z[1])[:k]


def polys(x, s):
    return W.ring_polys(list(x), s, False)[0]


def x_of(tau, sigma, deltas):
    """common-tilt ring: 16 parameters (theta_B, delta_B, theta_A, delta_A) per corner."""
    x = []
    for k in range(4):
        tB = HALF - tau if sigma[2 * k] else tau
        tA = HALF - tau if sigma[2 * k + 1] else tau
        x += [tB, deltas[2 * k], tA, deltas[2 * k + 1]]
    return x


def x_free(us, sigma, deltas):
    """non-uniform ring: member i has tau_i = us[i]."""
    x = []
    for k in range(4):
        tB = HALF - us[2 * k] if sigma[2 * k] else us[2 * k]
        tA = HALF - us[2 * k + 1] if sigma[2 * k + 1] else us[2 * k + 1]
        x += [tB, deltas[2 * k], tA, deltas[2 * k + 1]]
    return x


def tilts_of(x):
    """the eight tau_i in radians, in member order."""
    return [min(x[4 * k + j], HALF - x[4 * k + j]) for k in range(4) for j in (0, 2)]


def poke(pose, P, s, wall):
    return PK.poke_margin(list(pose), P, s, wall)


def poke_all_walls(pose_by_wall, P, s):
    return {w: poke(pose_by_wall[w], P, s, w) for w in pose_by_wall}


def joint(x, pose, s, wall):
    m = feas(x, s)
    if m < -0.25:
        return m
    return min(m, poke(pose, polys(x, s), s, wall))


def find_poker(P, s, restarts=3, seed=7, walls=(0, 1, 2, 3), maxiter=1200):
    """A252's `poker252.find_poker` with an explicit iteration budget (same objective, poke_margin)."""
    import numpy as np
    from scipy.optimize import minimize
    rng = np.random.default_rng(seed)
    best = (-9.0, None, None)
    for wall in walls:
        x0, x1, y0, y1 = PK.overlap_cell(s, wall)
        for _ in range(restarts):
            cx = rng.uniform(x0, x1) + (0.8 if wall == 0 else -0.8 if wall == 2 else 0.0)
            cy = rng.uniform(y0, y1) + (0.8 if wall == 1 else -0.8 if wall == 3 else 0.0)
            r = minimize(lambda z: -PK.poke_margin(z, P, s, wall),
                         [cx, cy, rng.uniform(0, HALF)], method='Nelder-Mead',
                         options={'xatol': 1e-9, 'fatol': 1e-11, 'maxiter': maxiter})
            if -r.fun > best[0]:
                best = (float(-r.fun), [float(v) for v in r.x], wall)
    return best


def poke_gaps(pose, x, s, wall):
    """the poker's separate margins: containment, ribbon depth, and the gap to each ring square."""
    P = polys(x, s)
    F = G.verts(list(pose))
    out = [('poker_in', float(min(F[:, 0].min(), F[:, 1].min(), s - F[:, 0].max(), s - F[:, 1].max()))),
           ('poker_ribbon', float(G.depth_rect(F, PK.overlap_cell(s, wall))))]
    out += [('poker_gap_' + n, float(G.poly_gap(F, V))) for V, n in zip(P, NAMES)]
    return sorted(out, key=lambda z: z[1])


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


def shat_ring():
    """A249's exact C2 ring at s-hat, expanded to the 16 coordinates."""
    import json
    j = json.load(open(os.path.join(ROOT, 'attempts', 'A249-type-t-chase', 'results',
                                    'twotilted249_ring2.json'), encoding='utf-8'))
    y = j['3.877084']['result']['x']
    return list(y[:4]) + list(y[4:8]) + list(y[:4]) + list(y[4:8])


if __name__ == '__main__':
    x = shat_ring()
    print('s-hat ring: feas %+.5f  tilts(deg) %s' % (feas(x, SW), [round(t / DEG, 3) for t in tilts_of(x)]))
    print('  binding:', [(n, round(v, 5)) for n, v in feas_named(x, SW)])
    pm, pose, wall = PK.find_poker(polys(x, SW), SW, restarts=12)
    print('  poker %+.6f wall %d pose %s' % (pm, wall, [round(v, 5) for v in pose]))
    print('  poker terms:', [(n, round(v, 6)) for n, v in poke_gaps(pose, x, SW, wall)[:4]])
