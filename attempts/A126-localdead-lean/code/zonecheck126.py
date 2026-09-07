"""A126 T3 -- finding F-COVER: is a node's NO zone INSIDE its YES box?

    python zonecheck126.py [node ...]      (default: A120's four CLOSED nodes)

A120's cover `H = YES u NO_1 u ... u NO_|L|` is a tautology **iff `ZONE_i` is contained in
`BOX_i` as a set of poses**: a configuration that fails the YES side fails it because NO square
is in `BOX_i`, and to land in `NO_i` it must then have no square in `ZONE_i` either.

A120's runner builds the zone EXACTLY and records it at full precision in
`results/nodes/<child>.json` (`hyp.nofams`, with the box's own theta interval in DEGREES); the
`case-measure-certificate-v1` file then writes it as exact rationals, and THAT is where the
rounding happens.  So the comparison that isolates the defect is CERTIFICATE against RECORD, and
it works for every node whatever its `D4` frame map -- comparing against A119's unmapped boxes
would only be meaningful for a node whose `struct_op` fixes them.

Read-only on A120 and A119.  Prints, per NO child, every bound of the certificate's zone that
lies OUTSIDE the recorded box, with the amount.  Exit 0 either way: this is a measurement.
"""
from __future__ import annotations

import glob, json, math, os, sys
from fractions import Fraction as Q

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
A120C = os.path.join(ROOT, "attempts", "A120-no-side-runner", "certs")
A120N = os.path.join(ROOT, "attempts", "A120-no-side-runner", "results", "nodes")
CLOSED = ["k5_11_interior_Y0230", "k5_11_interior_Y0637",
          "k5_11_interior_Y0709", "k5_11_interior_Y0997"]
TOL = 1e-12                       # a bound this close counts as "on the boundary", not outside


def tanh2(deg):
    return math.tan(math.radians(deg) / 2.0)


def record_for(child):
    """the node record of a NO child; a re-priced child (`_r6`) reuses its base record."""
    p = os.path.join(A120N, child + ".json")
    if os.path.exists(p):
        return json.load(open(p, encoding="utf-8"))
    base = child.rsplit("_r", 1)[0]
    p = os.path.join(A120N, base + ".json")
    if os.path.exists(p):
        return json.load(open(p, encoding="utf-8"))
    return None


def check_node(node):
    files = sorted(glob.glob(os.path.join(A120C, "%s_a120__a116N__NO*.json" % node)))
    files = [f for f in files if os.path.exists(f[:-5] + ".report.json")
             and json.load(open(f[:-5] + ".report.json", encoding="utf-8")).get("result") == "PASS"]
    print("node %s : %d PASSing NO certificates" % (node, len(files)))
    worst = {}
    for f in files:
        child = os.path.basename(f)[:-5]
        rec = record_for(child)
        if rec is None:
            print("  %-46s -> NO RECORD, skipped" % child)
            continue
        b = rec["hyp"]["nofams"][0]
        c = json.load(open(f, encoding="utf-8"))
        z = c["hypotheses"]["nofams"][0]
        bad = []
        for k, sgn in (("x0", +1), ("x1", -1), ("y0", +1), ("y1", -1)):
            d = sgn * (float(Q(z[k])) - b[k])
            if d < -TOL:
                bad.append((k, -d))
        zt = [(float(Q(a)), float(Q(bb))) for a, bb in z["t_intervals"]]
        bt = [(tanh2(lo), tanh2(hi)) for lo, hi in b["thetas"]]
        if len(zt) != len(bt):
            bad.append(("#t-intervals %d vs %d" % (len(zt), len(bt)), float("nan")))
        else:
            for (a, bb), (lo, hi) in zip(sorted(zt), sorted(bt)):
                if a < lo - TOL:
                    bad.append(("t-lo", lo - a))
                if bb > hi + TOL:
                    bad.append(("t-hi", bb - hi))
        for k, v in bad:
            worst[k] = max(worst.get(k, 0.0), v)
        print("  %-46s zone OUTSIDE the recorded box: %s"
              % (child, ", ".join("%s by %.2e" % kv for kv in bad) or "nowhere (zone is inside)"))
    return worst


def main(*nodes):
    nodes = list(nodes) or CLOSED
    allworst = {}
    for n in nodes:
        for k, v in check_node(n).items():
            allworst[k] = max(allworst.get(k, 0.0), v)
        print()
    if allworst:
        print("F-COVER over %d node(s): the split is a tautology only up to %s"
              % (len(nodes), ", ".join("%s %.2e" % (k, v) for k, v in sorted(allworst.items()))))
        print("  A120's runner builds the zone EXACTLY (the record above); the certificate FILE")
        print("  emits it rounded OUTWARD -- the right direction for the verifier, the wrong one")
        print("  for the cover.  Fix: emit the zone INWARD and re-certify (these amounts are far")
        print("  below the resolution at which the certificates pass).")
    else:
        print("every zone is inside its box: the split is a tautology as certified")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
