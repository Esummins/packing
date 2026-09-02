#!/usr/bin/env python
# -*- coding: ascii -*-
"""loop413m.py -- A74 T1 mixed-depth emission loop, corners4 (k4_13) beta=0.

One iteration:
  1. solve the MIXED-DEPTH depth-priced covering LP (pairlp413m) on the catalog;
  2. assemble the v2 certificate (emit413m; Trump canary inside, per run);
  3. survey with the COMPILED Rust verify_pair2 (--jobs 8, A39 discipline:
     the compiled run is cheap, use it inside the loop);
  4. grow the catalog with the definitive witnesses' placements;
  5. repeat until the survey is clean at budget (then escalate to the
     certification run) or a wall is measured (Lemma W-double-prime rows).
"""
import argparse
import json
import os
import subprocess
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
A74 = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(A74, ".."))
RS = os.path.join(ATT, "A73-pair-v2", "code", "verify_pair2_rs",
                  "target", "release", "verify_pair2.exe")
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


def witness_placements(rep):
    """extract exact (t, cx, cy) floats from a Rust survey report's definitive
    witnesses (confirm.square1/square2)."""
    out = []
    for w in rep.get("witnesses", []):
        if w.get("kind") != "definitive":
            continue
        cf = w.get("confirm")
        if not cf:
            continue
        for key in ("square1", "square2"):
            sq = cf.get(key)
            if not sq:
                continue
            t = float(Fr(sq["t"]))
            cx = float(Fr(sq["cx"]))
            cy = float(Fr(sq["cy"]))
            out.append((round(t, 9), round(cx, 9), round(cy, 9)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--etas", default="0.05,0.02,0.008,0.002")
    ap.add_argument("--mu", type=float, default=0.02)
    ap.add_argument("--iters", type=int, default=4)
    ap.add_argument("--survey_nodes", type=int, default=2000000)
    ap.add_argument("--survey_depth", type=int, default=34)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--faildump", type=int, default=300)
    ap.add_argument("--catalog", default=os.path.join(
        ATT, "A71-pair-emission", "results", "catalog_k4_13_colgen_a71cg.json"))
    ap.add_argument("--lp_budget", type=float, default=3600.0)
    ap.add_argument("--lp_time", type=float, default=450.0)
    ap.add_argument("--stop_value", type=float, default=20.95)
    ap.add_argument("--lp_extra", default="",
                    help="extra pairlp413m args, comma-separated k=v")
    ap.add_argument("--consolidate_rounds", type=int, default=6)
    ap.add_argument("--tag", default="mloop")
    ap.add_argument("--start_iter", type=int, default=0)
    args = ap.parse_args()

    fh = open(os.path.join(A74, "logs", "%s.log" % args.tag), "a")
    catalog_path = args.catalog
    state_path = os.path.join(A74, "progress", "%s_state.json" % args.tag)
    state = {"iters": [], "etas": args.etas, "mu": args.mu}

    for it in range(args.start_iter, args.iters):
        lp_tag = "_%s_i%d" % (args.tag, it)
        # 1. mixed-depth LP
        cmd = [PY, os.path.join(HERE, "pairlp413m.py"), "--cls", "k4_13",
               "--beta", "0", "--etas", args.etas, "--mu", str(args.mu),
               "--catalog", catalog_path, "--tag", lp_tag,
               "--cls_budget", str(args.lp_budget),
               "--lp_time", str(args.lp_time),
               "--stop_value", str(args.stop_value),
               "--purge_every", "2", "--purge_min", "100",
               "--max_cuts", "1000", "--cuts_per_point", "2",
               "--max_nnz", "9000000",
               "--consolidate_rounds", str(args.consolidate_rounds),
               "--headroom", "6"]
        for kv in [x for x in args.lp_extra.split(",") if x]:
            k, v = kv.split("=")
            cmd += ["--" + k, v]
        rc = run(cmd, fh, "LP i%d" % it)
        if rc != 0:
            log("LP failed rc=%d -- stop" % rc, fh)
            state["verdict"] = "lp_failed"
            break
        lpres = json.load(open(os.path.join(
            A74, "results", "pairlp413m_k4_13%s.json" % lp_tag)))
        val = float(lpres["value_emitted"])
        w2 = float(lpres["W2_emitted"])
        log("LP i%d: value=%.6f W2=%.6f verdict=%s hist=%s converged=%s"
            % (it, val, w2, lpres["verdict"],
               json.dumps(lpres["depth_hist_emitted"]), lpres["converged"]), fh)
        if lpres["verdict"] == "OVER":
            if lpres["converged"]:
                log("LP value >= 21 on the restricted rows AND separation "
                    "converged: MIXED-DEPTH WALL (W-double-prime measurement)", fh)
                state["verdict"] = "value_wall"
            else:
                log("LP value >= 21 but separation UNCONVERGED: budget wall, "
                    "not a value wall -- raise lp_time/cls_budget", fh)
                state["verdict"] = "budget_wall"
            state["wall"] = dict(value=val, hist=lpres["depth_hist_emitted"],
                                 converged=lpres["converged"])
            break
        primal = lpres["primal"]
        # 2. emit + canary
        cert = os.path.join(A74, "certs", "pair_k4_13_s0_b0_%s_i%d.json"
                            % (args.tag, it))
        rc = run([PY, os.path.join(HERE, "emit413m.py"), "--seed", primal,
                  "--out", cert], fh, "EMIT i%d" % it)
        if rc != 0:
            log("emit/canary failed rc=%d -- stop" % rc, fh)
            state["verdict"] = "emit_failed"
            break
        # 3. survey with the compiled verifier
        rep_fp = os.path.join(A74, "results", "survey_%s_i%d.report.json"
                              % (args.tag, it))
        rc = run([RS, cert, "--depth", str(args.survey_depth),
                  "--nodes", str(args.survey_nodes), "--jobs", str(args.jobs),
                  "--survey", "--faildump", str(args.faildump),
                  "--report", rep_fp], fh, "SURVEY i%d" % it)
        rep = json.load(open(rep_fp))
        wk = rep.get("witness_kinds", {})
        ndef, ncap = int(wk.get("definitive", 0)), int(wk.get("cap", 0))
        log("survey i%d: rc=%d verdict=%s definitive=%d cap=%d examined=%s "
            "counts=%s" % (it, rc, rep.get("verdict"), ndef, ncap,
                           rep["counts"]["pairs_examined"],
                           json.dumps(rep["counts"])), fh)
        state["iters"].append(dict(iter=it, lp_value=val, W2=w2,
                                   hist=lpres["depth_hist_emitted"],
                                   definitive=ndef, cap=ncap, cert=cert,
                                   report=rep_fp, verdict=rep.get("verdict")))
        json.dump(state, open(state_path, "w"), indent=1)
        if rc == 0:
            log("SURVEY PASS at budget -- escalate to certification run", fh)
            state["verdict"] = "survey_clean"
            break
        if ndef == 0:
            log("no definitive rows (cap witnesses only) -- deepen survey", fh)
            state["verdict"] = "cap_only"
            break
        # 4. grow catalog
        cat = json.load(open(catalog_path))
        pl = cat["placements"]
        seen = set(tuple(round(float(v), 9) for v in p) for p in pl)
        added = 0
        for tup in witness_placements(rep):
            if tup not in seen:
                seen.add(tup)
                pl.append([tup[0], tup[1], tup[2]])
                added += 1
        log("catalog grow: +%d placements (total %d)" % (added, len(pl)), fh)
        grown = os.path.join(A74, "results", "catalog_k4_13_%s_i%d.json"
                             % (args.tag, it + 1))
        cat["placements"] = pl
        cat["n"] = len(pl)
        cat.setdefault("note", "")
        cat["note"] += " +A74 %s iter %d survey witnesses" % (args.tag, it)
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
