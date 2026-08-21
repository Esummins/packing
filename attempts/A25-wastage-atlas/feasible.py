"""feasible.py -- can a pair-atlas entry actually be realised?  Grid search over
both core boxes for two interior-disjoint unit squares inside [0,s]^2.  A pair
whose answer is NO gives a vacuously-true (and useless) dead-area statement, so
those entries are flagged and excluded from the min-k analysis."""
import itertools, json, math, sys
from fractions import Fraction as F
import numpy as np
from atlas_lib import clip_box

def corners(cx, cy, th):
    c, s = math.cos(th), math.sin(th)
    return np.array([[cx + c*u - s*v, cy + s*u + c*v]
                     for (u, v) in ((-.5,-.5),(.5,-.5),(.5,.5),(-.5,.5))])

def gap(A, ca, sa, B, cb, sb):
    best = -1e18
    for (ax, ay) in ((ca,sa),(-sa,ca),(cb,sb),(-sb,cb)):
        pa = A[:,0]*ax + A[:,1]*ay; pb = B[:,0]*ax + B[:,1]*ay
        best = max(best, max(pb.min()-pa.max(), pa.min()-pb.max()))
    return best

def samples(box, s, n=4, nt=4):
    t0,t1,x0,x1,y0,y1 = box
    out = []
    for t in np.linspace(t0, t1, nt):
        th = 2*math.atan(t); w2 = (math.cos(th)+math.sin(th))/2
        lo_x, hi_x = max(x0, w2), min(x1, s-w2)
        lo_y, hi_y = max(y0, w2), min(y1, s-w2)
        if lo_x > hi_x or lo_y > hi_y: continue
        for cx in np.linspace(lo_x, hi_x, n):
            for cy in np.linspace(lo_y, hi_y, n):
                out.append((cx, cy, th))
    return out

def feasible(boxes, s, n=4, nt=4):
    A = samples(boxes[0], s, n, nt); B = samples(boxes[1], s, n, nt)
    if not A or not B: return False, None
    CA = [(corners(*p), math.cos(p[2]), math.sin(p[2])) for p in A]
    CB = [(corners(*p), math.cos(p[2]), math.sin(p[2])) for p in B]
    best = -1e18; arg = None
    for (a,(Ac,ca,sa)) in zip(A,CA):
        for (b,(Bc,cb,sb)) in zip(B,CB):
            g = gap(Ac,ca,sa,Bc,cb,sb)
            if g > best: best, arg = g, (a,b)
            if g >= 0: return True, (a,b)
    return False, (best, arg)

if __name__ == '__main__':
    S = F(sys.argv[2]) if len(sys.argv) > 2 else F(96,25)
    d = json.load(open(sys.argv[1]))
    nf = 0; out = {}
    for c in d['cells']:
        bs = []
        for sub in (c['A'], c['B']):
            t0,t1 = F(sub['t'][0]), F(sub['t'][1])
            cl = clip_box(t0,t1,F(sub['cx'][0]),F(sub['cx'][1]),F(sub['cy'][0]),F(sub['cy'][1]),S)
            bs.append((float(t0),float(t1))+tuple(float(v) for v in cl))
        ok, _ = feasible(bs, float(S), 5, 5)
        out[c['id']] = ok
        c['realisable'] = ok
        if not ok: nf += 1
    json.dump(d, open(sys.argv[1],'w'), indent=1)
    feas = [c for c in d['cells'] if c['realisable']]
    print(f"pair atlas: {len(d['cells'])} entries, {nf} NOT realisable, "
          f"{len(feas)} realisable; max realisable dead = "
          f"{max((c['dead_lb_float'] for c in feas), default=0):.4f}")
    for c in feas[:5]:
        print(f"   {c['dead_lb_float']:.4f} {c['id']}")
