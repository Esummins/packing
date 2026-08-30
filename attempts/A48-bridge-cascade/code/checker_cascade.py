# A48 standalone corruption-gated checker for the cascade-balance certificates
# (results/r1_bridge.json, r3_wall.json, b2_chain.json).
# Independent algebra: trig and residuals are re-implemented HERE from the
# stored rational data alone (no import of exact_trig / verify_* modules).
# Usage: python checker_cascade.py            -> verify all three, then run the
#                                               5 corruption gates (must FAIL).
import copy, json, os
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")

def CS(tstr):
    t = F(tstr); den = 1 + t * t
    return ((1 - t * t) / den, 2 * t / den)

def check_r1(d):
    assert d["n_cases"] >= 30
    for c in d["cases"]:
        cd, sd = CS(c["t_d"]); cg, sg = CS(c["t_g"])
        mu, lam, u = F(c["mu_f"]), F(c["lam_ab"]), F(c["u"])
        assert F(c["cone_sin_d_minus_g"]) == sd * cg - cd * sg
        assert (F(c["t_g"]) > F(c["t_d"])) == c["g_gt_d"]
        assert (sd * cg - cd * sg <= 0) == (F(c["t_g"]) >= F(c["t_d"]))
        # stationarity residuals recomputed
        assert sd - mu * sg == 0, "x row"
        assert lam - cd + mu * cg == 0, "y row"
        assert -u + mu * (cd * cg + sd * sg) == 0, "torque row"
        assert (lam > 0) == c["g_gt_d"], "strict step"
        assert mu > 0
        if c["g_gt_d"]:
            assert 0 < u < 1
    for c in d["c3_cases"]:
        cp, sp = CS(c["t_psi"]); cd, sd = CS(c["t_d"])
        assert c["in_cone"] is True
        assert c["blocks_iff_psi_lt_45"] == (cp > sp)
        assert c["vertical_evasion_in_cone"] == (sd <= 0)

def check_r3(d):
    for c in d["c5a_cases"]:
        cb, sb = CS(c["t_beta"]); cdd, sdd = CS(c["t_d"])
        sin_ta = sb * cdd + cb * sdd
        assert F(c["sin_t_a"]) == sin_ta and F(c["tau_wall"]) == sin_ta
        assert c["blocks"] == (sin_ta > 0)
    for c in d["c5b_cases"]:
        cd, sd = CS(c["t_d"])
        lw, lab, u = F(c["lam_w"]), F(c["lam_ab"]), F(c["u"])
        assert lw == sd and lab == cd and u == sd * sd
        assert -lw + sd == 0 and lab - cd == 0 and lw * sd - u == 0
        assert c["u_equals_sin2d"] is True and 0 < u < 1

def check_chain(d):
    for ch in d["chains"]:
        prev_sig, prev_qy = None, F(0)
        for lv in ch:
            cd, sd = CS(lv["t_d"]); cg, sg = CS(lv["t_g"])
            mu, lam, u = F(lv["mu_f"]), F(lv["lam_ab"]), F(lv["u"])
            assert sd - mu * sg == 0 and lam - cd + mu * cg == 0
            assert -u + mu * (cd * cg + sd * sg) == 0
            assert lam > 0 and F(lv["t_g"]) > F(lv["t_d"])
            sig = F(lv["sigma_sin"])
            if prev_sig is not None:
                assert sig > prev_sig, "slope monotonicity"
            qn = F(lv["q_next_y"])
            assert qn < prev_qy, "height descent"
            assert F(lv["drop"]) > 0
            prev_sig, prev_qy = sig, qn

CHECKS = {"r1_bridge.json": check_r1, "r3_wall.json": check_r3,
          "b2_chain.json": check_chain}

def load(name):
    return json.load(open(os.path.join(RES, name)))

def gate(name, mutate, data):
    bad = copy.deepcopy(data)
    mutate(bad)
    try:
        CHECKS[name](bad)
    except (AssertionError, KeyError, ZeroDivisionError):
        return True          # corruption caught
    return False

def main():
    for name, fn in CHECKS.items():
        fn(load(name))
        print("OK  ", name)
    gates = [
        ("r1_bridge.json", "sign-flip lam_ab",
         lambda d: d["cases"].__setitem__(0, {**d["cases"][0],
                   "lam_ab": str(-F(d["cases"][0]["lam_ab"]))})),
        ("r1_bridge.json", "swap t_d/t_g (g<d, flag kept)",
         lambda d: d["cases"].__setitem__(1, {**d["cases"][1],
                   "t_d": d["cases"][1]["t_g"], "t_g": d["cases"][1]["t_d"]})),
        ("r3_wall.json", "u off by 1e-6",
         lambda d: d["c5b_cases"].__setitem__(0, {**d["c5b_cases"][0],
                   "u": str(F(d["c5b_cases"][0]["u"]) + F(1, 10**6))})),
        ("b2_chain.json", "raise a q_next_y (break descent)",
         lambda d: d["chains"][0].__setitem__(1, {**d["chains"][0][1],
                   "q_next_y": str(F(d["chains"][0][1]["q_next_y"]) + 1)})),
        ("b2_chain.json", "zero a mu_f",
         lambda d: d["chains"][1].__setitem__(0, {**d["chains"][1][0],
                   "mu_f": "0"})),
    ]
    n_caught = 0
    for name, label, mut in gates:
        caught = gate(name, mut, load(name))
        print(("GATE caught: " if caught else "GATE MISSED: ") + label)
        n_caught += caught
    assert n_caught == len(gates), "corruption gate failure"
    print("ALL PASS: 3 certificates verified, %d/%d corruptions caught" %
          (n_caught, len(gates)))

if __name__ == "__main__":
    main()
