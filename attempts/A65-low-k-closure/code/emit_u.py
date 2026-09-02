"""
A65 T1: emit the 11 Theorem-U re-insertion certificates (obligation U-O1) and compute the
exact side-condition ledger (core containment margins + nofam-to-basin containment).

Spec: docs/proofs/unique_transfer.md section 4.  Per square i: remove it, core the other 10
at slack half-side a = 1/2 - delta (delta = 1e-4), budget 1, one nofams zone of half-width
1e-3 around the dilated missing square's (c, t); side s'' = 3877083591023/10^12 (the A03
tight-certificate side: rational, above s-hat by ~1.0e-9, inside T1's isolating interval,
and REALISED by a verified packing -- certs/trump11_certificate_tight.json).

Rational dilated coordinates = the tight certificate's own centres/tilts (constructed as
lambda*c-hat rounded to 1e-14, t-hat's convergent 2731751/7468508).  Truth anchor for the
side conditions: A22 krawczyk_cert.json z0 with ||z-hat - z0||_inf <= r_0 = 1e-50
(A22 notes.md section 3), coordinates (cx, cy, theta)_i, s.

Everything on the decision path is fractions.Fraction; the single non-rational evaluation
(|2*atan(t_rat) - theta0| for the common tilt) uses mpmath at 80 digits with an outward
slop of 1e-13 -- same trust tier as A22's own interval arithmetic, noted in the ledger.

Writes: certs/u_reinsert_{i}.json (i = 00..10), results/u_ledger.json.
"""
import json, os, sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))

DELTA = F(1, 10000)          # core slack: a = 1/2 - delta
A_CORE = F(1, 2) - DELTA     # 4999/10000
HW = F(1, 1000)              # nofam half-width (centre and t)
RBASIN = F(3, 2000)          # theta_t_transfer.md X.3
R0 = F(1, 10**50)            # A22 enclosure radius

def main():
    tight = json.load(open(os.path.join(ROOT, "certs", "trump11_certificate_tight.json")))
    kraw = json.load(open(os.path.join(ROOT, "attempts", "A22-local-rigidity",
                                       "results", "krawczyk_cert.json")))
    s2 = F(tight["side"])                       # s'' = 3877083591023/10^12
    sq = [{k: F(q[k]) for k in ("cx", "cy", "t")} for q in tight["squares"]]
    z0 = [F(x) for x in kraw["z0"]]
    assert F(kraw["r_0"]) == R0
    s_lo, s_hi = z0[33] - R0, z0[33] + R0        # s-hat enclosure
    assert s_hi < s2, "s'' must lie strictly above the s-hat enclosure"
    lam_lo, lam_hi = s2 / s_hi, s2 / s_lo        # lambda = s''/s-hat enclosure
    assert lam_lo > 1

    # ---- tilt evaluation (the one non-rational step, mpmath dps=80, outward slop 1e-13)
    import mpmath as mp
    mp.mp.dps = 80
    t_rat = sq[6]["t"]                            # common convergent 2731751/7468508
    th0 = z0[3 * 6 + 2]                           # A22 rational theta for square 6
    for j in range(6, 11):
        assert sq[j]["t"] == t_rat and z0[3 * j + 2] == th0
    dth_f = abs(2 * mp.atan(mp.mpf(t_rat.numerator) / t_rat.denominator)
                - mp.mpf(th0.numerator) / th0.denominator)
    dt_f = abs(mp.tan(mp.mpf(th0.numerator) / th0.denominator / 2)
               - mp.mpf(t_rat.numerator) / t_rat.denominator)
    assert dth_f < 1e-14 and dt_f < 1e-14, (dth_f, dt_f)
    DTH_TILT = F(1, 10**13) + 2 * R0              # |theta_core - theta-hat_j| bound, outward
    DT_TILT = F(1, 10**13)                        # |t_rat - tan(theta0/2)| bound, outward
    # uprights: A22 z0 thetas ~ 1e-71; |theta-hat_j| <= |z0 theta| + r0
    DTH_UP = max(abs(z0[3 * j + 2]) for j in range(6)) + R0

    ledger = {"s2": str(s2), "lambda_interval": [str(lam_lo), str(lam_hi)],
              "delta": str(DELTA), "a_core": str(A_CORE), "hw_nofam": str(HW),
              "rBasin": str(RBASIN),
              "tilt_eval": {"method": "mpmath dps=80, outward slop 1e-13",
                            "dtheta_bound": str(DTH_TILT), "dt_bound": str(DT_TILT),
                            "dtheta_upright_bound": str(DTH_UP)},
              "cores": [], "nofams": []}

    # ---- per-square core containment margin:  K_j inside Delta_lambda(zhat_j) interior
    # margin >= 1/2 - a*(cos+sin)(dtheta) - (|off_x| + |off_y|),  cos+sin <= 1 + dtheta
    for j in range(11):
        cx, cy = sq[j]["cx"], sq[j]["cy"]
        zx_lo, zx_hi = z0[3 * j] - R0, z0[3 * j] + R0
        zy_lo, zy_hi = z0[3 * j + 1] - R0, z0[3 * j + 1] + R0
        # interval of lambda*c-hat (all coordinates positive)
        lx_lo, lx_hi = lam_lo * zx_lo, lam_hi * zx_hi
        ly_lo, ly_hi = lam_lo * zy_lo, lam_hi * zy_hi
        off = max(abs(cx - lx_lo), abs(cx - lx_hi)) + max(abs(cy - ly_lo), abs(cy - ly_hi))
        dth = DTH_TILT if j >= 6 else DTH_UP
        margin = F(1, 2) - A_CORE * (1 + dth) - off
        assert margin > 0, (j, float(margin))
        ledger["cores"].append({"j": j, "offset_bound": str(off),
                                "margin_lower_bound": str(margin),
                                "margin_float": float(margin)})

    # ---- per-square nofam-to-basin containment:  lambda^{-1} F_i inside the rBasin box
    for i in range(11):
        cx, cy = sq[i]["cx"], sq[i]["cy"]
        zx_lo, zx_hi = z0[3 * i] - R0, z0[3 * i] + R0
        zy_lo, zy_hi = z0[3 * i + 1] - R0, z0[3 * i + 1] + R0
        # exempt centre after division by lambda: [(c-hw)/lam_hi, (c+hw)/lam_lo]
        dev_x = max(abs((cx - HW) / lam_hi - zx_hi), abs((cx + HW) / lam_lo - zx_lo))
        dev_y = max(abs((cy - HW) / lam_hi - zy_hi), abs((cy + HW) / lam_lo - zy_lo))
        if i >= 6:
            dev_t = HW + DT_TILT + R0   # |t_Q - tan(theta-hat/2)| (r0 via X.1 contraction)
            t_ints = [[str(t_rat - HW), str(t_rat + HW)]]
        else:
            # branch t in [0, hw]: dev_t = hw + |t-hat| <= hw + dtheta_up.
            # branch t in [1-hw, 1]: equivalent tilt theta' with
            # |theta'| <= 2*atan(hw/(2-hw)) <= 2*hw/(2-hw); t' = tan(|theta'|/2) <= x + x^3,
            # x = hw/(2-hw)  (exact rational chain, atan x <= x <= tan x)
            x = HW / (2 - HW)
            dev_t = max(HW + DTH_UP, x + x ** 3 + DTH_UP)
            t_ints = [["0", str(HW)], [str(1 - HW), "1"]]
        assert dev_x < RBASIN and dev_y < RBASIN and dev_t < RBASIN, (i,)
        ledger["nofams"].append({"i": i, "dev_x": str(dev_x), "dev_y": str(dev_y),
                                 "dev_t": str(dev_t),
                                 "dev_float": [float(dev_x), float(dev_y), float(dev_t)],
                                 "t_intervals": t_ints})

    # ---- emit the 11 certificates
    outdir = os.path.join(BASE, "certs")
    os.makedirs(outdir, exist_ok=True)
    for i in range(11):
        cores = [{"kx": str(sq[j]["cx"]), "ky": str(sq[j]["cy"]),
                  "tm": str(sq[j]["t"]), "a": str(A_CORE)}
                 for j in range(11) if j != i]
        nf = {"x0": str(sq[i]["cx"] - HW), "x1": str(sq[i]["cx"] + HW),
              "y0": str(sq[i]["cy"] - HW), "y1": str(sq[i]["cy"] + HW),
              "t_intervals": ledger["nofams"][i]["t_intervals"]}
        cert = {"format": "case-lp-certificate-v1",
                "claim": "Theorem U re-insertion %02d: no 11-packing at side s'' contains the "
                         "10 slack cores of z-hat minus square %d with the free square outside "
                         "the pocket zone (unique_transfer.md sec. 4, U-O1)" % (i, i),
                "s": str(s2), "n": 11, "budget": 1,
                "atoms": [], "weights": [], "total": "0",
                "hypotheses": {"cores": cores, "nofams": [nf]},
                "provenance": {"attempt": "A65-low-k-closure", "emitter": "code/emit_u.py",
                               "coordinates": "certs/trump11_certificate_tight.json",
                               "truth_anchor": "A22 krawczyk_cert.json z0, r_0=1e-50",
                               "delta": str(DELTA), "nofam_halfwidth": str(HW),
                               "ledger": "results/u_ledger.json"}}
        with open(os.path.join(outdir, "u_reinsert_%02d.json" % i), "w") as fh:
            json.dump(cert, fh, indent=1)
    os.makedirs(os.path.join(BASE, "results"), exist_ok=True)
    with open(os.path.join(BASE, "results", "u_ledger.json"), "w") as fh:
        json.dump(ledger, fh, indent=1)
    print("emitted 11 certs; min core margin %.3e; max nofam dev %.3e; lambda-1 in [%.3e, %.3e]"
          % (min(float(F(c["margin_lower_bound"])) for c in ledger["cores"]),
             max(max(n["dev_float"]) for n in ledger["nofams"]),
             float(lam_lo - 1), float(lam_hi - 1)))

if __name__ == "__main__":
    main()
