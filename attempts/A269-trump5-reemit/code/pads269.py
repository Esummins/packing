"""A269 -- the two window pads for trump5 and the pin slack of each re-emitted record set, EXACT (notes/trump5_row.md s.1).

Setting (A211 notes/coarse_tree.md S6; A257 notes/window257.md s.1).  A node at pad lam is a statement about the dilated
family F = Delta_{s0/m} P of a packing P at a side m in the slab (s0/lam, s0]; the pad enters the chain ONLY through
Theorem FC's slot pads and CC's lam -- never through the pins.  The pins enter through the record's pin cores: F's pin
k is P's corner square dilated, an UPRIGHT unit square centred at lam*alpha + beta*s0 = slot_k(s0) + (lam - 1)*alpha,
so the record's pin box slot_k(s0) +- delta_pin contains it iff (lam - 1)|alpha| <= delta_pin (Corollary B', A = 3/2
for trump5: |alpha| in {1/2, 3/2}).  A pad verdict is a window statement ONLY when that holds for the pad's lam.

  pad A  "tube"    slab (3.832084, s0]   lam_A = s0/3.832084 = 969271/958021   records *_r269a, delta_pin = 9/500
  pad B  "window"  slab (3.82, s0]       lam_B = s0/3.82     = 969271/955000   records *_r269b, delta_pin = 9/400

Why 1.8e-2 for pad A and not 1e-2: Lemma SEAM's reach is s-hat - min(T_tube, T_K(delta_pin)); at 1e-2 T_K = 0.025676
binds and the tube slab stops at 3.851408 (THREE slabs); at >= 0.017615 T_tube = 9/200 binds and the tube slab reaches
3.832084 (the TWO-slab cover).  1.8e-2 is the first round number above 0.017615 (drift at lam_A: 0.0176143).
Why 9/400 for pad B and not 1.8e-2: the drift at lam_B is (lam_B - 1)*3/2 = 42813/1910000 = 0.0224152 > 1.8e-2, so a
1.8e-2 record at pad B is NOT a window statement below m = 3.83111; 9/400 = 0.0225 clears it by 8.5e-5.

    python pads269.py            -> prints the table and writes results/pads269.json
    pads269.install()            -> registers pad "tube" in quick200.PADS and ray256.PADS (dict mutation, in process)"""
import json
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, "..", ".."))

S0 = Fr(969271, 250000)
A_T5 = Fr(3, 2)                                    # max |alpha| over trump5's pins {0, 1, 2, 3, 5}
T_TUBE = Fr(9, 200)                                # certs/tube_slot_T4.5e-2_landing.json (verify_tube.py)
S_BOT = {"tube": Fr(3832084, 1000000), "window": Fr(382, 100)}
LAM = {p: S0 / b for p, b in S_BOT.items()}
DPIN = {"tube": Fr(9, 500), "window": Fr(9, 400)}
SUFFIX = {"tube": "_r269a", "window": "_r269b"}
PAD_OF_SUFFIX = {v: k for k, v in SUFFIX.items()}


def shat():
    for p in (os.path.join(ROOT, "attempts", "A211-coarse-tree", "code"), os.path.join(ROOT, "attempts", "A256-trump5-passes", "code")):
        if p not in sys.path:
            sys.path.append(p)
    import trump256 as TR                          # READ-ONLY (A256): s-hat from A03's 60-digit rational
    return Fr(TR.shat())


def T_K(d, sh):
    """Lemma SEAM (contraction_tube.md s.4.1): the depth below s-hat the (K) side reaches at pin slack d."""
    return (Fr(2, 3) * d * sh - (S0 - sh)) / (1 + Fr(2, 3) * d)


def table():
    sh = shat()
    out = dict(s0=str(S0), shat=float(sh), A=str(A_T5), T_tube=str(T_TUBE), pads={})
    d_star = A_T5 * (T_TUBE + (S0 - sh)) / (sh - T_TUBE)          # T_K(d*) = T_tube exactly
    out["delta_star_tube_binds"] = float(d_star)
    for p in ("tube", "window"):
        lam, d = LAM[p], DPIN[p]
        drift = (lam - 1) * A_T5
        Tp = sh - S_BOT[p]
        out["pads"][p] = dict(lam=str(lam), lam_f=float(lam), s_bot=str(S_BOT[p]), s_bot_f=float(S_BOT[p]),
                              delta_pin=str(d), drift_3_2=str(drift), drift_3_2_f=float(drift), drift_1_2_f=float((lam - 1) / 2),
                              window_statement=bool(drift < d), margin=float(d - drift), T_prime=float(Tp), T_K=float(T_K(d, sh)),
                              tube_kill_possible=bool(Tp <= T_TUBE and Tp <= T_K(d, sh)), suffix=SUFFIX[p])
    return out


def install():
    """register pad 'tube' (lam_A) in the chain's pad tables; 'window' (lam_B) is already there with the same value."""
    import quick200 as QP
    import ray256 as RAY
    for tab in (QP.PADS, RAY.PADS):
        tab["tube"] = LAM["tube"]
        if tab.get("window") != LAM["window"]:
            raise SystemExit("A269: the chain's 'window' pad is %s, not s0/3.82" % tab.get("window"))
    return dict(tube=float(QP.PADS["tube"]), window=float(QP.PADS["window"]))


if __name__ == "__main__":
    t = table()
    print("s0 = %s, s-hat = %.15f, T_tube = 9/200, delta* (T_K = T_tube) = %.7f" % (t["s0"], t["shat"], t["delta_star_tube_binds"]))
    for p, r in t["pads"].items():
        print("pad %-6s lam = %s = %.9f  slab (%s, s0]  delta_pin %s: drift(3/2) %.7f -> window statement %s (margin %.2e); "
              "T' %.7f, T_K %.7f, TUBE-KILL possible %s" % (p, r["lam"], r["lam_f"], r["s_bot_f"], r["delta_pin"], r["drift_3_2_f"],
                                                             r["window_statement"], r["margin"], r["T_prime"], r["T_K"], r["tube_kill_possible"]))
    o = os.path.join(ATT, "results", "pads269.json")
    os.makedirs(os.path.dirname(o), exist_ok=True)
    json.dump(t, open(o, "w", encoding="utf-8"), indent=1)
