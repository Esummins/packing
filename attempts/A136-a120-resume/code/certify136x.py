"""A136 -- `certify136.py` with A170's EXACT cores carried INSIDE the witness-feedback loop.

`certify136.py` splices A136's F-COVER `narrow` into A112's `certify.py` at emission.  This variant
splices A170's `carry_exact_cores` in FRONT of it, so every certificate the loop emits -- not just
the last one -- exempts A135's certified EXACT core rather than `caselp`'s stock core:

    caselp.make_certificate  ->  carry_exact_cores (A170, ENLARGE only)  ->  a136lib.narrow (A136)

Order matters and this is the only sound one.  `carry_exact_cores` only ever widens a core and only
when A135's exact vertex test passes with the same `(kx, ky, tm)`, which can only REMOVE
verification obligations; `narrow` then rewrites the NO zone inward and runs the decidable
`ZONE subset BOX` on the WRITTEN rationals and RAISES on failure, so the F-COVER property is still
established on the file that is actually written.  Neither step touches the LP.

WHY A SECOND EMISSION RATHER THAN A PATCH.  `exactcert136.py` patches an ALREADY-WRITTEN certificate
and re-runs only the frozen verifier -- free, and it recovered 2 of 16.  It cannot help a
certificate whose verdict is `total mass >= budget: certificate proves nothing`, because that is not
a coverage failure the cores can fix: the emitted MEASURE is short and only more witness-feedback
rounds build a bigger one.  This entry point exists for exactly that case, and it starts the loop
with the wider cores so each round has more room.

    python certify136x.py <node_json> --s_rat ... [every certify.py flag]

`certify.py`, `caselp.py`, `certwrap170.py` and the frozen `verify_case.py` are all IMPORTED, never
edited or copied.  PYTHONDONTWRITEBYTECODE=1.
"""
from __future__ import annotations

import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a136lib as A                                                # noqa: E402  (BLAS pin inside)

sys.path.insert(0, os.path.join(A.ROOT, "attempts", "A170-certfix", "code"))
import certwrap170 as W                                            # noqa: E402  READ-ONLY (A170)

sys.path.insert(0, A.A112C)
import certify                                                     # noqa: E402

W.assert_frozen()                                                  # byte-identical or refuse

_NODE = sys.argv[1]
_SIDE = _NODE + ".a136box.json"
if not os.path.exists(_SIDE):
    sys.stderr.write("a136x: no box sidecar %s -- refusing to emit an unchecked certificate\n"
                     % _SIDE)
    sys.exit(4)
_BOXES = json.load(open(_SIDE, encoding="utf-8"))["boxes"]
_ORIG = certify.make_certificate
_STATS = dict(rounds=0, applied=0, max_ratio=1.0)


def _patched(res, s_rat, scale=1.03, **kw):
    cert = _ORIG(res, s_rat, scale=scale, **kw)
    rep = W.carry_exact_cores(cert)                                # A170: ENLARGE ONLY
    _STATS["rounds"] += 1
    _STATS["applied"] += sum(1 for r in rep if r.get("applied"))
    _STATS["max_ratio"] = max([_STATS["max_ratio"]]
                              + [r.get("ratio") or 1.0 for r in rep])
    cert.setdefault("provenance", {})["a170_core_report"] = rep
    cert["provenance"]["a136x"] = (
        "cores enlarged to A135's exact vertex-certified core by A170 certwrap170."
        "carry_exact_cores BEFORE A136's F-COVER narrow; no LP change")
    out, _r = A.narrow(cert, res["hyp"]["nofams"], _BOXES, res["s"],
                       tag=os.path.basename(_NODE))
    return out


certify.make_certificate = _patched

if __name__ == "__main__":
    rc = certify.main()
    sys.stderr.write("a136x: %d emissions, %d cores enlarged, max ratio %.4f\n"
                     % (_STATS["rounds"], _STATS["applied"], _STATS["max_ratio"]))
    sys.exit(rc)
