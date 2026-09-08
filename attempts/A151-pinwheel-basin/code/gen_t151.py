"""A151 -- run A133's t = tan(theta/2) generator and its independent checker on an A151 spec,
with every WRITE redirected into this attempt.

    python gen_t151.py <cert id> [--time-cap 700] [--min-cell 1/5000] [--check]

A133's `gen_local_t.py` and `check_local_t.py` are IMPORTED unchanged (read-only); their
module-level `BASE` (which is A133's attempt directory, the destination of the emitted
`certs/<id>.tcert.json.gz`) is re-pointed at `attempts/A151-pinwheel-basin/` before anything runs,
so nothing under attempts/A133-* is written.  The source certificate is this attempt's own
A119-format meta file (`code/mk_a119_src.py`).
"""
from __future__ import annotations
import argparse, os, sys, types

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A133C = os.path.join(ROOT, "attempts", "A133-tan-half-emission", "code")
sys.path.insert(0, A133C)

import gen_local_t as GEN        # noqa: E402  (imported read-only)
GEN.BASE = BASE                  # every emit() write now lands in THIS attempt
GEN.A119CERT = os.path.join(BASE, "certs")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="+")
    ap.add_argument("--min-cell", default="1/5000")
    ap.add_argument("--cap", type=int, default=900000)
    ap.add_argument("--time-cap", type=float, default=700.0)
    ap.add_argument("--certdir", default=os.path.join(BASE, "certs"))
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    for cid in a.ids:
        GEN.run_one(cid, a)
    if a.check:
        # A133's check_local_t.main() writes its record into A133's results/ (a path derived from
        # its own __file__), so the Checker is driven directly here and the record is written HERE.
        import gzip, json, time
        import check_local_t as CHK      # noqa: E402  (imported read-only)
        out = []
        for cid in a.ids:
            p = os.path.join(BASE, "certs", cid + ".tcert.json.gz")
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
            out.append(rec)
            print("%-30s %s leaves %-6d rows %-7d implied %-7d min %s  %.1f s"
                  % (rec["id"], "VALID  " if ok else "INVALID(%d)" % len(C_.errors),
                     len(C_.leaves), C_.n["rows"], C_.n["rows_implied"],
                     ("%.9f" % rec["certified_min_float"]) if C_.min_bound is not None else "-",
                     rec["seconds"]))
            for e in C_.errors[:5]:
                print("    !", e)
        rp = os.path.join(BASE, "results", "check_local_t151.json")
        prev = json.load(open(rp, encoding="utf-8")).get("runs", []) if os.path.exists(rp) else []
        json.dump(dict(when=time.strftime("%Y-%m-%dT%H:%M:%S"), runs=out, previous=prev[:20]),
                  open(rp, "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
