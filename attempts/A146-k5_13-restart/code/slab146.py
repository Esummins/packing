#!/usr/bin/env python3
"""
slab146.py -- A146 track 2: does A114's SLAB-WIDTH LAW size k5_13's failing window?

No LP, no new certificate.  The frozen A56 verifier
(`attempts/A56-sparametric/code/verify_param.py`) is run on the EXISTING A56 parametric
certificate `attempts/A56-sparametric/certs/k5_13.param.json` (106 atoms, margin 0.037449) over
narrow sub-windows.  A56's own run covered the whole window in ONE slab of width 0.057084 and
FAILed depth-limited (max_depth 48, max_s_depth 10, worst witness `undecided`, 0 holes) -- the
signature docs/budget.md section E calls "a slab over its width_max", never node hardness.

The law (docs/budget.md section E, A114's k6_07 log):

    a slab passes iff  log2(width / w_min) + d_pose <= 48,
    and from ONE PASSING probe slab:  w_min = width / 2^(max s-depth),
                                      d_pose = max depth - max s-depth,
                                      width_max = w_min * 2^(48 - d_pose).

Soundness of a slab sweep: each PASSing slab is a sound partial transfer (P3), and a union of
closed sub-windows covering [S_LO, S0] is the A86 T4 WindowRows disjunction -- exactly the
mechanism A114 used for k5_02/k5_03/k6_07/k6_23/k6_27.  Every slab endpoint is checked against
the verifier's integer grid BEFORE anything is launched (verify_param builds D = 250000 <<
(depth+2) and REFUSES an endpoint whose denominator does not divide it: A114 lost a 30-slab grid
to that, every slab "FAIL" in 0.3 s).

Writes only under attempts/A146-k5_13-restart/.  RESUMABLE: results/slab146.json is rewritten
after every slab; a re-launch skips every slab that already has a result.

Usage:
  python slab146.py probe                     # width ladder at the bottom of the window
  python slab146.py sweep --width 1/2000      # cover [S_LO, S0] in slabs of that width
"""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse                                                        # noqa: E402
import json                                                            # noqa: E402
import subprocess                                                      # noqa: E402
import sys                                                             # noqa: E402
import time                                                            # noqa: E402
from fractions import Fraction as F                                    # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
A146 = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(A146, ".."))
A56 = os.path.join(ATT, "A56-sparametric")
VP = os.path.join(A56, "code", "verify_param.py")
SPEC = os.path.join(A56, "code", "specialize.py")
VC = os.path.join(ATT, "A53-simple-strata", "code", "verify_case.py")
CERT = os.path.join(A56, "certs", "k5_13.param.json")

CERTS = os.path.join(A146, "certs")
RESULTS = os.path.join(A146, "results")
LOGS = os.path.join(A146, "logs")
for _d in (CERTS, RESULTS, LOGS):
    os.makedirs(_d, exist_ok=True)

S_LO, S0 = F(191, 50), F(969271, 250000)
WIDTH = S0 - S_LO
S_DEN = 250000
RC = {0: "PASS", 1: "FAIL", 2: "MALFORMED", 124: "TIMEOUT"}
REC = os.path.join(RESULTS, "slab146.json")
LOG = os.path.join(LOGS, "slab146.log")


def L(*x):
    with open(LOG, "a", encoding="utf-8") as fh:
        print(*x, file=fh, flush=True)
    print(*x, flush=True)


def save(rec):
    tmp = REC + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=1)
    os.replace(tmp, REC)


def load():
    if os.path.exists(REC):
        try:
            return json.load(open(REC))
        except Exception:
            pass
    return {"attempt": "A146", "class": "k5_13", "cert": CERT, "law": "docs/budget.md section E",
            "slabs": {}}


def on_grid(q, depth):
    return ((S_DEN << (depth + 2)) % q.denominator) == 0


def sh(cmd, timeout=None):
    t0 = time.time()
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write("\n$ " + " ".join(str(c) for c in cmd) + "\n")
        fh.flush()
        try:
            rc = subprocess.run([str(c) for c in cmd], stdout=fh, stderr=subprocess.STDOUT,
                                timeout=timeout,
                                creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS).returncode
        except subprocess.TimeoutExpired:
            fh.write(f"*** TIMEOUT after {timeout}s\n")
            rc = 124
    return rc, time.time() - t0


def vparam(lo, hi, depth, tag, timeout, sscale="8", jobs=1, maxw=200, perbox=8):
    rep = os.path.join(CERTS, f"{tag}.report.json")
    wit = os.path.join(CERTS, f"{tag}.wit.json")
    rc, dt = sh([sys.executable, VP, CERT, "--slo", str(lo), "--shi", str(hi),
                 "--depth", str(depth), "--sscale", sscale, "--jobs", str(jobs), "--split", "3",
                 "--strict-margin", "0", "--report", rep, "--witness-file", wit,
                 "--max-witnesses", str(maxw), "--max-witnesses-per-box", str(perbox),
                 "--quiet"], timeout=timeout)
    r = {"slo": str(lo), "shi": str(hi), "slo_f": float(lo), "shi_f": float(hi),
         "width": float(hi - lo), "depth": depth, "sscale": sscale, "jobs": jobs,
         "seconds": round(dt, 1), "result": RC.get(rc, rc), "report": rep}
    if os.path.exists(rep):
        try:
            d = json.load(open(rep))
            r["stats"] = {q: d.get("stats", {}).get(q) for q in
                          ("boxes", "covered", "exempt", "vacuous", "split", "s_splits",
                           "s_cells", "max_depth", "max_s_depth", "witnesses")}
            r["witness_s_range"] = d.get("witness_s_range")
        except Exception:
            pass
    if rc == 0 and r.get("stats", {}).get("max_s_depth") is not None:
        sd = r["stats"]["max_s_depth"]
        md = r["stats"]["max_depth"]
        w_min = float(hi - lo) / (2.0 ** sd)
        d_pose = md - sd
        r["law"] = {"w_min": w_min, "d_pose": d_pose,
                    "width_max": w_min * (2.0 ** (48 - d_pose))}
    if rc == 1 and os.path.exists(wit):
        try:
            W = json.load(open(wit))["witnesses"]
            r["n_witnesses"] = len(W)
            r["search_complete"] = len(W) < maxw
            r["holes"] = sum(1 for w in W if w.get("kind") == "hole")
            r["kinds"] = sorted({w.get("kind") for w in W})
        except Exception:
            pass
    return rc, r


def stage(rec, tag, fn):
    if tag in rec["slabs"] and rec["slabs"][tag].get("result") is not None:
        L(f"    [skip] {tag} -> {rec['slabs'][tag]['result']}")
        return rec["slabs"][tag]
    rc, r = fn()
    rec["slabs"][tag] = r
    save(rec)
    law = r.get("law")
    L(f"    {tag} [{r['slo_f']:.6f},{r['shi_f']:.6f}] w={r['width']:.6g} -> {r['result']} "
      f"{r['seconds']}s" + (f"  w_min={law['w_min']:.3g} d_pose={law['d_pose']} "
                            f"width_max={law['width_max']:.4g}" if law else ""))
    return r


def cmd_probe(a):
    rec = load()
    rec["mode"] = "probe"
    save(rec)
    # a width ladder at the BOTTOM of the window (cheapest end, docs/budget.md section E's cost
    # profile), each endpoint a multiple of 1/250000 so it is on the verifier's grid.
    for units in a.units:
        lo, hi = S_LO, S_LO + F(units, S_DEN)
        if hi > S0:
            continue
        for q in (lo, hi):
            if not on_grid(q, a.depth):
                raise SystemExit(f"endpoint {q} not on the grid at depth {a.depth}")
        r = stage(rec, f"probe.u{units}",
                  lambda lo=lo, hi=hi, u=units: vparam(lo, hi, a.depth, f"probe.u{u}",
                                                       a.timeout, jobs=a.jobs))
        if r["result"] == "PASS":
            rec["probe_pass"] = r
            save(rec)
            L(f"    PROBE PASSES at width {r['width']:.6g}: "
              f"width_max = {r['law']['width_max']:.6g}")
            return 0
    rec["probe_pass"] = None
    save(rec)
    L("    no probe slab passed in the ladder")
    return 1


def slab(rec, lo, hi, a, tag, depth_left, covered, failed):
    """Verify [lo, hi]; on FAIL/TIMEOUT halve it and recurse (A56 sub-window bisection, A114's
    mechanism).  A FAIL here is a RESOLUTION verdict about the slab, not about the node: the
    width law says a slab over width_max exhausts the (t, cx, cy) depth budget before the
    s-axis is cut finely enough.  Only a `hole` witness would be a statement about the node,
    and that is recorded explicitly."""
    r = stage(rec, tag, lambda: vparam(lo, hi, a.depth, tag, a.timeout, jobs=a.jobs))
    if r["result"] == "PASS":
        covered.append([str(lo), str(hi)])
        return True
    if r.get("holes"):
        L(f"    *** {tag}: {r['holes']} HOLE witness(es) -- this is NOT a resolution artefact")
        failed.append([str(lo), str(hi), "holes"])
        return False
    mid = (lo + hi) / 2
    if depth_left <= 0 or not on_grid(mid, a.depth):
        failed.append([str(lo), str(hi), r["result"]])
        return False
    L(f"    bisecting {tag} ({r['result']}) at {float(mid):.7f}")
    ok1 = slab(rec, lo, mid, a, tag + "a", depth_left - 1, covered, failed)
    ok2 = slab(rec, mid, hi, a, tag + "b", depth_left - 1, covered, failed)
    return ok1 and ok2


def cmd_sweep(a):
    rec = load()
    rec["mode"] = "sweep"
    w = F(a.width)
    n = -((-WIDTH) // w)                                  # ceil(WIDTH / w), exact on Fractions
    edges = [S_LO + i * w for i in range(int(n))] + [S0]
    edges = sorted({min(e, S0) for e in edges})
    for e in edges:
        if not on_grid(e, a.depth):
            raise SystemExit(f"slab endpoint {e} not on the verifier's grid at depth {a.depth}")
    rec["sweep"] = {"width": str(w), "n_slabs": len(edges) - 1, "depth": a.depth,
                    "bisect_levels": a.bisect}
    save(rec)
    L(f"=== sweep: {len(edges) - 1} slabs of width {float(w):.6g} over "
      f"[{float(S_LO):.6f},{float(S0):.6f}] at depth {a.depth}, "
      f"<= {a.bisect} bisection levels per failing slab")
    t0 = time.time()
    covered, failed = [], []
    for i in range(len(edges) - 1):
        lo, hi = edges[i], edges[i + 1]
        if hi <= lo:
            continue
        tag = f"sweep.w{a.width.replace('/', '_')}.s{i:03d}"
        slab(rec, lo, hi, a, tag, a.bisect, covered, failed)
        rec["sweep"]["covered"] = merge_str(covered)
        rec["sweep"]["failed"] = failed
        rec["sweep"]["coverage"] = round(
            sum(float(F(y) - F(x)) for x, y in rec["sweep"]["covered"]) / float(WIDTH), 6)
        rec["sweep"]["seconds"] = round(time.time() - t0, 1)
        save(rec)
        if time.time() - t0 > a.budget:
            L(f"    *** slab budget {a.budget}s reached; stopping (NOT a verdict)")
            rec["sweep"]["stopped"] = "budget"
            rec["sweep"]["reached"] = str(hi)
            save(rec)
            break
    L(f"=== sweep coverage {rec['sweep'].get('coverage')} in "
      f"{rec['sweep'].get('seconds')}s; failed {failed}")
    return 0 if not failed and rec["sweep"].get("coverage") == 1.0 else 1


def merge_str(pairs):
    iv = []
    for a_, b_ in sorted((F(x), F(y)) for x, y in pairs):
        if iv and a_ <= iv[-1][1]:
            iv[-1][1] = max(iv[-1][1], b_)
        else:
            iv.append([a_, b_])
    return [[str(x), str(y)] for x, y in iv]


def cmd_c2(a):
    """canary C2: the UNMODIFIED A53 verify_case.py on the specialisation at lo/mid/hi."""
    rec = load()
    out = []
    for lbl, s in (("lo", S_LO), ("mid", (S_LO + S0) / 2), ("hi", S0)):
        sp = os.path.join(CERTS, f"c2.{lbl}.json")
        rp = os.path.join(CERTS, f"c2.{lbl}.report.json")
        rc, _ = sh([sys.executable, SPEC, CERT, "--s", str(s), "-o", sp])
        if rc != 0:
            out.append({"s": str(s), "result": "SPECIALIZE_ERROR"})
            break
        rc, dt = sh([sys.executable, VC, sp, "--depth", str(a.depth), "--jobs", str(a.jobs),
                     "--report", rp, "--max-witnesses", "20", "--quiet"], timeout=2400)
        out.append({"s": str(s), "s_float": float(s), "time_s": round(dt, 1),
                    "result": RC.get(rc, rc)})
        L(f"    c2 {lbl} s={float(s):.6f} -> {out[-1]['result']} {out[-1]['time_s']}s")
        if rc != 0:
            break
    rec["c2"] = out
    save(rec)
    return 0 if all(x.get("result") == "PASS" for x in out) else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("probe")
    p.add_argument("--units", type=int, nargs="+", default=[50, 12, 4, 1],
                   help="slab widths in units of 1/250000")
    p.add_argument("--depth", type=int, default=48)
    p.add_argument("--jobs", type=int, default=1)
    p.add_argument("--timeout", type=float, default=900.0)
    p.set_defaults(fn=cmd_probe)
    p = sub.add_parser("sweep")
    p.add_argument("--width", default="1/2000")
    p.add_argument("--depth", type=int, default=48)
    p.add_argument("--jobs", type=int, default=1)
    p.add_argument("--timeout", type=float, default=1500.0)
    p.add_argument("--budget", type=float, default=5400.0)
    p.add_argument("--bisect", type=int, default=3)
    p.set_defaults(fn=cmd_sweep)
    p = sub.add_parser("c2")
    p.add_argument("--depth", type=int, default=44)
    p.add_argument("--jobs", type=int, default=1)
    p.set_defaults(fn=cmd_c2)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    raise SystemExit(main())
