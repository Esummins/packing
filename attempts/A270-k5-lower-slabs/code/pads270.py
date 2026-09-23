"""A270 -- the k5 slab pads g2, g3, g4 for the A211 chain, EXACT (notes/slabs270.md s.2).

Setting (A211 notes/coarse_tree.md S6; A257 notes/window257.md s.1; A269 code/pads269.py).  A node at pad lam is a
statement about the dilated family F = Delta_{s0/m} P of a packing P at a side m in (s0/lam, s0]; the pad enters the
chain ONLY through Theorem FC's slot pads (lam - 1)(i + 1 + 1/sqrt2) (quick200.pad_i, rounded UP) and rule CC's lam.
The pins enter through the record: geo178.load_record makes pin k the upright role box slot_k(s0) +- dpin,
dpin = max(1/2 - a, box half-width).  F's pin k is P's upright pin dilated: centre lam*alpha + beta*s0 =
slot_k(s0) + (lam - 1)*alpha, so the record's pin box holds it iff (lam - 1)|alpha| <= dpin -- Corollary B'
(closed_disjoint_bridge.md B.2) in the chain's box form.  k5_11 and k5_16 both have max|alpha| = A_S = 3/2
(pins at (1/2,1/2), (1/2,3/2), (1/2,s-1/2), and (3/2,1/2) resp. (s-1/2,s-1/2), (s-1/2,1/2): slot_crowds.md s.0).

  pad   slab bottom            lam = s0/bottom           conservative drift (lam-1)*3/2   delta_pin for the records
  g1    3.861637 (A57 G1)      3877084/3861637           0.0060                             1e-2 (A57's, on disk)
  g2    3.847016 (A57 G2)      3877084/3847016           0.0117239                          3/250 = 0.012
  g3    3.832450 (A57 G3)      3877084/3832450           0.0174695                          9/500 = 0.018
  g4    3.82     (the window)  969271/955000 ('window')  0.0224152                          9/400 = 0.0225 (A269's)

Pads are measured from s0: pad g_k covers (bottom_k, s0] = G1 u ... u G_k (slabs do not stack, A257 s.1), so pad g4 IS
the chain's existing 'window' pad (quick200.PADS['window'] = s0/3.82 exactly; install() checks it).

    python pads270.py            -> prints the table, writes results/pads270.json
    pads270.install()            -> registers 'g2', 'g3', 'g4' in quick200.PADS (dict mutation, in process only)"""
import json
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, "..", ".."))

S0 = Fr(969271, 250000)
A_S = Fr(3, 2)                                     # max |alpha| over the pins of k5_11 and of k5_16 (read from the records)
SQ2H_UP = Fr(7071067812, 10 ** 10)                 # fastprop.SQ2H_UP (> 1/sqrt2), the constant quick200.pad_i uses
BOT = {"g1": Fr(3861637, 1000000), "g2": Fr(3847016, 1000000), "g3": Fr(383245, 100000), "g4": Fr(382, 100)}
LAM = {p: S0 / b for p, b in BOT.items()}
DPIN = {"g1": Fr(1, 100), "g2": Fr(3, 250), "g3": Fr(9, 500), "g4": Fr(9, 400)}
SUFFIX = {"g2": "_r270g2", "g3": "_r270g3", "g4": "_r270g4"}
PAD_OF_SUFFIX = {v: k for k, v in SUFFIX.items()}
SUFFIX_COVER = "_r270w4"                          # the campaign records: pad g4, box from pop270 (the 9/400 cover)
PAD_OF_SUFFIX[SUFFIX_COVER] = "g4"
DPIN_A57 = Fr(1, 100)                              # the A57 G1 records: pin cores a = 49/100, pin box half-width h = sqrt2/200
RHO_EXACT = Fr(1, 2) - Fr(33873816211, 68719476736)   # A137 / A149 exact-core LP kills: pin core a_used = 1/2 - 0.0070711


def reach(dpin, A=A_S):
    """the lowest side m a record of pin slack dpin covers: (s0/m - 1) A <= dpin  <=>  m >= s0 / (1 + dpin/A)."""
    return S0 / (1 + dpin / A)


def table():
    out = dict(s0=str(S0), A_S=str(A_S), pads={}, records={})
    for p in ("g1", "g2", "g3", "g4"):
        lam, d = LAM[p], DPIN[p]
        drift = (lam - 1) * A_S
        out["pads"][p] = dict(
            lam=str(lam), lam_f=float(lam), s_bot=str(BOT[p]), s_bot_f=float(BOT[p]), depth_below_s0=float(S0 - BOT[p]),
            fc_pad_i={str(i): float((lam - 1) * (i + 1 + SQ2H_UP)) for i in (0, 1, 2)}, cc_lam=float(lam),
            drift_3_2=str(drift), drift_3_2_f=float(drift), drift_sharp_f=float((lam - 1) * (A_S - Fr(1, 2))),
            drift_census_5_2_f=float((lam - 1) * Fr(5, 2)),
            delta_pin=str(d), delta_pin_f=float(d), margin=float(d - drift), window_statement=bool(drift <= d),
            a57_records_cover=bool(drift <= DPIN_A57), suffix=SUFFIX.get(p, "(A57's records)"))
    for name, d in (("A57 G1 records (chain box, pins +-1e-2)", DPIN_A57),
                    ("A57 LP leaves, Lemma B' with A_S = 3/2 (rho = 1e-2)", DPIN_A57),
                    ("A57 LP leaves, Lemma B' census A = 5/2 (A57 T23's own G1 slab)", None),
                    ("A137 / A149 exact-core LP kills (rho = 0.0070711), A_S = 3/2", RHO_EXACT),
                    ("A137 / A149 exact-core LP kills, census A = 5/2", None)):
        if d is None:
            rr = reach(DPIN_A57 if "A57 LP" in name else RHO_EXACT, Fr(5, 2))
        else:
            rr = reach(d)
        out["records"][name] = dict(reach_m=float(rr), covers={p: bool(rr <= BOT[p]) for p in BOT})
    return out


def install():
    """register g2, g3, g4 in the chain's pad table (quick200.PADS); 'window' must equal g4 exactly."""
    import quick200 as QP
    if QP.PADS.get("window") != LAM["g4"]:
        raise SystemExit("A270: the chain's 'window' pad is %s, not s0/3.82" % QP.PADS.get("window"))
    if QP.PADS.get("g1") != LAM["g1"]:
        raise SystemExit("A270: the chain's 'g1' pad is %s, not s0/3.861637" % QP.PADS.get("g1"))
    for p in ("g2", "g3", "g4"):
        QP.PADS[p] = LAM[p]
    return {p: float(QP.PADS[p]) for p in ("g1", "g2", "g3", "g4")}


if __name__ == "__main__":
    t = table()
    print("s0 = %s, A_S = 3/2 (k5_11, k5_16)" % t["s0"])
    for p, r in t["pads"].items():
        print("pad %s lam = %-18s = %.9f  slab (%s, s0], depth %.6f; FC pads i=0,1,2: %s; drift (3/2) %.7f (sharp %.7f, census %.7f); "
              "delta_pin %s margin %.2e; A57 1e-2 records cover it: %s" % (
                  p, r["lam"], r["lam_f"], r["s_bot_f"], r["depth_below_s0"], ", ".join("%.6f" % v for v in r["fc_pad_i"].values()),
                  r["drift_3_2_f"], r["drift_sharp_f"], r["drift_census_5_2_f"], r["delta_pin"], r["margin"], r["a57_records_cover"]))
    for k, r in t["records"].items():
        print("%-66s reach m >= %.6f  covers %s" % (k, r["reach_m"], [p for p, v in r["covers"].items() if v]))
    o = os.path.join(ATT, "results", "pads270.json")
    json.dump(t, open(o, "w", encoding="utf-8"), indent=1)
    print("wrote", os.path.relpath(o, ROOT))
