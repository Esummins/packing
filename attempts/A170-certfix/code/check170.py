"""A170 -- the 100 % INDEPENDENT check on every recovered PASS.

Three checks, none of them sharing code with `exactcore.exact_a` (the bisection that CHOSE the
half-side) or with the frozen verifier's own core-exemption path:

  C1  CORE CONTAINMENT, re-derived from scratch.  For every core the recovered certificate carries,
      the four corners of the square `(kx, ky, tm, a)` are tested DIRECTLY with A132's
      `polycore.vertex_ok(vx, vy, box, t_lo(th0), t_hi(th1))` -- the two exact rational quadratics in
      `t = tan(theta/2)` over the four corners of the centre rectangle.  This is the proof obligation
      the enlargement rests on, checked on the WRITTEN rationals rather than on the ones `exact_a`
      returned.  A159/A156 tripwire 1 in the same form: no core half-side may reach 1/2.

  C2  THE MEASURE, exactly.  `sum(weights)` is recomputed in `Fraction` from the written strings and
      must equal the written `total` and be `< budget`; every weight must be > 0; the atom count must
      match; and `budget == 11 - #cores` (the claim's own arithmetic).

  C3  A DEEPER FROZEN REPLAY.  The frozen `verify_case.py` is run again at bisection depth 64
      (against depth 56 in the recert pass) with a different `--jobs`, so the PASS is not an artefact
      of the split schedule.  Same byte-identical verifier, asserted by sha256.

    python code/check170.py
"""
import json
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, ".."))
sys.path.insert(0, HERE)
for _p in (os.path.join(ATT, "A57-shadow-trees", "code"),
           os.path.join(ATT, "A132-polygon-core", "code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import certwrap170 as W                                        # noqa: E402
from caselp import Box, cos_sin_t, t_lo, t_hi                  # noqa: E402  READ-ONLY (A57)
import polycore                                                # noqa: E402  READ-ONLY (A132)

HALF = Fr(1, 2)


def c1_cores(cert):
    """EXACT containment of every written core in every pose of its own box, from scratch."""
    rows = []
    for i, cj in enumerate((cert.get("hypotheses", {}) or {}).get("cores") or []):
        kx, ky, tm, a = Fr(cj["kx"]), Fr(cj["ky"]), Fr(cj["tm"]), Fr(cj["a"])
        b = W.box_from_core_json(cj)
        if b is None:
            rows.append(dict(i=i, ok=False, why="no box"))
            continue
        cm, sm = cos_sin_t(tm)
        t0, t1 = t_lo(b.th0), t_hi(b.th1)
        corners = [(kx + a * (p * cm - q * sm), ky + a * (p * sm + q * cm))
                   for p, q in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
        ok = all(polycore.vertex_ok(vx, vy, b, t0, t1) for vx, vy in corners)
        rows.append(dict(i=i, ok=bool(ok and 0 < a < HALF), a=str(a), a_lt_half=bool(a < HALF),
                         vertex_ok=bool(ok)))
    return rows


def c2_measure(cert):
    W_ = [Fr(w) for w in cert["weights"]]
    tot = sum(W_, Fr(0))
    budget = cert["budget"]
    ncores = len(((cert.get("hypotheses", {}) or {}).get("cores") or []))
    return dict(total_matches=bool(tot == Fr(cert["total"])),
                total_lt_budget=bool(tot < budget),
                all_weights_pos=all(w > 0 for w in W_),
                n_atoms_matches=bool(len(cert["atoms"]) == len(W_)),
                budget_is_11_minus_cores=bool(budget == 11 - ncores),
                total=str(tot), budget=budget, ncores=ncores)


def main():
    W.assert_frozen()
    summ = json.load(open(os.path.join(BASE, "results", "summary170.json"), encoding="utf-8"))
    out = []
    nbad = 0
    for r in summ["passes"]:
        p = os.path.join(ROOT, r["cert"])
        cert = json.load(open(p, encoding="utf-8"))
        c1 = c1_cores(cert)
        c2 = c2_measure(cert)
        rc, txt = W.run_frozen_verifier(p, jobs=2, depth=64, timeout=1800.0)
        tail = W.verifier_tail(txt)
        c3 = "PASS" if rc == 0 else ("TIMEOUT" if rc is None else "FAIL")
        ok = (all(x["ok"] for x in c1) and all(v for k, v in c2.items()
                                               if isinstance(v, bool)) and c3 == "PASS")
        nbad += (0 if ok else 1)
        out.append(dict(id=r["id"], cert=r["cert"], C1=c1, C2=c2, C3=c3,
                        C3_verifier=tail[:2], all_ok=bool(ok)))
        print("%-58s C1 %s  C2 %s  C3(depth 64) %-5s  %s"
              % (r["id"], "OK" if all(x["ok"] for x in c1) else "BAD",
                 "OK" if all(v for k, v in c2.items() if isinstance(v, bool)) else "BAD",
                 c3, "ALL OK" if ok else "*** FAILED ***"), flush=True)
    json.dump(dict(n=len(out), n_bad=nbad, verifier_sha=W.FROZEN_SHA, depth=64, rows=out),
              open(os.path.join(BASE, "results", "check170.json"), "w"), indent=1)
    print("\n%d of %d recovered PASSes clear all three independent checks"
          % (len(out) - nbad, len(out)))
    return 1 if nbad else 0


if __name__ == "__main__":
    sys.exit(main())
