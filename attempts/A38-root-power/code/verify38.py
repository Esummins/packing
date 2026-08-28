#!/usr/bin/env python3
"""A38 task 5: a-posteriori verification of the level-1 kills (lab standard).

(a) EVERY dead(T1) node: re-check the final LP feasibility claim from the STORED solution --
    last iteration added_rows == 0, minmass >= 1, and the exact rational certificate total
    (make_certificate, Fraction arithmetic) < budget.  Cheap, no verifier.
(b) A random sample of --sample dead nodes (+ the root) gets the FULL exact verify_case
    certification through certify.py (re-solve at eps_geo, witness-feedback loop).
    Certificates land in results/certs_l1_sample/.

    python verify38.py --sample 8 --seed 38 --jobs 2 --par 3
"""
from __future__ import annotations

import argparse, json, os, random, subprocess, sys, time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RES = os.path.join(HERE, "..", "results")
NODEDIR = os.path.join(RES, "l1_nodes")
CERTDIR = os.path.join(RES, "certs_l1_sample")
S_RAT = "969271/250000"


def cheap_recheck(node_json, budget, scale=1.03):
    """(a): feasibility of the stored solution + exact rational total < budget."""
    import caselp
    res = json.load(open(node_json))
    ht = (res.get("hist_tail") or [{}])[-1]
    added = ht.get("added_rows")
    minmass = res.get("minmass")
    ok_feas = (added == 0) and (minmass is not None and minmass >= 1 - 1e-6)
    out = dict(node=os.path.basename(node_json), tau=res["tau"], minmass=minmass,
               last_added_rows=added, converged=res.get("converged"), feasible=bool(ok_feas))
    best = None
    for sc in (scale, 1.02, 1.01, 1.005):
        cert = caselp.make_certificate(res, S_RAT, scale=sc)
        tot = F(cert["total"])
        if best is None or tot < best[1]:
            best = (sc, tot)
        if tot < budget:
            best = (sc, tot)
            break
    out.update(cert_scale=best[0], cert_total=str(best[1]), cert_total_float=float(best[1]),
               budget=budget, exact_total_lt_budget=bool(best[1] < budget))
    out["PASS"] = bool(out["feasible"] and out["exact_total_lt_budget"])
    return out


def run_certify(node_json, out_cert, s_rat, budget, eps_geo, jobs, depth, rounds, tl):
    cmd = [sys.executable, os.path.join(HERE, "certify.py"), node_json, "--s_rat", s_rat,
           "--scale", "0", "--rounds", str(rounds), "--jobs", str(jobs), "--depth", str(depth),
           "--time_limit", str(tl), "--eps_geo", str(eps_geo), "--out", out_cert,
           "--max_cols", "600", "--resolve_time", str(tl)]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True)
    txt = p.stdout + p.stderr
    with open(out_cert.replace(".json", ".certify.log"), "w") as f:
        f.write(txt)
    return dict(node=node_json, cert=out_cert, rc=p.returncode,
                result=("PASS" if p.returncode == 0 else "FAIL"), seconds=time.time() - t0,
                tail=[l for l in txt.splitlines() if l.startswith(("PASS", "FAIL", "CERTIFIED",
                                                                  "NOT certified", "[round",
                                                                  "certificate total"))][-8:])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=8)
    ap.add_argument("--seed", type=int, default=38)
    ap.add_argument("--budget", type=int, default=10)
    ap.add_argument("--eps_geo", type=float, default=0.003)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--par", type=int, default=3, help="concurrent certify.py processes")
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--time_limit", type=float, default=300)
    ap.add_argument("--skip_root", action="store_true")
    a = ap.parse_args()
    os.makedirs(CERTDIR, exist_ok=True)
    mat = json.load(open(os.path.join(RES, "l1_a38.json")))["matrix"]
    dead = [r["idx"] for r in mat if r["status"] == "dead(T1)"]
    print("dead(T1) nodes: %d" % len(dead), flush=True)

    # ---------------------------------------------------------------- (a) cheap recheck of ALL
    rech, bad = [], []
    for idx in dead:
        nj = os.path.join(NODEDIR, "node_%03d.json" % idx)
        if not os.path.exists(nj):
            rech.append(dict(idx=idx, PASS=False, error="node json missing")); bad.append(idx); continue
        try:
            d = cheap_recheck(nj, a.budget)
        except Exception as e:
            d = dict(PASS=False, error=repr(e)[:300])
        d["idx"] = idx
        rech.append(d)
        if not d.get("PASS"):
            bad.append(idx)
    n_pass = sum(1 for d in rech if d.get("PASS"))
    print("(a) stored-solution recheck: %d/%d PASS  (fail: %s)" % (n_pass, len(rech), bad), flush=True)

    # --------------------------------------------------------- (b) full exact certification
    rng = random.Random(a.seed)
    samp = sorted(rng.sample(dead, min(a.sample, len(dead)))) if dead else []
    jobs = [(os.path.join(NODEDIR, "node_%03d.json" % i),
             os.path.join(CERTDIR, "node_%03d.json" % i)) for i in samp]
    if not a.skip_root:
        rn = os.path.join(RES, "root_node_cw06.json")
        if os.path.exists(rn):
            jobs.append((rn, os.path.join(CERTDIR, "root_s0.json")))
    print("(b) full verify_case certification on %d cases: %s" % (len(jobs), samp), flush=True)
    import concurrent.futures as cf
    full = []
    with cf.ThreadPoolExecutor(max_workers=a.par) as ex:
        futs = [ex.submit(run_certify, nj, oc, S_RAT,
                          (11 if "root" in oc else a.budget), a.eps_geo, a.jobs, a.depth,
                          a.rounds, a.time_limit) for nj, oc in jobs]
        for fu in cf.as_completed(futs):
            r = fu.result()
            full.append(r)
            print("   %-28s %-4s %5.0fs  %s" % (os.path.basename(r["cert"]), r["result"],
                                                r["seconds"], r["tail"][-1] if r["tail"] else ""),
                  flush=True)
    doc = dict(when=time.strftime("%Y-%m-%dT%H:%M:%S"), budget=a.budget, s=S_RAT,
               eps_geo_certify=a.eps_geo, seed=a.seed,
               stored_solution_recheck=dict(n=len(rech), n_pass=n_pass,
                                            n_fail=len(rech) - n_pass, failures=bad,
                                            records=rech),
               full_certification=dict(n=len(full), sample=samp,
                                       n_pass=sum(1 for r in full if r["result"] == "PASS"),
                                       n_fail=sum(1 for r in full if r["result"] != "PASS"),
                                       records=full),
               label_rule="sampled+PASS = kill(certified); other dead(T1) = kill(LP)")
    json.dump(doc, open(os.path.join(RES, "verification_l1.json"), "w"), indent=1)
    # merge into l1_a38.json
    p = os.path.join(RES, "l1_a38.json")
    d = json.load(open(p))
    d["verification"] = {k: v for k, v in doc.items() if k != "stored_solution_recheck"}
    d["verification"]["stored_solution_recheck"] = {
        k: v for k, v in doc["stored_solution_recheck"].items() if k != "records"}
    certified = {r["cert"]: r["result"] for r in full}
    for r in d["matrix"]:
        if r["status"] == "dead(T1)":
            c = os.path.join(CERTDIR, "node_%03d.json" % r["idx"])
            r["kill_label"] = ("kill(certified)" if certified.get(c) == "PASS"
                               else ("kill(FAILED-CERT)" if c in certified else "kill(LP)"))
    json.dump(d, open(p, "w"), indent=1)
    print("wrote results/verification_l1.json and merged into l1_a38.json", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
