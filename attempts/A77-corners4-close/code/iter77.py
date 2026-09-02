#!/usr/bin/env python
# -*- coding: ascii -*-
"""iter77.py -- one A77 loop iteration for corners4 (k4_13) beta=0.

  grow   : catalog(prev) + hole placements harvested by hintbatch (float-admissible
           interior-disjoint pairs collecting < 1) -> catalog(new)
  lp     : pairlp413m (A74 recipe, dual-seeded incl. the previous primal) on catalog(new)
  emit   : emit413m (Trump canary inside) -> certs/pair_k4_13_s0_b0_<tag>.json
  build  : hintbatch complete-tree build at a fixed per-root cap -> hinted cert + holes

Everything emission-side; the frozen verifiers are untouched (hintbatch imports
verify_pair2 read-only for roots/clip).  Subcommands can be run separately.
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
A77 = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(A77, ".."))
A74 = os.path.join(ATT, "A74-mixed-depth")
PY = sys.executable


def log(msg, fh):
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    fh.write(line + "\n")
    fh.flush()


def run(cmd, fh, tag, cwd=None):
    log("RUN %s: %s" % (tag, " ".join(cmd)), fh)
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if r.stdout:
        fh.write(r.stdout[-6000:])
    if r.stderr:
        fh.write(r.stderr[-3000:])
    fh.flush()
    return r.returncode


def grow(prev_catalog, holes_files, out, fh, snap=1e-4):
    cat = json.load(open(prev_catalog))
    pl = cat["placements"]

    def key(p):
        return tuple(round(float(v) / snap) for v in p)
    seen = set(key(p) for p in pl)
    added, nh = 0, 0
    for hf in holes_files:
        d = json.load(open(hf))
        for h in d["holes"]:
            nh += 1
            for side in ("A", "B"):
                p = h[side]                      # [t, cx, cy]
                k = key(p)
                if k in seen:
                    continue
                seen.add(k)
                pl.append([float(p[0]), float(p[1]), float(p[2])])
                added += 1
    cat["placements"] = pl
    cat["n"] = len(pl)
    cat["note"] = cat.get("note", "") + " +A77 %d hole placements from %s" % (
        added, ",".join(os.path.basename(x) for x in holes_files))
    json.dump(cat, open(out, "w"))
    log("grow: %d holes -> +%d placements (total %d) -> %s" % (nh, added, len(pl), out), fh)
    return added


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["grow", "lp", "emit", "build", "all"])
    ap.add_argument("--tag", required=True, help="e.g. md9")
    ap.add_argument("--prev_catalog", default="")
    ap.add_argument("--holes", default="", help="comma list of hintbatch hole files")
    ap.add_argument("--catalog", default="")
    ap.add_argument("--seeds", default="")
    ap.add_argument("--lp_extra", default="")
    ap.add_argument("--cap", type=int, default=60000)
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--rule", default="certain")
    ap.add_argument("--maxdepth", type=int, default=60)
    ap.add_argument("--cert_in", default="")
    args = ap.parse_args()
    fh = open(os.path.join(A77, "logs", "iter_%s.log" % args.tag), "a")
    R = os.path.join(A77, "results")
    catalog = args.catalog or os.path.join(R, "catalog_k4_13_%s.json" % args.tag)
    if args.stage in ("grow", "all"):
        assert args.prev_catalog and args.holes
        grow(args.prev_catalog, args.holes.split(","), catalog, fh)
    primal = os.path.join(R, "pair_primal_k4_13_b0_%s.json" % args.tag)
    if args.stage in ("lp", "all"):
        seeds = args.seeds or ",".join([
            os.path.join(R, "seed_md8.json"),
            os.path.join(A74, "results", "seed_md7.json"),
            os.path.join(A74, "results", "seed_md5.json"),
            os.path.join(ATT, "A71-pair-emission", "results", "pair_dual_k4_13_a71cg.json"),
            os.path.join(ATT, "A73-pair-v2", "results", "pair_dual_k4_13eta001.json")])
        cmd = [PY, os.path.join(HERE, "pairlp413m.py"), "--cls", "k4_13", "--beta", "0",
               "--etas", "0.05,0.02,0.008,0.002,0.0005", "--mu", "0.01",
               "--catalog", catalog, "--tag", "_" + args.tag,
               "--seed_dual", seeds, "--seed_dual_cap", "500",
               "--max_cuts", "300", "--cuts_per_point", "2", "--max_rows", "30000",
               "--max_nnz", "14000000", "--purge_every", "4", "--purge_min", "150",
               "--stop_value", "20.9", "--lp_solver", "ipm", "--loop_crossover", "on",
               "--final_solver", "ipm", "--lp_time", "1500", "--cls_budget", "6000",
               "--consolidate_rounds", "12", "--consol_wmin", "0.0005",
               "--consol_guard", "20.97", "--headroom", "6", "--headroom_wait", "3600"]
        for kv in [x for x in args.lp_extra.split(",") if x]:
            k, v = kv.split("=")
            cmd += ["--" + k, v]
        rc = run(cmd, fh, "LP " + args.tag)
        res = json.load(open(os.path.join(R, "pairlp413m_k4_13_%s.json" % ("_" + args.tag))))
        log("LP %s: rc=%d W2=%.6f value=%.6f verdict=%s atoms=%s hist=%s note=%s secs=%.0f"
            % (args.tag, rc, res["W2_emitted"], res["value_emitted"], res["verdict"],
               json.load(open(res["primal"]))["provenance"]["n_atoms"],
               json.dumps(res["depth_hist_emitted"]), res["note"], res["total_seconds"]), fh)
        if res["verdict"] != "UNDER":
            log("LP verdict %s -- stop" % res["verdict"], fh)
            sys.exit(2)
        primal = res["primal"]
    cert = os.path.join(A77, "certs", "pair_k4_13_s0_b0_%s.json" % args.tag)
    if args.stage in ("emit", "all"):
        rc = run([PY, os.path.join(HERE, "emit413m.py"), "--seed", primal, "--out", cert],
                 fh, "EMIT " + args.tag)
        if rc != 0:
            log("emit/canary failed rc=%d -- stop" % rc, fh)
            sys.exit(3)
        cj = json.load(open(os.path.join(R, "canary_trump.json")))
        log("canary: %s" % json.dumps(cj)[:300], fh)
    if args.stage in ("build", "all"):
        cin = args.cert_in or cert
        hinted = os.path.join(A77, "certs", "pair_k4_13_s0_b0_%s_hb.json" % args.tag)
        holes = os.path.join(R, "hb_%s.json" % args.tag)
        rc = run([PY, os.path.join(HERE, "hintbatch.py"), cin, hinted, "--cap", str(args.cap),
                  "--maxdepth", str(args.maxdepth), "--jobs", str(args.jobs), "--chunk", "512",
                  "--rule", args.rule, "--keep_open", "500", "--holes", holes],
                 fh, "BUILD " + args.tag)
        s = json.load(open(holes))["summary"]
        log("build %s: nodes=%d census=%s holes=%d open=%d budget_roots=%d secs=%s"
            % (args.tag, s["nodes"], json.dumps(s["census"]), s["n_holes"], s["n_open"],
               s["budget_roots"], s["seconds"]), fh)
    fh.close()


if __name__ == "__main__":
    main()
