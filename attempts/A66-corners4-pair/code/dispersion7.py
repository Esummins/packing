"""A66 T1 probe: max-min margin for 7 points in the corners4 centre region C(s).
Constraints (all must be >= 0 at a feasible 7-point config):
  pairwise: |pi-pj| - 1 ;  pin: 2*dist(p, pin)-1 ;  walls: hard box [1/2, s-1/2]^2.
Maximise the min margin by multistart + coordinate polish (numpy, no scipy)."""
import numpy as np, sys, json
rng = np.random.default_rng(7)

def margins(P, s):
    n = len(P)
    D = np.sqrt(((P[:,None,:]-P[None,:,:])**2).sum(-1))
    pw = (D + np.eye(n)*9)[np.triu_indices(n,1)] - 1.0
    pins = [(0,1,0,1),(s-1,s,0,1),(0,1,s-1,s),(s-1,s,s-1,s)]
    pm = []
    for (x0,x1,y0,y1) in pins:
        dx = np.maximum(np.maximum(x0-P[:,0],0), P[:,0]-x1)
        dy = np.maximum(np.maximum(y0-P[:,1],0), P[:,1]-y1)
        pm.append(2*np.sqrt(dx*dx+dy*dy)-1.0)
    return np.concatenate([pw]+pm)

def polish(P, s, iters=4000, step0=0.08):
    lo, hi = 0.5, s-0.5
    best = margins(P,s).min(); bestP = P.copy(); step = step0
    for it in range(iters):
        Q = np.clip(P + rng.normal(0, step, P.shape), lo, hi)
        m = margins(Q,s).min()
        if m > best: best, bestP, P = m, Q.copy(), Q
        else:
            # single-point moves
            i = rng.integers(0,len(P))
            Q = P.copy(); Q[i] = np.clip(Q[i]+rng.normal(0,step,2), lo, hi)
            m = margins(Q,s).min()
            if m > best: best, bestP, P = m, Q.copy(), Q
        step = step0 * (1 - it/iters) + 1e-3
    return best, bestP

out = {}
for s in [3.82, 3.83, 3.84, 3.85, 3.86, 3.8660254, 3.87, 3.877084]:
    best = -9; bP = None
    for trial in range(60):
        P = rng.uniform(0.5, s-0.5, (7,2))
        b, Q = polish(P, s, iters=1500)
        if b > best: best, bP = b, Q
    # extra polish on the champion
    for _ in range(3):
        b, Q = polish(bP, s, iters=4000, step0=0.02)
        if b > best: best, bP = b, Q
    out[str(s)] = dict(maxmin=float(best), pts=[[float(x),float(y)] for x,y in bP])
    print("s=%.7f  max-min margin = %+.5f" % (s, best), flush=True)
json.dump(out, open("C:/Users/esumm/code/packing/attempts/A66-corners4-pair/results/dispersion7.json","w"), indent=1)
