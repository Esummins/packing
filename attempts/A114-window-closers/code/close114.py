#!/usr/bin/env python3
"""
close114.py -- A114: close the cheap window fragments and stragglers of docs/residue_ledger.md
section 2 (the A56 scoreboard's PARTIAL/OPEN rows) with banked machinery only.

Two mechanisms, no new mathematics:

  (R) THE RESOLVER (A96 step 3c, attempts/A96-a57-parametric/code/resolve96.py).  A 4-D FAIL is
      usually an s-RESOLUTION artifact, not node hardness: verify_param splits the widest axis of
      a 4-D cell, so on the full window the (t, cx, cy) depth budget is exhausted before the
      s-axis is cut finely enough at the one or two places where the measure is tight.  Restrict
      the window to those places and the SAME certificate passes in seconds.  Soundness: the FAIL
      run DISCHARGED every placement whose s lies outside the union of the witness cells'
      s-intervals (every box containing such a placement was decided), so the window splits as
      the A86 T4 WindowRows disjunction -- a finite union of closed sub-windows.  This is sound
      ONLY if the witness set is COMPLETE (A56 soundness.md P6(iv)); every enumeration pass here
      therefore runs at --jobs 1 with an effectively unbounded per-box cap and records
      `search_complete` = (n_witnesses < --max-witnesses), and NOTHING is claimed when it is
      false.

  (B) SUB-WINDOW BISECTION (A56 pass 3, code/bisect_subwindow.py).  Halve the open band and run
      the frozen verifier on each half; every PASSing slab is a sound partial transfer (P3), and
      the residue is handed to (R).

Frozen verifiers, byte for byte: A56 code/verify_param.py (sha256 recorded in every record file;
identical to A96's copy), A56 code/specialize.py, and the UNMODIFIED A53 code/verify_case.py for
the C2 canary.  This script never edits them and never writes outside attempts/A114-window-closers
(the scoreboard is written by update_scoreboard114.py, once, atomically).

RESUMABLE.  Every stage writes results/<class>.json before and after it runs; a re-launch skips
every stage that already has a verdict.  Kill it whenever.

DISCIPLINE.  <= 2 processes; BLAS pinned to one thread; before every verifier launch, free COMMIT
> 6144 MB and free PHYSICAL > 3 GB (two consecutive readings, 60 s apart).

Usage:
  python close114.py resolve --name k6_23 --band 3877/1000,969271/250000
  python close114.py resolve --name k5_02            # full window, resolver-first
  python close114.py band    --name k6_07 --band 956767/250000,969271/250000
"""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse                                                        # noqa: E402
import ctypes                                                          # noqa: E402
import hashlib                                                         # noqa: E402
import json                                                            # noqa: E402
import subprocess                                                      # noqa: E402
import sys                                                             # noqa: E402
import time                                                            # noqa: E402
from fractions import Fraction as F                                    # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
A114 = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(A114, ".."))
A56 = os.path.join(ATT, "A56-sparametric")
A56C = os.path.join(A56, "code")
VP = os.path.join(A56C, "verify_param.py")
SPEC = os.path.join(A56C, "specialize.py")
VC = os.path.join(ATT, "A53-simple-strata", "code", "verify_case.py")

CERTS = os.path.join(A114, "certs")
RESULTS = os.path.join(A114, "results")
LOGS = os.path.join(A114, "logs")
for _d in (CERTS, RESULTS, LOGS):
    os.makedirs(_d, exist_ok=True)

S_LO, S0 = F(191, 50), F(969271, 250000)
WIDTH = float(S0 - S_LO)
DIR = CERTS                      # per-class artefact directory, set by the sub-command
MIN_FREE_COMMIT_MB = 6144.0
MIN_FREE_PHYS_MB = 3072.0
RC = {0: "PASS", 1: "FAIL", 2: "MALFORMED", 124: "TIMEOUT"}


# ---------------------------------------------------------------- box gates (A109 crowd92)
class _MS(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def mem():
    m = _MS()
    m.dwLength = ctypes.sizeof(_MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ullAvailPageFile / 1048576.0, m.ullAvailPhys / 1048576.0


def gate(tag, need=2, deadline=None):
    """proceed only after `need` consecutive readings with free commit > 6144 MB AND free
    physical > 3 GB."""
    ok, n = 0, 0
    while True:
        c, p = mem()
        good = c > MIN_FREE_COMMIT_MB and p > MIN_FREE_PHYS_MB
        ok = ok + 1 if good else 0
        if ok >= need:
            return {"free_commit_mb": round(c), "free_phys_mb": round(p), "waits": n}
        if deadline is not None and time.time() > deadline:
            return None
        # two readings are required, so a healthy box waits only for the second one
        wait = 5 if good else 60
        if not good:
            print(f"  [gate] commit {c:.0f} MB / phys {p:.0f} MB below the gate "
                  f"({MIN_FREE_COMMIT_MB:.0f} / {MIN_FREE_PHYS_MB:.0f}); sleep {wait} s ({tag})",
                  flush=True)
            n += 1
        time.sleep(wait)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None


# ---------------------------------------------------------------- record (resumable)
def load(name):
    p = os.path.join(RESULTS, f"{name}.json")
    if os.path.exists(p):
        try:
            return json.load(open(p))
        except Exception:
            pass
    return None


def save(rec):
    p = os.path.join(RESULTS, f"{rec['class']}.json")
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=1)
    os.replace(tmp, p)


def stage(rec, key, fn):
    """run fn() once; the result is cached in the record file, so a relaunch skips it."""
    st = rec["stages"].get(key)
    if st is not None and st.get("done"):
        print(f"  [resume] {key}: {st.get('result')} (cached)", flush=True)
        return st
    rec["stages"][key] = {"started": time.strftime("%Y-%m-%dT%H:%M:%S"), "done": False}
    save(rec)
    out = fn()
    out["done"] = True
    out["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    rec["stages"][key] = out
    rec["wall_s"] = round(rec.get("wall_s", 0.0) + float(out.get("seconds") or 0.0), 1)
    save(rec)
    return out


# ---------------------------------------------------------------- the frozen verifier
def sh(cmd, log, timeout=None):
    t0 = time.time()
    with open(log, "a", encoding="utf-8") as fh:
        fh.write("\n$ " + " ".join(str(c) for c in cmd) + "\n")
        fh.flush()
        try:
            rc = subprocess.run([str(c) for c in cmd], stdout=fh, stderr=subprocess.STDOUT,
                                timeout=timeout).returncode
        except subprocess.TimeoutExpired:
            fh.write(f"*** TIMEOUT after {timeout}s\n")
            rc = 124
    return rc, time.time() - t0


def vparam(cert, lo, hi, depth, tag, log, timeout, sscale="8", maxw=2000, perbox=10 ** 6,
           jobs=1):
    """the frozen A56/A96 verify_param on [lo, hi].  jobs=1 and an unbounded per-box cap: the
    search then terminates ONLY by exhaustion or by --max-witnesses, so `search_complete` below
    is exact (A56 soundness.md P6(iv) without its heuristic)."""
    g = gate(tag)
    rep = os.path.join(DIR, f"{tag}.report.json")
    wit = os.path.join(DIR, f"{tag}.wit.json")
    rc, dt = sh([sys.executable, VP, cert, "--slo", str(lo), "--shi", str(hi),
                 "--depth", str(depth), "--sscale", sscale, "--jobs", str(jobs), "--split", "3",
                 "--strict-margin", "0", "--report", rep, "--witness-file", wit,
                 "--max-witnesses", str(maxw), "--max-witnesses-per-box", str(perbox),
                 "--quiet"], log, timeout=timeout)
    r = {"slo": str(lo), "shi": str(hi), "slo_f": float(lo), "shi_f": float(hi), "depth": depth,
         "sscale": sscale, "jobs": jobs, "max_witnesses": maxw, "seconds": round(dt, 1),
         "result": RC.get(rc, rc), "report": rep, "gate": g}
    if os.path.exists(rep):
        try:
            d = json.load(open(rep))
            r["stats"] = {q: d.get("stats", {}).get(q) for q in
                          ("boxes", "covered", "exempt", "vacuous", "s_splits", "s_cells",
                           "max_depth", "max_s_depth", "witnesses")}
            r["witness_s_range"] = d.get("witness_s_range")
        except Exception:
            pass
    if rc == 1 and os.path.exists(wit):
        W = json.load(open(wit))["witnesses"]
        r["n_witnesses"] = len(W)
        r["search_complete"] = len(W) < maxw
        r["witness_file"] = wit
        r["holes"] = sum(1 for w in W if w.get("kind") == "hole")
        r["gaps"] = [[str(a), str(b)] for a, b in merge([(F(w["box"]["s"][0]), F(w["box"]["s"][1]))
                                                         for w in W if "box" in w])]
    return rc, r


S_DEN = 250000


def on_grid(q, depth):
    """verify_param builds one integer grid with D = 250000 << (depth+2) and REFUSES an s
    endpoint whose denominator does not divide D (verify_param.py: "s endpoint ... not on the
    grid").  Denominators must be 2^a * 5^b with b <= 6.  Checked before anything is launched:
    a refused endpoint makes the verifier exit non-zero, which the sweep would otherwise record
    as a FAIL verdict -- A114 lost a 30-slab grid to exactly that (every slab "FAIL" in 0.3 s)."""
    return ((S_DEN << (depth + 2)) % q.denominator) == 0


def check_grid(points, depths, where):
    bad = [(str(q), d) for q in points for d in depths if not on_grid(q, d)]
    if bad:
        raise SystemExit(f"{where}: s endpoint(s) not on the verifier's grid (denominator must "
                         f"be 2^a * 5^b with b <= 6): {bad[:6]}")


def merge(iv):
    out = []
    for a, b in sorted(iv):
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return [(a, b) for a, b in out]


def c2(name, cert, lo, hi, log, tag, depth="44", timeout=2400):
    """canary C2: the UNMODIFIED A53 verify_case.py on the specialisations at lo, mid, hi.

    The depth is the canary's own budget, not part of the claim: a depth-limited `undecided`
    (0 holes) means the canary ran out of subdivision, NOT that the certificate is wrong.  The
    A56 convention is depth 44; k6_23 -- the 501-atom certificate whose parametric run needed
    depth 56 -- needs the canary at the same depth to decide (recorded per class)."""
    out = []
    for lbl, s in (("lo", lo), ("mid", (lo + hi) / 2), ("hi", hi)):
        gate(f"c2 {tag} {lbl}")
        sp = os.path.join(DIR, f"{tag}.c2.{lbl}.json")
        rp = os.path.join(DIR, f"{tag}.c2.{lbl}.report.json")
        rc, _ = sh([sys.executable, SPEC, cert, "--s", str(s), "-o", sp], log)
        if rc != 0:
            out.append({"s": str(s), "result": "SPECIALIZE_ERROR"})
            break
        rc, dt = sh([sys.executable, VC, sp, "--depth", depth, "--jobs", "1", "--report", rp,
                     "--max-witnesses", "20", "--quiet"], log, timeout=timeout)
        e = {"s": str(s), "s_float": float(s), "time_s": round(dt, 1), "depth": depth,
             "result": RC.get(rc, rc)}
        if rc == 1 and os.path.exists(rp):
            try:
                d = json.load(open(rp))
                W = d.get("witnesses_preview") or []
                e["n_witnesses"] = d.get("stats", {}).get("witnesses")
                e["holes"] = sum(1 for w in W if w.get("kind") == "hole")
                e["kinds"] = sorted({w.get("kind") for w in W})
            except Exception:
                pass
        out.append(e)
        if rc != 0:
            break
    return out


# ---------------------------------------------------------------- the resolver
def resolver(rec, cert, band, log, a, prefix):
    """(R): enumerate the EXACT uncovered s-intervals of [lo, hi], then re-verify the SAME
    certificate on each one, bisecting a sub-window that still fails.  Returns
    (closed: bool, rows, residual)."""
    lo, hi = band
    tag = f"{prefix}.enum"
    if getattr(a, "gaps_from", None):
        # DIAGNOSTIC MODE (the brief's "resolver first" step): take the cells out of an EXISTING
        # witness file.  Those files were written at --jobs 3 --max-witnesses 20 and are
        # TRUNCATED, so closing them proves nothing about the window -- it answers the cheap
        # question "is this failure the verifier starving the s-axis, or is it node hardness?"
        # A full-window claim needs the complete enumeration pass (no --gaps_from).
        W = json.load(open(a.gaps_from))["witnesses"]
        r = {"result": "FAIL", "seconds": 0.0, "search_complete": False, "diagnostic": True,
             "witness_file": a.gaps_from, "n_witnesses": len(W),
             "gaps": [[str(x), str(y)] for x, y in
                      merge([(F(w["box"]["s"][0]), F(w["box"]["s"][1])) for w in W
                             if "box" in w])]}
        rec["stages"][tag] = dict(r, done=True)
        save(rec)
    else:
        r = stage(rec, tag, lambda: vparam(cert, lo, hi, a.depth, tag, log, a.enum_timeout,
                                           sscale=a.sscale, maxw=a.max_witnesses)[1])
    if r.get("diagnostic"):
        rows, residual = [], []
        for i, (x, y) in enumerate(r["gaps"], 1):
            t = f"{prefix}.cell{i}"
            rr = stage(rec, t, lambda x=x, y=y, t=t: vparam(
                cert, F(x), F(y), a.gap_depth, t, log, a.gap_timeout, sscale="1",
                maxw=a.max_witnesses)[1])
            (rows if rr["result"] == "PASS" else residual).append(
                [x, y, float(F(x)), float(F(y)), rr["result"], rr["seconds"]])
        return False, rows, residual
    if r["result"] == "PASS":
        return True, [[str(lo), str(hi), float(lo), float(hi), r["seconds"]]], []
    if r["result"] != "FAIL" or not r.get("search_complete"):
        return False, [], [[str(lo), str(hi), float(lo), float(hi),
                            f"enumeration {r['result']}"
                            + ("" if r.get("search_complete", True) else " (TRUNCATED)")]]
    rows, residual = [], []
    stack = [(F(g[0]), F(g[1]), 0) for g in r["gaps"]]
    n = 0
    while stack:
        glo, ghi, d = stack.pop(0)
        n += 1
        t = f"{prefix}.g{n}"
        rr = stage(rec, t, lambda glo=glo, ghi=ghi, t=t: vparam(
            cert, glo, ghi, a.gap_depth, t, log, a.gap_timeout, sscale="1",
            maxw=a.max_witnesses)[1])
        if rr["result"] == "PASS":
            rows.append([str(glo), str(ghi), float(glo), float(ghi), rr["seconds"]])
        elif d < a.max_bisect:
            m = (glo + ghi) / 2
            stack.append((glo, m, d + 1))
            stack.append((m, ghi, d + 1))
        else:
            residual.append([str(glo), str(ghi), float(glo), float(ghi), rr["result"]])
    if not residual:
        rows = [[str(lo), str(hi), float(lo), float(hi), None]]
    return (not residual), rows, residual


def cmd_resolve(a):
    global DIR
    name = a.name
    DIR = os.path.join(CERTS, name)
    os.makedirs(DIR, exist_ok=True)
    cert = a.cert or os.path.join(A56, "certs", f"{name}.param.json")
    band = tuple(F(x) for x in a.band.split(",")) if a.band else (S_LO, S0)
    log = os.path.join(LOGS, f"{name}.log")
    rec = load(name) or {
        "class": name, "attempt": "A114", "mechanism": "resolver (A96 step 3c) on the A56 "
        "parametric certificate: enumerate the EXACT uncovered s-intervals at jobs=1 with an "
        "unbounded per-box witness cap, then re-verify the SAME certificate on each one",
        "band": [str(band[0]), str(band[1])], "band_float": [float(band[0]), float(band[1])],
        "cert": cert, "cert_sha256": sha(cert), "verifier": VP, "verifier_sha256": sha(VP),
        "verify_case": VC, "verify_case_sha256": sha(VC),
        "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "stages": {}, "wall_s": 0.0}
    rec["stages"] = rec.get("stages", {})
    check_grid(list(band), [a.depth, a.gap_depth], "resolve")
    save(rec)

    closed, rows, residual = resolver(rec, cert, band, log, a, "R")
    rec["rows"] = rows
    rec["residual"] = residual
    if closed:
        ck = f"c2.band.d{a.c2_depth}"
        rec["c2"] = stage(rec, ck, lambda: {"result": "done",
                                            "c2": c2(name, cert, band[0], band[1], log, ck,
                                                     depth=str(a.c2_depth))})["c2"]
        good = all(x.get("result") == "PASS" for x in rec["c2"])
        rec["verdict"] = ("A114 CLOSES the band" if good else "C2-DISCREPANCY")
        rec["gained"] = [[str(band[0]), str(band[1])]] if good else []
    elif rec["stages"].get("R.enum", {}).get("diagnostic"):
        # the cells came from a TRUNCATED witness file: each PASS is a sound partial transfer,
        # but the complement is NOT certified, so the row's window claim does not move here.
        rec["diagnostic"] = True
        rec["cells_before"] = rec["stages"]["R.enum"]["gaps"]
        rec["cells_pass"] = [[r[0], r[1]] for r in rows]
        rec["cells_still_open"] = [[r[0], r[1]] for r in residual]
        rec["gained"] = []
        rec["verdict"] = (
            f"DIAGNOSTIC: {len(rows)}/{len(rows) + len(residual)} recorded 4-D witness cells "
            f"close with the SAME certificate"
            + ("; the failure is the verifier starving the s-axis, so a complete enumeration "
               "pass is worth paying for" if not residual else
               "; at least one cell is genuinely hard, so this is node hardness, not resolution"))
    else:
        rec["verdict"] = "still open"
        rec["gained"] = [[r[0], r[1]] for r in rows] if rows else []
    rec["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save(rec)
    print(f"{name}: {rec['verdict']} ({rec['wall_s']}s)", flush=True)
    return 0 if closed else 1


# ---------------------------------------------------------------- bisection + resolver
def cmd_band(a):
    """(B) then (R): halve the open band, bank every PASSing slab, hand the residue to the
    resolver."""
    global DIR
    name = a.name
    DIR = os.path.join(CERTS, name)
    os.makedirs(DIR, exist_ok=True)
    cert = a.cert or os.path.join(A56, "certs", f"{name}.param.json")
    lo, hi = (F(x) for x in a.band.split(","))
    log = os.path.join(LOGS, f"{name}.log")
    rec = load(name) or {
        "class": name, "attempt": "A114",
        "mechanism": "A56 sub-window bisection of the open band with the frozen parametric "
                     "certificate, then the A96 resolver on every residual slab",
        "band": [str(lo), str(hi)], "band_float": [float(lo), float(hi)],
        "cert": cert, "cert_sha256": sha(cert), "verifier": VP, "verifier_sha256": sha(VP),
        "verify_case": VC, "verify_case_sha256": sha(VC),
        "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "stages": {}, "wall_s": 0.0}
    rec["stages"] = rec.get("stages", {})
    rec["band"] = [str(lo), str(hi)]
    rec["band_float"] = [float(lo), float(hi)]
    rec["mechanism_band"] = ("A56 sub-window bisection of [%s, %s] with the frozen parametric "
                             "certificate (every slab PASS is a sound partial transfer and needs "
                             "no witness completeness), then the A96 resolver on the residue"
                             % (lo, hi))
    save(rec)

    # --cuts: explicit slab boundaries.  A cut point is a HINT (it may come from a truncated
    # witness file); it can only cost time, never soundness -- every PASS is on a closed
    # sub-window, and whatever does not pass is handed on.
    edges = [lo] + sorted(F(x) for x in a.cuts.split(",") if x.strip()) + [hi] if a.cuts \
        else [lo, hi]
    check_grid(edges, [int(x) for x in a.depths.split(",")] + [a.gap_depth], "band")
    # A previously banked range STAYS banked: a slab PASS is a standing fact about the
    # certificate, independent of the grid that produced it.
    gained = [(F(x), F(y)) for x, y in (rec.get("gained") or [])]
    # Rebuild the banked set from the stage cache as well: EVERY cached PASS is a standing
    # partial transfer, whichever grid produced it, so a record that was killed mid-sweep (or
    # whose grid was replaced) keeps everything its verifier runs earned.
    for k, st in rec["stages"].items():
        if st.get("done") and st.get("result") == "PASS" and st.get("slo") and st.get("shi"):
            gained.append((F(st["slo"]), F(st["shi"])))
    gained = list(merge(gained))
    open_slabs = []
    slabs = [(edges[i], edges[i + 1], 0) for i in range(len(edges) - 1)]
    n = 0
    while slabs:
        s0_, s1_, d = slabs.pop(0)
        n += 1
        if any(x <= s0_ and s1_ <= y for x, y in gained):
            print(f"  slab {n} [{float(s0_):.6f}, {float(s1_):.6f}]: already banked", flush=True)
            continue
        got = False
        for depth in [int(x) for x in a.depths.split(",")]:
            t = f"{a.tag_prefix}.s{n}_d{depth}"
            # a stage key does not encode its window, so a cached entry is only reusable when
            # its recorded bounds are the ones being asked about (A114 hit this when k6_07's
            # band was re-gridded: B.s3 meant a different slab in each grid)
            old = rec["stages"].get(t)
            if old and (old.get("slo") != str(s0_) or old.get("shi") != str(s1_)):
                rec["stages"]["OLDGRID_%s_%s_%s" % (t, old.get("slo_f"), old.get("shi_f"))] = \
                    rec["stages"].pop(t)
                save(rec)
            # a bisection slab only needs its EXIT CODE, so the witness cap is small: a full
            # enumeration on a wide slab that is going to fail anyway is pure cost (measured:
            # > 20 min on k6_07's 0.05-wide band at depth 48, vs 87 s for A56's capped probe)
            r = stage(rec, t, lambda s0_=s0_, s1_=s1_, depth=depth, t=t: vparam(
                cert, s0_, s1_, depth, t, log, a.slab_timeout, sscale=a.sscale,
                maxw=a.slab_maxw, perbox=8, jobs=a.slab_jobs)[1])
            print(f"  slab {n} [{float(s0_):.6f}, {float(s1_):.6f}] depth {depth}: "
                  f"{r['result']} ({r['seconds']}s)", flush=True)
            if r["result"] == "PASS":
                gained.append((s0_, s1_))
                got = True
                break
        if not got:
            if d < a.max_bisect:
                m = (s0_ + s1_) / 2
                slabs.append((s0_, m, d + 1))
                slabs.append((m, s1_, d + 1))
            else:
                open_slabs.append((s0_, s1_))
        # persist after EVERY slab, pass or fail: a killed sweep must not lose the ranges it
        # banked (A114 killed k5_03's sweep after ten PASSes and the record still showed only
        # the pre-sweep range, because the success branch used to `continue` past this save)
        rec["gained"] = [[str(x), str(y)] for x, y in merge(gained)]
        rec["still_open"] = [[str(x), str(y)] for x, y in open_slabs]
        save(rec)

    # resolver on every slab bisection could not close
    for i, (s0_, s1_) in enumerate(list(open_slabs)):
        closed, rows, residual = resolver(rec, cert, (s0_, s1_), log, a,
                                          f"{a.tag_prefix}R{i}")
        if closed:
            gained.append((s0_, s1_))
            open_slabs.remove((s0_, s1_))
        rec.setdefault("resolver", []).append(
            {"slab": [str(s0_), str(s1_)], "closed": closed, "rows": rows, "residual": residual})
        rec["gained"] = [[str(x), str(y)] for x, y in merge(gained)]
        rec["still_open"] = [[str(x), str(y)] for x, y in open_slabs]
        save(rec)

    g = merge(gained)
    rec["gained"] = [[str(x), str(y)] for x, y in g]
    rec["still_open"] = [[str(x), str(y)] for x, y in merge(open_slabs)]
    rec["band_width_closed"] = round(sum(float(y - x) for x, y in g), 9)
    rec["c2"] = []
    for i, (x, y) in enumerate(g):
        ck = f"c2.{float(x):.6f}_{float(y):.6f}.d{a.c2_depth}"
        rec["c2"] += stage(rec, ck, lambda x=x, y=y, ck=ck: {
            "result": "done",
            "c2": c2(name, cert, x, y, log, ck, depth=str(a.c2_depth))})["c2"]
        save(rec)
    if g and not all(x.get("result") == "PASS" for x in rec["c2"]):
        rec["verdict"] = "C2-DISCREPANCY"
        save(rec)
        return 1
    rec["verdict"] = ("A114 CLOSES the band" if not rec["still_open"] else
                      f"band partially closed (+{rec['band_width_closed']:.6f} of s)")
    rec["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save(rec)
    print(f"{name}: {rec['verdict']} ({rec['wall_s']}s)", flush=True)
    return 0 if not rec["still_open"] else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for nm in ("resolve", "band"):
        p = sub.add_parser(nm)
        p.add_argument("--name", required=True)
        p.add_argument("--cert", default=None)
        p.add_argument("--band", default=None)
        p.add_argument("--depth", type=int, default=48, help="enumeration pass depth")
        p.add_argument("--gap_depth", type=int, default=56, help="gap re-verification depth")
        p.add_argument("--sscale", default="8")
        p.add_argument("--max_bisect", type=int, default=3)
        p.add_argument("--max_witnesses", type=int, default=2000)
        p.add_argument("--enum_timeout", type=float, default=2400)
        p.add_argument("--gap_timeout", type=float, default=600)
        p.add_argument("--slab_timeout", type=float, default=1800)
        p.add_argument("--depths", default="48,56")
        p.add_argument("--cuts", default=None,
                       help="explicit slab boundaries inside the band (exact rationals)")
        p.add_argument("--tag_prefix", default="B",
                       help="stage-key prefix for this sweep's slabs (use a fresh one when "
                            "re-gridding a band, so the two grids' caches cannot mix)")
        p.add_argument("--slab_jobs", type=int, default=1,
                       help="workers for a bisection slab; only its exit code is used, so >1 is "
                            "sound here (it is NOT for the enumeration pass -- see L1)")
        p.add_argument("--slab_maxw", type=int, default=8,
                       help="witness cap for a bisection slab (its exit code is all that is "
                            "used; the resolver's enumeration pass uses --max_witnesses)")
        p.add_argument("--gaps_from", default=None,
                       help="DIAGNOSTIC: take the cells from this existing witness file instead "
                            "of running a complete enumeration (see L1 in notes/lemmas.md)")
        p.add_argument("--c2_depth", type=int, default=44,
                       help="canary depth for the UNMODIFIED A53 verify_case.py (A56 uses 44; "
                            "a certificate whose parametric run needed depth 56 needs the "
                            "canary there too, or the canary reports depth-limited undecided)")
    a = ap.parse_args(argv)
    if a.cmd == "resolve":
        if not a.band:
            a.band = f"{S_LO},{S0}"
        return cmd_resolve(a)
    return cmd_band(a)


if __name__ == "__main__":
    sys.exit(main())
