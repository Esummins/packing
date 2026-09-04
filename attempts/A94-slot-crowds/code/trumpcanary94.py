"""A94 -- the Trump canary for the SLOT-CROWD lemma, on the exact Trump (A03 trump11_exact.json,
60 significant digits; t = tan(theta/2) taken from the file so that cos/sin are exact rationals).

For every completable slot p of trump5 (8 cells) at side s_T = s-hat:
  * the slot frame (backed vertex at the origin, box = [0,1]^2, retreat diagonal = (1,1));
  * for every square Q: f_p(Q) = min over Q of max(x', y')  (exact, vertices + diagonal crossings),
    depth d_p(Q) = max(0, 1 - f_p(Q)); a MEETER has d_p > 0 (open-interior meeting);
  * the back-intrusion check of the containment lemma: min y' over Q n {x' <= 0} and
    min x' over Q n {y' <= 0} (must be >= 1, or the clip empty, for every non-pin square);
  * the count of non-pin meeters, the two largest depths, and the pin clips.
Also: the D4-image realisation table of the CW-S hypothesis for trump5 at a range of a_w
(informational: trump5 is never a target; the numbers say where a trump5 certificate would be
image-realised), and the corner depths (A92's K0 quantities) for cross-checking with A90/A92.
"""
import json, os, sys
from decimal import Decimal, getcontext
from fractions import Fraction as Fr

getcontext().prec = 80
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))
from slots94 import cell_centre, completable, cells_of, S0, CORNERS  # noqa: E402

TOL = Fr(1, 10 ** 40)
EXACT = os.path.join(ROOT, "attempts", "A03-upper-reconstruct", "trump11_exact.json")


def D(s):
    return Fr(Decimal(s))


def load_trump():
    d = json.load(open(EXACT))
    sT = D(d["s"])
    t = D(d["t_tan_half_theta"])
    co, si = (1 - t * t) / (1 + t * t), 2 * t / (1 + t * t)
    sq = []
    for i, q in enumerate(d["squares"]):
        cx, cy, th = D(q["cx"]), D(q["cy"]), D(q["theta"])
        if abs(th) < Fr(1, 10 ** 50):
            c, s_ = Fr(1), Fr(0)
        else:
            c, s_ = co, si
        sq.append(dict(i=i, cx=cx, cy=cy, cos=c, sin=s_, upright=(s_ == 0)))
    return sT, sq


def verts(q):
    h = Fr(1, 2)
    e1 = (h * q["cos"], h * q["sin"])
    e2 = (-h * q["sin"], h * q["cos"])
    return [(q["cx"] + a * e1[0] + b * e2[0], q["cy"] + a * e1[1] + b * e2[1])
            for a, b in ((1, 1), (1, -1), (-1, -1), (-1, 1))]


def frame(corner, i, j, s):
    """map absolute (x,y) -> slot-frame (x', y') for cell (i,j) of corner c."""
    def phi(p):
        x, y = p
        u = x if corner in ("BL", "TL") else s - x
        v = y if corner in ("BL", "BR") else s - y
        return (u - i, v - j)
    return phi


def f_min_max_poly(P):
    best = min(max(x, y) for x, y in P)
    n = len(P)
    for k in range(n):
        (px, py), (qx, qy) = P[k], P[(k + 1) % n]
        dx, dy = qx - px, qy - py
        if dx == dy:
            continue
        s = (py - px) / (dx - dy)
        if 0 <= s <= 1:
            best = min(best, px + s * dx)
    return best


def clip_halfplane(P, keep):
    """Sutherland-Hodgman: keep(p) -> bool for an affine half-plane; edge crossing exact."""
    out = []
    n = len(P)
    for k in range(n):
        a, b = P[k], P[(k + 1) % n]
        ka, kb = keep(a), keep(b)
        if ka:
            out.append(a)
        if ka != kb:
            # crossing of the half-plane boundary g = 0 with g affine: solve by the values
            ga, gb = keep.g(a), keep.g(b)
            s = ga / (ga - gb)
            out.append((a[0] + s * (b[0] - a[0]), a[1] + s * (b[1] - a[1])))
    return out


class HP:
    def __init__(self, g):
        self.g = g

    def __call__(self, p):
        return self.g(p) >= 0


def back_intrusion(P):
    """(min y' over Q n {x' <= 0}) and (min x' over Q n {y' <= 0}); None if the clip is empty."""
    left = clip_halfplane(P, HP(lambda p: -p[0]))
    below = clip_halfplane(P, HP(lambda p: -p[1]))
    my = min(y for x, y in left) if left else None
    mx = min(x for x, y in below) if below else None
    return my, mx


def main():
    sT, sq = load_trump()
    names = json.load(open(os.path.join(ROOT, "attempts", "A53-simple-strata", "results", "name_to_slots.json")))
    # trump5 pins at side s_T
    pins_s0 = [(Fr(str(x)), Fr(str(y))) for x, y in names["trump5"]]
    from slots94 import snap, slot_at
    pins_s0 = frozenset((snap(x), snap(y)) for x, y in pins_s0)
    pins_T = {slot_at(p, sT) for p in pins_s0}
    # identify Trump's pin squares (upright, centre at a slot)
    pin_idx = {}
    for q in sq:
        if q["upright"]:
            for p in pins_T:
                if abs(q["cx"] - p[0]) < Fr(1, 10 ** 40) and abs(q["cy"] - p[1]) < Fr(1, 10 ** 40):
                    pin_idx[q["i"]] = p
    assert len(pin_idx) == 5, pin_idx
    free = [q for q in sq if q["i"] not in pin_idx]
    print("Trump side s_T = %.30f ; pins = squares %s ; free = %s" % (float(sT), sorted(pin_idx), [q["i"] for q in free]))
    rows = []
    for (c, i, j) in completable(pins_s0, S0):
        phi = frame(c, i, j, sT)
        ent = dict(cell="%s(%d,%d)" % (c, i, j))
        pin_clips = []
        for q in sq:
            P = [phi(v) for v in verts(q)]
            f = f_min_max_poly(P)
            d = max(Fr(0), 1 - f)
            if q["i"] in pin_idx:
                # pins are axis-aligned: open overlap with the slot box iff |dx| < 1 and |dy| < 1
                px, py = pin_idx[q["i"]]
                bx, by = cell_centre(c, i, j, sT)
                if abs(px - bx) < 1 and abs(py - by) < 1:
                    pin_clips.append((q["i"], float((1 - abs(px - bx)) * (1 - abs(py - by)))))
                continue
            if d < TOL:
                d = Fr(0)
            my, mx = back_intrusion(P)
            # strict form of the containment lemma: a violation needs a point with x' < 0 (resp.
            # y' < 0) AND min y' (resp. x') over the closed clip < 1
            vx = any(x < 0 for x, y in P)
            vy = any(y < 0 for x, y in P)
            ent.setdefault("free", []).append(dict(sq=q["i"], f=float(f), depth=float(d),
                                                   back_min_y=None if (my is None or not vx) else float(my),
                                                   back_min_x=None if (mx is None or not vy) else float(mx)))
        meet = sorted([r for r in ent["free"] if r["depth"] > 0], key=lambda r: -r["depth"])
        ent["pin_clips"] = pin_clips
        ent["n_free_meeters"] = len(meet)
        ent["meeters"] = [(r["sq"], r["depth"]) for r in meet]
        ent["d1"] = meet[0]["depth"] if meet else 0.0
        ent["d2"] = meet[1]["depth"] if len(meet) > 1 else 0.0
        bad = [r for r in ent["free"] if (r["back_min_y"] is not None and r["back_min_y"] < 1) or
               (r["back_min_x"] is not None and r["back_min_x"] < 1)]
        ent["containment_lemma_violations"] = [(r["sq"], r["back_min_y"], r["back_min_x"]) for r in bad]
        rows.append(ent)
        print("%-9s pin_clips=%-22s free meeters=%d  depths=%s  d2=%.6f  back-intrusion viol=%s"
              % (ent["cell"], pin_clips, len(meet), [(s_, round(dd, 6)) for s_, dd in ent["meeters"]],
                 ent["d2"], ent["containment_lemma_violations"]))
    # corner depths (A92 K0 quantities) for cross-check
    print("corner depths (all squares, A90/A92 convention):")
    for c in CORNERS:
        phi = frame(c, 0, 0, sT)
        ds = sorted([(q["i"], float(max(Fr(0), 1 - f_min_max_poly([phi(v) for v in verts(q)])))) for q in sq
                     if q["i"] not in pin_idx],
                    key=lambda r: -r[1])
        print("  %s (non-pin squares): %s   [pins at this corner: %s]" % (c, [(a, round(b, 6)) for a, b in ds if b > 1e-40],
              [q for q, p in pin_idx.items() if p == cell_centre(c, 0, 0, sT)]))
    # image-realisation table of the CW-S hypothesis for trump5 (informational)
    unclipped = [r for r in rows if not r["pin_clips"]]
    print("trump5 unclipped completable slots: %s" % [r["cell"] for r in unclipped])
    d2min = min(r["d2"] for r in unclipped)
    print("min over unclipped slots of d2 = %.6f  => trump5's CW-S hypothesis is image-realised iff a_w >= %.6f"
          % (d2min, 1 - d2min))
    out = dict(s_T=str(sT), pins=sorted(pin_idx), rows=rows, d2_min_unclipped=d2min,
               note="exact Fractions from the 60-digit A03 data; open-interior meeting = depth > 0")
    json.dump(out, open(os.path.join(ROOT, "attempts", "A94-slot-crowds", "results", "trump_canary94.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
