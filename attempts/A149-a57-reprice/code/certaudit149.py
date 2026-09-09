"""A149 -- audit every certificate THIS attempt wrote for A166's stock-core reversion.

A166's finding: the `ExactHyp` pattern replaces `Hyp.cores` with A135's exact cores, so the LP
drops the right rows -- but `caselp.make_certificate` rebuilds the hypothesis with
`Hyp.from_json`, which recomputes each core with `Box.core()` and so writes the STOCK core into
the certificate.  The written measure then under-exempts by an annulus and the frozen verifier
reports spurious holes.

A149's lanes never call `caselp.make_certificate`.  Both node paths emit through A135's
`emit135.make_cert`, which takes the cores from the LIVE `Hyp` object -- that function exists for
exactly this reason and says so in its docstring.  This script MEASURES that rather than asserting
it: for every certificate under `certs/`, recompute `exactcore.exact_core` from the box the
certificate itself carries and compare with the carried `a`.

  carried == exact                -> clean (the exact core was written)
  carried == Box.core()  < exact  -> the A166 reversion (would need re-certifying)

Read-only.  Writes one report under this attempt.
"""
import glob
import json
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
for _p in (os.path.join(ROOT, "A57-shadow-trees", "code"),
           os.path.join(ROOT, "A132-polygon-core", "code"),
           os.path.join(ROOT, "A135-polycore-verifier", "code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from caselp import Box                                                   # noqa: E402
import exactcore                                                        # noqa: E402

OUT = os.path.join(BASE, "results", "certaudit149.json")


def main():
    rows, clean, reverted, unknown = [], 0, 0, 0
    worst = 0.0
    for p in sorted(glob.glob(os.path.join(BASE, "certs", "**", "*.json"), recursive=True)):
        b = os.path.basename(p)
        if b.endswith((".witnesses.json", ".report.json", ".certify.json", ".resolve.json")) \
                or ".resolve" in b:
            continue
        try:
            d = json.load(open(p))
        except Exception:
            continue
        cs = (d.get("hypotheses") or {}).get("cores")
        if not cs:
            continue
        verdicts = []
        for i, c in enumerate(cs):
            if not c.get("box"):
                verdicts.append("no-box")
                continue
            box = Box.from_json(c["box"])
            try:
                e = exactcore.exact_core(box)
                stock = box.core()
            except Exception:
                verdicts.append("exact-core-failed")
                continue
            carried = Fr(c["a"])
            if carried == e.a:
                verdicts.append("exact")
            elif stock is not None and carried == stock.a:
                verdicts.append("STOCK")
                worst = max(worst, float((e.a - carried) / e.a))
            else:
                verdicts.append("other:%.9f_vs_exact_%.9f" % (float(carried), float(e.a)))
        st = ("reverted" if any(v == "STOCK" for v in verdicts)
              else "clean" if all(v == "exact" for v in verdicts) else "unknown")
        rows.append(dict(cert=os.path.relpath(p, BASE), status=st, per_box=verdicts))
        clean += st == "clean"
        reverted += st == "reverted"
        unknown += st == "unknown"
    out = dict(attempt="A149", n_certificates=len(rows), clean=clean, reverted=reverted,
               unknown=unknown, worst_relative_shortfall=worst, rows=rows,
               finding="A149's two node paths (A137 node137 -> A135 emit135.certify, and this "
                       "attempt's node_a60) both emit through A135's make_cert, which reads the "
                       "LIVE Hyp; caselp.make_certificate is never called, so A166's stock-core "
                       "reversion cannot arise here.  This file measures it.")
    json.dump(out, open(OUT, "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    for r in rows:
        if r["status"] != "clean":
            print("  %-50s %s %s" % (r["cert"], r["status"], r["per_box"]))


if __name__ == "__main__":
    main()
