"""A166 -- does the `make_certificate` stock-core reversion explain OTHER attempts' certificate FAILs?

`certfix166.py` established the mechanism on A166's own kill.  This script tests it on A150's FAILed
certificates WITHOUT touching A150: it READS a certificate, recomputes A135's exact core from the BOX
the certificate itself carries, writes the patched copy under `attempts/A166-.../certs/` and runs the
FROZEN `verify_case.py` on it.

Only A150's own nodes are considered (`q_*`, `r_*`).  The `l1_104_spread_*` certificates in the same
directory were written today by the LIVE A165 cascade and are left strictly alone.

A PASS here means the node was ALREADY LP-dead and its "certificate pending" status was an artefact of
the emission path, not of the LP.

    python code/certaudit166.py
"""
import argparse
import glob
import json
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
sys.path.insert(0, HERE)

import geo166 as G                                              # noqa: E402
import lp166 as L                                               # noqa: E402
from caselp import Box                                          # noqa: E402  READ-ONLY (A57)

RES = os.path.join(BASE, "results")
CERTS = os.path.join(BASE, "certs")
A150 = os.path.join(ATT, "A150-four-corner-product", "certs")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=A150)
    ap.add_argument("--prefixes", default="q_,r_")
    a = ap.parse_args()
    pref = tuple(a.prefixes.split(","))
    out = []
    for f in sorted(glob.glob(os.path.join(a.dir, "*.certify.json"))):
        base = os.path.basename(f)[:-len(".certify.json")]
        if not base.startswith(pref):
            continue
        d = json.load(open(f, encoding="utf-8"))
        if d.get("result") != "FAIL":
            continue
        cp = os.path.join(a.dir, base + ".json")
        if not os.path.exists(cp):
            continue
        cert = json.load(open(cp, encoding="utf-8"))
        cc = cert.get("hypotheses", {}).get("cores") or []
        if not cc or any("box" not in c for c in cc):
            print("%-34s no boxes in the certificate -- skipped" % base)
            continue
        ok = True
        rows = []
        for c in cc:
            b = Box(**{k: c["box"][k] for k in ("x0", "x1", "y0", "y1", "th0", "th1")})
            try:
                e = G.exact_core(b)
            except Exception as ex:                              # noqa: BLE001
                ok = False
                rows.append(dict(error=repr(ex)[:120]))
                break
            rows.append(dict(carried_a=c["a"], exact_a=str(e.a),
                             ratio=float(e.a) / float(Fr(c["a"]))))
            c["a"], c["kx"], c["ky"], c["tm"] = str(e.a), str(e.kx), str(e.ky), str(e.tm)
        if not ok:
            print("%-34s exact core failed -- skipped (%s)" % (base, rows[-1]))
            continue
        cert.setdefault("provenance", {})["a166_note"] = (
            "A166 audit: cores substituted with A135 exact_a cores recomputed from the boxes the "
            "certificate carries; caselp.make_certificate reverts to Hyp.from_json's stock b.core()")
        q = os.path.join(CERTS, "a150audit_" + base + "_exactcore.json")
        json.dump(cert, open(q, "w"), indent=0)
        rc, txt = L.run_verifier(q, jobs=2, depth=56)
        tail = [l for l in txt.splitlines() if l.startswith(("PASS", "FAIL", "boxes", "MALFORMED"))]
        res = "PASS" if rc == 0 else "FAIL"
        out.append(dict(node=base, src=os.path.relpath(cp, os.path.dirname(ATT)).replace("\\", "/"),
                        was="FAIL", now=res, cores=rows, total=cert.get("total"),
                        budget=cert.get("budget"), verifier=tail[:3],
                        patched=os.path.basename(q)))
        print("%-34s was FAIL -> %s   (core ratios %s) | %s"
              % (base, res, ["%.4f" % r["ratio"] for r in rows],
                 (tail[-1][:120] if tail else "")), flush=True)
    json.dump(dict(dir=a.dir, verifier_sha=L.VERIFIER_SHA, rows=out),
              open(os.path.join(RES, "certaudit166.json"), "w"), indent=1)
    n = sum(1 for r in out if r["now"] == "PASS")
    print("%d of %d previously-FAILing A150 certificates PASS once the exact cores are carried"
          % (n, len(out)), flush=True)


if __name__ == "__main__":
    main()
