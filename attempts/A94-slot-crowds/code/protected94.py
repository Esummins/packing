"""A94 -- the Trump-image ceiling of the slot-crowd chain for every open class (exact).

For a class S (pins P_S) and each D4 image g.z-hat of the exact Trump (side s_T = s-hat) that
CONTAINS the pins of S (an axis-aligned square exactly at every slot of S at side s_T), compute at
every unclipped completable slot p of S the second-largest depth d2(g, p) among the NON-pin squares
of the image (the image's own slot crowd).  A slot-crowd certificate for S at depth delta is
consistent with Trump iff NO compatible image has d2(g, p) >= delta at EVERY slot used, i.e. iff
delta > delta_T(S, U) := max_g min_{p in U} d2(g, p) over the slot set U used.  Theorem N-S then
reaches at most s-hat - delta_T(S, U) from below: the chain's Trump ceiling, before any LP.

Output: results/protected94.json and a table.  Uses slots94 (census + extension status) and the
exact Trump loader of trumpcanary94.
"""
import json, os, sys
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(__file__))
from slots94 import (load_names, load_status, analyse, cell_centre, completable, slot_at, S0, ROOT)
from trumpcanary94 import load_trump, verts, frame, f_min_max_poly, TOL

CLASSES = ["k5_11", "k5_16", "trump5", "k4_03", "k4_05", "k4_06", "k4_08", "k4_11", "k4_13",
           "k3_01", "k3_02", "k3_03", "k3_04", "k3_05", "k2_00", "k2_01", "k2_02", "k1_00", "k0_00"]


def image(sq, k, s):
    """the D4 image k (bit0 x-flip, bit1 y-flip, bit2 transpose) of a square list at side s."""
    out = []
    for q in sq:
        cx, cy, co, si = q["cx"], q["cy"], q["cos"], q["sin"]
        # represent the square by its 4 vertices, map them, and keep the polygon (no tilt bookkeeping)
        V = verts(q)
        W = []
        for (x, y) in V:
            if k & 1:
                x = s - x
            if k & 2:
                y = s - y
            if k & 4:
                x, y = y, x
            W.append((x, y))
        c = (sum(x for x, y in W) / 4, sum(y for x, y in W) / 4)
        out.append(dict(i=q["i"], poly=W, centre=c, upright=q["upright"]))
    return out


def main():
    sT, sq = load_trump()
    names = load_names()
    status = load_status()
    res = {}
    lines = []
    for S in CLASSES:
        pins0 = names[S]
        pinsT = {slot_at(p, sT) for p in pins0}
        rows = analyse(S, names, status)
        unclipped = [r for r in rows if not r["clipped"]]
        usable_now = [r["cell"] for r in unclipped if r["extension_status"].startswith("FULL")]
        # "with the k5 shadows dead" = extensions k5_11 / k5_16 count as usable (A94 target + A57 shell)
        usable_after = [r["cell"] for r in unclipped
                        if r["extension_status"].startswith("FULL") or r["extension"] in ("k5_11", "k5_16")]
        # partial windows (k6_23 to 3877/1000) count as usable for the reach computation
        usable_now += [r["cell"] for r in unclipped if r["extension_status"].startswith("PARTIAL") and r["extension"] == "k6_23"]
        usable_after += [r["cell"] for r in unclipped if r["extension_status"].startswith("PARTIAL") and r["extension"] == "k6_23"]
        usable_now = sorted(set(usable_now)); usable_after = sorted(set(usable_after))
        images = []
        for k in range(8):
            img = image(sq, k, sT)
            # which image squares sit exactly at the pins of S?
            pin_sq = {}
            for q in img:
                if q["upright"]:
                    for p in pinsT:
                        if abs(q["centre"][0] - p[0]) < TOL and abs(q["centre"][1] - p[1]) < TOL:
                            pin_sq[q["i"]] = p
            if len(pin_sq) != len(pinsT):
                continue
            d2 = {}
            for r in unclipped:
                c, ij = r["cell"][:2], r["cell"][2:]
                i, j = int(ij[1]), int(ij[3])
                phi = frame(c, i, j, sT)
                ds = sorted([max(Fr(0), 1 - f_min_max_poly([phi(v) for v in q["poly"]]))
                             for q in img if q["i"] not in pin_sq], reverse=True)
                ds = [d for d in ds if d >= TOL]
                d2[r["cell"]] = float(ds[1]) if len(ds) > 1 else 0.0
            images.append(dict(g=k, pin_squares=sorted(pin_sq), d2=d2))
        def delta_T(U):
            if not U or not images:
                return 0.0
            return max(min(im["d2"][p] for p in U) for im in images)
        dT_now, dT_after = delta_T(usable_now), delta_T(usable_after)
        res[S] = dict(k=len(pins0), N=11 - len(pins0), n_unclipped=len(unclipped),
                      usable_now=usable_now, usable_after_k5_shadows=usable_after,
                      compatible_images=[im["g"] for im in images], per_image=images,
                      delta_T_now=dT_now, delta_T_after=dT_after,
                      reach_now=float(sT) - dT_now if usable_now else None,
                      reach_after=float(sT) - dT_after if usable_after else None)
        lines.append("%-8s k=%d N=%d unclipped=%d | usable now %d %s | after k5 shadows %d | images %s | delta_T now %.4f after %.4f | chain ceiling now %s after %s"
                     % (S, len(pins0), 11 - len(pins0), len(unclipped), len(usable_now), usable_now,
                        len(usable_after), [im["g"] for im in images], dT_now, dT_after,
                        "%.4f" % res[S]["reach_now"] if usable_now else "n/a",
                        "%.4f" % res[S]["reach_after"] if usable_after else "n/a"))
        for im in images:
            lines.append("      image g%d pins=%s d2 per unclipped slot: %s" % (im["g"], im["pin_squares"],
                         {p: round(v, 4) for p, v in im["d2"].items()}))
    print("\n".join(lines))
    json.dump(res, open(os.path.join(ROOT, "attempts", "A94-slot-crowds", "results", "protected94.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
