"""A94 canaries (`notes/chore_slot_cert.md` sec 6), all exact.

(i)  TRUMP SLOT CANARY -- recompute, with THIS chore's slot frames and f_p (corner85.f_min_max on
     the frame centre and the frame t), the number of free meeters and the two largest depths at
     every completable slot of trump5 on the exact Trump, and compare with the lead's
     `results/trump_canary94.json` to 1e-9.  This validates the reflected-frame maps and the
     theta mapping BEFORE they drive the LP right-hand sides.
(ii) IMAGE GATE -- no D4 image of the (s0-dilated) Trump, re-dilated to side s, holds an
     axis-aligned square within h of EVERY pin slot of the class at side s, i.e. no image
     realises the PIN hypothesis of the node.  Post-checked after every certified PASS.
"""
import json, math, os, sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
sys.path.insert(0, HERE)

import blas1  # noqa: F401
from corner85 import f_min_max
import slotfam94 as SF
from slotfam94 import CLASSES, slot_at, pin_at, _sig

TOLC = 1e-9


# ---------------------------------------------------------------- (i) the Trump slot canary
def frame_pose(c, i, j, s, cx, cy, t):
    """(frame centre, frame t) of the pose (cx, cy, t) for the slot cell (i,j) of corner c."""
    u = (cx if c in ("BL", "TL") else s - cx) - i
    v = (cy if c in ("BL", "BR") else s - cy) - j
    tt = t if c in ("BL", "TR") else _sig(t)
    return u, v, tt


def load_trump_t():
    """the exact Trump with t = tan(theta/2) per square (A03 trump11_exact.json, 60 digits)."""
    from decimal import Decimal, getcontext
    getcontext().prec = 80
    d = json.load(open(os.path.join(ROOT, "attempts", "A03-upper-reconstruct",
                                    "trump11_exact.json")))
    sT = Fr(Decimal(d["s"]))
    t = Fr(Decimal(d["t_tan_half_theta"]))
    out = []
    for i, q in enumerate(d["squares"]):
        cx, cy, th = Fr(Decimal(q["cx"])), Fr(Decimal(q["cy"])), Fr(Decimal(q["theta"]))
        up = abs(th) < Fr(1, 10 ** 50)
        out.append(dict(i=i, cx=cx, cy=cy, t=(Fr(0) if up else t), upright=up))
    return sT, out


def trump_slot_canary(log=print):
    from slots94 import completable, snap, slot_at as slot94_at
    sT, sq = load_trump_t()
    names = json.load(open(os.path.join(ROOT, "attempts", "A53-simple-strata", "results",
                                        "name_to_slots.json")))
    pins_s0 = frozenset((snap(Fr(str(x))), snap(Fr(str(y)))) for x, y in names["trump5"])
    pins_T = {slot94_at(p, sT) for p in pins_s0}
    pin_idx = {}
    for q in sq:
        if q["upright"]:
            for p in pins_T:
                if abs(q["cx"] - p[0]) < Fr(1, 10 ** 40) and abs(q["cy"] - p[1]) < Fr(1, 10 ** 40):
                    pin_idx[q["i"]] = p
    assert len(pin_idx) == 5, pin_idx
    ref = {r["cell"]: r for r in json.load(open(os.path.join(BASE, "results",
                                                             "trump_canary94.json")))["rows"]}
    rows, worst = [], 0.0
    for (c, i, j) in completable(pins_s0, SF.S0):
        cell = "%s(%d,%d)" % (c, i, j)
        ds = []
        for q in sq:
            if q["i"] in pin_idx:
                continue
            t = q["t"]
            u, v, tt = frame_pose(c, i, j, sT, q["cx"], q["cy"], t)
            f = f_min_max(u, v, tt)
            d = 1 - f
            if d > Fr(1, 10 ** 40):
                ds.append((float(d), q["i"]))
        ds.sort(reverse=True)
        d1 = ds[0][0] if ds else 0.0
        d2 = ds[1][0] if len(ds) > 1 else 0.0
        R = ref[cell]
        e1, e2 = abs(d1 - R["d1"]), abs(d2 - R["d2"])
        worst = max(worst, e1, e2, abs(len(ds) - R["n_free_meeters"]))
        rows.append(dict(cell=cell, n_meeters=len(ds), d1=d1, d2=d2,
                         ref_n=R["n_free_meeters"], ref_d1=R["d1"], ref_d2=R["d2"],
                         err=max(e1, e2), pin_clipped=bool(R["pin_clips"])))
        log("    %-9s meeters=%d (ref %d)  d1=%.9f d2=%.9f  |err|=%.2e %s"
            % (cell, len(ds), R["n_free_meeters"], d1, d2, max(e1, e2),
               "[pin-clipped]" if R["pin_clips"] else ""))
    ok = worst <= TOLC
    log("    TRUMP SLOT CANARY %s (max deviation %.3e, tol %.0e)"
        % ("OK" if ok else "**FAIL**", worst, TOLC))
    return ok, worst, rows


# ---------------------------------------------------------------- (ii) the image gate
_IMG = {}


def _images():
    if "c" not in _IMG:
        import class85 as K85
        _IMG["c"] = K85.load_class("k0_00", K85.DELTA_PIN)
    return _IMG["c"]


def image_pin_hits(cls_name, s, h, tol_deg=1e-6):
    """per image, the number of pin slots of the class at side s that hold an axis-aligned Trump
    square within h (sup norm).  The image REALISES the pin hypothesis iff that number is k."""
    C = _images()
    sc = float(s) / float(SF.S0)
    pins = [pin_at(p, s) for p in CLASSES[cls_name]["pins"]]
    out = []
    for im in C["images"]:
        hits, per = 0, []
        for (px, py) in pins:
            n = 0
            for (x, y, th) in im["placements"]:
                d = math.degrees(th) % 90.0
                if min(d, 90.0 - d) > tol_deg:
                    continue
                if abs(x * sc - float(px)) <= h and abs(y * sc - float(py)) <= h:
                    n += 1
            per.append(n)
            hits += (n > 0)
        out.append(dict(image=im["key"], per_pin=per, n_pins_hit=hits,
                        realises=(hits == len(pins))))
    return out


def image_gate(cls_name, s, h, log=print):
    rows = image_pin_hits(cls_name, s, h)
    real = [r["image"] for r in rows if r["realises"]]
    log("    IMAGE GATE %s at s=%.6f h=%.6f: pin-hit counts %s -> realising=%s"
        % (cls_name, float(s), h,
           ";".join("%s:%d" % (r["image"], r["n_pins_hit"]) for r in rows), real or "NONE"))
    return (not real), rows


if __name__ == "__main__":
    ok1, w, rows = trump_slot_canary()
    allok = ok1
    for cls in ("k5_11", "k5_16"):
        for wt in ("s0_G2", "G4_lo", "s0_lo"):
            s, m_lo = SF.WINDOWS[wt]
            rho = SF.rho_of(s, m_lo, CLASSES[cls]["A_S"])
            h = float(rho) / math.sqrt(2.0) * (1 + 1e-12)
            ok, _ = image_gate(cls, s, h)
            allok = allok and ok
    print("CANARIES %s" % ("PASS" if allok else "FAIL"))
    sys.exit(0 if allok else 1)
