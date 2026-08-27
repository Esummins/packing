"""A34 T1 sanity: known optimal packings satisfy the lifted POP (formulation.md section 1).
Independent of the Julia model. Exact-ish float check, tol 1e-12; prints worst residuals."""
import math

def corners(x, y, g, s):  # g=cos, s=sin
    e = (g, s); ep = (-s, g)
    return [(x + s1*e[0]/2 + s2*ep[0]/2, y + s1*e[1]/2 + s2*ep[1]/2)
            for s1 in (1, -1) for s2 in (1, -1)]

def check(name, S, sq, u):
    """sq: list of (x,y,theta_deg); u: dict (i,j)->(u1,u2) separating i from j (u.(pi-qj)>=0)."""
    worst = {}
    def rec(k, v): worst[k] = min(worst.get(k, 1e9), v)
    Z = []
    for (x, y, th) in sq:
        t = math.radians(th); g, si = math.cos(t), math.sin(t)
        assert g >= -1e-15 and si >= -1e-15, (name, th)
        Z.append((x, y, g, si))
        rec('C1', 1e9 if abs(g*g+si*si-1) > 1e-12 else 0)
        w = (g+si)/2
        rec('C2', min(x-w, S-x-w, y-w, S-y-w))
        rec('R3', min(g+si-1, math.sqrt(2)-(g+si)))
    n = len(sq)
    for i in range(n):
        for j in range(i+1, n):
            ui = u[(i, j)]
            nu = math.hypot(*ui); ui = (ui[0]/nu, ui[1]/nu)
            pi = corners(*Z[i], ); qj = corners(*Z[j])
            m = min(ui[0]*(p[0]-q[0]) + ui[1]*(p[1]-q[1]) for p in pi for q in qj)
            rec('C3', m)
            dx, dy = Z[i][0]-Z[j][0], Z[i][1]-Z[j][1]
            rec('R1', ui[0]*dx + ui[1]*dy - 1)
            rec('R2', dx*dx + dy*dy - 1)
    ok = all(v >= -1e-9 for v in worst.values())
    print(f"{name}: {'PASS' if ok else 'FAIL'}  worst residuals: " +
          ", ".join(f"{k}={v:.3e}" for k, v in sorted(worst.items())))
    return ok

allok = True
# n=2, s=2: two uprights side by side
allok &= check("n=2 s=2", 2.0,
               [(0.5, 1.0, 0), (1.5, 1.0, 0)],
               {(0, 1): (-1, 0)})
# n=3, s=2: three uprights in the 2x2 (2 bottom, 1 top)
allok &= check("n=3 s=2", 2.0,
               [(0.5, 0.5, 0), (1.5, 0.5, 0), (0.5, 1.5, 0)],
               {(0, 1): (-1, 0), (0, 2): (0, -1), (1, 2): (1, -1)})
# n=5, s=2+1/sqrt2 (Goebel): 4 corner uprights + centre square at 45 deg
S5 = 2 + 1/math.sqrt(2); c = S5/2; r2 = math.sqrt(2)/2
allok &= check("n=5 Goebel", S5,
               [(0.5, 0.5, 0), (S5-0.5, 0.5, 0), (0.5, S5-0.5, 0), (S5-0.5, S5-0.5, 0),
                (c, c, 45)],
               {(0, 1): (-1, 0), (0, 2): (0, -1), (0, 3): (-r2, -r2), (1, 2): (r2, -r2),
                (1, 3): (0, -1), (2, 3): (-1, 0),
                (0, 4): (-r2, -r2), (1, 4): (r2, -r2), (2, 4): (-r2, r2), (3, 4): (r2, r2)})
print("ALL PASS" if allok else "SOME FAIL")
