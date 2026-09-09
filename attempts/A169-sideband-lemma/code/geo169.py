"""A169 shared geometry: exact-ish SAT on closed unit squares, meeting the OPEN corner box, quadrant containment.
Squares: centre (cx, cy), tilt th (radians, edges at th and th+90 deg)."""
import math
S0 = 969271 / 250000
W0 = 0.025509
LAM = S0 / 3.82  # lambda_max of the window (K0-WIDEN: w = (lam-1)(1+sqrt2/2))

def verts(cx, cy, th):
    c, s = math.cos(th), math.sin(th)
    return [(cx + a * c - b * s, cy + a * s + b * c) for a, b in ((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5))]

def axes_of(P):
    out = []
    for i in range(4):
        (ax, ay), (bx, by) = P[i], P[(i + 1) % 4]
        ex, ey = bx - ax, by - ay
        n = math.hypot(ex, ey)
        out.append((-ey / n, ex / n))
    return out

def sat_gap(P, Q, axes=None):
    """max over separating axes of the projection gap; >= 0 means interior-disjoint (closed convex polygons)."""
    if axes is None:
        axes = axes_of(P) + axes_of(Q)
    best = -9.0
    for ux, uy in axes:
        pp = [x * ux + y * uy for x, y in P]
        qq = [x * ux + y * uy for x, y in Q]
        best = max(best, min(qq) - max(pp), min(pp) - max(qq))
    return best

def in_quadrant(P):
    return min(v[0] for v in P) >= -1e-12 and min(v[1] for v in P) >= -1e-12

def meets_open_box(P, c, eps=-1e-7):
    """closed square P meets the OPEN box (0,c)^2  <=>  no separating axis with gap >= 0 (box open)."""
    B = [(0, 0), (c, 0), (c, c), (0, c)]
    return sat_gap(P, B) < eps

def wall_flush_poses(c, ntilt=180, nh=120):
    """extremal candidates: Q2 with one vertex ON the wall x=0 (resp. floor y=0) at height (resp. abscissa) in a
    fine range, every tilt.  Any admissible Q2 can be translated toward a wall until it touches (meeting the open
    box and disjointness are preserved along -x? no -- so these are SEEDS, refined afterwards)."""
    out = []
    for k in range(ntilt):
        th = k * (math.pi / 2) / ntilt
        cs, sn = math.cos(th), math.sin(th)
        h = 0.5 * (cs + sn)
        for m in range(nh):
            u = 0.02 + m * (c + 0.7) / nh
            out.append((h, u, th))          # left vertex on the wall x=0 (centre x = h), centre height u
            out.append((u, h, th))          # bottom vertex on the floor
    return out

def second_meeter_exists(Q1, c, pitch=0.02, ntilt=90, refine=True):
    """Search Q2 (in the quadrant, interior-disjoint from Q1, meeting the open box (0,c)^2).
    Wall-flush seeds + grid, keep the K best, refine each.  Returns (found, best_pose, best_gap).
    A `found` is a certificate (SAT gap >= 0); a `not found` is evidence only."""
    cands = []
    for cx, cy, th in wall_flush_poses(c):
        P = verts(cx, cy, th)
        if not in_quadrant(P) or not meets_open_box(P, c):
            continue
        g = sat_gap(P, Q1)
        if g >= 0:
            return True, (cx, cy, th), g
        cands.append((g, (cx, cy, th)))
    tilts = [k * (math.pi / 2) / ntilt for k in range(ntilt)]
    n = int(2.3 / pitch)
    for i in range(n):
        for j in range(n):
            cx, cy = 0.5 + i * pitch, 0.5 + j * pitch
            for th in tilts:
                P = verts(cx, cy, th)
                if not in_quadrant(P) or not meets_open_box(P, c):
                    continue
                g = sat_gap(P, Q1)
                if g >= 0:
                    return True, (cx, cy, th), g
                cands.append((g, (cx, cy, th)))
    if not cands:
        return False, None, -9.0
    cands.sort(key=lambda z: -z[0])
    best = (cands[0][1], cands[0][0])
    if refine:
        for g, pose in cands[:12]:
            pose2, g2 = local_refine(Q1, c, pose)
            if g2 >= 0:
                return True, pose2, g2
            if g2 > best[1]:
                best = (pose2, g2)
    return False, best[0], best[1]

def local_refine(Q1, c, pose, iters=400):
    """coordinate-descent on the SAT gap subject to quadrant + meeting the open box."""
    cx, cy, th = pose
    g0 = sat_gap(verts(cx, cy, th), Q1)
    step = 0.02
    for _ in range(iters):
        improved = False
        for dx, dy, dt in ((step, 0, 0), (-step, 0, 0), (0, step, 0), (0, -step, 0), (0, 0, step), (0, 0, -step)):
            P = verts(cx + dx, cy + dy, th + dt)
            if not in_quadrant(P) or not meets_open_box(P, c):
                continue
            g = sat_gap(P, Q1)
            if g > g0 + 1e-15:
                cx, cy, th, g0 = cx + dx, cy + dy, th + dt, g
                improved = True
        if not improved:
            step *= 0.5
            if step < 1e-9:
                break
    return (cx, cy, th), g0
