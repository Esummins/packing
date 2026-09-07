"""A131 -- INDEPENDENT checker for `pin-clip-kill-certificate-v1`.

Written so that it shares no decision code with `pinclip.py`.  `pinclip.dead_q` decides
"the unit square at centre offset d meets the pin core at EVERY tilt of the sub-bin" from the
theta-sinusoid form (max of `P cos + Q sin` at an endpoint or the interior critical point).  This
checker re-derives the same test in the t = tan(theta/2) parametrisation instead:

    f(t) = (P(1 - t^2) + 2Qt) / (1 + t^2),
    f'(t) = 0  <=>  Q t^2 + 2P t - Q = 0,

so an interior extremum exists iff `g(t) = Q t^2 + 2P t - Q` changes sign across [t0, t1], and at
such a t the value is +-sqrt(P^2 + Q^2), compared as `P^2 + Q^2 < 1/4`.  Endpoint values are exact
rationals.  Everything is `Fraction`; there is no epsilon in the decision.

What the checker verifies, per certificate:
  1. the pin slots equal the class's own slots (`A53-simple-strata/results/name_to_slots.json`) --
     the certificate cannot invent its pins;
  2. `a_pin = 1/2 - pin_delta` and `pin_delta` matches the node's recorded `pin_delta`;
  3. the rational outer box CONTAINS the node's recorded float box;
  4. the sub-bins tile [t_first, t_last] with no gap, and that t-interval covers the node's own
     tilt range (checked in floats against the cover's own 2^-24 outward rounding);
  5. each sub-bin's trace REPLAYS: every "slab" step's four corner points are dead against the
     named pin over that sub-bin (D_i is convex, so that proves the whole slab dead), the
     "container" step is the exact intersection with [w_min/2, s - w_min/2]^2, and the sub-bin
     terminates EMPTY;
  6. every sub-bin ends EMPTY.

    python code/checkclip131.py certs/backlog/<id>.clipkill.json ...
    python code/checkclip131.py --all
"""
import argparse, glob, json, math, os, sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
A53 = os.path.abspath(os.path.join(BASE, "..", "A53-simple-strata"))

HALF = Fr(1, 2)
QUARTER = Fr(1, 4)


def cs(t):
    tt = t * t
    return (1 - tt) / (1 + tt), 2 * t / (1 + tt)


def _max_lt_half(P, Q, t0, t1, c0, s0, c1, s1):
    """max over the sub-bin of (P cos theta + Q sin theta) < 1/2, in the t-parametrisation.

    f(t) = (P(1-t^2) + 2Qt)/(1+t^2)  has  f'(t) = -2 g(t) / (1+t^2)^2  with
    g(t) = Q t^2 + 2 P t - Q, so f' has the OPPOSITE sign to g.  An interior MAXIMUM (f' going
    + -> -) is therefore g going - -> +, and only then is the maximum +sqrt(P^2+Q^2); an interior
    minimum (g going + -> -) leaves the maximum at an endpoint.  Distinguishing the two matters:
    treating every interior extremum as a maximum rejects 23 of 132 sound certificates."""
    g0 = Q * t0 * t0 + 2 * P * t0 - Q
    g1 = Q * t1 * t1 + 2 * P * t1 - Q
    if g0 <= 0 <= g1 and not (g0 == 0 and g1 == 0):
        return P * P + Q * Q < QUARTER
    v0 = P * c0 + Q * s0
    v1 = P * c1 + Q * s1
    return (v0 if v0 > v1 else v1) < HALF


def dead(dx, dy, a, t0, t1, c0, s0, c1, s1, wmin):
    if not (-(wmin / 2 + a) < dx < wmin / 2 + a):
        return False
    if not (-(wmin / 2 + a) < dy < wmin / 2 + a):
        return False
    for (P, Q) in ((dx - a, dy - a), (-dx - a, -dy - a),
                   (dy - a, -dx - a), (-dy - a, dx - a)):
        if not _max_lt_half(P, Q, t0, t1, c0, s0, c1, s1):
            return False
    return True


def check(path, slots_all):
    c = json.load(open(path))
    errs = []
    if c.get("format") != "pin-clip-kill-certificate-v1":
        return ["bad format tag"], c
    cls = c["class"]
    # (1) pins are the class's own slots
    want = [[Fr(str(x)), Fr(str(y))] for x, y in slots_all[cls]]
    got = [[Fr(p[0]), Fr(p[1])] for p in c["pins"]]
    if want != got:
        errs.append("pin slots do not match the class")
    # (2) a_pin
    delta = Fr(c["pin_delta"])
    if Fr(c["a_pin"]) != HALF - delta:
        errs.append("a_pin != 1/2 - pin_delta")
    if abs(float(delta) - float(c["node_pin_delta"])) > 1e-15:
        errs.append("pin_delta != the node's recorded pin_delta")
    s_rat = Fr(c["s"])
    a = Fr(c["a_pin"])
    # (3) the rational outer box contains the float box
    b = c["box"]
    ox0, ox1, oy0, oy1 = (Fr(v) for v in c["box_rational_outer"])
    if not (ox0 <= Fr(str(b["x0"])) and Fr(str(b["x1"])) <= ox1 and
            oy0 <= Fr(str(b["y0"])) and Fr(str(b["y1"])) <= oy1):
        errs.append("rational outer box does not contain the recorded box")
    # (4) sub-bins tile, and cover the node's tilt range
    bins = c["sub_bins"]
    prev = None
    for sb in bins:
        t0, t1 = Fr(sb["t0"]), Fr(sb["t1"])
        if t1 <= t0:
            errs.append("empty sub-bin")
        if prev is not None and t0 != prev:
            errs.append("sub-bins do not tile")
        prev = t1
    tf, tl = Fr(bins[0]["t0"]), Fr(bins[-1]["t1"])
    if not (float(tf) <= math.tan(math.radians(b["th0"]) / 2) + 1e-15 and
            math.tan(math.radians(b["th1"]) / 2) <= float(tl) + 1e-15):
        errs.append("sub-bins do not cover the node's tilt range")
    # (5)/(6) replay
    for k, sb in enumerate(bins):
        t0, t1 = Fr(sb["t0"]), Fr(sb["t1"])
        c0, s0 = cs(t0)
        c1, s1 = cs(t1)
        wmin = min(c0 + s0, c1 + s1)
        rect = [ox0, ox1, oy0, oy1]
        done = False
        for st in sb["trace"]:
            op = st["op"]
            if op == "container":
                if Fr(st["w_min"]) != wmin:
                    errs.append(f"bin {k}: w_min mismatch")
                exp = [max(rect[0], wmin / 2), min(rect[1], s_rat - wmin / 2),
                       max(rect[2], wmin / 2), min(rect[3], s_rat - wmin / 2)]
                if [Fr(v) for v in st["rect"]] != exp:
                    errs.append(f"bin {k}: container step is not the exact intersection")
                rect = exp
            elif op == "slab":
                i = st["pin"]
                px, py = Fr(c["pins"][i][0]), Fr(c["pins"][i][1])
                frm, to = Fr(st["from"]), Fr(st["to"])
                side = st["side"]
                idx = {"x0": 0, "x1": 1, "y0": 2, "y1": 3}[side]
                if Fr(rect[idx]) != frm:
                    errs.append(f"bin {k}: slab 'from' does not match the current rect")
                if side in ("x0", "x1"):
                    pts = [(frm, rect[2]), (frm, rect[3]), (to, rect[2]), (to, rect[3])]
                    if side == "x0" and not (frm <= to <= rect[1]):
                        errs.append(f"bin {k}: x0 slab out of range")
                    if side == "x1" and not (rect[0] <= to <= frm):
                        errs.append(f"bin {k}: x1 slab out of range")
                else:
                    pts = [(rect[0], frm), (rect[1], frm), (rect[0], to), (rect[1], to)]
                    if side == "y0" and not (frm <= to <= rect[3]):
                        errs.append(f"bin {k}: y0 slab out of range")
                    if side == "y1" and not (rect[2] <= to <= frm):
                        errs.append(f"bin {k}: y1 slab out of range")
                for (qx, qy) in pts:
                    if not dead(qx - px, qy - py, a, t0, t1, c0, s0, c1, s1, wmin):
                        errs.append(f"bin {k}: slab corner ({qx},{qy}) is NOT dead vs pin {i}")
                rect[idx] = to
            elif op == "empty":
                i = st["pin"]
                px, py = Fr(c["pins"][i][0]), Fr(c["pins"][i][1])
                r = [Fr(v) for v in st["rect"]]
                if r != rect:
                    errs.append(f"bin {k}: 'empty' step rect does not match the current rect")
                for qx in (r[0], r[1]):
                    for qy in (r[2], r[3]):
                        if not dead(qx - px, qy - py, a, t0, t1, c0, s0, c1, s1, wmin):
                            errs.append(f"bin {k}: 'empty' corner ({qx},{qy}) NOT dead vs pin {i}")
                done = True
                break
            elif op == "collapse":
                if st["axis"] == "x" and rect[1] > rect[0]:
                    errs.append(f"bin {k}: claimed x-collapse but x1 > x0")
                if st["axis"] == "y" and rect[3] > rect[2]:
                    errs.append(f"bin {k}: claimed y-collapse but y1 > y0")
                done = True
                break
            else:
                errs.append(f"bin {k}: unknown op {op}")
        if not done:
            errs.append(f"bin {k}: trace does not terminate in EMPTY")
    return errs, c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    paths = a.paths or (sorted(glob.glob(os.path.join(BASE, "certs", "backlog", "*.clipkill.json")))
                        if a.all else [])
    slots_all = json.load(open(os.path.join(A53, "results", "name_to_slots.json")))
    ok = bad = 0
    failures = []
    for p in paths:
        errs, c = check(p, slots_all)
        if errs:
            bad += 1
            failures.append(dict(cert=os.path.basename(p), errors=errs[:6]))
            print(f"FAIL {os.path.basename(p)}: {errs[:3]}")
        else:
            ok += 1
    print(f"checked {ok + bad} certificates: {ok} PASS, {bad} FAIL")
    if a.all:
        json.dump(dict(checked=ok + bad, passed=ok, failed=bad, failures=failures),
                  open(os.path.join(BASE, "results", "checkclip131.json"), "w"), indent=1)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
