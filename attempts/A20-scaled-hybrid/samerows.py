"""Same-rows F on/off comparison from a saved A20 state (the decisive number)."""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "A19-hybrid-kernel"))
sys.path.insert(0, os.path.join(HERE, "..", "A17-kernel-root"))
from features import FeatureMap
from block_sdp import BlockHybridSDP
tag, s = sys.argv[1], float(sys.argv[2])
st = np.load(os.path.join(HERE, "results", tag + "_state.npz"), allow_pickle=True)
fm = FeatureMap(st["A"], st["w"], s)
hs = BlockHybridSDP(fm, None, r_mask=st["r_mask"].astype(bool))
hs.add_diag(st["diag_pts"])
if len(st["pair_x"]):
    hs.add_pairs(st["pair_x"], st["pair_y"])
print(f"[{tag}] rows {len(hs.diag_meta)}d/{len(hs.pair_meta)}p k={hs.k} n_forb={hs.n_forb}")
r0 = hs.solve(allow_F=False)
print(f"[{tag}] F = 0 : lam = {r0['lam']:.6f} ({r0['time']:.0f}s {r0['status']})")
r1 = hs.solve()
print(f"[{tag}] F on  : lam = {r1['lam']:.6f} ({r1['time']:.0f}s {r1['status']})")
print(f"[{tag}] F buys {r0['lam'] - r1['lam']:+.6f} on identical rows")
from check_feas import verify
verify(hs, fm, r1["g_orb"], r1["f"], r1["lam"], tag + "-Fon")
json.dump(dict(lam_F0=r0["lam"], lam_hybrid=r1["lam"], nd=len(hs.diag_meta),
               npair=len(hs.pair_meta), k=int(hs.k)),
          open(os.path.join(HERE, "results", f"samerows_{tag}.json"), "w"), indent=1)
