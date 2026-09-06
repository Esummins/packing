"""PI's drain of the 3.9907 record: rotate square 3 CCW to axis-aligned, then simultaneous snaps."""
import json, math, itertools
R = r'C:\Users\esumm\code\packing'
rec = json.load(open(R + r'\attempts\A87-drain-flow\results\k0dir2_87.records.json'))['floors']['1e-03']
s = rec['certified_side_upper_bound']
P = [(p['cx'], p['cy'], math.radians(p['tilt_deg'])) for p in rec['poses']]
def sq(cx, cy, th):
    c, s_ = math.cos(th), math.sin(th)
    return [(cx + 0.5*(dx*c - dy*s_), cy + 0.5*(dx*s_ + dy*c)) for dx, dy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
def sep(p, q):
    axes = []
    for poly_ in (p, q):
        for i in range(4):
            a, b = poly_[i], poly_[(i+1)%4]; ex, ey = b[0]-a[0], b[1]-a[1]; n = math.hypot(ex, ey); axes.append((-ey/n, ex/n))
    best = -9
    for ax in axes:
        pp = [x*ax[0]+y*ax[1] for x, y in p]; qq = [x*ax[0]+y*ax[1] for x, y in q]
        best = max(best, min(qq)-max(pp), min(pp)-max(qq))
    return best
def wall_gap(p):  # min distance of polygon to leaving the container (negative = outside)
    return min(min(x for x, y in p), min(y for x, y in p), s - max(x for x, y in p), s - max(y for x, y in p))
def valid(poses, tol=5e-9):
    polys = [sq(*q) for q in poses]
    worst = min(wall_gap(p) for p in polys)
    for i in range(len(polys)):
        for j in range(i+1, len(polys)):
            worst = min(worst, sep(polys[i], polys[j]))
    return worst >= -tol, worst
ok, w = valid(P); print('record valid', ok, 'worst gap', f'{w:.2e}')

# ---- A. contacts of square 3 and torque sign about its centre for a CCW rotation
i3 = 3; cx3, cy3, th3 = P[i3]; poly3 = sq(cx3, cy3, th3)
print(f'square 3 centre ({cx3:.5f},{cy3:.5f}) tilt {math.degrees(th3)%90:.4f} deg = {math.degrees(th3)%90-90:.4f} deg from axis')
def contact_point(p, q):
    # approximate contact point: pair of (vertex of one, edge of other) with minimal distance
    best = (9, None)
    for A, B in ((p, q), (q, p)):
        for v in A:
            for k in range(4):
                a, b = B[k], B[(k+1)%4]; ex, ey = b[0]-a[0], b[1]-a[1]; L = ex*ex+ey*ey
                t = max(0, min(1, ((v[0]-a[0])*ex + (v[1]-a[1])*ey)/L)); fx, fy = a[0]+t*ex, a[1]+t*ey
                d = math.hypot(v[0]-fx, v[1]-fy)
                if d < best[0]: best = (d, ((v[0]+fx)/2, (v[1]+fy)/2))
    return best
for j, q in enumerate(P):
    if j == i3: continue
    g = sep(poly3, sq(*q))
    if g < 1e-6:
        d, pt = contact_point(poly3, sq(*q))
        # contact normal = outward normal of the touched EDGE (PI correction 2026-09-06: the centre-to-contact direction
        # gave the wrong sign for square 8, whose 25-degree edge has slope 0.47 < 1 and torques 3 CCW)
        qp = sq(*q); best = (9, None)
        for A, B, owner in ((poly3, qp, q), (qp, poly3, P[i3])):
            for v in A:
                for k in range(4):
                    a, b = B[k], B[(k+1)%4]; ex, ey = b[0]-a[0], b[1]-a[1]; L = ex*ex+ey*ey
                    t = max(0, min(1, ((v[0]-a[0])*ex + (v[1]-a[1])*ey)/L)); f = (a[0]+t*ex, a[1]+t*ey)
                    dd = math.hypot(v[0]-f[0], v[1]-f[1])
                    if dd < best[0]:
                        n = (-ey, ex); nn = math.hypot(*n); n = (n[0]/nn, n[1]/nn); mid = ((a[0]+b[0])/2, (a[1]+b[1])/2)
                        if (mid[0]-owner[0])*n[0] + (mid[1]-owner[1])*n[1] < 0: n = (-n[0], -n[1])  # outward from the edge's own square
                        F = n if owner is q else (-n[0], -n[1])  # force ON 3 points into 3
                        best = (dd, (v, F))
        v, F = best[1]; rx, ry = v[0]-cx3, v[1]-cy3
        torque = rx*F[1] - ry*F[0]
        print(f'  contact with square {j}: gap {g:.2e} at ({v[0]:.4f},{v[1]:.4f}); torque on 3 about its centre: {"CCW" if torque>0 else "CW"} ({torque:+.4f})')
for name, gap, pt_fn, nrm in (('right wall', s - max(x for x, y in poly3), lambda: max(poly3, key=lambda v: v[0]), (-1, 0)),
                            ('bottom wall', min(y for x, y in poly3), lambda: min(poly3, key=lambda v: v[1]), (0, 1))):
    if gap < 1e-6:
        pt = pt_fn(); rx, ry = pt[0]-cx3, pt[1]-cy3; torque = rx*nrm[1]-ry*nrm[0]
        print(f'  contact with {name}: gap {gap:.2e} at ({pt[0]:.4f},{pt[1]:.4f}); torque {"CCW" if torque>0 else "CW"} ({torque:+.4f})')
print('  lowest vertex of 3:', min(poly3, key=lambda v: v[1]), ' BR cell top y=1 -> intrusion', 1 - min(y for x, y in poly3))

# ---- B. rotation sweep of square 3 about its centre, CCW to axis-aligned
target = round(th3 / (math.pi/2)) * (math.pi/2)  # nearest axis-aligned angle
print(f'rotate 3 about centre from {math.degrees(th3):.4f} to {math.degrees(target):.4f} deg ({"CCW" if target>th3 else "CW"})')
worst_along = 9; N = 2000
for k in range(N+1):
    th = th3 + (target-th3)*k/N
    Q = list(P); Q[i3] = (cx3, cy3, th)
    ok, w = valid(Q, tol=5e-9)
    worst_along = min(worst_along, w)
    if not ok: print(f'  BLOCKED at step {k} angle {math.degrees(th):.4f}: worst gap {w:.2e}'); break
else:
    print(f'  rotation about centre is collision-free; worst gap along the path {worst_along:.2e}')
P1 = list(P); P1[i3] = (cx3, cy3, target)
poly3a = sq(*P1[i3]); print('  after rotation: 3 lowest y', min(y for x, y in poly3a), ' BR cell intrusion', max(0, 1 - min(y for x, y in poly3a)))
# BR cell meeters now
def cell_depth(p, x0, y0):  # depth into unit cell [x0,x0+1]x[y0,y0+1]
    xs = [x for x, y in p]; ys = [y for x, y in p]
    dx = min(max(xs), x0+1) - max(min(xs), x0); dy = min(max(ys), y0+1) - max(min(ys), y0)
    return min(dx, dy) if dx > 1e-12 and dy > 1e-12 else 0.0
corner_cells = {'BL': (0, 0), 'BR': (s-1, 0), 'TR': (s-1, s-1), 'TL': (0, s-1)}
for name, (x0, y0) in corner_cells.items():
    print(f'  {name} meeters after rotation:', [(i, round(cell_depth(sq(*q), x0, y0), 5)) for i, q in enumerate(P1) if cell_depth(sq(*q), x0, y0) > 1e-7])

# ---- C. simultaneous snaps: candidate cells for every near-axis square, exhaustive assignment, keep valid packings
lattices = {'BL': lambda i, j: (i+0.5, j+0.5), 'BR': lambda i, j: (s-i-0.5, j+0.5), 'TR': lambda i, j: (s-i-0.5, s-j-0.5), 'TL': lambda i, j: (i+0.5, s-j-0.5)}
def candidates(q, rad=0.7, tilt_tol=3.0):
    cx, cy, th = q; t = math.degrees(th) % 90; t = min(t, 90-t)
    if t > tilt_tol: return []
    out = [None]
    for L, f in lattices.items():
        for i in range(4):
            for j in range(4):
                X, Y = f(i, j)
                if abs(X-cx) <= rad and abs(Y-cy) <= rad and 0.5 <= X <= s-0.5 and 0.5 <= Y <= s-0.5:
                    out.append((L, i, j, X, Y))
    return out
cands = {i: candidates(q) for i, q in enumerate(P1)}
for i, c in cands.items():
    if len(c) > 1: print(f'  square {i} candidate cells:', [(L, a, b) for (L, a, b, X, Y) in c[1:]])
movers = [i for i, c in cands.items() if len(c) > 1]
best = None; n_valid = 0
for choice in itertools.product(*[cands[i] for i in movers]):
    Q = list(P1)
    for i, c in zip(movers, choice):
        if c is not None: Q[i] = (c[3], c[4], 0.0)
    ok, w = valid(Q, tol=5e-9)
    if ok:
        n_valid += 1; moved = sum(c is not None for c in choice)
        if best is None or moved > best[0]: best = (moved, choice, Q)
print(f'valid simultaneous snap assignments: {n_valid}; best moves {best[0]} squares')
moved, choice, Q = best
for i, c in zip(movers, choice):
    if c is not None: print(f'  square {i} -> {c[0]}({c[1]},{c[2]}) at ({c[3]:.4f},{c[4]:.4f}), displacement {math.hypot(c[3]-P1[i][0], c[4]-P1[i][1]):.4f}')
# Young diagram per corner from the final config
def occupied(Q):
    occ = {}
    for L, f in lattices.items():
        cells = set()
        for i in range(4):
            for j in range(4):
                X, Y = f(i, j)
                for q in Q:
                    if abs(q[0]-X) < 1e-9 and abs(q[1]-Y) < 1e-9 and abs(math.sin(2*q[2])) < 1e-9: cells.add((i, j))
        # Young closure: keep cells whose whole rectangle to the corner is occupied
        young = {(i, j) for (i, j) in cells if all((a, b) in cells for a in range(i+1) for b in range(j+1))}
        occ[L] = sorted(young)
    return occ
occ = occupied(Q); print('Young cells per corner (final):', occ, ' total simple k =', sum(len(v) for v in occ.values()))
print('final config valid:', valid(Q))
json.dump({'side': s, 'before': P, 'after_rotation': P1, 'final': Q, 'moves': {str(i): c for i, c in zip(movers, choice) if c}, 'young': occ}, open('drain3_result.json', 'w'), indent=1)
