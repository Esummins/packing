"""A20 validation gates.

V0  rpair_orbits_fast == A19's rpair_orbits (same pair partition) at k = 148.
V1  block decomposition exact: eigs of the dense (k+1) Z == union of isotypic-block eigs.
V2  gate (A19 reproduction): block-diagonal solve on the h384/h380 saved rows reproduces
    A19's Clarabel values (hybrid 11.145789 / F0 11.144063 at 3.84; 10.503689 / 10.506152
    at 3.80) to 1e-5-ish.
V2b fdist = sqrt(2) restriction cost on the same rows (should be ~0: distant pairs never
    co-occur in a diag row).

usage: python validate_a20.py [h384|h380|both] [--skip-solve]
"""
import json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "attempts", "A19-hybrid-kernel"))
sys.path.insert(0, os.path.join(ROOT, "attempts", "A17-kernel-root"))

from features import FeatureMap
from hybrid import HybridSDP, rpair_orbits
from block_sdp import BlockHybridSDP, rpair_orbits_fast

A19RES = os.path.join(ROOT, "attempts", "A19-hybrid-kernel", "results")
REFS = {"h384": dict(s=3.84, hybrid=11.145789, F0=11.144063),
        "h380": dict(s=3.80, hybrid=10.503689, F0=10.506152)}


def load_rows(tag, hs, pair_cap=2200):
    st = np.load(os.path.join(A19RES, tag + "_state.npz"), allow_pickle=True)
    nd = hs.add_diag(st["diag_pts"])
    npr = 0
    if len(st["pair_x"]):
        PX, PY = st["pair_x"], st["pair_y"]
        if len(PX) > pair_cap:
            from oracle_pair import overlap_depth_many
            dep = overlap_depth_many(PX, PY)
            keep = np.argsort(-dep)[:pair_cap]
            PX, PY = PX[keep], PY[keep]
        npr = hs.add_pairs(PX, PY)
    return nd, npr


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "h384"
    tags = ["h384", "h380"] if which == "both" else [which]
    skip_solve = "--skip-solve" in sys.argv
    out = {}
    for tag in tags:
        ref = REFS[tag]
        st = np.load(os.path.join(A19RES, tag + "_state.npz"), allow_pickle=True)
        fm = FeatureMap(st["A"], st["w"], ref["s"])
        r_mask = st["r_mask"].astype(bool)
        r_idx = np.nonzero(r_mask)[0]

        # V0: pair-orbit partition equality
        po1, n1, op1 = rpair_orbits(fm, r_idx)
        po2, n2, op2 = rpair_orbits_fast(fm, r_idx, None)
        assert n1 == n2, (n1, n2)
        # partitions equal up to relabeling: canonical member key per orbit
        k1 = sorted(tuple(sorted(m)) for m in op1)
        k2 = sorted(tuple(sorted(m)) for m in op2)
        assert k1 == k2, "orbit partitions differ"
        print(f"[{tag}] V0 PASS: {n1} pair orbits identical (fast vs A19)")

        hs = BlockHybridSDP(fm, None, r_mask=r_mask)
        hs.build_blocks()
        err = hs.check_blocks(np.random.default_rng(0))
        print(f"[{tag}] V1 block-eig match: max err {err:.2e}")
        assert err < 1e-9
        out[tag] = dict(V0_orbits=n1, V1_err=err)
        if skip_solve:
            continue

        nd, npr = load_rows(tag, hs)
        print(f"[{tag}] rows: {nd} diag, {npr} pair; k={hs.k}, n_forb={hs.n_forb}")
        t0 = time.time()
        r1 = hs.solve()
        print(f"[{tag}] V2 block hybrid (F on): lam = {r1['lam']:.6f} "
              f"(A19 {ref['hybrid']:.6f}, diff {r1['lam']-ref['hybrid']:+.2e}) [{r1['time']:.0f}s]")
        r0 = hs.solve(allow_F=False)
        print(f"[{tag}] V2 block F=0:          lam = {r0['lam']:.6f} "
              f"(A19 {ref['F0']:.6f}, diff {r0['lam']-ref['F0']:+.2e}) [{r0['time']:.0f}s]")
        # V2b: fdist restriction on the same rows
        hs2 = BlockHybridSDP(fm, None, r_mask=r_mask, fdist=2 ** 0.5)
        hs2.build_blocks()
        load_rows(tag, hs2)
        r2 = hs2.solve()
        print(f"[{tag}] V2b fdist=sqrt2 hybrid: lam = {r2['lam']:.6f} "
              f"(n_forb {hs2.n_forb} vs {hs.n_forb}; cost {r2['lam']-r1['lam']:+.2e}) [{r2['time']:.0f}s]")
        out[tag].update(lam_hybrid=r1["lam"], lam_F0=r0["lam"], lam_fdist=r2["lam"],
                        n_forb=hs.n_forb, n_forb_fdist=hs2.n_forb,
                        t_hybrid=r1["time"], ref=ref)
    json.dump(out, open(os.path.join(HERE, "results", "validate.json"), "w"), indent=1)
    print("saved results/validate.json")


if __name__ == "__main__":
    main()
