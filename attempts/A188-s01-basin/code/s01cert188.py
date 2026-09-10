"""A188 T2 -- the S01 basin as exact LINE certificates, per class frame.

For each frame (k5_11, k5_16, trump5) and each axis-parallel line through a row / column of its
pins, the hypothesis N = "the k pins on the line (in their slack cores) + (4 - k) OTHER squares
whose centres lie within w of the line, any position along it, tilt in the variant's window" has,
by A144's Lemma LINE-2, chord sum >= k + (4 - k) * minchord >= 4 > s0, so Dead(N, s0).  For k = 3
the fourth square only needs chord > s0 - 3 = 0.877084 (the A144 node-level guard-line kill, with
a wider band).  k = 0 (four free squares on one line, no pin) is frame-independent and is emitted
once, for the k0_00 lane as well.

Every bound is `guardline.minchord_box` (exact rationals); the entry records the exact rhs and the
three c's it was checked at (the statement is translation-invariant along the normal as long as the
band lies inside the container).

    python s01cert188.py     -> results/s01_basin.jsonl
"""
from __future__ import annotations

import json, os, sys, time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib188 as L                          # noqa: E402

VARIANTS = [("any", 0.0, 90.0), ("pm10", 0.0, 10.0), ("pm20", 0.0, 20.0), ("pm30", 0.0, 30.0)]


def halfwidth(th0, th1, thr):
    """largest w (safe, to 1/20000) with minchord >= thr over [0,s] x [c-w, c+w] x [th0, th1]."""
    lo, hi = Fr(0), Fr(1, 2)
    c = Fr(3, 2)
    if L.minchord(L.band_box("h", c, lo, th0, th1), "h", c) < thr:
        return Fr(0)
    while hi - lo > Fr(1, 20000):
        m = (lo + hi) / 2
        if L.minchord(L.band_box("h", c, m, th0, th1), "h", c) >= thr:
            lo = m
        else:
            hi = m
    return lo


def entry(frame, orient, key, names, c_lo, c_hi, variant, th0, th1):
    k = len(names)
    n_free = 4 - k
    thr = Fr(1) if k < 3 else (L.S_RAT - 3)
    w = halfwidth(th0, th1, thr) if k < 3 else halfwidth(th0, th1, thr)
    if k < 3 and w > L.W_ANY and variant == "any":
        w = L.W_ANY                                  # the closed-form tilt-free width
    # the band must lie inside the container: c in [w, s - w]
    # 1/1000 inside the pins' full-chord interval: at its exact endpoint the pin's chord is the
    # limit case |v| = 1/2 of minchord_box's degenerate-tilt branch (a measure-zero artefact)
    c_lo2, c_hi2 = max(Fr(c_lo) + Fr(1, 1000), w), min(Fr(c_hi) - Fr(1, 1000), L.S_RAT - w)
    checks = []
    for c in (c_lo2, (c_lo2 + c_hi2) / 2, c_hi2):
        mc = L.minchord(L.band_box(orient, c, w, th0, th1), orient, c)
        pin_terms = [L.minchord(L.pin_box(n), orient, c) for n in names]
        rhs = L.S_RAT - sum(pin_terms, Fr(0)) - n_free * mc
        checks.append(dict(c=str(c), c_float=float(c), minchord_free=str(mc),
                           pin_chords=[str(t) for t in pin_terms], rhs=str(rhs),
                           rhs_float=float(rhs), dead=bool(rhs < 0)))
    dead = all(ch["dead"] for ch in checks)
    cm = float((c_lo2 + c_hi2) / 2)
    boxes = []
    for i in range(n_free):
        b = L.band_box(orient, Fr(cm), w, th0, th1)
        boxes.append(dict(name="b%d" % i, kind="free", x=[b.x0, b.x1], y=[b.y0, b.y1],
                          theta_deg=[th0, th1], anchor=[0.5 * (b.x0 + b.x1), 0.5 * (b.y0 + b.y1),
                                                        0.5 * (th0 + th1)],
                          normal=orient, band=[float(-w), float(w)]))
    return dict(id="S01_%s_%s%s_k%d_%s" % (frame, orient, key.replace("/", "_"), k, variant),
                tag="S01", cls=frame, s_star=4.0, theorem="LINE-2 (A144) with 4 chords: docs/proofs/local_certificate_s01.md",
                line=dict(orient=orient, c_lo=str(c_lo2), c_hi=str(c_hi2), c_lo_float=float(c_lo2),
                          c_hi_float=float(c_hi2), pins_on_line=names, k=k),
                variant=variant, tilt_deg=[th0, th1], tilt_note="[90-rho, 90] is the same statement by the x<->y symmetry of a square",
                w=str(w), w_float=float(w), chord_threshold=str(thr), n_free=n_free,
                r_normal=float(w), r_along="unbounded (whole container)", rho_deg=0.5 * (th1 - th0) if th1 - th0 < 90 else 45.0,
                boxes=boxes, checks=checks, dead=dead, verdict="DEAD" if dead else "OPEN",
                checker="attempts/A144-guard-lines/code/guardline.py minchord_box (exact rationals)")


def main():
    out = []
    for frame, pins in L.CLASS_PINS.items():
        for (orient, key), (names, c_lo, c_hi) in sorted(L.pin_lines(pins).items()):
            for variant, th0, th1 in VARIANTS:
                out.append(entry(frame, orient, key, names, c_lo, c_hi, variant, th0, th1))
    # k = 0: four free squares on one line, no pin -- every frame, k0_00 included
    for variant, th0, th1 in VARIANTS:
        e = entry("any", "h", "free", [], Fr(0), L.S_RAT, variant, th0, th1)
        e["cls"] = "any (k0_00 included)"
        out.append(e)
    p = os.path.join(L.RES, "s01_basin.jsonl")
    with open(p, "w", encoding="utf-8") as fh:
        for e in out:
            fh.write(json.dumps(e) + "\n")
    print("wrote", p, len(out), "entries;", sum(1 for e in out if e["dead"]), "DEAD")
    for e in out:
        if e["variant"] == "any":
            print("  %-34s k=%d n_free=%d w=%.4f c in [%.3f, %.3f] rhs=%.6f %s" % (
                e["id"], e["line"]["k"], e["n_free"], e["w_float"], e["line"]["c_lo_float"],
                e["line"]["c_hi_float"], e["checks"][1]["rhs_float"], e["verdict"]))


if __name__ == "__main__":
    main()
