#!/usr/bin/env python3
"""
make_param.py -- A56 T2(A).  base case-measure-certificate-v1  ->  parametric-kill-certificate-v1.

Every geometric object of the certificate becomes an affine function of the side s:

    core centre   k(s) = (akx + bkx*s, aky + bky*s),   b in {0,1}   (the slot's anchor)
    atom          p(s) = (ax  + bx *s, ay  + by *s),   b in [0,1] cap Q  (a MODELLING CHOICE, P3)

with the offsets DERIVED so that the s0-specialisation is the identity:  a = coord_s0 - b*s0
(canary C1, asserted here with Fractions and re-checked by specialize.py + the unmodified
A53 verify_case.py).

CORE anchors are forced, not chosen: kx must be one of 1/2, 3/2, 5/2 (L-anchored, b=0) or
s0-1/2, s0-3/2, s0-5/2 (R-anchored, b=1); anything else is an error.  The derived (alpha,beta)
pairs are cross-checked against A53 results/name_to_slots.json when the class name is known.

ATOM anchors are the free part (soundness.md P3: "anchor choice is completeness, never
soundness" -- a bad anchoring can only make the verification FAIL).  Rules:
    default  ("nearest-wall")   b = 1 iff coord > s0/2, else b = 0
    --beta-mid W ("mid-band")   b = 1/2 for coord in [s0/2 - W, s0/2 + W]; nearest-wall outside
    --overrides FILE            JSON {"<cert name>": {"<atom index>": [bx, by]}} beats both

Usage:
    python make_param.py BASE.json -o OUT.json [--name k6_05] [--beta-mid [W]] [--overrides f.json]
"""
import argparse
import json
import os
import sys
from fractions import Fraction as F

S0 = F(969271, 250000)
S_LO = F(191, 50)

L_SLOTS = {F(1, 2), F(3, 2), F(5, 2)}
R_SLOTS = {S0 - F(1, 2), S0 - F(3, 2), S0 - F(5, 2)}


def rat(x):
    if isinstance(x, F):
        return x
    if isinstance(x, bool):
        raise ValueError("bool is not a number")
    if isinstance(x, int):
        return F(x)
    if isinstance(x, float):
        raise ValueError(f"float {x!r} in certificate: numbers must be exact strings or ints")
    return F(str(x).strip())


def core_anchor(coord):
    """(alpha, beta) for a core coordinate; beta in {0,1}, alpha in {+-1/2,+-3/2,+-5/2}."""
    if coord in L_SLOTS:
        return coord, F(0)
    if coord in R_SLOTS:
        return coord - S0, F(1)
    raise ValueError(f"core coordinate {coord} (~{float(coord)}) is not a slot of the s0 census")


def atom_anchor(coord, mid_w, thr=None):
    """thr = the L/R corridor threshold for this axis (default s0/2, the nearest-wall rule)."""
    T = S0 / 2 if thr is None else thr
    if mid_w is not None and (T - mid_w) <= coord <= (T + mid_w):
        b = F(1, 2)
    else:
        b = F(1) if coord > T else F(0)
    return coord - b * S0, b


def gap_threshold(coords, lo, hi):
    """The corridor rule: put the L/R threshold in the MIDDLE OF THE WIDEST GAP of the
    certificate's own coordinates inside the search band [lo,hi].  The two anchored diagrams of a
    stratum are separated by a corridor; splitting there keeps every local cluster of atoms
    rigid, which is what the coverage of a placement next to that cluster needs.  Falls back to
    s0/2 when the band contains fewer than two coordinates."""
    v = sorted(set(c for c in coords if lo <= c <= hi))
    if len(v) < 2:
        return S0 / 2
    best = max(range(len(v) - 1), key=lambda i: v[i + 1] - v[i])
    return (v[best] + v[best + 1]) / 2


def build(base, name=None, mid_w=None, overrides=None, slots=None, thr=None, gap_band=None):
    if base.get("format") != "case-measure-certificate-v1":
        raise ValueError(f"unexpected format {base.get('format')!r}")
    if base.get("symmetry"):
        raise ValueError("symmetry expansion is s-dependent; not supported (library has none)")
    s = rat(base["s"])
    if s != S0:
        raise ValueError(f"base certificate is at s = {s}, expected s0 = {S0}")
    n = int(base.get("n", 11))
    hyp = base.get("hypotheses", {}) or {}
    if hyp.get("nofams"):
        raise ValueError("nofams are not supported (library has none)")

    cores = []
    for c in hyp.get("cores", []):
        kx, ky = rat(c["kx"]), rat(c["ky"])
        axk, bxk = core_anchor(kx)
        ayk, byk = core_anchor(ky)
        assert axk + bxk * S0 == kx and ayk + byk * S0 == ky, "C1 identity (core)"
        cores.append({"akx": str(axk), "bkx": str(bxk), "aky": str(ayk), "bky": str(byk),
                      "tm": str(rat(c["tm"])), "a": str(rat(c["a"])),
                      "s0_kx": str(kx), "s0_ky": str(ky)})

    if slots is not None and name in slots:
        want = sorted((F(str(x)), F(str(y))) for x, y in slots[name])
        got = sorted((rat(c["s0_kx"]), rat(c["s0_ky"])) for c in cores)
        if want != got:
            raise ValueError(f"cores of {name} disagree with name_to_slots: {got} vs {want}")

    raw = base["atoms"]
    if raw and isinstance(raw[0], dict):
        pts = [(rat(a["x"]), rat(a["y"])) for a in raw]
        ws = [rat(a["w"]) for a in raw]
    else:
        pts = [(rat(x), rat(y)) for x, y in raw]
        ws = [rat(w) for w in base["weights"]]
    if len(pts) != len(ws):
        raise ValueError("atoms/weights length mismatch")

    thr_x = thr_y = None
    if thr is not None:
        thr_x, thr_y = thr
    elif gap_band is not None:
        lo, hi = gap_band
        thr_x = gap_threshold([p[0] for p in pts] + [rat(c["s0_kx"]) for c in cores], lo, hi)
        thr_y = gap_threshold([p[1] for p in pts] + [rat(c["s0_ky"]) for c in cores], lo, hi)

    ov = (overrides or {}).get(name or "", {}) if overrides else {}
    atoms = []
    n_ov = 0
    for i, ((px, py), w) in enumerate(zip(pts, ws)):
        if w < 0:
            raise ValueError("negative weight")
        key = str(i)
        if key in ov:
            bx, by = F(str(ov[key][0])), F(str(ov[key][1]))
            n_ov += 1
        else:
            _, bx = atom_anchor(px, mid_w, thr_x)
            _, by = atom_anchor(py, mid_w, thr_y)
        if not (0 <= bx <= 1 and 0 <= by <= 1):
            raise ValueError(f"atom {i}: beta out of [0,1]")
        ax, ay = px - bx * S0, py - by * S0
        assert ax + bx * S0 == px and ay + by * S0 == py, "C1 identity (atom)"
        # admissibility on the whole window (soundness.md P3): 0 <= p(s) <= s for all s in W
        for a, b, c in ((ax, bx, px), (ay, by, py)):
            if a + b * S_LO < 0 or a + b * S0 < 0:
                raise ValueError(f"atom {i} leaves [0,s]^2 at the low end of W")
            if a + b * S_LO > S_LO or a + b * S0 > S0:
                raise ValueError(f"atom {i} leaves [0,s]^2 at the high end of W")
        atoms.append({"ax": str(ax), "bx": str(bx), "ay": str(ay), "by": str(by), "w": str(w)})

    total = sum(ws, F(0))
    budget = int(base.get("budget", n))
    if budget != n - len(cores):
        raise ValueError(f"budget {budget} != n - #cores")
    if total >= budget:
        raise ValueError(f"total {total} >= budget {budget}")

    return {
        "format": "parametric-kill-certificate-v1",
        "name": name,
        "n": n,
        "budget": budget,
        "s0": str(S0),
        "s_window": [str(S_LO), str(S0)],
        "total": str(total),
        "atoms": atoms,
        "hypotheses": {"cores": cores, "nofams": []},
        "anchoring": {"rule": ("threshold" if thr is not None else
                               ("gap" if gap_band is not None else
                                ("mid-band" if mid_w is not None else "nearest-wall"))),
                      "threshold_x": str(thr_x) if thr_x is not None else str(S0 / 2),
                      "threshold_y": str(thr_y) if thr_y is not None else str(S0 / 2),
                      "threshold_x_float": float(thr_x if thr_x is not None else S0 / 2),
                      "threshold_y_float": float(thr_y if thr_y is not None else S0 / 2),
                      "mid_band_half_width": str(mid_w) if mid_w is not None else None,
                      "gap_band": [str(g) for g in gap_band] if gap_band else None,
                      "n_overrides": n_ov},
        "provenance": {"tool": "A56 make_param.py", "base": base.get("provenance"),
                       "base_claim": base.get("claim")},
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("base")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--name", default=None)
    ap.add_argument("--beta-mid", nargs="?", const="1/2", default=None,
                    help="use beta = 1/2 for coordinates within W of s0/2 (default W = 1/2)")
    ap.add_argument("--overrides", default=None)
    ap.add_argument("--beta-threshold", default=None,
                    help="TX[,TY]: beta = 1 iff coord > T (default T = s0/2, the nearest-wall rule)")
    ap.add_argument("--beta-gap", nargs="?", const="19/10,49/20", default=None,
                    help="LO,HI: put the threshold in the widest gap of the certificate's own "
                         "coordinates inside [LO,HI] (default band [1.9, 2.45])")
    ap.add_argument("--slots", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                    "..", "..", "A53-simple-strata", "results",
                                                    "name_to_slots.json"))
    a = ap.parse_args(argv)

    base = json.load(open(a.base))
    name = a.name or os.path.splitext(os.path.basename(a.base))[0]
    mid_w = F(a.beta_mid) if a.beta_mid is not None else None
    ov = json.load(open(a.overrides)) if a.overrides else None
    slots = None
    if a.slots and os.path.exists(a.slots):
        slots = json.load(open(a.slots))
    thr = None
    if a.beta_threshold:
        parts = [F(z) for z in a.beta_threshold.split(",")]
        thr = (parts[0], parts[-1])
    gap_band = None
    if a.beta_gap:
        parts = [F(z) for z in a.beta_gap.split(",")]
        gap_band = (parts[0], parts[1])
    out = build(base, name=name, mid_w=mid_w, overrides=ov, slots=slots, thr=thr,
                gap_band=gap_band)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"{name}: {len(out['atoms'])} atoms, {len(out['hypotheses']['cores'])} cores, "
          f"budget {out['budget']}, anchoring {out['anchoring']['rule']} -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
