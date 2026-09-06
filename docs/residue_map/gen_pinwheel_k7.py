"""PI candidate (2026-09-06): TL 1, TR 1, BR 2 stacked, BL 3 L-shape (7 axis-aligned slot squares), 4 free squares as a
pinwheel in the centre. Minimise the side s over the 4 free squares (cx, cy, theta) and s, SLSQP with many restarts,
seeded from random pinwheels and from A57's Y0036 LP shadow. Reports s*, the contact graph, and draws it."""
import math, random, json, sys
import numpy as np
from scipy.optimize import minimize
SHAT = 3.877083590022814
def fixed(s):
    return [(0.5, 0.5), (1.5, 0.5), (0.5, 1.5), (0.5, s-0.5), (s-0.5, s-0.5), (s-0.5, 0.5), (s-0.5, 1.5)]
FIXED_NAMES = ['BL(0,0)', 'BL(1,0)', 'BL(0,1)', 'TL(0,0)', 'TR(0,0)', 'BR(0,0)', 'BR(0,1)']
def sat_gap(c1, t1, c2, t2):
    best = -1e9
    for (cc, tt, oc, ot) in ((c1, t1, c2, t2), (c2, t2, c1, t1)):
        co, si = math.cos(tt), math.sin(tt)
        for ax in ((co, si), (-si, co)):
            d = abs((oc[0]-cc[0])*ax[0] + (oc[1]-cc[1])*ax[1])
            g = abs(ax[0]*math.cos(ot) + ax[1]*math.sin(ot)) + abs(-ax[0]*math.sin(ot) + ax[1]*math.cos(ot))
            best = max(best, d - 0.5 - 0.5*g)
    return best
def unpack(z):
    s = z[0]; F = [(z[1+3*i], z[2+3*i], z[3+3*i]) for i in range(4)]
    return s, F
def cons(z):
    s, F = unpack(z); out = []
    fx = fixed(s)
    for i in range(4):
        cx, cy, th = F[i]; w = (abs(math.cos(th)) + abs(math.sin(th)))/2
        out += [cx - w, s - w - cx, cy - w, s - w - cy]
        for j in range(i+1, 4): out.append(sat_gap((cx, cy), th, F[j][:2], F[j][2]))
        for p in fx: out.append(sat_gap((cx, cy), th, p, 0.0))
    return np.array(out)
def solve(z0):
    r = minimize(lambda z: z[0], z0, method='SLSQP', constraints=[{'type': 'ineq', 'fun': cons}],
                 bounds=[(3.5, 4.5)] + [(0, 4.5), (0, 4.5), (-10, 10)]*4, options={'maxiter': 400, 'ftol': 1e-12})
    return r.x, r.x[0], cons(r.x).min()
def pinwheel(s, cx, cy, r, th, phi):
    return [(cx + r*math.cos(phi + k*math.pi/2), cy + r*math.sin(phi + k*math.pi/2), th) for k in range(4)]
rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
starts = []
# the LP shadow of Y0036_D07_D00 (three at 41.25 deg + the conditioned square)
starts.append((3.95, [(1.2498, 2.4512, math.radians(41.25)), (1.9485, 3.1715, math.radians(41.25)), (2.6094, 2.4200, math.radians(41.25)), (1.88, 1.53, math.radians(84.0))]))
for _ in range(int(sys.argv[2]) if len(sys.argv) > 2 else 300):
    s = rng.uniform(3.9, 4.2); th = rng.uniform(0, math.pi/2); phi = rng.uniform(0, 2*math.pi)
    starts.append((s, pinwheel(s, rng.uniform(1.6, 2.6), rng.uniform(1.8, 2.8), rng.uniform(0.45, 0.95), th, phi)))
best = None; sols = []
for s, F in starts:
    z0 = np.array([s] + [v for f in F for v in f])
    try: z, sv, feas = solve(z0)
    except Exception: continue
    if feas >= -1e-7:
        sols.append((sv, z))
        if best is None or sv < best[0]: best = (sv, z)
sols.sort(key=lambda t: t[0])
print(f'feasible solutions {len(sols)} of {len(starts)}; best s* = {best[0]:.6f} (s-hat {SHAT:.6f}, diff {best[0]-SHAT:+.6f})')
print('distinct minima (s rounded 1e-4):', sorted({round(sv, 4) for sv, _ in sols})[:12])
s, F = unpack(best[1]); fx = fixed(s)
print('free squares:'); [print(f'  {i}: ({cx:.5f}, {cy:.5f}, {math.degrees(th)%90:.3f} deg)') for i, (cx, cy, th) in enumerate(F)]
print('contacts (gap < 1e-6):')
names = [f'free{i}' for i in range(4)] + FIXED_NAMES
allsq = [(f[0], f[1], f[2]) for f in F] + [(p[0], p[1], 0.0) for p in fx]
for i in range(len(allsq)):
    for j in range(i+1, len(allsq)):
        if i >= 4 and j >= 4: continue
        g = sat_gap(allsq[i][:2], allsq[i][2], allsq[j][:2], allsq[j][2])
        if g < 1e-6: print(f'  {names[i]} - {names[j]}: gap {g:+.2e}')
for i, (cx, cy, th) in enumerate(F):
    w = (abs(math.cos(th)) + abs(math.sin(th)))/2
    for nm, g in (('left', cx-w), ('right', s-w-cx), ('bottom', cy-w), ('top', s-w-cy)):
        if g < 1e-6: print(f'  free{i} - {nm} wall: gap {g:+.2e}')
json.dump({'s': s, 'free': F, 'fixed': fx, 'all_minima': sorted({round(sv, 6) for sv, _ in sols})}, open('pinwheel_result.json', 'w'), indent=1)
