"""A136 -- emit and check the ONE missing YES leaf, so the NO-COMPLETE node becomes a closure.

THE HOLE.  `results/no_complete136.jsonl` holds exactly one node, `k5_11_interior_Y0274`.  Its four
NO children are certified dead by the frozen `verify_case.py` with ZONE subset BOX on the written
rationals, but its YES leaf is A160 union entry 34,
`S02_k5_11_A160slice_a151B_f2+00.0_f3+40.0`, for which NO CERTIFICATE ARTEFACT EXISTS:
`attempts/A160-s02-f0-slide/certs/` is empty and `N_boxes160.json` carries only an in-run FLOAT
`tree_verdict` produced by the generator itself (entry151.A160_NO_CERTIFICATE).  A160's
`consumer160.json` puts Y0274 INSIDE only the SLICES union (slack +0.12722) and OUTSIDE A151-B
(-0.58751) and the CHAIN (-0.93248), so no already-certified box set can be cited instead -- the
certificate has to be emitted.

WHAT THIS DOES.  `attempts/A160-s02-f0-slide/code/gent160.py` is IMPORTED UNCHANGED (it in turn
imports A133's `gen_local_t.py` and `check_local_t.py` unchanged) and its write targets are
re-pointed into THIS attempt -- `gent160.CERTS`, `lib160.BASE`, `lib160.RES` -- exactly the way
gent160 itself re-points A133's, so nothing under `attempts/A160-*`, `attempts/A133-*` or
`attempts/A119-*` is written.  Then:

  1. the source meta is rebuilt from A160's own `results/slice160.jsonl` row (d2 = 0, d3 = 40),
  2. its bodies are asserted to be THE SAME BOXES, float for float, as `N_boxes160.json` entry 34 --
     the boxes the NO side was actually cut against.  A certificate for a DIFFERENT box set would
     not license the citation, so this check is fatal,
  3. A133's t-generator rebuilds the tree from scratch in exact rationals,
  4. A133's INDEPENDENT rational checker runs on the emitted `.tcert.json.gz`, and its exact
     rational `certified_min` is compared with s0 = 969271/250000 IN FRACTIONS.

Nothing is claimed unless the checker reports zero errors AND certified_min > s0 exactly.

    python yesleaf136.py --emit        # steps 1-4, writes certs_a160yes/ + results/yesleaf136.json
    python yesleaf136.py --adopt       # rewrite the Y0274 record's YES leaf and re-status it

READ-ONLY on every campaign and prior attempt.  PYTHONDONTWRITEBYTECODE=1.
"""
from __future__ import annotations

import argparse, gzip, json, os, sys, time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a136lib as A6                                               # noqa: E402

ROOT = A6.ROOT
NODE = "k5_11_interior_Y0274"
EID = "S02_k5_11_A160slice_a151B_f2+00.0_f3+40.0"
LINK = 34
S0 = Fr(969271, 250000)

A160 = os.path.join(ROOT, "attempts", "A160-s02-f0-slide")
SLICES = os.path.join(A160, "results", "slice160.jsonl")
NBOXES = os.path.join(A160, "results", "N_boxes160.json")
# gen_local_t writes its .tcert to <its BASE>/certs while gent160 looks for it in CERTS, so the
# two must agree: a dedicated sub-base whose certs/ IS the output dir keeps A160's and A133's
# BASE-relative writes and this attempt's NO-side certs/ apart.
YESBASE = os.path.join(A6.BASE, "yesleaf")
OUTCERT = os.path.join(YESBASE, "certs")
REPORT = os.path.join(A6.RES, "yesleaf136.json")


def entry34():
    with open(NBOXES, encoding="utf-8") as f:
        for e in json.load(f)["N"]:
            if e["id"] == EID:
                return e
    raise SystemExit("entry %s not in %s" % (EID, NBOXES))


def emit(time_cap, min_cell):
    os.makedirs(OUTCERT, exist_ok=True)
    sys.path.insert(0, os.path.join(A160, "code"))
    import lib160 as L                                             # noqa: E402
    import gent160 as G                                            # noqa: E402

    # every write target re-pointed into THIS attempt before main() runs
    L.BASE, L.RES, L.CERTS = YESBASE, A6.RES, OUTCERT
    G.CERTS = OUTCERT
    print("write targets re-pointed: gent160.CERTS=%s  lib160.BASE=%s  lib160.RES=%s"
          % (G.CERTS, L.BASE, L.RES))

    argv = ["gent160.py", "--from-slice", SLICES, "--slice-d2", "0.0", "--slice-d3", "40.0",
            "--id", EID, "--check", "--time-cap", str(time_cap), "--min-cell", min_cell]
    old = sys.argv
    sys.argv = argv
    t0 = time.time()
    try:
        G.main()
    finally:
        sys.argv = old
    print("gent160 done in %.0f s" % (time.time() - t0))


def check_only():
    """A133's check_local_t.py on the emitted .tcert, imported UNCHANGED, recording the same row
    gent160 --check records (into this attempt's results/check_local_t160.json)."""
    sys.path.insert(0, os.path.join(ROOT, "attempts", "A133-tan-half-emission", "code"))
    import check_local_t as CHK                                    # noqa: E402
    p = os.path.join(OUTCERT, EID + ".tcert.json.gz")
    t0 = time.time()
    with gzip.open(p, "rt", encoding="utf-8") as f:
        cert = json.load(f)
    C_ = CHK.Checker(cert)
    ok = C_.run()
    rec = dict(file=os.path.basename(p), id=cert["meta"]["id"], ok=bool(ok),
               sha256=CHK.sha256_of(p), seconds=round(time.time() - t0, 1),
               bytes=os.path.getsize(p), counts=dict(C_.n), n_leaves=len(C_.leaves),
               certified_min=(None if C_.min_bound is None else str(C_.min_bound)),
               certified_min_float=(None if C_.min_bound is None else float(C_.min_bound)),
               s0=float(CHK.S0), n_errors=len(C_.errors), errors=C_.errors[:5],
               checker="attempts/A133-tan-half-emission/code/check_local_t.py (imported)")
    print("%-44s %s leaves %-6d rows %-7d min %s  %.1f s"
          % (rec["id"], "VALID  " if ok else "INVALID(%d)" % len(C_.errors),
             len(C_.leaves), C_.n["rows"],
             ("%.10f" % rec["certified_min_float"]) if C_.min_bound is not None else "-",
             rec["seconds"]))
    rp = os.path.join(A6.RES, "check_local_t160.json")
    prev = json.load(open(rp, encoding="utf-8")).get("runs", []) if os.path.exists(rp) else []
    json.dump(dict(when=time.strftime("%Y-%m-%dT%H:%M:%S"), runs=[rec] + prev),
              open(rp, "w", encoding="utf-8"), indent=1)


def check_boxes():
    """The emitted source meta must carry EXACTLY the boxes of N_boxes160 entry 34."""
    src = os.path.join(OUTCERT, EID + ".cert.json.gz")
    if not os.path.exists(src):
        return dict(ok=False, errors=["not emitted yet: %s" % src], n_free=0, names=[])
    with gzip.open(src, "rt", encoding="utf-8") as f:
        meta = json.load(f)["meta"]
    import math
    want = {b["name"]: b for b in entry34()["boxes"]}
    got = {b["name"]: b for b in meta["bodies"] if b["kind"] == "free"}
    bad = []
    if set(want) - set(got):
        bad.append("free bodies missing from the emitted meta: %s" % sorted(set(want) - set(got)))
    for nm, w in want.items():
        g = got.get(nm)
        if g is None:
            continue
        for k, a, b in (("x0", w["cx"][0], g["x0"]), ("x1", w["cx"][1], g["x1"]),
                        ("y0", w["cy"][0], g["y0"]), ("y1", w["cy"][1], g["y1"]),
                        ("t0", math.radians(w["theta_deg"][0]), g["t0"]),
                        ("t1", math.radians(w["theta_deg"][1]), g["t1"])):
            if a != b:
                bad.append("%s.%s: entry34 %.17g != emitted %.17g" % (nm, k, a, b))
    return dict(ok=not bad, errors=bad, n_free=len(got), names=sorted(got))


def checker_run():
    """The LAST recorded run of A133's independent checker for this id (gent160 --check writes
    check_local_t160.json into the re-pointed RES = this attempt's results/)."""
    p = os.path.join(A6.RES, "check_local_t160.json")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        for r in json.load(f).get("runs", []):
            if r.get("id") == EID:
                return r
    return None


def verdict():
    box = check_boxes()
    run = checker_run()
    tcert = os.path.join(OUTCERT, EID + ".tcert.json.gz")
    ok_file = os.path.exists(tcert)
    cm = (run or {}).get("certified_min")
    margin = (Fr(cm) - S0) if cm else None
    ok = bool(ok_file and box["ok"] and run and run.get("ok")
              and not run.get("n_errors") and margin is not None and margin > 0)
    return dict(
        node=NODE, entry_id=EID, union_link=LINK, when=time.strftime("%Y-%m-%d %H:%M:%S"),
        citeable=ok,
        tcert=(os.path.relpath(tcert, ROOT).replace("\\", "/") if ok_file else None),
        sha256=(run or {}).get("sha256"),
        box_identity=box,
        checker=run,
        certified_min=cm, certified_min_float=(float(Fr(cm)) if cm else None),
        s0=str(S0), margin_over_s0=(str(margin) if margin is not None else None),
        margin_over_s0_float=(float(margin) if margin is not None else None),
        source=dict(generator="attempts/A160-s02-f0-slide/code/gent160.py (imported unchanged; "
                              "write targets re-pointed into attempts/A136-a120-resume)",
                    tgen="attempts/A133-tan-half-emission/code/gen_local_t.py (imported by gent160)",
                    checker="attempts/A133-tan-half-emission/code/check_local_t.py (imported)",
                    slice_row="attempts/A160-s02-f0-slide/results/slice160.jsonl  d2=0.0 d3=40.0",
                    boxes_compared_against="attempts/A160-s02-f0-slide/results/N_boxes160.json "
                                           "entry %d (%s)" % (LINK, EID)))


def adopt():
    v = verdict()
    if not v["citeable"]:
        raise SystemExit("NOT citeable -- refusing to adopt:\n" + json.dumps(v, indent=1)[:2000])
    rp = os.path.join(A6.RES, "nodes_a160", "rec__k5_11__%s.json" % NODE)
    rec = A6.jload(rp)
    if rec.get("status") != "NO-COMPLETE":
        print("record status is %r, not NO-COMPLETE -- nothing to adopt" % rec.get("status"))
        return 0
    st = rec.get("child_status") or []
    if not st or any(s != "DEAD-CERT" for s in st):
        raise SystemExit("NO side is not complete: %s" % st)
    cert = dict(
        id=EID, format="local-cert-t-v1",
        file=v["tcert"], sha256=v["sha256"], dead=True,
        status="CHECKED (A136 yesleaf136.py: emitted by A160 gent160 = A133 gen_local_t, verified "
               "by A133's INDEPENDENT rational checker check_local_t with %d errors; its EXACT "
               "certified minimum %s exceeds s0 %s by %s; the emitted bodies are float-for-float "
               "the boxes of N_boxes160.json entry %d, which is the box set the NO side was cut "
               "against)" % (v["checker"]["n_errors"], v["certified_min"], v["s0"],
                             v["margin_over_s0"], LINK),
        certified_min=v["certified_min"], margin_over_s0=v["margin_over_s0_float"],
        checker=v["checker"], boxes="A160 N_boxes160.json entry %d, re-emitted and checked" % LINK,
        supersedes=dict(status="PENDING-CERTIFICATE",
                        was=(rec.get("yes_leaf_pending") or {}),
                        why="the certificate that entry151.A160_NO_CERTIFICATE said was one "
                            "emission away now exists and has been independently checked"))
    rec.setdefault("a136", {})["yes_leaf_certificate"] = cert
    rec["yes_leaf_pending"] = None
    rec["yes_leaf_resolved_by"] = "attempts/A136-a120-resume/code/yesleaf136.py"
    rec["status"] = "CLOSED"
    rec["claim"] = ("A57 node %s: all %d NO children are certified dead by the frozen "
                    "verify_case.py with ZONE subset BOX on the written rationals, and the YES "
                    "leaf now cites the CHECKED local certificate %s.  CLOSED." % (NODE, len(st), EID))
    A6.jdump(rp, rec)
    print("adopted -- %s is now CLOSED (%s)" % (NODE, rp))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit", action="store_true")
    ap.add_argument("--check_only", action="store_true",
                    help="skip the (already done) generation and run A133's INDEPENDENT rational "
                         "checker on the emitted .tcert, recording the run exactly as gent160 "
                         "--check does")
    ap.add_argument("--adopt", action="store_true")
    ap.add_argument("--time-cap", type=float, default=1800.0)
    ap.add_argument("--min-cell", default="1/5000")
    a = ap.parse_args()
    if a.emit:
        emit(a.time_cap, a.min_cell)
    if a.check_only:
        check_only()
    v = verdict()
    A6.jdump(REPORT, v)
    print(json.dumps({k: v[k] for k in ("node", "entry_id", "citeable", "sha256", "certified_min",
                                        "s0", "margin_over_s0", "box_identity")}, indent=1)[:2000])
    print("->", REPORT)
    if a.adopt:
        return adopt()
    return 0


if __name__ == "__main__":
    sys.exit(main())
