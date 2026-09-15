import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import geom217 as G
rng = np.random.default_rng(0)
z = np.concatenate([rng.uniform(0.7, 3.3, 33), [4.0]]); z[2::3] = rng.uniform(0, 1.5, 11)
g, J = G.wall_rows(z)
sel, gaps = G.best_selection(z)
p, JP = G.pair_rows(z, sel)
eps = 1e-6
for name, f, Ja in (('wall', lambda x: G.wall_rows(x)[0], J), ('pair', lambda x: G.pair_rows(x, sel)[0], JP)):
    Jn = np.zeros((len(f(z)), 34))
    for k in range(34):
        d = np.zeros(34); d[k] = eps
        Jn[:, k] = (f(z + d) - f(z - d)) / (2 * eps)
    print(name, 'max jac err', np.abs(Jn - Ja).max())
q = G.corners(z); i, k = 3, 2
r = q[i, k] - z[3*i:3*i+2]
print('torque x=0 row', J.reshape(11, 4, 4, 34)[i, k, 0, 3*i+2], ' r x n =', r[0]*0 - r[1]*1)
# Trump: settled corners + meeters
import json
T = json.load(open(os.path.join(os.path.dirname(__file__), '../../A03-upper-reconstruct/trump11_float.json')))
zt = np.concatenate([np.array(T['X']).reshape(-1), [T['s']]])
print('trump gaps min', min(G.pair_gaps(zt).values()), 'wall min', G.wall_rows(zt)[0].min())
for c in G.CORNER_NAMES:
    print(c, 'settled', G.settled(zt, c), 'meeters', G.corner_meeters(zt, c))
