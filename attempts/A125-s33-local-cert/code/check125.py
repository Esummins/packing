"""A125 -- run A119's INDEPENDENT checker on A125's certificates.

A119's `check_local.py` is imported and used UNMODIFIED (`Checker`, `load`, `sha256_of`): the
decision path is entirely its own -- exact dyadic-rational interval arithmetic (`exactiv.Fx`),
its own re-derivation of every Lemma RELAX row, no numpy, no scipy, no generator code.  Only the
report is different: `check_local.main` writes into attempts/A119-local-cert-lean/results, which
this attempt is READ-ONLY on, so the loop is repeated here and the report is written to
attempts/A125-s33-local-cert/results/check_local.json instead.

    python check125.py ../certs/*.cert.json.gz
"""
from __future__ import annotations
import json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
A119C = os.path.abspath(os.path.join(HERE, "..", "..", "A119-local-cert-lean", "code"))
sys.path.insert(0, A119C)
import check_local as CL  # noqa: E402  (A119's checker, imported unmodified)

RES = os.path.abspath(os.path.join(HERE, "..", "results"))
LOGS = os.path.abspath(os.path.join(HERE, "..", "logs"))
for d in (RES, LOGS):
    os.makedirs(d, exist_ok=True)


def main(paths):
    sys.setrecursionlimit(400000)
    logp = os.path.join(LOGS, "check_local.log")

    def log(s):
        print(s, flush=True)
        with open(logp, "a", encoding="utf-8") as f:
            f.write(time.strftime("[%H:%M:%S] ") + s + "\n")

    res = os.path.join(RES, "check_local.json")
    prev = []
    if os.path.exists(res):
        try:
            d = json.load(open(res, encoding="utf-8"))
            prev = d.get("runs", [])
        except Exception:
            prev = []
    out = list(prev)
    ok_all = True
    for p in paths:
        t0 = time.time()
        cert = CL.load(p)
        C = CL.Checker(cert)
        ok = C.walk(cert["root"], C.root_cells(), {}, {}, {})
        wall = time.time() - t0
        rec = dict(file=os.path.basename(p), id=cert["meta"]["id"], ok=bool(ok),
                   checker="attempts/A119-local-cert-lean/code/check_local.py (imported unmodified)",
                   sha256=CL.sha256_of(p), seconds=round(wall, 1), bytes=os.path.getsize(p),
                   counts=dict(C.n),
                   certified_min=(None if C.min_bound is None else float(C.min_bound)),
                   s0=float(CL.S0), errors=C.errors[:5],
                   when=time.strftime("%Y-%m-%dT%H:%M:%S"))
        out = [q for q in out if q["id"] != rec["id"]] + [rec]
        with open(res, "w", encoding="utf-8") as f:
            json.dump(dict(when=time.strftime("%Y-%m-%dT%H:%M:%S"), runs=out), f, indent=1)
        log("%-28s %s  cells(bisect) %-7d branch %-5d imp %-6d dead-leaves %-7d rows %-9d "
            "min bound %.9f  %.0f s  %s"
            % (rec["id"], "VALID  " if ok else "INVALID", C.n["bisect"], C.n["branch"],
               C.n["imp"] + C.n["imp_sel"] + C.n["infeas"], C.n["dead"], C.n["rows"],
               rec["certified_min"] if rec["certified_min"] is not None else float("nan"),
               wall, "" if ok else C.errors[:1]))
        ok_all = ok_all and ok
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
