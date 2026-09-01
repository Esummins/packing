"""A57: how small can the branch zone Z be and still have a KILLABLE NO-child?

The tree cost is |cover(Z x [0,90])|, so the cheapest sound branch uses the SMALLEST zone whose
NO-child ("no square centre in Z") still carries an exact certificate.  The NO-child LP is cheap
(the NO-family deletes rows, so tau drops), so this sweep is minutes, not hours.
Every candidate that clears tau < budget is certified for real by certify.py -- tau is not the
arbiter (A54 S0).
"""
import argparse, json, math, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
A53 = os.path.abspath(os.path.join(BASE, "..", "A53-simple-strata"))
sys.path.insert(0, HERE)
from caselp import Box, NoFam, Hyp, solve_node
from run_skel import S0F
from warm57 import merged_warm

S_RAT = "969271/250000"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--halfs", default="0.8385,0.6,0.45,0.35,0.25,0.175,0.125")
    ap.add_argument("--tl", type=float, default=240)
    ap.add_argument("--cert_time", type=float, default=240)
    ap.add_argument("--certify", action="store_true")
    ap.add_argument("--tag", default="zs")
    a = ap.parse_args()

    slots = [tuple(p) for p in json.load(open(os.path.join(A53, "results", "name_to_slots.json")))[a.name]]
    pins = [Box(x, x, y, y, 0.0, 0.0) for (x, y) in slots]
    budget = 11 - len(slots)
    c = S0F / 2.0
    W, _ = merged_warm(a.name)
    warm = dict(atoms=W["atoms"], rows=[])
    outdir = os.path.join(BASE, "results", "zoneshrink")
    os.makedirs(outdir, exist_ok=True)
    os.makedirs(os.path.join(BASE, "certs", "zoneshrink"), exist_ok=True)
    recs = []
    for h in [float(x) for x in a.halfs.split(",")]:
        rect = (c - h, c + h, c - h, c + h)
        hyp = Hyp(pins, [NoFam(rect[0], rect[1], rect[2], rect[3], [(0.0, 90.0)])])
        nid = f"{a.name}_NOZ_{h:.4f}"
        npth = os.path.join(outdir, nid + ".json")
        t0 = time.time()
        if os.path.exists(npth):
            res = json.load(open(npth))
        else:
            res = solve_node(S0F, hyp, budget, sym_kind="C1", warm=warm, time_limit=a.tl,
                             max_iter=900, out=None, log=lambda *x: print(*x, flush=True),
                             prune=0, prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002,
                             max_cols_add=400, max_rows_add=2000, fine_slack=0.05, alternate=True)
            json.dump(res, open(npth, "w"))
        r = dict(name=a.name, half=h, rect=rect, budget=budget, tau=res["tau"],
                 eta=res["tau"] - budget, conv=res["converged"], minmass=res["minmass"],
                 lp_s=round(time.time() - t0, 1),
                 cover_children=int(math.ceil(2 * h / 0.15)) ** 2 * 8)
        if a.certify and res["tau"] < budget:
            cert = os.path.join(BASE, "certs", "zoneshrink", nid + ".json")
            cmd = [sys.executable, os.path.join(HERE, "certify.py"), npth, "--s_rat", S_RAT,
                   "--rounds", "2", "--jobs", "2", "--depth", "56", "--time_limit", str(a.cert_time),
                   "--out", cert, "--scale", "0", "--scale_cap", "1.40", "--max_w", "64", "--loop_cols"]
            t1 = time.time()
            p = subprocess.run(cmd, capture_output=True, text=True)
            r["cert"] = "PASS" if p.returncode == 0 else f"FAIL(rc={p.returncode})"
            r["cert_s"] = round(time.time() - t1, 1)
            if p.returncode == 0:
                open(cert + ".PASS", "w").write("ok")
            else:
                r["tail"] = [l for l in p.stdout.splitlines() if l.startswith(("  worst", "[round"))][-3:]
        recs.append(r)
        print(json.dumps(r), flush=True)
        json.dump(recs, open(os.path.join(BASE, "results", f"zoneshrink_{a.name}_{a.tag}.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
