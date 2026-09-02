#!/usr/bin/env python
# -*- coding: ascii -*-
"""loop413.py -- A73 T3 emission oracle loop, corners4 (k4_13) beta=0.

One iteration:
  1. assemble the v2 certificate from the current eta-primal (emit413_v2.build);
  2. run verify_pair2 --survey to hunt definitive continuum counterexample rows;
  3. append the witness placements to the catalog (adversarial catalog growth);
  4. re-solve the eta-deep covering LP (pairlp413e) on the grown catalog;
  5. repeat until the survey finds nothing at the given budget.

The catalog growth is the continuum-row mechanism of A71 T1, run through the v2
verifier instead of the float mock. Every LP re-solve re-prices ALL rows, so the
value trace is the honest restricted-to-continuum climb; abort if value >= 21.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
A73 = os.path.abspath(os.path.join(HERE, ".."))
A71 = os.path.abspath(os.path.join(A73, "..", "A71-pair-emission"))
PY = sys.executable


def log(msg, fh):
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    fh.write(line + "\n")
    fh.flush()


def run(cmd, log_fh, tag):
    log("RUN %s: %s" % (tag, " ".join(cmd)), log_fh)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.stdout:
        log_fh.write(r.stdout[-4000:])
    if r.stderr:
        log_fh.write(r.stderr[-2000:])
    log_fh.flush()
    return r.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eta", default="0.1")
    ap.add_argument("--iters", type=int, default=4)
    ap.add_argument("--survey_nodes", type=int, default=40000)
    ap.add_argument("--survey_depth", type=int, default=22)
    ap.add_argument("--faildump", type=int, default=300)
    ap.add_argument("--catalog", default=os.path.join(
        A71, "results", "catalog_k4_13_colgen_a71cg.json"))
    ap.add_argument("--lp_budget", type=float, default=1800.0)
    ap.add_argument("--tag", default="loop")
    ap.add_argument("--start_iter", type=int, default=0)
    args = ap.parse_args()

    fh = open(os.path.join(A73, "logs", "%s.log" % args.tag), "a")
    catalog_path = args.catalog
    state_path = os.path.join(A73, "progress", "%s_state.json" % args.tag)
    state = {"iters": [], "eta": args.eta}

    for it in range(args.start_iter, args.iters):
        # 1. LP solve on current catalog (skipped at iter 0 if primal exists fresh)
        primal = os.path.join(A73, "results", "pair_primal_k4_13_b0.json")
        lp_tag = "%s_i%d" % (args.tag, it)
        rc = run([PY, os.path.join(HERE, "pairlp413e.py"), "--cls", "k4_13",
                  "--betas", "0", "--eta", args.eta,
                  "--catalog", catalog_path, "--dump_primal", "0",
                  "--dump_support", "0", "--tag", lp_tag,
                  "--cls_budget", str(args.lp_budget),
                  "--total_budget", str(args.lp_budget),
                  "--headroom", "6"], fh, "LP i%d" % it)
        if rc != 0:
            log("LP failed rc=%d -- stop" % rc, fh)
            break
        lpres = json.load(open(os.path.join(
            A73, "results", "pairlp_k4_13%s.json" % lp_tag)))
        b0 = lpres["betas"].get("0.0") or list(lpres["betas"].values())[0]
        val = float(b0["value"])
        log("LP at eta=%s: value=%.6f scaled_lb=%.6f converged=%s"
            % (args.eta, val, float(b0.get("scaled_value", -1)),
               b0.get("converged")), fh)
        if val is not None and val >= 21.0:
            log("VALUE >= 21: eta too deep or route dead at this eta -- STOP", fh)
            state["verdict"] = "value_wall"
            break
        # 2. assemble cert (canary inside)
        cert = os.path.join(A73, "certs", "pair_k4_13_s0_b0_%s_i%d.json"
                            % (args.tag, it))
        rc = run([PY, os.path.join(HERE, "emit413_v2.py"), "--seed", primal,
                  "--out", cert], fh, "EMIT i%d" % it)
        if rc != 0:
            log("emit/canary failed rc=%d -- stop" % rc, fh)
            break
        # 3. survey
        rep = os.path.join(A73, "results", "survey_%s_i%d.report.json"
                           % (args.tag, it))
        rc = run([PY, os.path.join(HERE, "verify_pair2.py"), cert,
                  "--depth", str(args.survey_depth),
                  "--nodes", str(args.survey_nodes),
                  "--survey", "--faildump", str(args.faildump),
                  "--report", rep], fh, "SURVEY i%d" % it)
        r = json.load(open(rep))
        fails = r.get("failures", [])
        defs = [f for f in fails if f.get("kind") == "definitive"]
        caps = [f for f in fails if f.get("kind") == "cap"]
        log("survey i%d: verdict rc=%d definitive=%d cap=%d examined=%d"
            % (it, rc, len(defs), len(caps), r["counts"]["pairs_examined"]), fh)
        state["iters"].append({"iter": it, "lp_value": val,
                               "definitive": len(defs), "cap": len(caps),
                               "cert": cert, "report": rep})
        json.dump(state, open(state_path, "w"), indent=1)
        if rc == 0:
            log("SURVEY PASS at budget -- escalate depth/nodes for the "
                "certification run", fh)
            state["verdict"] = "survey_clean"
            break
        if not defs:
            log("no definitive rows (only cap witnesses) -- deepen survey or "
                "hand to compiled verifier", fh)
            state["verdict"] = "cap_only"
            break
        # 4. grow catalog with witness placements
        cat = json.load(open(catalog_path))
        pl = cat["placements"]
        seen = set(tuple(round(float(v), 9) for v in p) for p in pl)
        added = 0
        for f in defs:
            for key in ("plA", "plB"):
                cx, cy, t = [float(Fr(v)) for v in f[key]]
                tup = (round(t, 9), round(cx, 9), round(cy, 9))
                if tup not in seen:
                    seen.add(tup)
                    pl.append([tup[0], tup[1], tup[2]])
                    added += 1
        log("catalog grow: +%d placements (total %d)" % (added, len(pl)), fh)
        grown = os.path.join(A73, "results", "catalog_k4_13_%s_i%d.json"
                             % (args.tag, it + 1))
        cat["placements"] = pl
        cat["n"] = len(pl)
        cat.setdefault("note", "")
        cat["note"] += " +A73 %s iter %d survey witnesses" % (args.tag, it)
        json.dump(cat, open(grown, "w"))
        catalog_path = grown
        if added == 0:
            log("no new placements -- fixed point at this budget", fh)
            state["verdict"] = "fixed_point"
            break
    json.dump(state, open(state_path, "w"), indent=1)
    log("loop done: %s" % state.get("verdict", "iters_exhausted"), fh)


if __name__ == "__main__":
    main()
