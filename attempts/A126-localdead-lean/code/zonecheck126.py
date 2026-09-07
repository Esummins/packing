"""A126 T3 -- finding F-COVER: is a node's NO zone INSIDE its YES box?

    python zonecheck126.py [node]        (default k5_11_interior_Y0230)

A120's cover `H = YES u NO_1 u ... u NO_|L|` is a tautology **iff `ZONE_i` is contained in
`BOX_i` as a set of poses**: a configuration that fails the YES side fails it because NO square
is in `BOX_i`, and to land in `NO_i` it must then have no square in `ZONE_i` either.  A120's
runner builds the zone exactly (its node record carries the box's own theta-cell and the centre
rectangle in full precision) and asserts `box_identical_to_yes`; the rounding happens when the
`case-measure-certificate-v1` file is written, and it is OUTWARD -- the right direction for the
VERIFIER (a wider NO zone exempts more, justified by the correspondingly stronger hypothesis)
and the wrong one for the COVER.

Read-only: A119's certificate of `N` and A120's certificate files.  Prints, per NO child, every
bound of the zone that lies OUTSIDE the box, with the amount.  Exit 0 either way -- this is a
measurement, not a gate.
"""
from __future__ import annotations

import glob, gzip, json, math, os, sys
from fractions import Fraction as Q

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
A119 = os.path.join(ROOT, "attempts", "A119-local-cert-lean", "certs")
A120 = os.path.join(ROOT, "attempts", "A120-no-side-runner", "certs")
NCERT = "S02_k5_11_r0.20_rho10.cert.json.gz"          # the N A120's cover uses


def theta_of(t: float) -> float:
    return math.degrees(2 * math.atan(t))


def main(node="k5_11_interior_Y0230"):
    cert = json.load(gzip.open(os.path.join(A119, NCERT), "rt", encoding="utf-8"))
    boxes = {b["name"]: b for b in cert["meta"]["bodies"] if b["kind"] == "free"}
    files = sorted(glob.glob(os.path.join(A120, "%s_a120__a116N__NO*.json" % node)))
    files = [f for f in files if os.path.exists(f[:-5] + ".report.json")
             and json.load(open(f[:-5] + ".report.json", encoding="utf-8")).get("result") == "PASS"]
    print("N = %s ; node = %s ; %d PASSing NO certificates" % (cert["meta"]["id"], node, len(files)))
    worst = {}
    for f in files:
        c = json.load(open(f, encoding="utf-8"))
        z = c["hypotheses"]["nofams"][0]
        zx0, zx1, zy0, zy1 = (float(Q(z["x0"])), float(Q(z["x1"])),
                              float(Q(z["y0"])), float(Q(z["y1"])))
        ivs = [(float(Q(a)), float(Q(b))) for a, b in z["t_intervals"]]
        # the box: nearest centre rectangle among N's free bodies
        nm, b = min(boxes.items(), key=lambda kv: abs(zx0 - kv[1]["x0"]) + abs(zy0 - kv[1]["y0"]))
        bt0, bt1 = math.tan(b["t0"] / 2), math.tan(b["t1"] / 2)
        bad = []
        # centre: the zone must be inside; the clamp (x1 = s0 - 1/2) only shrinks it
        for k, zv, bv, sgn in (("x0", zx0, b["x0"], +1), ("x1", zx1, b["x1"], -1),
                               ("y0", zy0, b["y0"], +1), ("y1", zy1, b["y1"], -1)):
            if sgn * (zv - bv) < 0:
                bad.append((k, abs(zv - bv)))
        # tilt, in `t` and per emitted interval, against the certificate's cell FOLDED into the
        # fundamental domain (a cell straddling 0 is two `t`-intervals, and A120 emits both)
        folds = [(bt0, bt1)]
        if b["t0"] < 0.0:                       # the straddling cell folds to the far end
            folds.append((math.tan((b["t0"] + math.pi / 2) / 2), math.tan(math.pi / 4)))
            folds[0] = (math.tan(0.0), bt1)
        for (a, bb) in ivs:
            fl = min(folds, key=lambda fv: abs(a - fv[0]) + abs(bb - fv[1]))
            if a < fl[0]:
                bad.append(("t-lo", fl[0] - a))
            if bb > fl[1]:
                bad.append(("t-hi", bb - fl[1]))
        for k, v in bad:
            worst[k] = max(worst.get(k, 0.0), v)
        print("  %-46s -> box %-9s  zone OUTSIDE the box: %s"
              % (os.path.basename(f)[:-5], nm,
                 ", ".join("%s by %.2e" % kv for kv in bad) or "nowhere (zone is inside)"))
    if worst:
        print("F-COVER: the split is a tautology only up to %s"
              % ", ".join("%s %.2e" % (k, v) for k, v in sorted(worst.items())))
        print("         fix: emit the NO zone with INWARD rounding and re-certify (the amounts")
        print("         above are far below the resolution at which these certificates pass)")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
