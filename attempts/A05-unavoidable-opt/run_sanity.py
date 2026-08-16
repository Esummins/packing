"""Sanity checks of the evaluator / optimiser: n=5 (4 points) and n=10 (9 points)."""
import time, sys
import numpy as np
sys.path.insert(0, __file__.rsplit("\\", 1)[0])
from unavoid import *

# --- n=5: known set (1,1),(1,s-1),(s-1,1),(s-1,s-1) at s = 2+1/sqrt2
s5 = 2 + 1 / np.sqrt(2)
P5 = np.array([[1, 1], [1, s5 - 1], [s5 - 1, 1], [s5 - 1, s5 - 1]], float)
t0 = time.time()
wc = worst_configs(P5, s5, nth=180, nc=200, K=10)
print("n=5 Goebel set at s=2+1/sqrt2: max d = %.3e (time %.2fs)" % (wc[0][3], time.time() - t0))
print("  worst config:", wc[0])
for ds in [1e-3, 1e-2]:
    wc = worst_configs(P5, s5 + ds, nth=90, nc=100, K=10)
    print("  at s+%g: max d = %.3e" % (ds, wc[0][3]))
    wc = worst_configs(P5, s5 - ds, nth=90, nc=100, K=10)
    print("  at s-%g: max d = %.3e" % (ds, wc[0][3]))

# blind optimisation for 4 points, asymmetric parametrisation, several starts
rng = np.random.default_rng(1)
best = None
t0 = time.time()
for trial in range(6):
    s_init = 2.5
    param = Param("none", ["g"] * 4, s_init)
    z0 = param.random_z(rng)
    s_best, z_best, g_best, p_best = find_max_s0("none", ["g"] * 4, z0, s_init, m_target=0.0, tol_s=1e-4,
                                                slp_kw=dict(nth=48, nc=60, K=20, iters=150))
    print(f"  trial {trial}: s0={s_best:.5f}  P=" + np.array2string(p_best.P(z_best), precision=3))
    if best is None or s_best > best[0]:
        best = (s_best, p_best.P(z_best))
print("n=5 blind best s0 = %.5f  (target %.5f)  time %.1fs" % (best[0], s5, time.time() - t0))
print(best[1])

# --- n=10: 9 points.  Try 3x3 grid at s=3+1/sqrt2 and blind optimisation
s10 = 3 + 1 / np.sqrt(2)
g3 = np.array([[1, s10 / 2, s10 - 1]])
P9 = np.array([[x, y] for x in g3[0] for y in g3[0]])
wc = worst_configs(P9, s10, nth=90, nc=100, K=10)
print("n=10 3x3 grid at s=3+1/sqrt2: max d = %.4f worst=%s" % (wc[0][3], wc[0]))
best = None
t0 = time.time()
for grp, spec in [("D4", ["g", "c"]), ("D4", ["x", "d", "c"]), ("axes", ["g", "g", "c"]), ("axes", ["g", "v", "v", "c"]),
                  ("axes", ["g", "v", "h", "c"]), ("none", ["g"] * 9), ("none", ["g"] * 9), ("none", ["g"] * 9)]:
    s_init = 3.4
    param = Param(grp, spec, s_init)
    z0 = param.random_z(rng)
    s_best, z_best, g_best, p_best = find_max_s0(grp, spec, z0, s_init, m_target=0.0, tol_s=1e-4,
                                                slp_kw=dict(nth=48, nc=60, K=30, iters=200))
    print(f"  {grp} {spec}: s0={s_best:.5f}")
    if best is None or s_best > best[0]:
        best = (s_best, p_best.P(z_best), grp, spec)
print("n=10 (9 points) best s0 = %.5f (Stromquist s(10)=%.5f) time %.1fs" % (best[0], s10, time.time() - t0))
print(best[2], best[3]); print(np.array2string(best[1], precision=4))
np.save(__file__.rsplit("\\", 1)[0] + "/best9.npy", best[1])
