r"""rigid102.py -- A102: the RIGIDITY DRAIN.

Generalises `attempts/A87-drain-flow/code/pi_drain_3p9907.py` (the PI's by-eye drain of the
3.9907 record) into a tool and runs it on every strictly K0-BLOCKED packing the lab owns.

T1  rigidity test.  For each corner cell met by >= 2 squares, for each meeter Q (shallower
    first): enumerate Q's contacts (squares and walls, SAT gap < CONTACT_TOL), the contact
    point, the EDGE outward normal (PI correction: the centre-to-contact direction gives the
    wrong sign), the force on Q and the torque about Q's centre.  A first-order motion is
    feasible iff every contact point's velocity has a non-negative component along the force
    on Q:
        translation v   feasible  iff  v . F_k >= 0  for all k
        rotation w about p feasible iff w * ((r_k - p) x F_k)_z >= 0 for all k
    Hence: FREE-ROT (all torques about the centre one-signed, or <= 1 contact), FREE-TRANS
    (the normals' cone is not the whole plane), PINNED otherwise (opposing contacts recorded).
    Every free motion is then tested for real (exact target, SAT sweep >= 2000 steps, tol
    5e-9), and rotation about each contact vertex of Q is tested too.

T2  the drain.  When a free motion drops a corner to <= 1 meeter, apply it, then run the
    exhaustive simultaneous snap search of pi_drain_3p9907.py part C (all near-axis squares,
    corner lattice cells within 0.7, keep valid packings, maximise the Young-closed count),
    then re-run T1 on the remaining crowded corners.  Stop when no corner frees.

Pure geometry, one process, BLAS pinned, no LP.  Writes only under attempts/A102-rigidity-drain.
Usage: python rigid102.py [selftest|all|<packing name>]
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import json
import math
import time
from decimal import Decimal
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
A102 = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(A102))
ATT = os.path.join(ROOT, 'attempts')
A87R = os.path.join(ATT, 'A87-drain-flow', 'results')
RES = os.path.join(A102, 'results')
LOGS = os.path.join(A102, 'logs')

VALID_TOL = 5e-9          # certification tolerance of the drain (pi_drain_3p9907)
CONTACT_TOL = 1e-7        # a contact, per the brief
# A square MEETS a corner cell.  Primary bar 1e-9 (exact: any real intrusion counts, the bar
# at which every packing of the corpus is certified K0-BLOCKED); A102_BAR=1e-6 re-runs the
# whole thing at the strict85 / degen87 census bar, where a tangency-level "nick" is not a
# block and some corners of the corpus are K0-FREE to begin with.
MEET_TOL = float(os.environ.get('A102_BAR', '1e-9'))
BARTAG = '' if MEET_TOL == 1e-9 else '_bar%g' % MEET_TOL
MEET_TOL6 = 1e-6          # the strict85 / degen87 census bar
TAU_TOL = 1e-9            # a torque this small does not oppose
NSWEEP = 2000
CORNERS = ('BL', 'BR', 'TR', 'TL')
FSGN = {'BL': (1.0, 1.0), 'BR': (-1.0, 1.0), 'TR': (-1.0, -1.0), 'TL': (1.0, -1.0)}

T0 = time.time()
_fh = open(os.path.join(LOGS, 'rigid102%s.log' % BARTAG), 'a', encoding='utf-8')


def log(*a):
    m = ' '.join(str(v) for v in a)
    print(m, flush=True)
    _fh.write('[%7.1f] %s\n' % (time.time() - T0, m))
    _fh.flush()


# ============================================================ basic geometry

def verts(cx, cy, th):
    c, s_ = math.cos(th), math.sin(th)
    return [(cx + 0.5 * (dx * c - dy * s_), cy + 0.5 * (dx * s_ + dy * c))
            for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def sep(p, q):
    """SAT separation of two convex quads: >= 0 disjoint, < 0 penetration depth."""
    best = -9.0
    for poly_ in (p, q):
        for i in range(4):
            a, b = poly_[i], poly_[(i + 1) % 4]
            ex, ey = b[0] - a[0], b[1] - a[1]
            n = math.hypot(ex, ey)
            ax, ay = -ey / n, ex / n
            pp = [x * ax + y * ay for x, y in p]
            qq = [x * ax + y * ay for x, y in q]
            v = max(min(qq) - max(pp), min(pp) - max(qq))
            if v > best:
                best = v
    return best


def wall_gap(p, s):
    return min(min(x for x, y in p), min(y for x, y in p),
               s - max(x for x, y in p), s - max(y for x, y in p))


def valid(poses, s, tol=VALID_TOL):
    polys = [verts(*q) for q in poses]
    worst = min(wall_gap(p, s) for p in polys)
    n = len(polys)
    for i in range(n):
        for j in range(i + 1, n):
            g = sep(polys[i], polys[j])
            if g < worst:
                worst = g
    return worst >= -tol, worst


def valid_one(poses, i, newpose, s, tol=VALID_TOL):
    """Only square i moved: check it against the walls and the other (fixed) squares."""
    p = verts(*newpose)
    worst = wall_gap(p, s)
    if worst < -tol:
        return False, worst
    for j, q in enumerate(poses):
        if j == i:
            continue
        g = sep(p, verts(*q))
        if g < worst:
            worst = g
        if worst < -tol:
            return False, worst
    return True, worst


def corner_depth(sq, cn, s):
    """A90 / exchange87 depth: 1 - min over the square of max(px, py) in the corner frame."""
    ox, oy = (0.0, 0.0) if cn == 'BL' else (s, 0.0) if cn == 'BR' else \
        (s, s) if cn == 'TR' else (0.0, s)
    sx, sy = FSGN[cn]
    W = [(sx * (qx - ox), sy * (qy - oy)) for qx, qy in verts(*sq)]
    cand = list(W)
    for k in range(4):
        a, b = W[k], W[(k + 1) % 4]
        d = (b[0] - a[0]) - (b[1] - a[1])
        if abs(d) > 1e-14:
            t = (a[1] - a[0]) / d
            if -1e-12 <= t <= 1 + 1e-12:
                t = min(1.0, max(0.0, t))
                cand.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
    return max(0.0, 1.0 - min(max(p[0], p[1]) for p in cand))


def meeters(poses, s, cn, tol=MEET_TOL):
    out = [(i, corner_depth(q, cn, s)) for i, q in enumerate(poses)]
    return sorted([(i, d) for i, d in out if d > tol], key=lambda t: -t[1])


def meet_counts(poses, s, tol=MEET_TOL):
    return {cn: len(meeters(poses, s, cn, tol)) for cn in CORNERS}


# ============================================================ contact set

def _edge_normal_out(a, b, owner_centre):
    ex, ey = b[0] - a[0], b[1] - a[1]
    n = math.hypot(ex, ey)
    nx, ny = -ey / n, ex / n
    mx, my = (a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0
    if (mx - owner_centre[0]) * nx + (my - owner_centre[1]) * ny < 0:
        nx, ny = -nx, -ny
    return nx, ny


def contacts_of(poses, i, s, tol=CONTACT_TOL):
    """Every contact of square i: vertex-edge incidences with the other squares (gap < tol)
    and with the walls.  Contact normal = the outward normal of the touched EDGE; the force F
    reported is the one acting ON square i (pointing into i)."""
    P = poses[i]
    A = verts(*P)
    out = []
    for j, q in enumerate(poses):
        if j == i:
            continue
        B = verts(*q)
        if sep(A, B) >= tol:
            continue
        pairs = []
        # vertex of i on edge of j   -> normal owned by j, force on i = +n_out(j)
        # vertex of j on edge of i   -> normal owned by i, force on i = -n_out(i)
        for (V, E, own, sign) in ((A, B, q, +1.0), (B, A, P, -1.0)):
            for v in V:
                for k in range(4):
                    a, b = E[k], E[(k + 1) % 4]
                    ex, ey = b[0] - a[0], b[1] - a[1]
                    L = ex * ex + ey * ey
                    t = max(0.0, min(1.0, ((v[0] - a[0]) * ex + (v[1] - a[1]) * ey) / L))
                    fx, fy = a[0] + t * ex, a[1] + t * ey
                    d = math.hypot(v[0] - fx, v[1] - fy)
                    if d < tol:
                        nx, ny = _edge_normal_out(a, b, (own[0], own[1]))
                        pairs.append(((v[0] + fx) / 2.0, (v[1] + fy) / 2.0,
                                      sign * nx, sign * ny, d))
        for (px, py, fx, fy, d) in pairs:
            dup = False
            for c in out:
                if (abs(c['point'][0] - px) < 1e-6 and abs(c['point'][1] - py) < 1e-6
                        and c['F'][0] * fx + c['F'][1] * fy > 1.0 - 1e-6):
                    dup = True
                    break
            if not dup:
                out.append({'with': 'square %d' % j, 'j': j, 'point': (px, py),
                            'F': (fx, fy), 'dist': d, 'gap': sep(A, B)})
    walls = (('left wall', min(x for x, y in A), (1.0, 0.0), lambda v: v[0] - 0.0),
             ('bottom wall', min(y for x, y in A), (0.0, 1.0), lambda v: v[1] - 0.0),
             ('right wall', s - max(x for x, y in A), (-1.0, 0.0), lambda v: s - v[0]),
             ('top wall', s - max(y for x, y in A), (0.0, -1.0), lambda v: s - v[1]))
    for name, gap, nrm, dfn in walls:
        if gap < tol:
            for v in A:
                if dfn(v) < tol:
                    out.append({'with': name, 'j': None, 'point': (v[0], v[1]),
                                'F': nrm, 'dist': dfn(v), 'gap': gap})
    return out


def torques(C, pivot):
    return [(c['point'][0] - pivot[0]) * c['F'][1] - (c['point'][1] - pivot[1]) * c['F'][0]
            for c in C]


def one_signed(taus, tol=TAU_TOL):
    """+1 CCW free, -1 CW free, 0 opposed.  (both signs free -> +1 chosen by caller)"""
    if all(t >= -tol for t in taus):
        return +1
    if all(t <= tol for t in taus):
        return -1
    return 0


def screw_cone(C, tol=1e-9):
    """The FULL first-order motion cone of Q as a rigid body.  With v the velocity of the
    origin and w the angular velocity, the no-penetration condition at contact k is
        a_k . (v_x, v_y, w) >= 0,      a_k = (F_kx, F_ky, (r_k x F_k)_z).
    Q is first-order RIGID iff this cone is {0}.  Decided without an LP: if the rows span a
    plane or less, any vector in their null space is a motion; otherwise every extreme ray of
    the cone is +- a_i x a_j for some pair, so those are enumerated and tested.
    Returns (free, rays) with each ray = (vx, vy, w) normalised."""
    A = []
    for c in C:
        rx, ry = c['point']
        A.append((c['F'][0], c['F'][1], rx * c['F'][1] - ry * c['F'][0]))
    if not A:
        return True, [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)]

    def ok(w):
        n = math.sqrt(sum(x * x for x in w))
        if n < 1e-12:
            return False, None
        w = tuple(x / n for x in w)
        return all(a[0] * w[0] + a[1] * w[1] + a[2] * w[2] >= -tol for a in A), w

    rays = []
    # null-space directions (rank <= 2): Gram-Schmidt on the rows
    basis = []
    for a in A:
        v = list(a)
        for b in basis:
            d = sum(x * y for x, y in zip(v, b))
            v = [x - d * y for x, y in zip(v, b)]
        n = math.sqrt(sum(x * x for x in v))
        if n > 1e-9:
            basis.append([x / n for x in v])
    if len(basis) <= 2:
        for e in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
            v = list(e)
            for b in basis:
                d = sum(x * y for x, y in zip(v, b))
                v = [x - d * y for x, y in zip(v, b)]
            n = math.sqrt(sum(x * x for x in v))
            if n > 1e-9:
                r = ok([x / n for x in v])
                if r[0]:
                    rays.append(r[1])
    for i in range(len(A)):
        for j in range(i + 1, len(A)):
            a, b = A[i], A[j]
            cr = (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
                  a[0] * b[1] - a[1] * b[0])
            for sgn in (1.0, -1.0):
                r = ok([sgn * x for x in cr])
                if r[0] and not any(sum((x - y) ** 2 for x, y in zip(r[1], q)) < 1e-14
                                    for q in rays):
                    rays.append(r[1])
    if len(A) == 1:
        for e in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
            r = ok(list(e))
            if r[0]:
                rays.append(r[1])
    return bool(rays), rays[:12]


def ray_motion(ray, tol=1e-12):
    """(vx, vy, w) -> ('translate', unit direction) or ('rotate', pivot, sign)."""
    vx, vy, w = ray
    if abs(w) <= 1e-9:
        n = math.hypot(vx, vy)
        if n < 1e-12:
            return None
        return ('translate', (vx / n, vy / n))
    return ('rotate', (-vy / w, vx / w), 1 if w > 0 else -1)


def trans_cone(C, escape=None, tol=1e-9):
    """Feasible translation directions {v : v.F_k >= 0}.  Returns (feasible, best_dir,
    margin) where best_dir maximises the dot with `escape` among feasible directions."""
    F = [c['F'] for c in C]
    if not F:
        return True, (escape or (1.0, 0.0)), 1.0
    N = 1440
    best = None
    feas = []
    for k in range(N):
        a = 2 * math.pi * k / N
        v = (math.cos(a), math.sin(a))
        m = min(v[0] * f[0] + v[1] * f[1] for f in F)
        if m > tol:
            feas.append((v, m))
        if best is None or m > best[1]:
            best = (v, m)
    if not feas:
        return False, best[0], best[1]
    if escape is None:
        pick = max(feas, key=lambda t: t[1])
    else:
        pick = max(feas, key=lambda t: (t[0][0] * escape[0] + t[0][1] * escape[1]))
    return True, pick[0], pick[1]


# ============================================================ motion sweeps

def blocker_of(poses, i, pose, s):
    """Which square / wall is tightest at this pose."""
    p = verts(*pose)
    best = ('left wall', min(x for x, y in p))
    for nm, g in (('bottom wall', min(y for x, y in p)),
                  ('right wall', s - max(x for x, y in p)),
                  ('top wall', s - max(y for x, y in p))):
        if g < best[1]:
            best = (nm, g)
    for j, q in enumerate(poses):
        if j == i:
            continue
        g = sep(p, verts(*q))
        if g < best[1]:
            best = ('square %d' % j, g)
    return {'blocker': best[0], 'gap': float('%.3e' % best[1])}


def _pose_rot(cx, cy, th, pivot, a):
    px, py = pivot
    c, sn = math.cos(a), math.sin(a)
    return (px + (cx - px) * c - (cy - py) * sn,
            py + (cx - px) * sn + (cy - py) * c, th + a)


def rot_sweep(poses, i, pivot, th_target, s, n=NSWEEP):
    """Rotate square i about `pivot` until its angle reaches th_target.  On a block, the
    maximal feasible fraction is refined by 50 bisections.  Returns
    (ok, worst_gap, frac_reached, final_pose, blocker_or_None)."""
    cx, cy, th = poses[i]
    dth = th_target - th
    worst = 9.0
    last = (cx, cy, th)
    for k in range(1, n + 1):
        pose = _pose_rot(cx, cy, th, pivot, dth * k / n)
        ok, w = valid_one(poses, i, pose, s)
        worst = min(worst, w)
        if not ok:
            lo, hi = (k - 1) / n, k / n
            for _ in range(50):
                mid = (lo + hi) / 2
                pm = _pose_rot(cx, cy, th, pivot, dth * mid)
                if valid_one(poses, i, pm, s)[0]:
                    lo, last = mid, pm
                else:
                    hi = mid
            return False, w, lo, last, blocker_of(poses, i, pose, s)
        last = pose
    return True, worst, 1.0, last, None


def trans_sweep(poses, i, direction, dist, s, cn=None, n=NSWEEP, stop_on_exit=True):
    """Translate square i along `direction` by up to `dist`.  If cn is given, stop as soon as
    the square leaves the corner cell.  Returns (ok, worst, frac, pose, exited)."""
    cx, cy, th = poses[i]
    ux, uy = direction
    worst = 9.0
    last = (cx, cy, th)
    for k in range(1, n + 1):
        t = dist * k / n
        pose = (cx + ux * t, cy + uy * t, th)
        ok, w = valid_one(poses, i, pose, s)
        worst = min(worst, w)
        if not ok:
            lo, hi = (k - 1) / n, k / n
            for _ in range(50):
                mid = (lo + hi) / 2
                pm = (cx + ux * dist * mid, cy + uy * dist * mid, th)
                if valid_one(poses, i, pm, s)[0]:
                    lo, last = mid, pm
                else:
                    hi = mid
            ex = corner_depth(last, cn, s) <= MEET_TOL if cn else False
            return False, w, lo, last, ex, blocker_of(poses, i, pose, s)
        last = pose
        if stop_on_exit and cn is not None and corner_depth(pose, cn, s) <= MEET_TOL:
            return True, worst, t / dist, pose, True, None
    ex = cn is None or corner_depth(last, cn, s) <= MEET_TOL
    return True, worst, 1.0, last, ex, None


def axis_targets(th):
    below = math.floor(th / (math.pi / 2)) * (math.pi / 2)
    return below, below + math.pi / 2


# ============================================================ T1

def t1_meeter(poses, s, cn, i):
    """The rigidity test on square i as a meeter of corner cn."""
    P = poses[i]
    C = contacts_of(poses, i, s)
    tau_c = torques(C, (P[0], P[1]))
    rec = {'square': i, 'corner': cn,
           'depth': round(corner_depth(P, cn, s), 12),
           'tilt_deg': round(math.degrees(P[2]) % 90.0, 9),
           'n_contacts': len(C),
           'contacts': [{'with': c['with'], 'point': [round(v, 9) for v in c['point']],
                         'normal_force_on_Q': [round(v, 9) for v in c['F']],
                         'gap': float('%.3e' % c['gap']),
                         'torque_about_centre': round(t, 9)}
                        for c, t in zip(C, tau_c)],
           'motions': []}
    sgn = one_signed(tau_c)
    escape = FSGN[cn]
    esc = (escape[0] / math.sqrt(2), escape[1] / math.sqrt(2))
    feas, tdir, tmargin = trans_cone(C, esc)

    def _rot(kind, tgt, direction, first_order):
        ok, worst, frac, pose, blk = rot_sweep(poses, i, kind[1], tgt, s)
        m = {'kind': kind[0], 'direction': direction, 'first_order_free': bool(first_order),
             'target_deg': round(math.degrees(tgt), 9),
             'sweep_deg': round(math.degrees(tgt - P[2]), 9),
             'reached_deg': round(math.degrees((tgt - P[2]) * frac), 9),
             'collision_free': bool(ok), 'worst_gap': float('%.3e' % worst),
             'fraction_reached': round(frac, 6), 'blocked_by': blk,
             'pose': [round(v, 12) for v in pose]}
        if len(kind) > 2:
            m['pivot'] = [round(v, 9) for v in kind[1]]
            m['contact'] = kind[2]
        m.update(_effect(poses, s, i, pose, cn))
        rec['motions'].append(m)

    # ---- FREE-ROT about the centre (the first-order-free direction, and the nearest
    #      axis-aligned angle if that is the other way)
    below, above = axis_targets(P[2])
    ctr = ('rot_centre', (P[0], P[1]))
    if sgn != 0 or len(C) <= 1:
        d = sgn if sgn != 0 else +1
        _rot(ctr, above if d > 0 else below, 'CCW' if d > 0 else 'CW', True)
    nearest = round(P[2] / (math.pi / 2)) * (math.pi / 2)
    if not (sgn != 0 or len(C) <= 1) or abs(nearest - (above if (sgn or 1) > 0 else below)) > 1e-15:
        _rot(('rot_centre_nearest', (P[0], P[1])), nearest,
             'CCW' if nearest > P[2] else 'CW',
             (sgn > 0 and nearest > P[2]) or (sgn < 0 and nearest < P[2]) or len(C) <= 1)

    # ---- FREE-TRANS
    if feas:
        ok, worst, frac, pose, exited, blk = trans_sweep(poses, i, tdir, 1.6, s, cn)
        m = {'kind': 'translate', 'direction': [round(v, 6) for v in tdir],
             'cone_margin': round(tmargin, 9), 'first_order_free': True,
             'collision_free': bool(ok), 'worst_gap': float('%.3e' % worst),
             'travel': round(1.6 * frac, 9), 'exits_cell': bool(exited),
             'fraction_reached': round(frac, 6),
             'blocked_by': blk, 'pose': [round(v, 12) for v in pose]}
        m.update(_effect(poses, s, i, pose, cn))
        rec['motions'].append(m)

    # ---- rotation about each contact vertex of Q
    seen = []
    seen0 = []
    for c in C:
        p = c['point']
        if any(abs(p[0] - q[0]) < 1e-9 and abs(p[1] - q[1]) < 1e-9 for q in seen):
            continue
        seen.append(p)
        seen0.append(p)
        tp = torques(C, p)
        sp = one_signed(tp)
        if sp == 0:
            continue
        tgt = above if sp > 0 else below
        _rot(('rot_pivot', p, c['with']), tgt, 'CCW' if sp > 0 else 'CW', True)

    # ---- the full first-order motion cone (rotation about ANY point, translations included)
    free_screw, rays = screw_cone(C)
    rec['first_order_rigid'] = not free_screw
    rec['n_screw_rays'] = len(rays)
    tested_p = [(P[0], P[1])] + seen0
    tested_d = [tdir] if feas else []
    for ray in rays[:6]:
        mm = ray_motion(ray)
        if mm is None:
            continue
        if mm[0] == 'rotate':
            p, sp = mm[1], mm[2]
            if any(abs(p[0] - q[0]) < 1e-7 and abs(p[1] - q[1]) < 1e-7 for q in tested_p):
                continue
            if abs(p[0]) > 1e6 or abs(p[1]) > 1e6:
                continue
            tested_p.append(p)
            _rot(('rot_screw', p, 'motion cone ray'), above if sp > 0 else below,
                 'CCW' if sp > 0 else 'CW', True)
        else:
            d = mm[1]
            if any(d[0] * q[0] + d[1] * q[1] > 1 - 1e-7 for q in tested_d):
                continue
            tested_d.append(d)
            ok, worst, frac, pose, exited, blk = trans_sweep(poses, i, d, 1.6, s, cn)
            m = {'kind': 'translate_screw', 'direction': [round(v, 6) for v in d],
                 'first_order_free': True, 'collision_free': bool(ok),
                 'worst_gap': float('%.3e' % worst), 'travel': round(1.6 * frac, 9),
                 'fraction_reached': round(frac, 6), 'exits_cell': bool(exited),
                 'blocked_by': blk, 'pose': [round(v, 12) for v in pose]}
            m.update(_effect(poses, s, i, pose, cn))
            rec['motions'].append(m)

    # ---- class
    if len(C) <= 1:
        rec['class'] = 'FREE-ROT'
    elif sgn != 0:
        rec['class'] = 'FREE-ROT'
    elif feas:
        rec['class'] = 'FREE-TRANS'
    else:
        rec['class'] = 'PINNED'
    rec['torque_sign'] = int(sgn)
    rec['trans_cone_open'] = bool(feas)
    if rec['class'] == 'PINNED':
        pos = [c['with'] for c, t in zip(C, tau_c) if t > TAU_TOL]
        neg = [c['with'] for c, t in zip(C, tau_c) if t < -TAU_TOL]
        rec['opposing_contacts'] = {'CCW': pos, 'CW': neg}
        walls = [c for c in C if c['j'] is None]
        sqs = sorted({c['j'] for c in C if c['j'] is not None})
        rec['pin_kind'] = ('wall+one_square' if len(sqs) == 1 and walls else
                           'two_or_more_squares' if len(sqs) >= 2 else
                           'walls_only' if not sqs else 'one_square_only')
        rec['pinned_by'] = {'walls': sorted({c['with'] for c in walls}), 'squares': sqs}
    else:
        walls = [c for c in C if c['j'] is None]
        sqs = sorted({c['j'] for c in C if c['j'] is not None})
        rec['pinned_by'] = {'walls': sorted({c['with'] for c in walls}), 'squares': sqs}
    # a motion frees the corner if the pose it REACHES (full target, or the maximal feasible
    # fraction found by bisection) is a valid packing with <= 1 meeter left in the corner
    full = [m for m in rec['motions'] if m['collision_free'] and m['frees_corner']]
    part = [m for m in rec['motions'] if not m['collision_free'] and m['frees_corner']
            and m['fraction_reached'] > 0.0]
    rec['frees_corner'] = bool(full or part)
    rec['frees_corner_full'] = bool(full)
    rec['frees_corner_partial_only'] = bool(part and not full)
    rec['freeing_motion'] = (full + part)[0]['kind'] if (full or part) else None
    return rec


def _effect(poses, s, i, pose, cn):
    """Effect of moving square i to `pose`: the corner cn is FREED iff it is left with at most
    one meeter and the whole configuration is still a valid packing."""
    Q = list(poses)
    Q[i] = tuple(pose)
    mc = meet_counts(Q, s)
    mc6 = meet_counts(Q, s, MEET_TOL6)
    ok, w = valid(Q, s)
    return {'meet_counts_after': mc, 'meet_counts_after_1e6': mc6,
            'config_valid_after': bool(ok), 'worst_gap_after': float('%.3e' % w),
            'frees_corner': bool(ok and mc[cn] <= 1)}


def t1_packing(poses, s, tol=MEET_TOL):
    rows = []
    for cn in CORNERS:
        M = meeters(poses, s, cn, tol)
        if len(M) < 2:
            continue
        for (i, d) in sorted(M, key=lambda t: t[1]):   # shallower first
            r = t1_meeter(poses, s, cn, i)
            r['is_second_meeter'] = bool((i, d) == min(M, key=lambda t: t[1]))
            rows.append(r)
    return rows


# ============================================================ T2: snaps

def lattice(s):
    return {'BL': lambda i, j: (i + 0.5, j + 0.5),
            'BR': lambda i, j: (s - i - 0.5, j + 0.5),
            'TR': lambda i, j: (s - i - 0.5, s - j - 0.5),
            'TL': lambda i, j: (i + 0.5, s - j - 0.5)}


def candidates(q, s, rad=0.7, tilt_tol=3.0):
    cx, cy, th = q
    t = math.degrees(th) % 90.0
    t = min(t, 90.0 - t)
    if t > tilt_tol:
        return [None]
    out = [None]
    for L, f in lattice(s).items():
        for i in range(5):
            for j in range(5):
                X, Y = f(i, j)
                if (abs(X - cx) <= rad and abs(Y - cy) <= rad
                        and 0.5 <= X <= s - 0.5 and 0.5 <= Y <= s - 0.5):
                    if not any(abs(X - o[3]) < 1e-12 and abs(Y - o[4]) < 1e-12
                               for o in out[1:]):
                        out.append((L, i, j, X, Y))
    return out


def occupied_young(Q, s):
    occ = {}
    for L, f in lattice(s).items():
        cells = set()
        for i in range(5):
            for j in range(5):
                X, Y = f(i, j)
                for q in Q:
                    if (abs(q[0] - X) < 1e-9 and abs(q[1] - Y) < 1e-9
                            and abs(math.sin(2 * q[2])) < 1e-9):
                        cells.add((i, j))
        young = {(i, j) for (i, j) in cells
                 if all((a, b) in cells for a in range(i + 1) for b in range(j + 1))}
        occ[L] = sorted(young)
    return occ


def snap_search(P, s, cap=400000):
    """Exhaustive simultaneous snap (DFS with sound pruning): a partial assignment is pruned
    only against squares whose final pose is already fixed (non-movers and assigned movers).
    Objective: maximise the Young-closed count, then the number of squares moved."""
    cands = {i: candidates(q, s) for i, q in enumerate(P)}
    movers = [i for i, c in cands.items() if len(c) > 1]
    fixed = [i for i in range(len(P)) if i not in movers]
    best = [None]
    leaves = [0]
    truncated = [False]

    def score(Q):
        occ = occupied_young(Q, s)
        return sum(len(v) for v in occ.values())

    def rec(k, cur, placed):
        if truncated[0]:
            return
        if k == len(movers):
            leaves[0] += 1
            if leaves[0] > cap:
                truncated[0] = True
                return
            ok, w = valid(cur, s)
            if not ok:
                return
            sc = score(cur)
            moved = sum(1 for m in movers if cur[m] != P[m])
            if best[0] is None or (sc, moved) > (best[0][0], best[0][1]):
                best[0] = (sc, moved, list(cur), w)
            return
        i = movers[k]
        for c in cands[i]:
            pose = P[i] if c is None else (c[3], c[4], 0.0)
            p = verts(*pose)
            bad = wall_gap(p, s) < -VALID_TOL
            if not bad:
                for j in placed:
                    if sep(p, verts(*cur[j])) < -VALID_TOL:
                        bad = True
                        break
            if bad:
                continue
            nxt = list(cur)
            nxt[i] = pose
            rec(k + 1, nxt, placed + [i])

    rec(0, list(P), list(fixed))
    if best[0] is None:
        return P, 0, 0, truncated[0], {}
    sc, moved, Q, w = best[0]
    return Q, sc, moved, truncated[0], occupied_young(Q, s)


# ============================================================ T2 driver

def drain(name, poses, s, max_rounds=6):
    out = {'packing': name, 'side': s, 'n': len(poses),
           'initial': {'meet_counts': meet_counts(poses, s),
                       'meet_counts_1e6': meet_counts(poses, s, MEET_TOL6),
                       'd2': {}, 'valid': None},
           'rounds': [], 'moves': []}
    out['initial']['d2_1e6'] = {}
    for cn in CORNERS:
        M = meeters(poses, s, cn)
        M6 = meeters(poses, s, cn, MEET_TOL6)
        out['initial']['d2'][cn] = round(M[-1][1], 12) if len(M) >= 2 else None
        out['initial']['d2_1e6'][cn] = round(M6[-1][1], 12) if len(M6) >= 2 else None
    ok, w = valid(poses, s)
    out['initial']['valid'] = [bool(ok), float('%.3e' % w)]
    cur = list(poses)
    t1_all = []
    for rnd in range(max_rounds):
        rows = t1_packing(cur, s)
        t1_all.append(rows)
        fr = [r for r in rows if r['frees_corner']]
        rd = {'round': rnd, 'n_meeters_tested': len(rows),
              'classes': {r['class']: 0 for r in rows},
              'freed': bool(fr)}
        for r in rows:
            rd['classes'][r['class']] += 1
        if not fr:
            rd['stop'] = 'no corner frees'
            out['rounds'].append(rd)
            break
        # apply the first freeing motion (a full one before a partial one; within a round,
        # the shallowest meeter of the first crowded corner)
        r = ([x for x in fr if x['frees_corner_full']] or fr)[0]
        cands_m = ([mm for mm in r['motions'] if mm['collision_free'] and mm['frees_corner']]
                   or [mm for mm in r['motions'] if mm['frees_corner']
                       and mm['fraction_reached'] > 0.0])
        m = cands_m[0]
        cur[r['square']] = tuple(m['pose'])
        out['moves'].append({'round': rnd, 'corner': r['corner'], 'square': r['square'],
                             'class': r['class'], 'motion': m['kind'],
                             'detail': {k: m[k] for k in m
                                        if k in ('direction', 'sweep_deg', 'travel',
                                                 'pivot', 'target_deg', 'exits_cell')},
                             'meet_counts_after': m['meet_counts_after']})
        rd['applied'] = {'square': r['square'], 'corner': r['corner'], 'motion': m['kind']}
        # snaps
        Q, sc, moved, trunc, occ = snap_search(cur, s)
        okQ, wQ = valid(Q, s)
        rd['snap'] = {'young_k': sc, 'squares_moved': moved, 'truncated': trunc,
                      'young': occ, 'valid': [bool(okQ), float('%.3e' % wQ)]}
        if okQ and sc > 0:
            cur = list(Q)
            out['moves'].append({'round': rnd, 'kind': 'SNAP', 'squares_moved': moved,
                                 'young_k': sc, 'young': occ})
        out['rounds'].append(rd)
        rd['meet_counts_now'] = meet_counts(cur, s)
    occ = occupied_young(cur, s)
    ok, w = valid(cur, s)
    out['final'] = {'meet_counts': meet_counts(cur, s), 'young': occ,
                    'k': sum(len(v) for v in occ.values()),
                    'valid': [bool(ok), float('%.3e' % w)],
                    'poses': [[round(v, 12) for v in q] for q in cur]}
    out['t1'] = t1_all
    out['drained'] = bool(out['final']['k'] >= 1 and out['moves'])
    return out


# ============================================================ corpus

def _fr(x):
    return Fraction(x) if not isinstance(x, Fraction) else x


def load_corpus():
    C = []
    # (a) the four floor records of k0dir2_87
    d = json.load(open(os.path.join(A87R, 'k0dir2_87.records.json')))
    for k, v in sorted(d['floors'].items()):
        if not v.get('poses'):
            continue
        s = float(Fraction(v['container_side_exact']))
        P = [(float(Fraction(p['cx_exact'])), float(Fraction(p['cy_exact'])),
              float(Fraction(p['theta_exact']))) for p in v['poses']]
        C.append({'name': 'floor_%s_%s' % (k, v['tag']), 'src': 'k0dir2_87.records.json',
                  'group': 'floor record (delta=%s)' % k, 'side': s, 'poses': P,
                  'side_ub': v['certified_side_upper_bound']})
    # (b) the eight exact K0-BLOCKED packings of A87 (= the strict85 set)
    dd = json.load(open(os.path.join(A87R, 'k0dir87.json')))
    rec = dd['record_K0_BLOCKED_packing']
    z = [Fraction(a) for a in rec['z']]
    C.append({'name': 'record_%s' % rec['tag'], 'src': 'k0dir87.json',
              'group': 'A87 K0-BLOCKED', 'side': float(z[33]),
              'poses': [(float(z[3 * i]), float(z[3 * i + 1]), float(z[3 * i + 2]))
                        for i in range(11)]})
    for i, line in enumerate(open(os.path.join(A87R, 'k0dir87.polish.jsonl'))):
        r = json.loads(line)
        if not r.get('exact_K0_BLOCKED') or not r.get('z_polished'):
            continue
        z = [Fraction(a) for a in r['z_polished']]
        C.append({'name': 'polish%02d_%s' % (i, r['tag']),
                  'src': 'k0dir87.polish.jsonl#%d' % i, 'group': 'A87 K0-BLOCKED',
                  'side': float(z[33]),
                  'poses': [(float(z[3 * j]), float(z[3 * j + 1]), float(z[3 * j + 2]))
                            for j in range(11)]})
    df = json.load(open(os.path.join(A87R, 'd2front87.json')))
    src_list = [('own_side_anchored', df['own_side_anchored'])]
    src_list += [('cap' + k, v) for k, v in sorted(df['per_cap_anchored'].items())]
    seen = set()
    n = 0
    for src, v in src_list:
        if not v.get('anchored_only'):
            continue
        for c in v.get('candidates', []):
            key = tuple(c['z'])
            if key in seen:
                continue
            seen.add(key)
            z = [Fraction(a) for a in c['z']]
            C.append({'name': 'anchored%d_%s' % (n, c['tag']),
                      'src': 'd2front87.json:%s' % src, 'group': 'A87 K0-BLOCKED',
                      'side': float(z[33]),
                      'poses': [(float(z[3 * j]), float(z[3 * j + 1]),
                                 float(z[3 * j + 2])) for j in range(11)]})
            n += 1
    # the canary
    t = json.load(open(os.path.join(ATT, 'A03-upper-reconstruct', 'trump11_exact.json')))
    C.append({'name': 'TRUMP_canary', 'src': 'A03/trump11_exact.json', 'group': 'canary',
              'side': float(Fraction(Decimal(t['s']))),
              'poses': [(float(Fraction(Decimal(q['cx']))), float(Fraction(Decimal(q['cy']))),
                         float(Fraction(Decimal(q['theta'])))) for q in t['squares']]})
    return C


# ============================================================ self-test

def selftest():
    """Reproduce the PI's drain of the 3.9907 record (pi_drain_3p9907.py)."""
    C = [c for c in load_corpus() if c['name'].startswith('floor_1e-03')][0]
    s, P = C['side'], C['poses']
    ok, w = valid(P, s)
    log('selftest: %s side %.12f valid %s worst %.2e' % (C['name'], s, ok, w))
    i3 = 3
    CC = contacts_of(P, i3, s)
    tau = torques(CC, (P[i3][0], P[i3][1]))
    log('  square 3 contacts (%d):' % len(CC))
    for c, t in zip(CC, tau):
        log('    %-14s at (%.4f,%.4f) F=(%+.3f,%+.3f) torque %+.4f %s'
            % (c['with'], c['point'][0], c['point'][1], c['F'][0], c['F'][1], t,
               'CCW' if t > 0 else 'CW'))
    sgn = one_signed(tau)
    log('  one-signed: %d (expect +1, CCW)' % sgn)
    r = t1_meeter(P, s, 'BR', 3)
    log('  class %s  frees_corner %s via %s' % (r['class'], r['frees_corner'],
                                                r['freeing_motion']))
    dr = drain('selftest_' + C['name'], P, s)
    log('  drain: k=%d young=%s valid=%s' % (dr['final']['k'], dr['final']['young'],
                                             dr['final']['valid']))
    ok_all = (sgn == +1 and r['class'] == 'FREE-ROT' and r['frees_corner']
              and dr['final']['k'] == 7)
    log('SELFTEST %s (expect FREE-ROT, CCW, k=7 as in pi_drain_3p9907.json)'
        % ('PASS' if ok_all else 'FAIL'))
    return ok_all


# ============================================================ main

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if cmd == 'selftest':
        sys.exit(0 if selftest() else 1)
    C = load_corpus()
    if cmd not in ('all',):
        C = [c for c in C if c['name'] == cmd or cmd in c['name']]
    log('corpus: %d packings' % len(C))
    rows = []
    fjl = open(os.path.join(RES, 'rigid102%s.jsonl' % BARTAG), 'w', encoding='utf-8')
    for c in C:
        t = time.time()
        okv, wv = valid(c['poses'], c['side'])
        log('== %-22s side %.9f  input valid %s (%.2e)  meet %s'
            % (c['name'], c['side'], okv, wv, meet_counts(c['poses'], c['side'])))
        d = drain(c['name'], c['poses'], c['side'])
        d['src'] = c['src']
        d['group'] = c['group']
        d['secs'] = round(time.time() - t, 2)
        fjl.write(json.dumps(d) + '\n')
        fjl.flush()
        cls = {}
        for rr in d['t1'][0]:
            cls[rr['class']] = cls.get(rr['class'], 0) + 1
        log('   T1 %s | moves %d | final k %d | drained %s | %.1f s'
            % (cls, len([m for m in d['moves'] if m.get('kind') != 'SNAP']),
               d['final']['k'], d['drained'], d['secs']))
        rows.append(d)
    fjl.close()
    summ = {'attempt': 'A102 rigidity drain', 'n_packings': len(rows),
            'valid_tol': VALID_TOL, 'contact_tol': CONTACT_TOL, 'meet_tol': MEET_TOL,
            'sweep_steps': NSWEEP,
            'table': [{'packing': r['packing'], 'group': r['group'], 'side': r['side'],
                       'initial_meet': r['initial']['meet_counts'],
                       'd2': r['initial']['d2'],
                       'n_moves': len([m for m in r['moves'] if m.get('kind') != 'SNAP']),
                       'final_k': r['final']['k'], 'young': r['final']['young'],
                       'drained': r['drained'],
                       'classes': [{'corner': x['corner'], 'square': x['square'],
                                    'depth': x['depth'], 'class': x['class'],
                                    'pin_kind': x.get('pin_kind'),
                                    'frees': x['frees_corner']}
                                   for x in r['t1'][0]]}
                      for r in rows]}
    json.dump(summ, open(os.path.join(RES, 'rigid102%s.json' % BARTAG), 'w'), indent=1)
    log('wrote results/rigid102%s.{json,jsonl} (meet bar %g)' % (BARTAG, MEET_TOL))


if __name__ == '__main__':
    main()
