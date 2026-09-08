"""A136 -- A112's `certify.py`, UNMODIFIED, with the F-COVER wrapper spliced in at emission.

    python certify136.py <node_json> --s_rat ... [every certify.py flag]

A112's `certify.py` is IMPORTED, not copied, and its `main()` is what runs: the witness-feedback
loop, the auto-scale, the re-solves and the frozen `verify_case.py` call are byte-identical.  The
ONLY change is that the certificate dict `caselp.make_certificate` produces is passed through
`a136lib.narrow` BEFORE `certify.py` writes it, so

  * the NO zone is written INWARD (re-derived from the node's own exact `hyp.nofams`),
  * the mapped A119 box the YES side names is written into the certificate, INWARD,
  * the zone is intersected with that box, and `ZONE subset BOX` is checked on the WRITTEN
    rationals and RAISES on failure.

The narrowed zone exempts strictly FEWER boxes, so the verifier has strictly MORE to cover: the
loop and its verdict are unchanged in kind, only harder, and a PASS is the fixed-cover statement.

The boxes come from a sidecar `<node_json>.a136box.json` that the driver writes next to the node
json (`{"boxes": [...A120 `rec['boxes_used']`...]}`); with no sidecar this script refuses to run
rather than emitting an unchecked certificate.
"""
from __future__ import annotations

import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a136lib as A                                                # noqa: E402  (BLAS pin inside)

sys.path.insert(0, A.A112C)
import certify                                                     # noqa: E402

_NODE = sys.argv[1]
_SIDE = _NODE + ".a136box.json"
if not os.path.exists(_SIDE):
    sys.stderr.write("a136: no box sidecar %s -- refusing to emit an unchecked certificate\n"
                     % _SIDE)
    sys.exit(4)
_BOXES = json.load(open(_SIDE, encoding="utf-8"))["boxes"]
_ORIG = certify.make_certificate


def _patched(res, s_rat, scale=1.03, **kw):
    cert = _ORIG(res, s_rat, scale=scale, **kw)
    out, _rep = A.narrow(cert, res["hyp"]["nofams"], _BOXES, res["s"],
                         tag=os.path.basename(_NODE))
    return out


certify.make_certificate = _patched

if __name__ == "__main__":
    sys.exit(certify.main())
