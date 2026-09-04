"""A96 step 3: close the two recurring slivers.

A95 found that the parametric FAILs miss the SAME two s-cells on every node:

    A  [191/50, 977934271/256000000]          = [3.82,        3.820055746...]
    B  [979732417/256000000, 7654271/2000000] = [3.827079753..., 3.8271355  ]

Both are exactly one s-cell of width 14271/250000/1024 = 5.5746e-5 (the window bisected 10
times), A is the window's left-most cell and B ends exactly at the window's 1/8 point -- i.e.
they are cells adjacent to the coarse s-split boundaries, not per-node hardness.

DIAGNOSIS from A95's witness files: every witness on both slivers sits at a t-EXTREME,
t in [0, 1/4096] or [4095/4096, 1] (theta ~ 0 or ~90 deg), and its sample placement carries
exact_mass 4987/4000 > 1 -- the cell is UNDECIDED, not violated.  So this is an enclosure/
splitting-budget artifact at the axis-aligned corner of the t-range, and the natural repair is
to spend the budget where the trouble is (t) on the tiny sliver window, NOT to buy a new LP.

ROUTES PRICED HERE (brief item 3b):
  (ii) reverify: the SAME parametric certificate, verified on the sliver sub-window only, with
       the split budget re-weighted toward t and more depth.  Cost = one short verifier run;
       no LP, no new certificate, nothing new to audit -- the frozen verifier is re-run on a
       narrower window and its PASS composes by A86 T4's WindowRows disjunction.
  (i)  re-emit: a fresh fixed-side slack-core certificate at the sliver's midpoint, converted
       and verified over the sliver.  Cost = LP + certify + verify per node.  Priced from A57's
       own measured LP+cert wall for the node (results field fixed_wall_s), not guessed.

Route A (the [3.82, ...] sliver) is additionally checked against A.LB382: see notes/slivers.md.

Usage:  python code/sliver96.py [--procs 1] [--nodes id,id,...]
Writes results/sliver96.jsonl.
"""
import argparse, glob, json, os, subprocess, sys, time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
VP = os.path.join(HERE, "verify_param.py")
OUT = os.path.join(BASE, "results")
A95 = os.path.abspath(os.path.join(BASE, "..", "A95-a57-shortcuts", "results", "param"))

SLIVERS = {
    "A": ("191/50", "977934271/256000000"),
    "B": ("979732417/256000000", "7654271/2000000"),
}
# escalation ladder: (label, depth, tscale, sscale).  The verifier picks the widest axis after
# scaling, so tscale 8 makes it split t eight times more eagerly -- which is where every witness
# lives.  Baseline is the setting the full-window pass used, so a PASS at S0 would mean the
# sliver was only ever a budget artifact of the WIDE window.
LADDER = [("S0-baseline", 48, "2", "8"),
          ("S1-tsplit", 48, "8", "1"),
          ("S2-tsplit-deep", 64, "8", "1"),
          ("S3-deep", 80, "16", "1")]


def sliver_witnesses(covrec):
    """Which slivers does this node's coverage record leave open?"""
    out = []
    for k, (lo, hi) in SLIVERS.items():
        a, b = float(F(lo)), float(F(hi))
        for u in (covrec or {}).get("unproven", []):
            if u[0] < b - 1e-12 and u[1] > a + 1e-12:
                out.append(k)
                break
    return out


def collect():
    """(node id, param cert path, open slivers) from A95's completed FAILs and A96's own."""
    jobs = {}
    for src, pat in ((os.path.join(BASE, "..", "A95-a57-shortcuts", "results", "t1_param.jsonl"), A95),
                     (os.path.join(OUT, "param96.jsonl"), None)):
        if not os.path.exists(src):
            continue
        for ln in open(src):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if r.get("verdict") != "FAIL" or not r.get("search_complete"):
                continue
            sl = sliver_witnesses(r.get("coverage"))
            if not sl:
                continue
            if pat:
                pj = os.path.join(pat, r["id"] + ".param.json")
            else:
                pj = os.path.join(BASE, "certs", "param", r["cls"], r["id"] + ".param.json")
            if os.path.exists(pj):
                jobs[(r["id"], pj)] = dict(id=r["id"], cert=pj, slivers=sl,
                                           cls=r.get("cls", "k5_11_G1"),
                                           fixed_wall_s=r.get("fixed_wall_s"),
                                           full_window_wall_s=r.get("param_wall_s"),
                                           unproven=r.get("coverage", {}).get("unproven"))
    return list(jobs.values())


def run(cert, lo, hi, depth, tscale, sscale, tag, env, cap):
    rp = os.path.join(BASE, "certs", "sliver", f"{os.path.basename(cert)[:-11]}.{tag}.report.json")
    os.makedirs(os.path.dirname(rp), exist_ok=True)
    cmd = [sys.executable, VP, cert, "--slo", lo, "--shi", hi, "--depth", str(depth),
           "--tscale", tscale, "--sscale", sscale, "--jobs", "1", "--strict-margin", "0",
           "--report", rp, "--max-witnesses", "20", "--max-witnesses-per-box", "1", "--quiet"]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=cap)
        rc = p.returncode
    except subprocess.TimeoutExpired:
        rc = None
    wall = round(time.time() - t0, 1)
    boxes = None
    if rc is not None and os.path.exists(rp):
        try:
            boxes = json.load(open(rp))["stats"]["boxes"]
        except Exception:
            pass
    return dict(strategy=tag, depth=depth, tscale=tscale, sscale=sscale,
                verdict=("TIMEOUT" if rc is None else
                         {0: "PASS", 1: "FAIL", 2: "MALFORMED"}.get(rc, f"rc={rc}")),
                wall_s=wall, boxes=boxes, report=rp)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nodes", default="")
    ap.add_argument("--cap", type=float, default=900.0)
    a = ap.parse_args()
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
               MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
    jobs = collect()
    if a.nodes:
        want = set(a.nodes.split(","))
        jobs = [j for j in jobs if j["id"] in want]
    res = os.path.join(OUT, "sliver96.jsonl")
    done = set()
    if os.path.exists(res):
        for ln in open(res):
            try:
                r = json.loads(ln)
                done.add((r["id"], r["sliver"]))
            except Exception:
                pass
    print(f"{len(jobs)} node(s) with open slivers", flush=True)
    for j in jobs:
        for k in j["slivers"]:
            if (j["id"], k) in done:
                continue
            lo, hi = SLIVERS[k]
            rec = dict(id=j["id"], cls=j["cls"], sliver=k, slo=lo, shi=hi,
                       fixed_wall_s=j["fixed_wall_s"],
                       full_window_wall_s=j["full_window_wall_s"], attempts=[])
            for tag, d, ts, ss in LADDER:
                r = run(j["cert"], lo, hi, d, ts, ss, f"{k}.{tag}", env, a.cap)
                rec["attempts"].append(r)
                print(f"  {j['id']:26s} sliver {k} {tag:15s} -> {r['verdict']:8s} "
                      f"{r['wall_s']:7.1f}s boxes={r['boxes']}", flush=True)
                if r["verdict"] == "PASS":
                    break
            ok = [r for r in rec["attempts"] if r["verdict"] == "PASS"]
            rec["closed"] = bool(ok)
            rec["closing_strategy"] = ok[0]["strategy"] if ok else None
            rec["reverify_wall_s"] = round(sum(r["wall_s"] for r in rec["attempts"]), 1)
            with open(res, "a") as fh:
                fh.write(json.dumps(rec) + "\n")
    print("sliver96 done", flush=True)


if __name__ == "__main__":
    main()
