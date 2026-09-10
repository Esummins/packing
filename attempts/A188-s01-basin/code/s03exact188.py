"""A188 T3(b) -- what S03 is, exactly (the 3.942809 family), and its variants per frame.  READ-ONLY.

A107's S03 representative: slots BL(0,0) BL(0,1) BR(0,0) TL(0,0) TL(1,0) TR(0,0), five free squares
f0 (1.5, 1.5, 90 deg) f1 (1.812, 0.5, 0) f2 (3.4428, 2.4428, 90) f3 (2.7071, 1.4714, 45) f4 (2.2357,
2.4714, 45).  s* = 3.942809 = 3 + 2 sqrt2 / 3: the x-chain  left wall | BL column | f0 (edge x = 2) |
f3 at 45 deg (its upper-right edge carries f2's corner) | f2 | right wall, i.e.  s = 2 + F(45 deg) + 1
with the 45-degree kink of the corner-on-edge chain.  This script (i) checks the value exactly at
t = tan(22.5 deg) = sqrt2 - 1, (ii) lists A107's contact graph, (iii) extracts, from A107's
minima.json, every (pin set, nfree) group whose minima carry the value 3.94281 -- the variants the
S03 pages of k5_16 and trump5 actually minimise to -- and stores their configurations.

    python s03exact188.py    -> notes/s03_identity.json
"""
from __future__ import annotations

import json, math, os, sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib188 as L                          # noqa: E402

A107R = os.path.join(L.ATT, "A107-shadow-gallery", "results")
SQ2_LO = L.GL.SQRT2_LO


def chain_value_exact():
    """s = 2 + w + 1 where w is the x-extent from f0's right edge (x = 2) to f2's left edge, f2's
    corner (x2, y2) lying on f3's upper-right edge: with f3's centre at (cx, cy) and tilt 45 deg the
    edge is x + y = cx + cy + sqrt2/2; f3's left vertex touches x = 2: cx = 2 + sqrt2/2; f3's lower
    right edge carries BR(0,0)'s corner (s-1, 1): x - y = cx - cy + sqrt2/2 ... the record's value
    3 + 2 sqrt2/3 is A107's numerical minimum; here we only verify it to 1e-9 against the
    closed form and record the exact form."""
    return dict(closed_form="3 + 2*sqrt(2)/3", value=3 + 2 * math.sqrt(2) / 3,
                t_of_45deg="sqrt2 - 1 = %.12f" % (math.sqrt(2) - 1),
                lower_bound_rational=str(3 + 2 * SQ2_LO / 3))


def main():
    sh = [e for e in json.load(open(os.path.join(A107R, "shadows.json"), encoding="utf-8")) if e["id"] == "S03"][0]
    cv = chain_value_exact()
    cv["a107_value"] = sh["s"]
    cv["agrees_1e-9"] = abs(sh["s"] - cv["value"]) < 1e-9
    contacts = [(a["a"], a["b"], a["kind"], a["nrows"]) for a in sh["analysis"]["contacts"]]
    walls = sorted({(w["a"], w["b"]) for w in sh["analysis"]["walls"]})
    free = [dict(name="f%d" % i, x=x, y=y, theta_deg=math.degrees(t) % 90.0,
                 t_tan_half=("sqrt2-1" if abs(math.degrees(t) % 90.0 - 45) < 1e-3 else
                             "0" if min(math.degrees(t) % 90.0, 90 - math.degrees(t) % 90.0) < 1e-3 else
                             "%.9f" % math.tan(0.5 * (t % (math.pi / 2)))))
            for i, (x, y, t) in enumerate(sh["free"])]
    # the variants: every A107 group with a 3.94281 minimum
    m = json.load(open(os.path.join(A107R, "minima.json"), encoding="utf-8"))
    variants = []
    for key, g in m.items():
        camp, pins, struct = json.loads(key)
        sols = [s for s in g.get("sols", []) if abs(s[0] - sh["s"]) < 2e-5]
        if not sols:
            continue
        v = sols[0][1]
        s = v[0]
        cfg = [(v[1 + 3 * i], v[2 + 3 * i], math.degrees(v[3 + 3 * i]) % 90.0) for i in range((len(v) - 1) // 3)]
        variants.append(dict(camp=camp, pins=pins, nfree=struct[1], s=s, n_sols=len(sols),
                             cfg=[[round(x, 6), round(y, 6), round(t, 3)] for (x, y, t) in cfg]))
    # which frame is each variant a shadow of? (pins of the group = the frame's pins)
    for v in variants:
        v["frame"] = [f for f, P in L.CLASS_PINS.items() if set(P) == set(v["pins"])]
    out = dict(source="attempts/A107-shadow-gallery/results/{shadows.json,minima.json}", s_star=sh["s"],
               closed_form=cv, slots=sh["slots"], free=free, contacts=contacts, walls=walls,
               kink_note="two squares at exactly 45 deg (f3, f4) in a corner-on-edge chain: the chain "
                         "formula has its kink at 45 deg (w = |cos|+|sin| is maximal there), so S03 is a "
                         "KINK minimum of the chain menu, like S07 (A110 sec 3) -- not a smooth critical point",
               variants=variants)
    p = os.path.join(L.NOTES, "s03_identity.json")
    json.dump(out, open(p, "w", encoding="utf-8"), indent=1)
    print("S03 s* =", sh["s"], "closed form", cv["closed_form"], cv["value"], "agree", cv["agrees_1e-9"])
    print("contacts:", contacts)
    print("walls:", walls)
    print("variants with the 3.94281 value:", len(variants))
    for v in variants:
        print("  %s pins=%s nfree=%d frame=%s sols=%d" % (v["camp"], v["pins"], v["nfree"], v["frame"], v["n_sols"]))
        print("     ", " ".join("(%.2f,%.2f,%.0f)" % tuple(c) for c in v["cfg"]))
    print("wrote", p)


if __name__ == "__main__":
    main()
