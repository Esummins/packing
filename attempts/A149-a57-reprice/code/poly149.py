"""A149 -- the K'-pruned (polygon-core) arm, on named A57 nodes.

The coordinator's priority node `k5_11_interior_Y0130` (A145: 7 of its 10 support columns are
K'-only impossible, weight 3.5; A148 page #7, green area 0.004).  This attempt's ordinary
exact-core arm already ran it: **tau 5.500000 -> 4.99999999999996**, i.e. the exact square cores
take eta from +0.500 to -4e-14 and stall EXACTLY at the budget, which is the S01 signature.  Going
below the budget needs the polygon core itself, not its inscribed square.

That arm exists and is A135's: `emitpoly135.certify_poly` puts A132's certified polygon `K'(B)` on
the CONDITIONED box as a `polycores` entry (the pins keep their exact SQUARE core, which for a
zero-tilt box already IS their whole polygon core), uses the same objects in the LP row filter and
in the certificate, and certifies with `verify_case_v3.py`.  It is imported UNCHANGED and called
directly, so nothing under A135 is written: the certificate directory and the results file are
this attempt's.

Order of attempts per node, and it matters for what may be claimed:
  1. the FROZEN `verify_case.py` on the exact-square-core certificate  -- already run, NO-KILL;
  2. this arm, whose certificate carries `polycores` and whose arbiter is `verify_case_v3`.
A kill from (2) is a **v3 kill** and is recorded in the SEPARATE v3 ledger, never mixed with the
frozen-verifier rows: the brief allows v3 only where the frozen verifier fails, and a v3 kill
carries A135's outstanding Lean obligation with it.
"""
import argparse
import json
import os
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
A135 = os.path.join(ROOT, "A135-polycore-verifier", "code")
A57R = os.path.join(ROOT, "A57-shadow-trees", "results")
A145 = os.path.join(ROOT, "A145-impossible-weight", "results", "impossible_weight.jsonl")
if A135 not in sys.path:
    sys.path.insert(0, A135)


def box_of(nid):
    """the node's recorded centre box, from A145's measurement file or the corpus itself."""
    if os.path.exists(A145):
        for ln in open(A145, encoding="utf-8"):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if r.get("id") == nid and r.get("box"):
                return r["box"], r.get("budget", 5), r
    import glob
    for p in glob.glob(os.path.join(A57R, "tree_*.jsonl")):
        for ln in open(p, encoding="utf-8"):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if r.get("id") == nid and r.get("box"):
                return r["box"], r.get("budget", 5), r
    raise SystemExit("no recorded box for " + nid)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", nargs="+", required=True)
    ap.add_argument("--cap", type=float, default=900.0)
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--warm_rows", type=int, default=9000)
    ap.add_argument("--fine", type=int, default=1)
    ap.add_argument("--max_v", type=int, default=None)
    ap.add_argument("--scale_cap", type=float, default=1.03)
    ap.add_argument("--out", default=os.path.join(BASE, "results", "poly149.jsonl"))
    a = ap.parse_args()

    import emitpoly135                                                   # noqa: E402
    outdir = os.path.join(BASE, "certs", "poly")
    os.makedirs(outdir, exist_ok=True)

    def log(*x):
        print(*x, flush=True)

    for nid in a.ids:
        box, budget, rec0 = box_of(nid)
        log("[%s/poly] box %s budget %s; recorded tau %s eta %s; A145 poly-only columns "
            "%s of %s carrying weight %s" % (nid, json.dumps(box), budget, rec0.get("tau_rec"),
                                             rec0.get("eta_rec"), rec0.get("n_poly_only"),
                                             rec0.get("n_support"), rec0.get("w_poly_only")))
        t0 = time.time()
        try:
            rec = emitpoly135.certify_poly(nid, box, budget, a.cap, a.rounds, a.jobs, a.depth,
                                           a.warm_rows, bool(a.fine), a.scale_cap, outdir, log,
                                           a.max_v)
        except Exception as e:
            rec = dict(id=nid, scope="poly", result="ERROR", error=repr(e)[:400],
                       tb=traceback.format_exc()[-1500:])
            log("[%s/poly] ERROR %r" % (nid, e))
        rec["wall_s"] = round(time.time() - t0, 1)
        rec["attempt"] = "A149"
        rec["arbiter"] = "verify_case_v3.py (A135) -- polycores clause; NOT the frozen verifier"
        rec["tau_recorded_before"] = rec0.get("tau_rec")
        rec["eta_recorded_before"] = rec0.get("eta_rec")
        rec["when"] = time.strftime("%F %T")
        with open(a.out, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")
        log("[%s/poly] %s tau=%s in %s s" % (nid, rec.get("result"), rec.get("tau"),
                                             rec["wall_s"]))


if __name__ == "__main__":
    main()
