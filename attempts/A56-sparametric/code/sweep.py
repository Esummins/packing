#!/usr/bin/env python3
"""
sweep.py -- A56 T2(D).  Campaign runner for the s-parametric re-certification of the
stratum-kill library, with checkpointing (every row is written to results/ as soon as it is
known, so the campaign is resume-safe).

Sub-commands
    stage0   pricing map at the FAR endpoint.  For every multi-corner certificate: build the
             parametric certificate with the default (nearest-wall) anchoring, specialise at
             s = 191/50 and run the UNMODIFIED A53 verify_case.py.  A certificate that fails
             here cannot transfer with that anchoring; it is retried once with --beta-mid and,
             if it still fails, recorded as "anchoring-open" with its worst witness.
             -> results/stage0_endpoint.json
    sweep    the real thing.  For every requested certificate: build the parametric certificate
             (anchoring taken from the stage0 result), run verify_param.py over [slo, s0], and
             on PASS run canary C2 -- the OLD verify_case.py on the specialisations at
             s = 191/50, s = midpoint, s = s0; all three must PASS for the row to count as
             TRANSFERRED.  On FAIL, optionally bisect in s for the largest [a, s0] that passes
             ("partial transfer down to a").  -> results/scoreboard.json

Concurrency: at most --heavy (default 3) worker processes at any time, as required by the
A56 brief (A55 is running on the same machine).

single_corner certificates (k5_00, k5_01, k6_00, k6_01) are M1-free: soundness.md P2 theorem M1
transfers them to every s <= s0 with no computation.  They are marked "M1" and skipped.
"""
import argparse
import json
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
A56 = os.path.normpath(os.path.join(HERE, ".."))
ATTEMPTS = os.path.normpath(os.path.join(A56, ".."))
VERIFY_CASE = os.path.join(ATTEMPTS, "A53-simple-strata", "code", "verify_case.py")
MAKE_PARAM = os.path.join(HERE, "make_param.py")
SPECIALIZE = os.path.join(HERE, "specialize.py")
VERIFY_PARAM = os.path.join(HERE, "verify_param.py")
INVENTORY = os.path.join(A56, "results", "library_inventory.json")
CERTS = os.path.join(A56, "certs")
RESULTS = os.path.join(A56, "results")
LOGS = os.path.join(A56, "logs")

S0 = F(969271, 250000)
S_LO = F(191, 50)
M1_FREE = ("k5_00", "k5_01", "k6_00", "k6_01")

_lock = threading.Lock()


def sh(cmd, log, timeout=None):
    t0 = time.time()
    os.makedirs(os.path.dirname(log), exist_ok=True)
    with open(log, "a", encoding="utf-8") as fh:
        fh.write("\n$ " + " ".join(str(c) for c in cmd) + "\n")
        fh.flush()
        try:
            p = subprocess.run([str(c) for c in cmd], stdout=fh, stderr=subprocess.STDOUT,
                               timeout=timeout)
            rc = p.returncode
        except subprocess.TimeoutExpired:
            fh.write(f"*** TIMEOUT after {timeout}s\n")
            rc = 124
    return rc, time.time() - t0


def load_inventory():
    inv = json.load(open(INVENTORY))
    for c in inv["certs"]:
        c["path"] = c["path"].replace("\\", "/")
    return inv


def checkpoint(path, obj):
    with _lock:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, indent=1)
        os.replace(tmp, path)


def worst_witness(report_path):
    if not os.path.exists(report_path):
        return None
    try:
        r = json.load(open(report_path))
    except Exception:
        return None
    ws = r.get("witnesses_preview") or []
    if not ws:
        return None
    w = min(ws, key=lambda z: z.get("float_mass", 9e9))
    out = {"kind": w.get("kind"), "exact_mass": w.get("exact_mass"),
           "float_mass": w.get("float_mass"), "placement": w.get("placement"),
           "box": w.get("box")}
    return out


# ============================================================================ stage 0
# anchoring ladder (soundness.md P3: the anchoring is a COMPLETENESS choice only).
#   gap          threshold in the widest gap of the certificate's own coordinates in [1.9, 2.7]
#                -- keeps each local cluster of atoms rigid, which is what a placement next to
#                that cluster needs; this is the A56 default (see notes in make_param.py)
#   nearest-wall the brief's default rule, beta = 1 iff coord > s0/2
#   mid-band     beta = 1/2 in a band of half-width 1/2 around the threshold
ANCHORS = {
    "gap": ["--beta-gap", "19/10,27/10"],
    "nearest-wall": [],
    "mid-band": ["--beta-mid", "1/2"],
}


def build_param(name, base, out, anchor="nearest-wall", log=None):
    cmd = [sys.executable, MAKE_PARAM, base, "-o", out, "--name", name] + ANCHORS[anchor]
    return sh(cmd, log)


def stage0_one(c, args):
    name, base = c["name"], c["path"]
    d = os.path.join(CERTS, "stage0")
    os.makedirs(d, exist_ok=True)
    log = os.path.join(LOGS, f"stage0_{name}.log")
    row = {"name": name, "k": c["k"], "margin": c["margin"], "atoms": c["atoms"],
           "corners": c["corners"]}
    for anch in args.ladder.split(","):
        tag = {"gap": "gp", "nearest-wall": "nw", "mid-band": "mb"}[anch]
        par = os.path.join(d, f"{name}.{tag}.param.json")
        spec = os.path.join(d, f"{name}.{tag}.slo.json")
        rep = os.path.join(d, f"{name}.{tag}.slo.report.json")
        rc, _ = build_param(name, base, par, anch, log)
        if rc != 0:
            row.update({"result": "MAKE_PARAM_ERROR", "anchoring": anch})
            return row
        rc, _ = sh([sys.executable, SPECIALIZE, par, "--s", str(S_LO), "-o", spec], log)
        if rc != 0:
            row.update({"result": "SPECIALIZE_ERROR", "anchoring": anch})
            return row
        rc, dt = sh([sys.executable, VERIFY_CASE, spec, "--depth", args.depth0, "--jobs", "1",
                     "--report", rep, "--witness-file", os.path.join(d, f"{name}.{tag}.wit.json"),
                     "--max-witnesses", "40", "--quiet"], log, timeout=args.timeout)
        row.setdefault("attempts", []).append(
            {"anchoring": anch, "rc": rc, "time_s": round(dt, 1),
             "worst": worst_witness(rep) if rc == 1 else None})
        if rc == 0:
            row.update({"result": "PASS", "anchoring": anch, "time_s": round(dt, 1),
                        "param": par})
            return row
        if rc == 124:
            row.update({"result": "TIMEOUT", "anchoring": anch, "time_s": round(dt, 1)})
            return row
        if rc == 2:
            row.update({"result": "MALFORMED", "anchoring": anch})
            return row
    row.update({"result": "anchoring-open", "anchoring": "both tried",
                "worst": row["attempts"][-1]["worst"]})
    return row


def cmd_stage0(args):
    inv = load_inventory()
    todo = [c for c in inv["certs"] if not c["single_corner"]]
    if args.only:
        keep = set(args.only.split(","))
        todo = [c for c in todo if c["name"] in keep]
    todo.sort(key=lambda c: -c["margin"])
    out_path = os.path.join(RESULTS, "stage0_endpoint.json")
    state = {"s": str(S_LO), "depth": args.depth0, "rows": {}}
    if os.path.exists(out_path) and not args.restart:
        state = json.load(open(out_path))
        state.setdefault("rows", {})
    print(f"stage0: {len(todo)} multi-corner certificates at s = {S_LO}, depth {args.depth0}, "
          f"{args.heavy} concurrent")
    with ThreadPoolExecutor(max_workers=args.heavy) as ex:
        futs = {ex.submit(stage0_one, c, args): c["name"]
                for c in todo if c["name"] not in state["rows"]}
        for f in futs:
            pass
        done = 0
        for f, nm in list(futs.items()):
            row = f.result()
            state["rows"][row["name"]] = row
            checkpoint(out_path, state)
            done += 1
            print(f"  [{done}/{len(futs)}] {row['name']:8s} {row['result']:16s} "
                  f"{row.get('anchoring','')}  {row.get('time_s','')}s", flush=True)
    summ = {}
    for r in state["rows"].values():
        summ[r["result"]] = summ.get(r["result"], 0) + 1
    state["summary"] = summ
    checkpoint(out_path, state)
    print("stage0 summary:", summ)
    print("->", out_path)
    return 0


# ============================================================================ sweep
def c2_crosscheck(name, par, slo, args, log, tag=""):
    """canary C2: the OLD verify_case.py on the specialisations at slo, midpoint, s0."""
    d = os.path.join(CERTS, "c2")
    os.makedirs(d, exist_ok=True)
    out = []
    for lbl, s in (("lo", slo), ("mid", (slo + S0) / 2), ("hi", S0)):
        spec = os.path.join(d, f"{name}{tag}.{lbl}.json")
        rep = os.path.join(d, f"{name}{tag}.{lbl}.report.json")
        rc, _ = sh([sys.executable, SPECIALIZE, par, "--s", str(s), "-o", spec], log)
        if rc != 0:
            out.append({"s": str(s), "result": "SPECIALIZE_ERROR"})
            break
        rc, dt = sh([sys.executable, VERIFY_CASE, spec, "--depth", args.depth0,
                     "--jobs", str(args.heavy), "--report", rep,
                     "--witness-file", os.path.join(d, f"{name}{tag}.{lbl}.wit.json"),
                     "--max-witnesses", "20", "--quiet"], log, timeout=args.timeout)
        out.append({"s": str(s), "s_float": float(s),
                    "result": {0: "PASS", 1: "FAIL", 2: "MALFORMED", 124: "TIMEOUT"}.get(rc, rc),
                    "time_s": round(dt, 1)})
        if rc != 0:
            break
    return out


def run_param(name, par, slo, args, log, tag=""):
    rep = os.path.join(CERTS, f"{name}{tag}.param.report.json")
    rc, dt = sh([sys.executable, VERIFY_PARAM, par, "--slo", str(slo), "--shi", str(S0),
                 "--depth", str(args.depth), "--sscale", str(args.sscale),
                 "--tscale", str(args.tscale), "--split", str(args.split),
                 "--jobs", str(args.heavy), "--report", rep,
                 "--witness-file", os.path.join(CERTS, f"{name}{tag}.param.wit.json"),
                 "--max-witnesses", str(args.max_witnesses), "--quiet"],
                log, timeout=args.timeout)
    st = {}
    if os.path.exists(rep):
        try:
            st = json.load(open(rep))
        except Exception:
            st = {}
    return rc, dt, st, rep


def sweep_one(c, args, stage0_rows, state, out_path):
    name, base = c["name"], c["path"]
    log = os.path.join(LOGS, f"sweep_{name}.log")
    row = {"name": name, "k": c["k"], "margin": c["margin"], "atoms": c["atoms"],
           "corners": c["corners"], "single_corner": c["single_corner"]}
    if c["single_corner"]:
        row.update({"result": "M1", "note": "single-corner: transferred by soundness.md M1 "
                                            "(theorem, no computation)"})
        return row
    s0row = (stage0_rows or {}).get(name, {})
    if s0row.get("result") == "anchoring-open" and not args.force:
        row.update({"result": "anchoring-open", "stage0": s0row.get("result"),
                    "worst": s0row.get("worst"),
                    "note": "fails already at the far endpoint s = 191/50 with every anchoring"})
        return row
    ladder = args.ladder.split(",")
    if s0row.get("anchoring") == "mid-band":
        # stage0 found the plain rules already fail at the far endpoint: put mid-band first
        ladder = ["mid-band"] + [x for x in ladder if x != "mid-band"]
    rc = dt = st = rep = None
    par = None
    row["anchoring_tried"] = []
    for att, anch in enumerate(ladder[:args.max_anchors]):
        par = os.path.join(CERTS, f"{name}.param.json" if att == 0
                           else f"{name}.{anch}.param.json")
        rcb, _ = build_param(name, base, par, anch, log)
        if rcb != 0:
            row.update({"result": "MAKE_PARAM_ERROR"})
            return row
        rc, dt, st, rep = run_param(name, par, S_LO, args, log,
                                    tag="" if att == 0 else f".{anch}")
        row["anchoring_tried"].append({"anchoring": anch,
                                       "result": {0: "PASS", 1: "FAIL", 124: "TIMEOUT"}.get(rc, rc),
                                       "time_s": round(dt, 1)})
        row["anchoring"] = anch
        row["param_time_s"] = round(sum(a["time_s"] for a in row["anchoring_tried"]), 1)
        row["param_report"] = rep
        row["param_stats"] = {k: st.get("stats", {}).get(k) for k in
                              ("boxes", "covered", "exempt", "vacuous", "split", "s_splits",
                               "s_cells", "max_depth", "max_s_depth")}
        if rc == 0:
            row["param_result"] = "PASS"
            row["s_range"] = [str(S_LO), str(S0)]
            row["c2"] = c2_crosscheck(name, par, S_LO, args, log)
            row["result"] = ("TRANSFERRED" if all(x.get("result") == "PASS" for x in row["c2"])
                             else "C2-DISCREPANCY")
            return row
        if rc not in (1,):
            break
    row["param_result"] = {1: "FAIL", 2: "MALFORMED", 124: "TIMEOUT"}.get(rc, rc)
    row["witness_s_range"] = (st or {}).get("witness_s_range")
    row["worst"] = worst_witness(rep) if rep else None
    if rc != 1 or not args.bisect:
        row["result"] = "OPEN" if rc == 1 else row["param_result"]
        return row
    # partial transfer: a few probes for the largest [a, s0] that passes
    lo, hi = S_LO, S0                      # invariant: [lo,s0] fails, [hi,s0] passes (hi=s0 trivial)
    best = None
    probes = []
    for _ in range(args.bisect):
        a = (lo + hi) / 2
        a = F(round(a * 250000), 250000)   # keep the probe on the 1/250000 grid
        if a <= lo or a >= hi:
            break
        rc2, dt2, st2, _ = run_param(name, par, a, args, log, tag=f".a{a.numerator}")
        probes.append({"a": str(a), "a_float": float(a), "result": "PASS" if rc2 == 0 else "FAIL",
                       "time_s": round(dt2, 1)})
        if rc2 == 0:
            best, hi = a, a
        else:
            lo = a
    row["probes"] = probes
    if best is None:
        row["result"] = "OPEN"
        return row
    parb = par
    row["c2"] = c2_crosscheck(name, parb, best, args, log, tag=".partial")
    row["s_range"] = [str(best), str(S0)]
    row["result"] = ("partial" if all(x.get("result") == "PASS" for x in row["c2"])
                     else "C2-DISCREPANCY")
    return row


def cmd_sweep(args):
    inv = load_inventory()
    s0p = os.path.join(RESULTS, "stage0_endpoint.json")
    stage0_rows = json.load(open(s0p)).get("rows", {}) if os.path.exists(s0p) else {}
    todo = list(inv["certs"])
    if args.only:
        keep = [x for x in args.only.split(",") if x]
        todo = [c for c in todo if c["name"] in keep]
        todo.sort(key=lambda c: keep.index(c["name"]))
    else:
        todo.sort(key=lambda c: -c["margin"])           # cheapest first
    out_path = os.path.join(RESULTS, "scoreboard.json")
    state = {"window": [str(S_LO), str(S0)], "depth": args.depth, "sscale": args.sscale,
             "rows": {}}
    if os.path.exists(out_path) and not args.restart:
        state = json.load(open(out_path))
        state.setdefault("rows", {})
    t0 = time.time()
    spent = float(state.get("cumulative_verifier_time_s", 0.0))
    for c in todo:
        if c["name"] in state["rows"] and not args.redo:
            continue
        if args.budget and spent > args.budget:
            state["stopped_early"] = {"reason": "time budget", "budget_s": args.budget,
                                      "spent_s": round(spent, 1),
                                      "remaining": [x["name"] for x in todo
                                                    if x["name"] not in state["rows"]]}
            checkpoint(out_path, state)
            print(f"STOP: cumulative verifier time {spent/3600:.2f} h exceeds the budget; "
                  f"{len(state['stopped_early']['remaining'])} certificates remain")
            break
        row = sweep_one(c, args, stage0_rows, state, out_path)
        spent += float(row.get("param_time_s") or 0.0)
        for pr in row.get("probes", []) or []:
            spent += float(pr.get("time_s") or 0.0)
        state["rows"][row["name"]] = row
        state["cumulative_verifier_time_s"] = round(spent, 1)
        state["summary"] = summarize(state["rows"])
        checkpoint(out_path, state)
        print(f"  {row['name']:8s} k={row['k']} margin={row['margin']:.6f} -> {row['result']:14s} "
              f"param {row.get('param_time_s','-')}s  s-splits "
              f"{(row.get('param_stats') or {}).get('s_splits','-')}  "
              f"[cum {spent/60:.1f} min]", flush=True)
    state["summary"] = summarize(state["rows"])
    state["wall_time_this_run_s"] = round(time.time() - t0, 1)
    checkpoint(out_path, state)
    print("scoreboard:", json.dumps(state["summary"]))
    print("->", out_path)
    return 0


def summarize(rows):
    out = {"total": len(rows), "by_result": {}, "by_k": {}}
    for r in rows.values():
        out["by_result"][r["result"]] = out["by_result"].get(r["result"], 0) + 1
        key = f"k{r['k']}"
        d = out["by_k"].setdefault(key, {})
        d[r["result"]] = d.get(r["result"], 0) + 1
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for nm in ("stage0", "sweep"):
        p = sub.add_parser(nm)
        p.add_argument("--only", default=None, help="comma-separated certificate names")
        p.add_argument("--heavy", type=int, default=3, help="max concurrent worker processes")
        p.add_argument("--depth0", default="44", help="depth for the fixed-s verify_case runs")
        p.add_argument("--timeout", type=int, default=3600)
        p.add_argument("--restart", action="store_true")
        p.add_argument("--ladder", default="gap,nearest-wall,mid-band",
                       help="anchoring ladder, tried in order")
        if nm == "sweep":
            p.add_argument("--max-anchors", type=int, default=2,
                           help="how many anchorings of the ladder to try in the 4D run")
            p.add_argument("--depth", type=int, default=56)
            p.add_argument("--sscale", default="8")
            p.add_argument("--tscale", default="2")
            p.add_argument("--split", type=int, default=3)
            p.add_argument("--max-witnesses", type=int, default=20)
            p.add_argument("--bisect", type=int, default=0,
                           help="on FAIL, this many probes for the largest [a,s0] that passes")
            p.add_argument("--budget", type=float, default=None,
                           help="stop cleanly once cumulative verifier time exceeds this (s)")
            p.add_argument("--redo", action="store_true")
            p.add_argument("--force", action="store_true",
                           help="sweep even certificates stage0 marked anchoring-open")
    a = ap.parse_args(argv)
    os.makedirs(CERTS, exist_ok=True)
    os.makedirs(RESULTS, exist_ok=True)
    os.makedirs(LOGS, exist_ok=True)
    return cmd_stage0(a) if a.cmd == "stage0" else cmd_sweep(a)


if __name__ == "__main__":
    sys.exit(main())
