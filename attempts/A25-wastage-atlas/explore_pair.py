"""explore_pair.py -- which atlas-grid pair geometries are worth sweeping?"""
import time
from fractions import Fraction as F
from atlas_lib import pair_cell, single_cell, tanhalf

S = F(96, 25); h = F(3, 20)
tb = (tanhalf(30, False), tanhalf(33, True))

def box(i, j):
    return ((i*h, (i+1)*h), (j*h, (j+1)*h))

CASES = [ (8,8,8,0), (8,8,7,3), (8,11,8,0), (11,11,-8,0), (11,11,-7,3),
          (11,8,0,8), (5,11,8,0), (8,5,0,8), (11,11,-8,1), (12,12,-8,0) ]
sing = {}
for (ia,ja,di,dj) in CASES:
    for (i,j) in ((ia,ja),(ia+di,ja+dj)):
        if (i,j) in sing: continue
        xa, ya = box(i,j)
        r = single_cell(S, tb, xa, ya)
        sing[(i,j)] = 0.0 if r is None else float(r['area'])
for (ia,ja,di,dj) in CASES:
    xa, ya = box(ia,ja); xb, yb = box(ia+di, ja+dj)
    t0=time.time(); r = pair_cell(S, tb, xa, ya, tb, xb, yb, dict(work_budget=2500))
    sm = sing[(ia,ja)] + sing[(ia+di,ja+dj)]
    if r is None: print(f"A({ia},{ja})+d({di},{dj}) INADMISSIBLE"); continue
    if r.get('infeasible'): print(f"A({ia},{ja})+d({di},{dj}) INFEASIBLE"); continue
    print(f"A({ia},{ja}) d({di},{dj})  pair={float(r['area']):.4f}  "
          f"sing={sing[(ia,ja)]:.3f}+{sing[(ia+di,ja+dj)]:.3f}={sm:.3f}  "
          f"gain={float(r['area'])-sm:+.3f}  tops={r['n_tops']} {time.time()-t0:.0f}s")
