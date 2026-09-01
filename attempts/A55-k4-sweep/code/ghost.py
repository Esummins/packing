"""
A55: the TRUMP-GHOST PROFILE test (A54 S1's interior/side-zone mass fingerprint), for any node.

The node LP's optimal DUAL is a fractional packing {(cx, cy, theta; y)} of total weight tau.
Its fingerprint is the distribution of y over the nine coarse zones (substrat.zones, cw = 0.6:
corners [0.5,1.1]^2 etc., sides, interior [1.1, 2.777]^2), plus the tilted share (5 deg <= theta
mod 90 <= 85 deg) inside the interior.

A54 S1 measured the signature of Trump's own residual (trump5, provably alive):
    interior 2.97 (2.83 tilted), side_R 1.00, side_T 1.00, corners ~ 0
and found every straggler's optimum to be that same object with a different corner decoration
("Trump's ghost").  This script reproduces that measurement and scores any node against it:

    ghost_score = 1 - (L1 distance between the two zone profiles, each normalised to total 1) / 2
                  in [0, 1];  1.0 = identical fingerprint.

FLOAT diagnostic.  It decides nothing -- the arbiters remain verify_case.py (kill) and
alive.py's integral dual witness (unkillable).
"""
import argparse, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
A53 = os.path.abspath(os.path.join(BASE, "..", "A53-simple-strata"))
sys.path.insert(0, HERE)
from substrat import zones
from run_skel import S0F

ZORDER = ["interior", "side_L", "side_B", "side_R", "side_T",
          "corner_BL", "corner_BR", "corner_TR", "corner_TL"]


def load_node(name):
    for p in (os.path.join(BASE, "results", "nodes", f"{name}.json"),
              os.path.join(A53, "results", "nodes", f"{name}.json")):
        if os.path.exists(p):
            return json.load(open(p)), p
    raise SystemExit(f"no node json for {name}")


def profile(node, cw=0.6):
    Z = zones(S0F, cw)
    prof = {z: 0.0 for z in ZORDER}
    tilt = {z: 0.0 for z in ZORDER}
    out_of_zone = 0.0
    for p in node["packing"]:
        x, y, th, w = p["cx"], p["cy"], p["theta"], p["y"]
        thd = math.degrees(th) % 90.0
        hit = None
        for z in ZORDER:
            x0, x1, y0, y1 = Z[z]
            if x0 - 1e-9 <= x <= x1 + 1e-9 and y0 - 1e-9 <= y <= y1 + 1e-9:
                hit = z
                break
        if hit is None:
            out_of_zone += w
            continue
        prof[hit] += w
        if 5.0 <= thd <= 85.0:
            tilt[hit] += w
    return prof, tilt, out_of_zone


def score(pa, pb):
    """1 - L1(normalised profiles)/2 in [0,1]"""
    ta, tb = sum(pa.values()), sum(pb.values())
    if ta <= 0 or tb <= 0:
        return 0.0
    return 1.0 - sum(abs(pa[z] / ta - pb[z] / tb) for z in ZORDER) / 2.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--names", required=True, help="comma list")
    ap.add_argument("--ref", default="trump5")
    ap.add_argument("--cw", type=float, default=0.6)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    ref, refp = load_node(a.ref)
    rprof, rtilt, _ = profile(ref, a.cw)
    recs = {}
    print(f"reference {a.ref}  tau={ref['tau']:.6f} budget={ref['budget']}  "
          f"(node {os.path.relpath(refp, BASE)})")
    print(f"  {'node':10s} {'tau':>9s} {'bud':>4s} " +
          " ".join(f"{z[:6]:>6s}" for z in ZORDER) + "   int_tilt  ghost")
    def line(nm, nd, pr, tl):
        return (f"  {nm:10s} {nd['tau']:9.5f} {nd['budget']:4d} " +
                " ".join(f"{pr[z]:6.3f}" for z in ZORDER) +
                f"   {tl['interior']:6.3f}")
    print(line(a.ref, ref, rprof, rtilt) + "   1.000")
    for nm in a.names.split(","):
        nd, pth = load_node(nm)
        pr, tl, oz = profile(nd, a.cw)
        g = score(pr, rprof)
        print(line(nm, nd, pr, tl) + f"   {g:.3f}" + (f"  [off-zone {oz:.3f}]" if oz > 1e-6 else ""))
        recs[nm] = dict(tau=nd["tau"], budget=nd["budget"], eta=nd["tau"] - nd["budget"],
                        node=os.path.relpath(pth, BASE), zone_weight=pr,
                        zone_weight_tilted=tl, off_zone=oz, ghost_score=g)
    outp = a.out or os.path.join(BASE, "results", "ghost_profiles.json")
    json.dump(dict(ref=a.ref, ref_tau=ref["tau"], ref_zone_weight=rprof,
                   ref_zone_weight_tilted=rtilt, cw=a.cw, nodes=recs),
              open(outp, "w"), indent=1)
    print("->", os.path.relpath(outp, BASE))


if __name__ == "__main__":
    main()
