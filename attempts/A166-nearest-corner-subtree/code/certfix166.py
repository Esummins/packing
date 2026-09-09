"""A166 -- the CAUSE of the certificate FAIL, and the one-line fix, demonstrated.

DIAGNOSIS.  A150's and A166's LP nodes are solved with A135's certified **EXACT** axis cores: the
`ExactHyp` pattern builds `caselp.Hyp` and then REPLACES `self.cores` with the exact ones, so the LP's
row filter (`Hyp.ok_many`, `c.depth_many(...) > EPS_CORE`) drops every placement that overlaps an EXACT
core.  But `caselp.make_certificate` rebuilds the hypothesis with

    hyp = Hyp.from_json(res["hyp"])

and `Hyp.from_json` calls `b.core()` on each box, i.e. it silently reverts to the **STOCK** cores and
throws away the `cores` field the json carries.  So the emitted certificate exempts a SMALLER core than
the LP was allowed to ignore, and every placement in the annulus between the two cores is a guaranteed
HOLE.  Measured on `l2_p65_101_b8_005_512`: the exact core of box 0 has `a = 0.441823`, the stock core
`a = 0.412228`, and all 32 of the verifier's holes are the single axis-aligned placement
`(3.35109, 1.49, 0°)`, whose SAT depth is **+0.029594 against the exact core** (so the LP dropped it) and
**−0.000001 against the stock core** (so the certificate cannot exempt it).  That is why the A13/A14
separation loop makes no progress: the row it is asked to add is precisely a row the LP is entitled to
drop.  `exact_mass = 0` on every hole, not "just under 1" — this is not a robustness-margin failure.

THE FIX, and why it is sound.  Substitute the exact cores into the emitted certificate.  A135's
`exact_a` CERTIFIES `K(B) ⊆ Q(p)` for every pose `p ∈ B` (exact rational vertex test), and a square of
the packing distinct from the conditioned one is interior-disjoint from the conditioned square, hence
from its core; so exempting placements that overlap the EXACT core is sound, and the frozen
`verify_case.py` validates whatever cores the certificate carries.  Nothing frozen is edited: the
certificate is post-processed here, in A166's own code.

    python code/certfix166.py --node l2_p65_101_b8_005_512
"""
import argparse
import json
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import geo166 as G                                              # noqa: E402
import lp166 as L                                               # noqa: E402
from caselp import Box                                          # noqa: E402  READ-ONLY (A57)

RES = os.path.join(BASE, "results")
CERTS = os.path.join(BASE, "certs")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--node", required=True)
    ap.add_argument("--pad", default="wmax")
    ap.add_argument("--certs", default="", help="comma-separated certificate basenames to patch; "
                                               "default: <node>.json and every <node>_sc*_dn* file")
    a = ap.parse_args()
    nodes = json.load(open(os.path.join(RES, "nodes166_%s.json" % a.pad), encoding="utf-8"))
    n = [x for x in nodes if x["node"] == a.node][0]
    boxes = [Box(**b) for b in n["boxes"]]
    exact = [G.exact_core(b) for b in boxes]
    stock = [b.core() for b in boxes]
    print("node %s budget %d" % (a.node, n["budget"]))
    for i, (e, s) in enumerate(zip(exact, stock)):
        print("  core %d: exact a = %.9f   stock a = %.9f   ratio %.5f"
              % (i, float(e.a), float(s.a), float(e.a) / float(s.a)))
    if a.certs:
        names = a.certs.split(",")
    else:
        names = [a.node + ".json"] + sorted(
            f for f in os.listdir(CERTS)
            if f.startswith(a.node + "_sc") and f.endswith(".json")
            and not f.endswith((".certify.json", ".report.json", ".witnesses.json")))
    out = []
    for nm in names:
        p = os.path.join(CERTS, nm)
        if not os.path.exists(p):
            continue
        cert = json.load(open(p, encoding="utf-8"))
        cc = cert["hypotheses"]["cores"]
        if len(cc) != len(exact):
            print("  %s: %d cores in cert vs %d boxes -- skipped" % (nm, len(cc), len(exact)))
            continue
        carried = [Fr(c["a"]) for c in cc]
        for c, e in zip(cc, exact):
            c["a"] = str(e.a)
            c["kx"], c["ky"], c["tm"] = str(e.kx), str(e.ky), str(e.tm)
        cert["provenance"]["a166_note"] = (
            "cores substituted with A135 exact_a cores (the ones the LP row filter used); "
            "caselp.make_certificate reverts to Hyp.from_json's stock b.core()")
        q = os.path.join(CERTS, nm[:-5] + "_exactcore.json")
        json.dump(cert, open(q, "w"), indent=0)
        rc, txt = L.run_verifier(q, jobs=2, depth=56)
        tail = [l for l in txt.splitlines() if l.startswith(("PASS", "FAIL", "boxes", "MALFORMED"))]
        res = "PASS" if rc == 0 else "FAIL"
        out.append(dict(cert=nm, patched=os.path.basename(q), result=res,
                        carried_a=[str(x) for x in carried],
                        exact_a=[str(e.a) for e in exact], verifier=tail[:3],
                        total=cert["total"], budget=cert["budget"]))
        # a discoverable `.certify.json` beside the patched certificate, in the lab's usual shape,
        # so kill scanners see the PASS; the ORIGINAL FAIL record is left untouched.
        json.dump(dict(cert=q, result=res, verifier_sha=L.VERIFIER_SHA, budget=cert["budget"],
                       total=cert["total"], rounds=[dict(round=0, result=res, verifier=tail[:3])],
                       scope="s0_fixed_side",
                       window="carries [3.82, shat) by dilation: Lemma B.0 + Lemma K0-WIDEN, the "
                              "cover is stated at the full pad w_max (A166 notes/composition.md 5)",
                       note="A166: cores substituted with A135 exact_a cores (the ones the LP row "
                            "filter used); caselp.make_certificate reverts to Hyp.from_json's stock "
                            "b.core() -- see notes/certificate_bug.md"),
                  open(q.replace(".json", ".certify.json"), "w"), indent=1)
        print("  %-46s -> %s | %s" % (nm, res, (tail[-1][:140] if tail else "")), flush=True)
    json.dump(dict(node=a.node, budget=n["budget"], verifier_sha=L.VERIFIER_SHA,
                   exact_a=[float(e.a) for e in exact], stock_a=[float(s.a) for s in stock],
                   trials=out),
              open(os.path.join(RES, "certfix166_%s.json" % a.node), "w"), indent=1)
    print("wrote results/certfix166_%s.json" % a.node, flush=True)


if __name__ == "__main__":
    main()
