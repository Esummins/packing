# A48 verify Lemma C2b/C2c on explicit 3-step orientation-consistent B2 chains,
# exact rational arithmetic.
# Chain data per level i: local mismatch d_i, blocker slope g_i > d_i (angles as
# rational tan-halves). Frame propagation: t(b_0) = 0; t(f_i) = t(b_i) + g_i;
# t(b_{i+1}) = t(f_i) - d_{i+1} (orientation-consistent descent).
# Verified exactly per level:
#   (i)   local bridge balance (C1 formulas) in the local frame;
#   (ii)  sigma_{i+1} > sigma_i (support-edge slopes in the base frame);
#   (iii) contact heights strictly decrease in the base frame:
#         blocker contact p_i = q_i + e1(t_a_i); f_i's resting corner
#         q_{i+1} = p_i - v_i * u(T_i) + (sin T_i, -cos T_i), received at
#         parameter v_i in (0,1) along f_i's top edge (T_i = t(f_i)).
import json, os, sys
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from exact_trig import cs, add, sub, cross

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "b2_chain.json")

def unit(a):        # (cos,sin) pair -> vector
    return (a[0], a[1])

def bridge_local(td, tg):
    """C1 formulas with nu_e = 1; returns (mu_f, lam_ab, u); asserts balance."""
    cd, sd = cs(td); cg, sg = cs(tg)
    mu_f = sd / sg
    lam = (sg * cd - cg * sd) / sg
    u = (sd / sg) * (cg * cd + sg * sd)
    assert lam > 0 and mu_f > 0 and 0 < u < 1
    # exact stationarity (same identities as verify_r1_bridge, re-checked)
    assert 1 * sd + mu_f * (-sg) == 0
    assert lam - cd + mu_f * cg == 0
    assert -u + mu_f * (cd * cg + sd * sg) == 0
    return mu_f, lam, u

def run_chain(levels, v=F(1, 2)):
    """levels: list of (t_d, t_g) rational tan-halves, orientation-consistent."""
    base_b = cs(F(0))                    # t(b_0) = 0 as a (cos,sin) pair
    sigmas, heights, recs = [], [], []
    q = (F(0), F(0))
    tb = base_b                          # current receiving-edge angle (pair)
    for i, (td, tg) in enumerate(levels):
        assert tg > td > 0, "need g > d > 0"
        mu_f, lam, u = bridge_local(td, tg)
        ta = add(tb, cs(td))             # corner square world angle
        tf = add(tb, cs(tg))             # support-edge slope in base frame
        sigma = tf                       # (cos,sin) of sigma_i
        if sigmas:
            # strict increase: sin(sigma_i - sigma_{i-1}) > 0
            assert sub(sigma, sigmas[-1])[1] > 0, "C2b slope monotonicity FAILS"
        # blocker contact point p = q + e1(t_a)
        p = (q[0] + ta[0], q[1] + ta[1])
        # f_i rests: top edge dir u(T)=tf; received at param v from its top-left
        # corner A: A = p - v*u(T); resting (bottom-left) corner = A + (sin T, -cos T)
        A = (p[0] - v * tf[0], p[1] - v * tf[1])
        q_next = (A[0] + tf[1], A[1] - tf[0])
        drop = p[1] - q_next[1]          # = v sin T + cos T
        assert drop == v * tf[1] + tf[0]
        assert q_next[1] < q[1] or i == 0, "C2c height descent FAILS"
        # also p vs previous p heights handled via q chain; record
        sigmas.append(sigma); heights.append(q_next[1])
        recs.append({"i": i, "t_d": str(td), "t_g": str(tg),
                     "sigma_sin": str(sigma[1]), "q_y": str(q[1]),
                     "q_next_y": str(q_next[1]), "drop": str(drop),
                     "mu_f": str(mu_f), "lam_ab": str(lam), "u": str(u)})
        # next level frame: t(b_{i+1}) = t(f_i) - d_{i+1}
        if i + 1 < len(levels):
            tb = sub(tf, cs(levels[i + 1][0]))
        q = q_next
    # heights strictly decreasing overall
    hs = [F(0)] + heights
    assert all(hs[j + 1] < hs[j] for j in range(len(hs) - 1)), "height chain FAILS"
    return recs

def main():
    chains = [
        # slow escalation: d ~ 1 deg steps
        [(F(1, 120), F(1, 60)), (F(1, 100), F(1, 40)), (F(1, 80), F(1, 20))],
        # fast escalation to mid-tilt
        [(F(1, 100), F(1, 8)), (F(1, 50), F(1, 4)), (F(1, 30), F(1, 3))],
        # near-degenerate: g barely above d
        [(F(1, 100), F(101, 10000)), (F(1, 90), F(102, 9000)), (F(1, 80), F(103, 8000))],
    ]
    out_chains = [run_chain(ch) for ch in chains]
    out = {"what": "A48 Lemma C2b (slope monotonicity) + C2c (height descent) on "
                   "explicit 3-step orientation-consistent B2 chains, exact Fractions",
           "verdict": "PASS", "n_chains": len(out_chains), "chains": out_chains}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w"), indent=1)
    print("PASS b2_chain:", len(out_chains), "chains x 3 levels")

if __name__ == "__main__":
    main()
