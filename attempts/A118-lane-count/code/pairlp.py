"""A118 T4 stage B: the node LP on surviving PAIR-BOXES, under the PI's two-stage protocol.

For each sampled surviving pair-box (B_a, B_b) of a (node, cell): the child hypothesis is the
node's own boxes plus B_a and B_b at budget - 2.  Stage 1 = 240 s; a converged eta <= -1e-3 goes
straight to the frozen verify_case.py; the knife edge (eta in (-1e-3, +0.05)) is escalated to
900 s.  Read-only on every campaign; every certificate is written under A118/certs.

Trump canary: the pair-box of trump5's TL(0,0) that CONTAINS Trump's own 2-crowd (sq6, sq4) must
NOT be certified dead.
"""
import argparse
import json
import math
import os
import subprocess
import sys
import time
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blas1  # noqa: F401
import numpy as np

import lanelib as L
import corpus as CP
import lane as LN
import caselp
from caselp import Box, Hyp, solve_node, make_certificate

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
S0 = CP.S0
S_RAT = Fr(969271, 250000)
PIN_HW = CP.PIN_DELTA / math.sqrt(2.0)


def hyp_for(rec, extra):
    """A57's own hypothesis (delta = 1e-2 slack pin boxes at s0, plus the node's conditioned
    boxes) with two extra core boxes appended."""
    boxes = []
    if rec["cls"] != "k0_00":
        hw = 0.0 if rec["src"] == "A60" else PIN_HW
        for (px, py) in CP.CLASSES[rec["cls"]]["pins"]:
            boxes.append(Box(px - hw, px + hw, py - hw, py + hw, 0.0, 0.0))
    for bd in rec["cond"]:
        boxes.append(Box(bd["x0"], bd["x1"], bd["y0"], bd["y1"], bd["th0"], bd["th1"]))
    for b in extra:
        boxes.append(Box(b.x0, b.x1, b.y0, b.y1, b.th0, b.th1))
    return Hyp(boxes, [])


def certify(res, tag):
    outdir = os.path.join(BASE, "certs")
    os.makedirs(outdir, exist_ok=True)
    cert = make_certificate(res, S_RAT)
    p = os.path.join(outdir, tag + ".json")
    json.dump(cert, open(p, "w"))
    rep = p.replace(".json", ".report.json")
    t0 = time.time()
    r = subprocess.run([sys.executable, os.path.join(HERE, "verify_case.py"), p,
                        "--depth", "44", "--jobs", "1", "--report", rep,
                        "--max-witnesses", "8", "--quiet"],
                       capture_output=True, text=True)
    ok = (r.returncode == 0)
    return dict(cert=os.path.relpath(p, BASE), rc=r.returncode, PASS=ok,
                wall_s=round(time.time() - t0, 1),
                tail=(r.stdout or r.stderr or "")[-400:])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--census", default=os.path.join(BASE, "results", "pairbox_lp.json"))
    ap.add_argument("--out", default=os.path.join(BASE, "results", "pairlp.jsonl"))
    ap.add_argument("--n", type=int, default=24)
    ap.add_argument("--time_limit", type=int, default=240)
    ap.add_argument("--escalate", type=int, default=900)
    ap.add_argument("--seed", type=int, default=118)
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--canary", type=int, default=1)
    a = ap.parse_args()

    rows = json.load(open(a.census))["rows"]
    recs = {r["nid"]: r for r in CP.load_nodes()}
    rng = np.random.default_rng(a.seed)

    done = set()
    if os.path.exists(a.out):
        for ln in open(a.out):
            try:
                done.add(json.loads(ln)["tag"])
            except Exception:
                pass

    # stratified sample of surviving pair-boxes, plus the Trump canary pair-box
    jobs = []
    for row in rows:
        if not row["pairs"]:
            continue
        k = max(1, min(3, len(row["pairs"])))
        idx = rng.choice(len(row["pairs"]), size=k, replace=False)
        for t in idx:
            jobs.append((row, tuple(row["pairs"][int(t)]), "sample"))
    rng.shuffle(jobs)
    jobs = jobs[:a.n]
    ksh, nsh = (int(x) for x in a.shard.split("/"))
    if nsh > 1:
        jobs = [j for idx, j in enumerate(jobs) if idx % nsh == ksh]

    # the canary: trump5 TL(0,0), the pair-box pair whose boxes contain Trump's sq6 and sq4
    TR = json.load(open(os.path.join(CP.ROOT, "attempts", "A03-upper-reconstruct",
                                     "trump11_float.json")))
    for row in (rows if a.canary else []):
        if row["cls"] == "trump5" and row["cell"] == "TL(0,0)" and row["node"].endswith("ROOT"):
            B = [L.Bx(**b) for b in row["boxes_json"]]

            def find(k):
                x, y, th = TR["X"][k]
                td = math.degrees(th) % 90.0
                hits = [q for q, b in enumerate(B)
                        if b.x0 - 1e-9 <= x <= b.x1 + 1e-9 and b.y0 - 1e-9 <= y <= b.y1 + 1e-9
                        and b.th0 - 1e-9 <= td <= b.th1 + 1e-9]
                return hits
            h6, h4 = find(6), find(4)
            if h6 and h4:
                p = (min(h6[0], h4[0]), max(h6[0], h4[0]))
                jobs.append((row, p, "TRUMP-CANARY"))
            else:
                jobs.append((row, None, "TRUMP-CANARY-NOTFOUND:%s/%s" % (h6, h4)))
            break

    fh = open(a.out, "a")
    for row, pr, kind in jobs:
        if pr is None:
            fh.write(json.dumps(dict(tag="canary_notfound", kind=kind)) + "\n"); fh.flush()
            print("CANARY: Trump's sq6/sq4 not both inside a cover box:", kind, flush=True)
            continue
        tag = "%s__%s__%d_%d" % (row["node"], row["cell"].replace("(", "").replace(")", "")
                                 .replace(",", ""), pr[0], pr[1])
        if tag in done:
            continue
        rec = recs.get(row["node"])
        if rec is None:
            rec = dict(src=row["src"], nid=row["node"], cls=row["cls"], level=0, side=S0,
                       budget=row["budget"], cond=[])
        B = [L.Bx(**row["boxes_json"][q]) for q in pr]
        hyp = hyp_for(rec, B)
        budget = int(row["budget"]) - 2
        t0 = time.time()
        res = solve_node(S0, hyp, budget, sym_kind="C1", time_limit=a.time_limit,
                         max_iter=400, out=None, log=lambda *x: None,
                         prune=0, prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002,
                         max_cols_add=400, max_rows_add=2000, fine_slack=0.05, alternate=True)
        eta = res["tau"] - budget
        stage = 1
        if (not res["converged"]) and -1e-3 < eta < 0.05:
            res = solve_node(S0, hyp, budget, sym_kind="C1", time_limit=a.escalate,
                             max_iter=900, out=None, log=lambda *x: None,
                             prune=0, prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002,
                             max_cols_add=400, max_rows_add=2000, fine_slack=0.05, alternate=True)
            eta = res["tau"] - budget
            stage = 2
        lp_s = round(time.time() - t0, 1)
        cert = None
        if res["tau"] < budget - 1e-6:
            res["s"] = S0
            try:
                cert = certify(res, tag)
            except Exception as e:
                cert = dict(PASS=False, error=repr(e)[:200])
        rowout = dict(tag=tag, kind=kind, node=row["node"], cls=row["cls"], cell=row["cell"],
                      pair=list(pr), budget_parent=row["budget"], budget=budget,
                      tau=res["tau"], eta=eta, converged=res["converged"],
                      minmass=res.get("minmass"), lp_s=lp_s, stage=stage,
                      dead=bool(res["converged"] and eta < -1e-6),
                      dead_unconverged=bool(eta < -1e-6), cert=cert)
        fh.write(json.dumps(rowout) + "\n"); fh.flush()
        print("%-46s bud %d tau %.4f eta %+.4f conv %s %5.0fs cert %s"
              % (tag[:46], budget, res["tau"], eta, res["converged"], lp_s,
                 (cert or {}).get("PASS")), flush=True)
    fh.close()


if __name__ == "__main__":
    main()
