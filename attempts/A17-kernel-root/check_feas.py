"""Deep feasibility check: can the CURRENT row set be satisfied at lam = target with a long solve?
Decides solver-suboptimality vs class-infeasibility.  usage: python check_feas.py <tag> <lam> [maxiter] [rank]"""
import sys, time, json
import numpy as np
from features import FeatureMap, load_atoms_a07_384, build_symmetry
from sdp import KernelSDP

tag = sys.argv[1]; lam = float(sys.argv[2])
maxiter = int(sys.argv[3]) if len(sys.argv) > 3 else 4000
rank = int(sys.argv[4]) if len(sys.argv) > 4 else None
A, w, s = load_atoms_a07_384()
fm = FeatureMap(A, w, s)
sym = build_symmetry(fm)
prob = KernelSDP(sym)
st = np.load(f"results/{tag}_state.npz", allow_pickle=True)
dp, px, py = st["diag_pts"], st["pair_x"], st["pair_y"]
print(f"rows: {len(dp)} diag, {len(px)} pair; lam target {lam}, maxiter {maxiter}, rank {rank or 'state'}")
t0 = time.time()
for i0 in range(0, len(dp), 4000):
    prob.add_diag_rows(fm.phi(dp[i0:i0+4000]))
for i0 in range(0, len(px), 4000):
    prob.add_pair_rows(fm.phi(px[i0:i0+4000]), fm.phi(py[i0:i0+4000]))
print(f"rows built ({time.time()-t0:.0f}s)")
if rank is None:
    Y = {n: st["Y_" + n] for n in prob.names}
else:
    M0 = None
    Y = prob.init_Y(rank=rank, M0=None, scale=0.02)
    # warm from state by padding/truncating
    for n in prob.names:
        Ys = st["Y_" + n]
        r0 = Ys.shape[0]
        if rank <= r0:
            Y[n] = Ys[:rank].copy()
        else:
            Y[n][:r0] = Ys
            Y[n][r0:] *= 1e-3
t0 = time.time()
for rounds in range(6):
    Y, viol, F, nit, gd, gp = prob.solve_feas(Y, lam, maxiter=maxiter // 6)
    print(f"  round {rounds}: gd {gd:+.3e} gp {gp:+.3e} F {F:.3e} ({nit} it, {time.time()-t0:.0f}s)", flush=True)
    if max(gd, gp) < 1e-7:
        break
K = prob.row_values(Y)
g = K - prob.rhs(lam)
isd = prob._stack()["isd"]
print(f"FINAL at lam {lam}: max diag-row viol {g[isd].max():+.4e}, max pair-row viol {g[~isd].max():+.4e}")
# binding structure
gi = np.argsort(-g)
meta_pts = np.vstack([dp, px])  # not aligned for pairs, just report diag bindings
gd_idx = np.nonzero(isd)[0]
top = gd_idx[np.argsort(-(g[gd_idx]))][:10]
cov = fm.coverage(dp)
print("top binding/violated diag rows (cx, cy, theta_deg, coverage, g):")
o = 0
for t in top:
    i = int(np.nonzero(gd_idx == t)[0][0])
    print(f"  ({dp[i,0]:.3f}, {dp[i,1]:.3f}, {np.degrees(dp[i,2]):6.2f}) cov {cov[i]:.4f} g {g[t]:+.3e}")
