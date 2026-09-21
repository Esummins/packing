"""A256 -- the CONTRACTED Trump images along the tube rays, dilated back to s0 (notes/trump5_closure.md s.2).

A window node of the residual tree is a hypothesis about the DILATED family F = Delta_{s0/m} P of a packing P at side
m in the pad's slab.  The tube theorem (docs/proofs/contraction_tube.md s.1) speaks about z-hat - t v at side
m = s-hat - t.  Composing the two: the configuration a window node would have to hold, if the packing it describes is
a contracted Trump configuration at depth t, is

    RayImage(v, t) := Delta_{s0/m} ( z-hat - t v ),    m = s-hat - t.

* scale ray (v_i = c-hat_i / s-hat on every centre, v_theta = 0): z-hat - t v has centres c-hat (m / s-hat), so
  Delta_{s0/m} of it has centres c-hat (s0 / s-hat) -- INDEPENDENT of t.  One configuration covers the whole ray.
* slot ray (a pin centre coordinate rides its slot line k(s) = alpha + beta s, a free centre scales): the pinned
  coordinate is alpha + beta m, whose dilate is lam alpha + beta s0 with lam = s0/m in [1, lam_pad]; the free
  coordinates are c-hat (s0 / s-hat) again.  So the free half is the SAME single configuration and only the pins
  sweep an interval of length (lam_pad - 1)|alpha| per coordinate.
Tilts are unchanged by a dilation, so the tilt of every image square is z-hat's tilt (mod 90 deg, reflections
theta -> 90 deg - theta) exactly as in trump256.images().

Hence the RAY GATE over a pad's whole slab costs no more than the pad-0 gate: one image per D4 element for the free
squares, plus an interval instead of a point for each pinned coordinate.  `ray_images(pad)` returns exactly that.
Everything is exact rationals; `MARGIN` is applied OUTWARD, i.e. in favour of "the node might hold a ray image",
because the (a)/(b) split is a TRIAGE (both classes are decided by sound rules afterwards), and the expensive
mistake is to send a node that does hold an image to the kill rules."""
import math
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import trump256 as TR                                          # noqa: E402  (A212's image, D4, exact geometry)

S0 = TR.S0
MARGIN = Fr(1, 10 ** 6)                # outward, in favour of "holds a ray image" (see the module doc)
PADS = {"zero": Fr(1), "g1": S0 / Fr(3861637, 1000000), "window": S0 / Fr(382, 100)}
_RAY = {}


def pin_alpha(q):
    """(alpha_x, alpha_y) of an upright image square sitting on a corner slot: k(s) = alpha + beta s, beta in {0, 1}.

    A trump5 pin is a corner square of the container at side s: its centre coordinate is either i + 1/2 (beta = 0,
    alpha = i + 1/2, measured from the near wall) or s - (i + 1/2) (beta = 1, alpha = -(i + 1/2)).  The image square's
    s0 coordinate decides which: a coordinate below s0/2 is a near-wall one."""
    out = []
    for c in (q["cx"], q["cy"]):
        out.append((c, Fr(0)) if c * 2 <= S0 else (c - S0, Fr(1)))
    return out


def ray_images(pad="g1"):
    """{g: [square dicts]} with, per square, `cx`/`cy` the DILATED ray position (a single rational for a free square)
    and `cxi`/`cyi` the closed rational INTERVAL swept by that coordinate over the pad's slab (a point for the free
    squares and for the scale ray; an interval of length (lam_pad - 1)|alpha| for a pinned coordinate on the slot ray).

    The two rays together: the union of the two intervals per coordinate, which is the slot-ray interval (it contains
    the scale-ray point at lam = 1 end for a pin whose alpha is the near-wall one, and the free coordinates agree).
    Reported per-ray in `rays` so the caller can cite the one it uses."""
    key = str(pad)
    if key in _RAY:
        return _RAY[key]
    lam = PADS[pad]
    k = S0 / TR.shat()                                         # the dilation of the whole ray back to s0
    out = {}
    for g, sq in TR.images().items():
        row = []
        for q in sq:
            cx, cy = q["cx"] * k, q["cy"] * k                  # scale ray: one point, every t
            ivs = []
            for (c0, (al, be)) in zip((cx, cy), pin_alpha(dict(cx=q["cx"] * k, cy=q["cy"] * k))):
                lo = hi = c0                                   # slot ray: lam alpha + beta s0, lam in [1, lam_pad]
                if q["upright"]:
                    a, b = al + be * S0, lam * al + be * S0
                    lo, hi = min(a, b, c0), max(a, b, c0)
                ivs.append((lo, hi))
            row.append(dict(i=q["i"], cx=cx, cy=cy, reps=q["reps"], upright=q["upright"],
                            cxi=ivs[0], cyi=ivs[1]))
        out[g] = row
    _RAY[key] = dict(images=out, lam=lam, k=k, pad=pad,
                     rays=dict(scale="Delta_{s0/m} (z-hat - t v_scale) = c-hat (s0/s-hat), every t",
                               slot="free squares as scale; pinned coordinate lam alpha + beta s0, lam in [1, %s]" % lam))
    return _RAY[key]


def in_box_iv(iv, lo, hi, eps=MARGIN):
    """the closed interval `iv` of a ray coordinate meets [lo, hi] widened by eps."""
    return max(iv[0], Fr(lo) - eps) <= min(iv[1], Fr(hi) + eps)


def tilt_ok(q, d0, d1, eps=1e-6):
    """some tilt representative of the image square lies in the box's tilt window [d0, d1] (degrees, mod 90)."""
    for (t, _th, _c, _s) in q["reps"]:
        d = TR.MB.deg_of_t(t)
        for dd in (d, d - 90.0, d + 90.0):
            if float(d0) - eps <= dd <= float(d1) + eps:
                return True
    return False


def holds_ray_image(pins, hboxes, pad="g1", drift=None):
    """Does the node's ROOT hypothesis (its pin boxes + its H boxes) admit a D4 image of a contracted Trump
    configuration anywhere in the pad's slab?  -> dict(holds, g, assignment, why).

    `pins`   [(name, (x0, x1, y0, y1))] the pin centre boxes, already widened by `drift` by the caller;
    `hboxes` [(name, (x0, x1, y0, y1, d0, d1))] the H / named-role hull boxes of the record.
    SUPERSET by construction: every piece of every descendant of the node lies inside these boxes, so `holds` False
    at the root is inherited by the whole subtree (class (a)); `holds` True is only a "might" (class (b))."""
    R = ray_images(pad)
    for g, sq in R["images"].items():
        used, asg, ok = set(), {}, True
        for pn, box in pins:
            hit = next((q for q in sq if q["i"] not in used and q["upright"]
                        and in_box_iv(q["cxi"], box[0], box[1]) and in_box_iv(q["cyi"], box[2], box[3])), None)
            if hit is None:
                ok = False
                break
            used.add(hit["i"])
            asg[pn] = hit["i"]
        if not ok:
            continue
        for hn, box in hboxes:
            hit = next((q for q in sq if q["i"] not in used
                        and in_box_iv(q["cxi"], box[0], box[1]) and in_box_iv(q["cyi"], box[2], box[3])
                        and tilt_ok(q, box[4], box[5])), None)
            if hit is None:
                ok = False
                break
            used.add(hit["i"])
            asg[hn] = hit["i"]
        if ok:
            return dict(holds=True, g=g, assignment=asg, why="a D4 ray image fits every pin box and every H box")
    return dict(holds=False, g=None, assignment=None,
                why="no D4 image of z-hat - t v (t over the whole %s slab, dilated to s0) fits the node's pin and H boxes" % pad)


if __name__ == "__main__":
    R = ray_images("g1")
    print("pad g1 lam =", float(R["lam"]), " dilation k =", float(R["k"]))
    for q in R["images"]["id"][:6]:
        print(q["i"], float(q["cx"]), float(q["cy"]), "upright" if q["upright"] else "tilted",
              [float(v) for v in q["cxi"]], [float(v) for v in q["cyi"]])
