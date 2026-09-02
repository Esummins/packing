"""
A80 T1: re-emit the 11 Theorem-U re-insertion certificates (U_1) at FAT core slack delta,
with the pocket zone (nofam) half-widths as parameters, plus the exact side-condition ledger
(core containment margins; pocket-zone deviation vs the basin radii).

Derived from attempts/A65-low-k-closure/code/emit_u.py (same coordinates, same truth anchor,
same arithmetic); differences: delta, hw_c (centre half-width) and hw_t (tilt half-width in t)
are arguments; the near-upright t~1 branch is [1 - h1, 1] with h1 = 2 hw_t/(1 + hw_t), which
covers equivalent tilts |t'| <= hw_t exactly (theorem_u.md sec. 3: x = h1/(2 - h1) = hw_t);
--control emits the falsifier (nofams deleted) used to MEASURE the pocket.

Writes: certs/u1_<tag>_{i}.json (i = 00..10), results/u1_<tag>_ledger.json.
"""
import argparse, json, os
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))

R0 = F(1, 10**50)            # A22 enclosure radius
# basin radii (t-world centre radius, t radius) the pocket zone is compared against
BASINS = {"lean_A36_uniform": (F(3, 2000), F(3, 2000)),
          "A36_percoord": (F(37, 10000), F(37, 20000)),           # h, h/2 (pair_kill.md 6.8)
          "A40_percoord": (F(5794, 884563), F(5794, 2 * 884563))}  # h, h/2


def emit(delta, hwc, hwt, tag, control=False, rho_b=F(0)):
    """hwc, hwt: a Fraction (all squares) or a dict i -> Fraction (per-square zones)."""
    hwc_d = hwc if isinstance(hwc, dict) else {i: hwc for i in range(11)}
    hwt_d = hwt if isinstance(hwt, dict) else {i: hwt for i in range(11)}
    tight = json.load(open(os.path.join(ROOT, "certs", "trump11_certificate_tight.json")))
    kraw = json.load(open(os.path.join(ROOT, "attempts", "A22-local-rigidity",
                                       "results", "krawczyk_cert.json")))
    s2 = F(tight["side"])
    sq = [{k: F(q[k]) for k in ("cx", "cy", "t")} for q in tight["squares"]]
    z0 = [F(x) for x in kraw["z0"]]
    assert F(kraw["r_0"]) == R0
    s_lo, s_hi = z0[33] - R0, z0[33] + R0
    assert s_hi < s2
    lam_lo, lam_hi = s2 / s_hi, s2 / s_lo
    assert lam_lo > 1
    a_core = F(1, 2) - delta

    import mpmath as mp
    mp.mp.dps = 80
    t_rat = sq[6]["t"]
    th0 = z0[3 * 6 + 2]
    for j in range(6, 11):
        assert sq[j]["t"] == t_rat and z0[3 * j + 2] == th0
    dth_f = abs(2 * mp.atan(mp.mpf(t_rat.numerator) / t_rat.denominator)
                - mp.mpf(th0.numerator) / th0.denominator)
    dt_f = abs(mp.tan(mp.mpf(th0.numerator) / th0.denominator / 2)
               - mp.mpf(t_rat.numerator) / t_rat.denominator)
    assert dth_f < 1e-14 and dt_f < 1e-14
    DTH_TILT = F(1, 10**13) + 2 * R0
    DT_TILT = F(1, 10**13)
    DTH_UP = max(abs(z0[3 * j + 2]) for j in range(6)) + R0

    ledger = {"tag": tag, "s2": str(s2), "delta": str(delta), "a_core": str(a_core),
              "hw_c": {str(i): str(v) for i, v in hwc_d.items()},
              "hw_t": {str(i): str(v) for i, v in hwt_d.items()}, "rho_B": str(rho_b),
              "lambda_minus_1": [float(lam_lo - 1), float(lam_hi - 1)],
              "cores": [], "nofams": [], "basin_fit": {}}

    # core containment margins (K_j inside the open interior of Delta_lambda(zhat_j))
    for j in range(11):
        cx, cy = sq[j]["cx"], sq[j]["cy"]
        zx_lo, zx_hi = z0[3 * j] - R0, z0[3 * j] + R0
        zy_lo, zy_hi = z0[3 * j + 1] - R0, z0[3 * j + 1] + R0
        lx_lo, lx_hi = lam_lo * zx_lo, lam_hi * zx_hi
        ly_lo, ly_hi = lam_lo * zy_lo, lam_hi * zy_hi
        off = max(abs(cx - lx_lo), abs(cx - lx_hi)) + max(abs(cy - ly_lo), abs(cy - ly_hi))
        dth = DTH_TILT if j >= 6 else DTH_UP
        margin = F(1, 2) - a_core * (1 + dth) - off
        assert margin > 0
        ledger["cores"].append({"j": j, "margin_float": float(margin)})

    # pocket zone -> basin deviation (per square), exact
    worst = {"dev_c": F(0), "dev_t": F(0)}
    for i in range(11):
        hwc, hwt = hwc_d[i], hwt_d[i]
        h1 = 2 * hwt / (1 + hwt)             # t~1 branch width: x = h1/(2-h1) = hwt exactly
        x = h1 / (2 - h1)
        assert x == hwt
        cx, cy = sq[i]["cx"], sq[i]["cy"]
        zx_lo, zx_hi = z0[3 * i] - R0, z0[3 * i] + R0
        zy_lo, zy_hi = z0[3 * i + 1] - R0, z0[3 * i + 1] + R0
        dev_x = max(abs((cx - hwc) / lam_hi - zx_hi), abs((cx + hwc) / lam_lo - zx_lo))
        dev_y = max(abs((cy - hwc) / lam_hi - zy_hi), abs((cy + hwc) / lam_lo - zy_lo))
        if i >= 6:
            dev_t = hwt + DT_TILT + R0
            t_ints = [[str(t_rat - hwt), str(t_rat + hwt)]]
        else:
            dev_t = max(hwt + DTH_UP, x + x ** 3 + DTH_UP)
            t_ints = [["0", str(hwt)], [str(1 - h1), "1"]]
        # in the counting-row application the zone is additionally pulled back through
        # lambda = s''/m~ with m~ >= s-hat - rho_B: centre drift <= sqrt2 * rho_B (pair_kill 6)
        dev_c = max(dev_x, dev_y) + F(14143, 10000) * rho_b
        worst["dev_c"] = max(worst["dev_c"], dev_c)
        worst["dev_t"] = max(worst["dev_t"], dev_t)
        ledger["nofams"].append({"i": i, "dev_c": float(dev_c), "dev_t": float(dev_t),
                                 "t_intervals": t_ints})
    for name, (rc, rt) in BASINS.items():
        ledger["basin_fit"][name] = {"r_c": float(rc), "r_t": float(rt),
                                     "fits": bool(worst["dev_c"] < rc and worst["dev_t"] < rt),
                                     "headroom_c": float(rc - worst["dev_c"]),
                                     "headroom_t": float(rt - worst["dev_t"])}
    ledger["worst_dev"] = {k: float(v) for k, v in worst.items()}

    outdir = os.path.join(BASE, "certs")
    os.makedirs(outdir, exist_ok=True)
    names = []
    for i in range(11):
        hwc, hwt = hwc_d[i], hwt_d[i]
        cores = [{"kx": str(sq[j]["cx"]), "ky": str(sq[j]["cy"]),
                  "tm": str(sq[j]["t"]), "a": str(a_core)} for j in range(11) if j != i]
        nf = {"x0": str(sq[i]["cx"] - hwc), "x1": str(sq[i]["cx"] + hwc),
              "y0": str(sq[i]["cy"] - hwc), "y1": str(sq[i]["cy"] + hwc),
              "t_intervals": ledger["nofams"][i]["t_intervals"]}
        cert = {"format": "case-lp-certificate-v1",
                "claim": "U_1 re-insertion %02d at core slack %s: no 11-packing at side s'' "
                         "contains the 10 slack cores of z-hat minus square %d with the free "
                         "square outside the pocket zone (hw_c=%s, hw_t=%s)%s"
                         % (i, delta, i, hwc, hwt, " [CONTROL: nofam deleted]" if control else ""),
                "s": str(s2), "n": 11, "budget": 1,
                "atoms": [], "weights": [], "total": "0",
                "hypotheses": {"cores": cores, "nofams": [] if control else [nf]},
                "provenance": {"attempt": "A80-u-ladder", "emitter": "code/emit_u1.py",
                               "derived_from": "A65 code/emit_u.py",
                               "coordinates": "certs/trump11_certificate_tight.json",
                               "truth_anchor": "A22 krawczyk_cert.json z0, r_0=1e-50",
                               "delta": str(delta), "hw_c": str(hwc), "hw_t": str(hwt),
                               "ledger": "results/u1_%s_ledger.json" % tag}}
        fn = os.path.join(outdir, "u1_%s%s_%02d.json" % (tag, "_control" if control else "", i))
        with open(fn, "w") as fh:
            json.dump(cert, fh, indent=1)
        names.append(fn)
    os.makedirs(os.path.join(BASE, "results"), exist_ok=True)
    with open(os.path.join(BASE, "results", "u1_%s_ledger.json" % tag), "w") as fh:
        json.dump(ledger, fh, indent=1)
    return names, ledger


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--delta", required=True)
    ap.add_argument("--hwc", required=True)
    ap.add_argument("--hwt", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--rho_b", default="0")
    ap.add_argument("--control", action="store_true")
    a = ap.parse_args()
    names, led = emit(F(a.delta), F(a.hwc), F(a.hwt), a.tag, a.control, F(a.rho_b))
    print("emitted %d certs (%s); min core margin %.3e; worst dev (c,t) = (%.3e, %.3e); fits: %s"
          % (len(names), a.tag, min(c["margin_float"] for c in led["cores"]),
             led["worst_dev"]["dev_c"], led["worst_dev"]["dev_t"],
             {k: v["fits"] for k, v in led["basin_fit"].items()}))
