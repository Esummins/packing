"""A238 -- the TUBE LEAF (D) for a PROTECTED CLASS, i.e. A212's Lemma TUBE-LEAF in the CLASS direction v_{I_g}.

A212's tube leaf is written for trump5, where every pin is one of Trump's five simple squares and the tube used is the
SCALE ray (`certs/tube_scale_T5.71e-2_window.json`).  A protected class S is a Trump PARENT: its k_S pins are k_S of
Trump's simple squares, indices I_g in the Trump frame, and Lemma P-TREE Step 4 (docs/proofs/protected_trees.md s.2)
gives the pull-back in the SLOT(I_g) direction instead -- A83's emitter driven with `pins = I_g`, the certificates
`certs/tube_I_<I>_landing_T*_rc1o625_rt21o10000.json` swept and re-verified by A84 s.4 (frozen `certs/verify_tube.py`).

**Lemma TUBE-LEAF/S (the class form).**  Let N be a node of the class page of S (hypothesis M_S & YES(H), see
load238.py) at side s0 with all eleven squares named: the k_S pins and the N = 11 - k_S non-pin roles.  Let g be a D4
image accepted by A212's gate (trump212.gate: an injective assignment of the named squares to the squares of
g.z-hat_emb satisfying pins / pieces / named slots / NS misses), let I_g be the Trump-frame indices of the squares the
gate put on S's pins, and suppose

  (P) every pin's assigned image square is UPRIGHT and its centre is the pin's SLOT at s0 (exact, tolerance 1e-9); and
  (F) every piece of every NON-pin named role lies inside the box of half-widths (r_c', r_theta) about its assigned
      image square, r_c' = r_c - 2 (s0 - s-hat), with (r_c, r_theta) those of the SLOT(I_g) tube certificate.

Then for every m in [s-hat - T, s-hat] and every packing P' at side m satisfying M_S(m) whose dilate Delta_{s0/m}P'
satisfies N: P' = g.z-hat at m = s-hat, and no such P' exists at m < s-hat.

*Proof.*  Lemma P-TREE Step 4 verbatim with I_g in place of trump5's pin set.  M_S(m) puts P''s pin squares EXACTLY on
slots_S(m) = alpha + beta m, which is the slot(I_g) direction's pinned coordinate (w_i = 0, no radius needed) -- this
is what (P) checks the image against, and it is why the SLACK pin box of the s0 page (half-width delta_pin/sqrt2, a
relaxation used only for the tree's own branching and for the (K) certificates, Step 1) never enters the tube test.
For a free coordinate, (F) gives |c_F - c_emb| <= r_c' and the dilation algebra of A212 s.2(b) gives
|c_{P'} - (m/s-hat) c-hat| <= r_c' + 2(s0 - s-hat) = r_c; tilts are unchanged.  So g^{-1}P' is a feasible point of
Tube_{v_{I_g}}(T, (r_c, r_theta, 0)) at side m <= s-hat and Theorem T1 gives m >= s-hat.  []

The leaf is recorded TRUMP-TUBE -- a (D) discharge, never a kill: the node HOLDS the image.  A page whose every branch
is DEAD or TRUMP-TUBE has residue = the Trump image's basin, which for a Trump-parent class is exactly Lemma P-TREE
(b): the M_S packings at s-hat are the images g.z-hat, whose skeleton is trump5, not S.

This module is a SHIM over the read-only A212 module: `gate`, `images`, `box_pieces`, `meets_open_box` are A212's
untouched; `radii`, `tube`, `aligned_split` are the class forms.  Nothing in A212 is edited."""
import glob
import json
import math
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import path238                                                  # noqa: E402
path238.fix()
import trump212 as TR                                           # noqa: E402  READ-ONLY (A212)
import poly204 as P                                             # noqa: E402

FP, MB = P.FP, P.MB
S0 = MB.S_RAT
EPS = TR.EPS
PIN_SLOT_TOL = Fr(1, 10 ** 9)
CERTDIR = os.path.join(ROOT, "certs")
_R = {}

# A212's names, re-exported unchanged so this module can stand in for `trump212` inside tree212
gate = TR.gate
images = TR.images
base = TR.base
shat = TR.shat
box_pieces = TR.box_pieces
meets_open_box = TR.meets_open_box
in_piece = TR.in_piece
in_pin = TR.in_pin
theta_window = TR.theta_window
CLS = [None]                    # the class of the page being run (set by run238); None -> A212's scale tube
IG = [None]                     # the Trump-frame pin indices of the accepted image (set per tube() call)


def cert_for(I):
    """the SLOT(I) tube certificate at A60's landing radii (A84 s.4's sweep), or the scale ray when I is empty."""
    tag = "none" if not I else "_".join(str(i) for i in sorted(I))
    hit = sorted(glob.glob(os.path.join(CERTDIR, "tube_I_%s_landing_*.json" % tag)))
    if not hit:
        raise KeyError("A238: no landing tube certificate for the direction slot(I = %s) in certs/ "
                       "(A84 s.4 swept 19 pin sets; emit one with attempts/A84-protected-trees/code/tube84.py)" % (sorted(I),))
    return hit[0]


def radii(I=None):
    """the class direction's radii: dict(cert, r_c, r_theta, T, r_c_eff, r_s).  I = None -> the last tube() call's."""
    I = IG[0] if I is None else I
    key = tuple(sorted(I or []))
    if key not in _R:
        f = cert_for(key)
        c = json.load(open(f, encoding="utf-8"))
        rc, rt, T = Fr(c["r_c"]), Fr(c["r_theta"]), Fr(c["T"])
        _R[key] = dict(cert=os.path.relpath(f, ROOT).replace("\\", "/"), r_c=rc, r_theta=rt, T=T,
                       r_c_eff=rc - 2 * (S0 - shat()), r_s=Fr(c["r_s"]), I=list(key),
                       direction="slot(I = %s)" % (list(key),),
                       lemma="Lemma TUBE-LEAF/S (attempts/A238-k4-benchmark/code/tube238.py) = Lemma P-TREE Step 4 "
                             "(docs/proofs/protected_trees.md s.2) + Theorem T1 (docs/proofs/contraction_tube.md)")
    return _R[key]


def slot_of(box):
    """the pin role's slot = the centre of its (symmetric) slack box."""
    return (Fr(box[0]) + Fr(box[1])) / 2, (Fr(box[2]) + Fr(box[3])) / 2


def tube(pg, g, assign, pins):
    """the class tube test: (P) on the pins, (F) on the non-pin named roles.  Same record shape as A212's tube()."""
    sq = {q["i"]: q for q in images()[g]}
    I = sorted(pins.values())
    IG[0] = I
    R = radii(I)
    rc, rt = R["r_c_eff"] - EPS, R["r_theta"]
    rep, fits_all, worst = {}, True, None
    for pn, box in sorted(pg.pins.items()):
        q = sq[pins[pn]]
        kx, ky = slot_of(box)
        ok = bool(q["upright"]) and abs(q["cx"] - kx) <= PIN_SLOT_TOL and abs(q["cy"] - ky) <= PIN_SLOT_TOL
        rep[pn] = dict(square=q["i"], fits=ok, pinned=True, slot=[float(kx), float(ky)],
                       dx=float(abs(q["cx"] - kx)), dy=float(abs(q["cy"] - ky)), dt=0.0,
                       why="clause (P): the image square is upright and sits on this pin's slot, so the packing's pin "
                           "coordinate is the tube direction's PINNED coordinate (w = 0); no radius is used")
        fits_all &= ok
    for r, i in assign.items():
        q = sq[i]
        pcs = pg.pieces.get(r) or []
        if not pcs:
            pcs = box_pieces(pg.roles[r])
        x0, x1, y0, y1, t0, t1 = FP.pieces_hull(pcs)
        okc = q["cx"] - rc <= x0 and x1 <= q["cx"] + rc and q["cy"] - rc <= y0 and y1 <= q["cy"] + rc
        win = theta_window(q, rt)
        okt = any(all(lo <= float(bn.t0) and float(bn.t1) <= hi for bn, _ in pcs) for lo, hi, _th in win)
        dx, dy = float(max(x1 - q["cx"], q["cx"] - x0)), float(max(y1 - q["cy"], q["cy"] - y0))
        dt = min(max(abs(MB.deg_of_t(t0) - math.degrees(th)), abs(MB.deg_of_t(t1) - math.degrees(th))) for _lo, _hi, th in win)
        rep[r] = dict(square=i, fits=bool(okc and okt), fits_centre=bool(okc), fits_tilt=bool(okt), dx=dx, dy=dy,
                      dt_deg=dt, n_pieces=len(pcs), pinned=False,
                      hull=[float(v) for v in (x0, x1, y0, y1)] + [MB.deg_of_t(t0), MB.deg_of_t(t1)])
        fits_all &= (okc and okt)
        ex = max(dx / float(rc), dy / float(rc), math.radians(dt) / float(rt))
        if worst is None or ex > worst[1]:
            worst = (r, ex)
    return dict(fits=bool(fits_all), radii={k: (str(v) if isinstance(v, Fr) else v) for k, v in R.items()},
                r_c_eff_float=float(R["r_c_eff"]), roles=rep, worst=worst, g=g, I=I, cls=getattr(pg, "cls", None),
                assignment=dict(assign), pins=dict(pins), n_anon=pg.n_free - len(pg.role_cell),
                lemma=R["lemma"], direction=R["direction"])


def aligned_split(pg, g, assign):
    """A212's cut at the tube wall, with THIS class's radii (the pins are never cut: they carry no excess)."""
    R = radii()
    rc, rt = R["r_c_eff"] - EPS, R["r_theta"]
    sq = {q["i"]: q for q in images()[g]}
    best = None
    for r, i in assign.items():
        q = sq[i]
        pcs = pg.pieces.get(r) or []
        if not pcs:
            continue
        x0, x1, y0, y1, t0, t1 = FP.pieces_hull(pcs)
        for dim, (u0, u1, lo, hi, scale) in (("x", (x0, x1, q["cx"] - rc, q["cx"] + rc, float(rc))),
                                             ("y", (y0, y1, q["cy"] - rc, q["cy"] + rc, float(rc)))):
            for m, side, ex in ((hi, "lo", float(u1 - hi) / scale), (lo, "hi", float(lo - u0) / scale)):
                if ex > 0 and u0 < m < u1 and (best is None or ex > best["excess"]):
                    best = dict(role=r, dim=dim, m=m, side=side, excess=round(ex, 4), square=i)
        win = theta_window(q, rt)
        lo, hi, th = min(win, key=lambda w: abs(w[2] - MB.deg_of_t((t0 + t1) / 2) * math.pi / 180))
        for mf, side, ex in ((hi, "lo", (float(t1) - hi) / float(rt)), (lo, "hi", (lo - float(t0)) / float(rt))):
            m = Fr(round(mf * 10 ** 12)) / 10 ** 12
            if ex > 0 and t0 < m < t1 and (best is None or ex > best["excess"]):
                best = dict(role=r, dim="t", m=m, side=side, excess=round(ex, 4), square=i)
    return best


if __name__ == "__main__":
    for I in ([0, 2, 3, 5], [0, 1, 3], [0, 1, 2, 3], [0, 1, 2, 5]):
        R = radii(I)
        print("I = %-12s T %-8s r_c %-8s r_c' %-10.7f r_theta %-8s  %s" % (
            I, float(R["T"]), float(R["r_c"]), float(R["r_c_eff"]), float(R["r_theta"]), R["cert"]))
