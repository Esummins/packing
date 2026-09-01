"""
A57 EPS_CORE ladder — the repair for a child that converges to tau = budget EXACTLY.

Why it is sound.  caselp drops a row only if the placement penetrates a core by more than
`EPS_CORE = 2e-3` on every separating axis; `verify_case.py`, the arbiter, exempts a box only if
it **provably** meets a core (the exact predicate, no epsilon).  The LP is therefore strictly
more conservative than the verifier: it insists on covering a 2e-3 shell around every pinned
square that the verifier would exempt.  Measured on `k5_16_interior_Y0017` (a pinguard-ok child
that converged at tau = 5.000000000000014 = budget), three of the five dual rows of weight 1
penetrate a pin core by 2.6e-4 … 2.0e-3 — i.e. the whole knife edge is that shell.

Shrinking EPS_CORE can only LOWER tau (more rows are dropped), and it can never make a kill
unsound: the certificate is still handed to `verify_case.py` unchanged, and if the shell was
actually needed the verification simply FAILS.  So the ladder is: re-solve at successively
smaller EPS_CORE until tau < budget with margin, then certify; the first PASS wins.

Usage:  python code/epsladder.py --node results/tree/<key>/<id>.json --eps 2e-3,5e-4,2e-4,5e-5
"""
import argparse, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import caselp
from caselp import Hyp, solve_node, warm_from_result
from run_skel import S0F

S_RAT = "969271/250000"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--node", required=True, help="a child node json written by tree57.py")
    ap.add_argument("--eps", default="2e-3,5e-4,2e-4,5e-5,1e-5")
    ap.add_argument("--tl", type=float, default=300)
    ap.add_argument("--cert_time", type=float, default=300)
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--scale_cap", type=float, default=1.40)
    ap.add_argument("--outdir", default=None)
    a = ap.parse_args()

    res0 = json.load(open(a.node))
    nid = os.path.basename(a.node)[:-5]
    hyp = Hyp.from_json(res0["hyp"])
    budget = res0["budget"]
    warm = dict(atoms=warm_from_result(res0)["atoms"], rows=[])
    outdir = a.outdir or os.path.join(BASE, "results", "epsladder")
    certdir = os.path.join(BASE, "certs", "epsladder")
    os.makedirs(outdir, exist_ok=True); os.makedirs(certdir, exist_ok=True)
    recs = []
    for e in [float(x) for x in a.eps.split(",")]:
        caselp.EPS_CORE = e
        t0 = time.time()
        res = solve_node(S0F, hyp, budget, sym_kind="C1", warm=warm, time_limit=a.tl,
                         max_iter=900, out=None, log=lambda *x: print(*x, flush=True),
                         prune=0, prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002,
                         max_cols_add=400, max_rows_add=2000, fine_slack=0.05, alternate=True)
        res["eps_core"] = e
        npth = os.path.join(outdir, f"{nid}_eps{e:g}.json")
        json.dump(res, open(npth, "w"))
        r = dict(node=nid, eps_core=e, budget=budget, tau=res["tau"], eta=res["tau"] - budget,
                 conv=res["converged"], minmass=res["minmass"], maxcov=res["maxcov"],
                 lp_s=round(time.time() - t0, 1))
        if res["tau"] < budget:
            cert = os.path.join(certdir, f"{nid}_eps{e:g}.json")
            cmd = [sys.executable, os.path.join(HERE, "certify.py"), npth, "--s_rat", S_RAT,
                   "--rounds", str(a.rounds), "--jobs", str(a.jobs), "--depth", str(a.depth),
                   "--time_limit", str(a.cert_time), "--out", cert, "--scale", "0",
                   "--scale_cap", f"{a.scale_cap:.5f}", "--max_w", "64", "--loop_cols"]
            t1 = time.time()
            p = subprocess.run(cmd, capture_output=True, text=True)
            r["cert"] = "PASS" if p.returncode == 0 else f"FAIL(rc={p.returncode})"
            r["cert_s"] = round(time.time() - t1, 1)
            r["tail"] = [l.strip() for l in p.stdout.splitlines()
                         if l.strip().startswith(("worst", "[round", "PASS", "FAIL"))][-4:]
            if p.returncode == 0:
                open(cert + ".PASS", "w").write("ok")
        else:
            r["cert"] = "not attempted (tau >= budget)"
        recs.append(r)
        print(json.dumps(r), flush=True)
        json.dump(recs, open(os.path.join(BASE, "results", f"epsladder_{nid}.json"), "w"), indent=1)
        if r.get("cert") == "PASS":
            print(f"LADDER WON at EPS_CORE={e:g}", flush=True)
            break


if __name__ == "__main__":
    main()
