"""A238 -- the CANARY for Lemma TUBE-LEAF/S.

No node of the benchmark ever fits the tube box (A212 s.6: a gated node needs ~36 aligned cuts), so a bug in
`tube238.tube` would be invisible.  This test builds the leaf by hand on a real class page and checks both
directions:

  POSITIVE -- every non-pin role pinched to a tiny box around its assigned image square, and the pins on their
              slots: `fits` must be True, and every per-role margin must be inside (r_c', r_theta);
  NEGATIVE -- exactly one role displaced by 2 x r_c' (centre) and, separately, by 2 x r_theta (tilt): `fits` must be
              False, and the offending role must be the reported `worst`;
  PIN      -- a pin whose assigned image square is NOT on its slot (the slot moved by 10^-6, far below the slack
              box half-width delta_pin/sqrt2 = 1.4e-2): `fits` must be False, i.e. clause (P) is not vacuous.

    python test_tube238.py [k4_11 ...]
"""
import math
import sys
import os
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import path238                                                  # noqa: E402
path238.fix()
import load238                                                  # noqa: E402
load238.install()
import coarse211 as C11                                         # noqa: E402
import poly204 as P                                             # noqa: E402
import tube238 as TU                                            # noqa: E402

C11.install()
FP, MB = P.FP, P.MB


def page(nid):
    rec, cls, row = FP.load_page(nid)
    T = FP.Trace(wall=600)
    return C11.CoarsePage(rec, cls, nid, T, pad="zero", start={}, basins=[]), cls


def pinch(pg, g, assign, dx=Fr(0), dy=Fr(0), dt=Fr(0), only=None):
    """give every assigned role a one-piece box of half-width 10^-9 at its image square (+ the offset on `only`)."""
    sq = {q["i"]: q for q in TU.images()[g]}
    for r, i in assign.items():
        q = sq[i]
        e = Fr(1, 10 ** 9)
        ox, oy, ot = (dx, dy, dt) if (only is None or r == only) else (Fr(0), Fr(0), Fr(0))
        t = q["reps"][0][0] + ot
        t0, t1 = max(Fr(0), t - e), min(Fr(1), t + e)
        pg.pieces[r] = [(MB.Bin(t0, t1), (q["cx"] + ox - e, q["cx"] + ox + e, q["cy"] + oy - e, q["cy"] + oy + e))]
        pg.roles[r] = (float(q["cx"] + ox - e), float(q["cx"] + ox + e), float(q["cy"] + oy - e), float(q["cy"] + oy + e),
                       MB.deg_of_t(t0), MB.deg_of_t(t1))


def run(nid):
    pg, cls = page(nid)
    TU.CLS[0] = cls
    g = TU.gate(pg)
    assert g["contains"], "%s: the gate does not hold on the root -- pick an image-bearing class" % nid
    # give every FREE square a role, so the node is "all eleven named": pins + H + the image's other squares
    sq = {q["i"]: q for q in TU.images()[g["g"]]}
    used = set(g["pins"].values()) | set((g["assignment"] or {}).values())
    free = [i for i in sorted(sq) if i not in used]
    assign = dict(g["assignment"] or {})
    for k, i in enumerate(free):
        r = "F%d" % (k + 1)
        pg.roles[r] = (0.0, float(MB.S_RAT), 0.0, float(MB.S_RAT), 0.0, 90.0)
        assign[r] = i
    R = TU.radii(sorted(g["pins"].values()))
    rc, rt = R["r_c_eff"], R["r_theta"]
    out = []

    pinch(pg, g["g"], assign)
    tb = TU.tube(pg, g["g"], assign, g["pins"])
    out.append(("POSITIVE", tb["fits"] is True, "worst %s" % (tb["worst"],)))
    assert all(v["fits"] for v in tb["roles"].values()), "a role failed inside the positive control"

    for tag, kw in (("NEG centre x", dict(dx=2 * rc)), ("NEG centre y", dict(dy=2 * rc)),
                    ("NEG tilt", dict(dt=Fr(round(math.tan(2 * float(rt) / 2) * 10 ** 12) + 10 ** 3, 10 ** 12)))):
        role = sorted(assign)[0]
        pinch(pg, g["g"], assign, only=role, **kw)
        tb2 = TU.tube(pg, g["g"], assign, g["pins"])
        ok = (tb2["fits"] is False) and (tb2["worst"] or ["?"])[0] == role
        out.append((tag, ok, "fits %s worst %s (expected %s)" % (tb2["fits"], (tb2["worst"] or ["?"])[0], role)))

    pinch(pg, g["g"], assign)                                   # restore, then move ONE pin off its slot
    pn = sorted(pg.pins)[0]
    b = list(pg.pins[pn])
    b[0] += 1e-6
    b[1] += 1e-6
    pg.pins[pn] = tuple(b)
    tb3 = TU.tube(pg, g["g"], assign, g["pins"])
    out.append(("PIN clause (P)", tb3["fits"] is False and not tb3["roles"][pn]["fits"],
                "fits %s pin %s %s" % (tb3["fits"], pn, tb3["roles"][pn]["fits"])))
    return cls, R, out


if __name__ == "__main__":
    bad = 0
    for nid in (sys.argv[1:] or ["k4_11_root", "k3_02_root"]):
        cls, R, out = run(nid)
        print("== %s [%s]  direction %s  r_c' %.7f  r_theta %s  (%s)" % (
            nid, cls, R["direction"], float(R["r_c_eff"]), float(R["r_theta"]), R["cert"]))
        for tag, ok, detail in out:
            print("   %-16s %s   %s" % (tag, "OK" if ok else "FAIL", detail))
            bad += 0 if ok else 1
    print("A238 tube canary: %s" % ("ALL OK" if not bad else "%d FAILURE(S)" % bad))
    sys.exit(1 if bad else 0)
