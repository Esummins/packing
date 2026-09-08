"""A135 -- the v3 regression: on a certificate with no `polycores` field, `verify_case_v3.py` must
be the FROZEN `verify_case.py`, verdict and box-tree statistics both.

This is A117/A96's discipline for v2 ("the corpus was re-run under v2 to check that every
v1-passing certificate still passes; the new clause only ADDS exemptions"), applied to the third
disjunct.  v3 imports the frozen module rather than copying it, so the only way the two can differ
on a `polycores`-free certificate is the one added `if` -- which this measures rather than asserts.

Reads existing certificates read-only; writes only results/regress135.json.
"""
import argparse
import glob
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
FROZEN = os.path.join(ROOT, "A57-shadow-trees", "code", "verify_case.py")
V3 = os.path.join(HERE, "verify_case_v3.py")

KEYS = ("boxes", "covered", "vacuous", "exempt", "exempt_core", "exempt_nofam", "split",
        "exact_atom_checks", "max_depth", "witnesses")


def run(script, cert, depth, tmp_report):
    # --witness-file is MANDATORY here: without it a FAILing certificate makes the verifier write
    # <cert>.witnesses.json NEXT TO THE CERTIFICATE, i.e. into another attempt's certs directory.
    # A135 is read-only on every campaign; found the hard way on
    # attempts/A57-shadow-trees/certs/k5_11.witnesses.json (restored from git, tracked tree clean).
    cmd = [sys.executable, script, cert, "--jobs", "1", "--depth", str(depth),
           "--max-witnesses", "4", "--report", tmp_report, "--quiet",
           "--witness-file", os.path.join(BASE, "results", "_regress_witnesses.json")]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    st = {}
    if os.path.exists(tmp_report):
        try:
            st = json.load(open(tmp_report)).get("stats", {})
        except Exception:
            st = {}
    return p.returncode, st, round(time.time() - t0, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--depth", type=int, default=48)
    ap.add_argument("--glob", nargs="+", default=None)
    a = ap.parse_args()
    pats = a.glob or [
        os.path.join(ROOT, "A57-shadow-trees", "certs", "*.json"),
        os.path.join(ROOT, "A96-a57-parametric", "certs", "block96", "*.json"),
        os.path.join(BASE, "certs", "*__ex*.json"),
    ]
    cands = []
    for p in pats:
        for f in sorted(glob.glob(p)):
            b = os.path.basename(f)
            if b.endswith((".report.json", ".witnesses.json", ".certify.json", ".resolve.json",
                           ".param.json", ".replay.report.json")):
                continue
            try:
                d = json.load(open(f))
            except Exception:
                continue
            if d.get("format") != "case-measure-certificate-v1":
                continue
            if (d.get("hypotheses") or {}).get("polycores"):
                continue
            cands.append(f)
    cands = cands[:a.limit]
    print(f"{len(cands)} polycores-free certificates to regress", flush=True)
    rows, bad = [], 0
    tmp0 = os.path.join(BASE, "results", "_regress_v1.json")
    tmp3 = os.path.join(BASE, "results", "_regress_v3.json")
    for f in cands:
        for t in (tmp0, tmp3):
            if os.path.exists(t):
                os.remove(t)
        rc0, st0, w0 = run(FROZEN, f, a.depth, tmp0)
        rc3, st3, w3 = run(V3, f, a.depth, tmp3)
        diff = {k: (st0.get(k), st3.get(k)) for k in KEYS if st0.get(k) != st3.get(k)}
        ok = (rc0 == rc3) and not diff
        if not ok:
            bad += 1
        rows.append(dict(cert=os.path.relpath(f, ROOT), rc_v1=rc0, rc_v3=rc3, identical=ok,
                         diff=diff, wall_v1=w0, wall_v3=w3,
                         exempt_poly=st3.get("exempt_poly")))
        print(f"{'OK ' if ok else 'DIFF'} rc {rc0}/{rc3} {w0}s/{w3}s  {os.path.basename(f)}"
              + ("" if ok else f"  {diff}"), flush=True)
    out = os.path.join(BASE, "results", "regress135.json")
    json.dump(dict(n=len(rows), identical=len(rows) - bad, differing=bad, depth=a.depth,
                   rows=rows), open(out, "w"), indent=1)
    print(f"\n{len(rows) - bad}/{len(rows)} identical (verdict AND box-tree statistics); "
          f"{bad} differing.  -> {out}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
