"""
A13 certify.py: rigorous certificate for a DEAD node = A07's separation loop:
  round: build rational certificate (weights x scale) -> verify_case.py (exact) -> if FAIL, feed the witness placements
  (+ neighbours) back as extra LP rows, re-solve the node LP (rows only, warm) -> repeat.
Usage: python certify.py results/<tag>/node_<id>.json --s_rat 96/25 [--scale 1.03] [--rounds 4] [--jobs 4] [--depth 56]
Writes certs_wip/<tag>_node_<id>.json (+ .report.json) and prints PASS/FAIL.
"""
import argparse, json, os, subprocess, sys, time, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import caselp
from caselp import Hyp, solve_node, warm_from_result, make_certificate

HERE = os.path.dirname(os.path.abspath(__file__))


def run_verifier(cert_path, jobs, depth, max_w=64):
    cmd = [sys.executable, os.path.join(HERE, "verify_case.py"), cert_path, "--jobs", str(jobs), "--depth", str(depth),
           "--max-witnesses", str(max_w), "--report", "--quiet"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    out = p.stdout + p.stderr
    return p.returncode, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("node_json")
    ap.add_argument("--s_rat", required=True)
    ap.add_argument("--scale", type=float, default=1.03)
    ap.add_argument("--rounds", type=int, default=4)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--time_limit", type=float, default=300)
    ap.add_argument("--out", default=None)
    ap.add_argument("--eps_geo", type=float, default=None, help="re-solve the node LP with this row shrink margin first (robustness)")
    a = ap.parse_args()
    if a.eps_geo is not None:
        import lpbox
        lpbox.EPS_GEO = a.eps_geo
    res = json.load(open(a.node_json))
    tag = os.path.basename(os.path.dirname(a.node_json))
    nid = os.path.basename(a.node_json).replace(".json", "")
    out = a.out or os.path.join(HERE, "certs_wip", f"{tag}_{nid}.json")
    hyp = Hyp.from_json(res["hyp"])
    s = res["s"]; budget = res["budget"]
    sym = "D4" if hyp.is_symmetric_D4(s) else "C1"
    extra = []
    log = []
    if a.eps_geo is not None:
        print(f"re-solving node LP with EPS_GEO={a.eps_geo} (rows only, fine oracle) ...", flush=True)
        warm = warm_from_result(res)
        res = solve_node(s, hyp, budget, sym_kind=sym, warm=warm, time_limit=a.time_limit, out=None, log=lambda *x: print(*x, flush=True),
                         col_stop_iter=60, col_stop_cov=1.01, max_cols_add=400, fine_slack=99.0)
        print(f"   tau={res['tau']:.5f} conv={res['converged']} minmass={res['minmass']:.4f} maxcov={res['maxcov']:.4f}", flush=True)
        json.dump(res, open(out.replace(".json", ".resolve.json"), "w"))
    for rd in range(a.rounds + 1):
        cert = make_certificate(res, a.s_rat, scale=a.scale)
        tot = float(__import__("fractions").Fraction(cert["total"]))
        json.dump(cert, open(out, "w"), indent=0)
        print(f"[round {rd}] tau={res['tau']:.5f} conv={res['converged']} cert total={tot:.5f} budget={budget} atoms={len(cert['atoms'])}", flush=True)
        if tot >= budget:
            print("certificate total >= budget: cannot certify (LP tau too close to the budget for the margin)"); return 3
        rc, txt = run_verifier(out, a.jobs, a.depth)
        tail = [l for l in txt.splitlines() if l.startswith(("PASS", "FAIL", "boxes", "  worst", "MALFORMED"))]
        print("\n".join("    " + l for l in tail), flush=True)
        log.append(dict(round=rd, tau=res["tau"], total=tot, rc=rc, verifier=tail))
        if rc == 0:
            json.dump(dict(node=a.node_json, cert=out, rounds=log, result="PASS"), open(out.replace(".json", ".certify.json"), "w"), indent=1)
            print(f"CERTIFIED: {out}")
            return 0
        if rd == a.rounds:
            break
        wf = out.replace(".json", ".witnesses.json")
        if not os.path.exists(wf):
            print("no witness file; abort"); return 2
        W = json.load(open(wf))["witnesses"]
        new = []
        for w in W:
            p = w.get("placement")
            if not p:
                continue
            th = math.radians(p["theta_deg"])
            new.append((p["cx_float"], p["cy_float"], th))
            for d in (0.002, 0.005):
                for dx, dy in ((d, 0), (-d, 0), (0, d), (0, -d), (d, d), (-d, -d), (d, -d), (-d, d)):
                    new.append((p["cx_float"] + dx, p["cy_float"] + dy, th))
                for dth in (d, -d):
                    new.append((p["cx_float"], p["cy_float"], th + dth))
        extra += new
        print(f"    feeding back {len(new)} witness rows (total extra {len(extra)}), re-solving (rows only)", flush=True)
        warm = warm_from_result(res)
        res = solve_node(s, hyp, budget, sym_kind=sym, warm=warm, time_limit=a.time_limit, out=None, log=lambda *x: None,
                         extra_rows=extra, neigh_rows=0, col_stop_iter=0, fine_slack=99.0)
    json.dump(dict(node=a.node_json, cert=out, rounds=log, result="FAIL"), open(out.replace(".json", ".certify.json"), "w"), indent=1)
    print("NOT certified")
    return 1


if __name__ == "__main__":
    sys.exit(main())
