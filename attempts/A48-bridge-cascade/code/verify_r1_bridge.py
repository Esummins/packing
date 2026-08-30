# A48 verify R1 (Lemma C1) + C3 cone facts, exact rational arithmetic.
# Frame: E_b along x, q = origin, a's edges e1a = (cos d, sin d), e2a = (-sin d, cos d).
# Bridge: presser e on a's top edge at param u from q+e2a, force -e2a, mult nu_e;
#         blocker f edge through q+e1a with normal n_f = (-sin g, cos g), mult mu_f;
#         base row (a,b) force (0,1), mult lam_ab.
# Claims verified exactly, per rational-angle pair (d, g):
#   (cone)   n_f . e1a <= 0  IFF  g >= d
#   (flush)  g == d IFF (a,f) mismatch 0 (flush; excluded)
#   (bal)    with nu_e = 1: mu_f = sin d / sin g, lam_ab = sin(g-d)/sin g,
#            u = (sin d / sin g) cos(g-d) satisfy a's x, y, torque rows EXACTLY
#   (strict) lam_ab > 0 IFF g > d;  u in (0,1);  mu_f > 0
#   (C3)     for psi: n = -(cos psi e1a + sin psi e2a) is in the far-corner cone,
#            blocks iff psi < 45; the world-vertical evasion n = (-1,0) violates
#            the cone for every d > 0 (n . e2a = sin d > 0).
import json, os, sys
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from exact_trig import cs, sub, cross, dot, on_circle

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "r1_bridge.json")

# rational tan-half grids: d small..mid, g adversarial around d
TD = [F(1, 1000), F(1, 100), F(1, 40), F(1, 12), F(1, 5), F(1, 3)]  # ~0.1..37 deg
REL = [F(-1, 2), F(-1, 100), F(0), F(1, 1000), F(1, 100), F(1, 10), F(1, 2), F(2)]

def check_pair(td, tg):
    cd, sd = cs(td); cg, sg = cs(tg)
    assert on_circle((cd, sd)) and on_circle((cg, sg))
    e1a, e2a = (cd, sd), (-sd, cd)
    nf = (-sg, cg)
    rec = {"t_d": str(td), "t_g": str(tg)}
    g_ge_d = tg >= td            # angles monotone in tan-half on (0,90)
    g_gt_d = tg > td
    # (cone)
    cone = dot(nf, e1a)          # = sin(d-g)
    assert (cone <= 0) == g_ge_d, "cone iff g>=d FAILS"
    # sin(d-g) identity
    smd = sd * cg - cd * sg
    assert cone == smd
    # (flush)
    rec["flush_iff_geqd"] = (td == tg)
    if tg == 0 or sg == 0:
        return None
    # (bal): nu_e = 1
    mu_f = sd / sg
    lam = (sg * cd - cg * sd) / sg          # sin(g-d)/sin g
    cgd = cg * cd + sg * sd                 # cos(g-d)
    u = (sd / sg) * cgd
    # a's rows: x, y, torque about q
    x_res = 1 * sd + mu_f * nf[0]                     # presser x + f x  (b: 0)
    y_res = lam + 1 * (-cd) + mu_f * nf[1]
    tau_e = -u                                        # presser torque
    tau_f = cross(e1a, nf)                            # = cos(g-d)
    t_res = 1 * tau_e + mu_f * tau_f
    assert x_res == 0 and y_res == 0 and t_res == 0, "exact stationarity FAILS"
    assert tau_f == cgd
    # (strict)
    assert (lam > 0) == g_gt_d, "lam>0 iff g>d FAILS"
    assert mu_f > 0
    if g_gt_d:
        assert 0 < u < 1, "u range FAILS"
    rec.update({"mu_f": str(mu_f), "lam_ab": str(lam), "u": str(u),
                "cone_sin_d_minus_g": str(cone), "g_gt_d": g_gt_d,
                "residuals": ["0", "0", "0"]})
    return rec

def check_c3(td, tpsi):
    cd, sd = cs(td); cp, sp = cs(tpsi)
    e1a, e2a = (cd, sd), (-sd, cd)
    # n = -(cos psi e1a + sin psi e2a) in world coords
    n = (-(cp * e1a[0] + sp * e2a[0]), -(cp * e1a[1] + sp * e2a[1]))
    in_cone = dot(n, e1a) <= 0 and dot(n, e2a) <= 0
    assert in_cone, "C3 cone FAILS"
    blocks = (cp - sp) > 0                    # n2 - n1 = cos psi - sin psi
    # world-vertical evasion: n_v = (-1, 0)
    nv = (-1, 0)
    evasion_ok = dot(nv, e2a) <= 0            # must be False for d > 0
    assert dot(nv, e2a) == sd
    assert (not evasion_ok) == (td > 0), "vertical-evasion cone check FAILS"
    return {"t_d": str(td), "t_psi": str(tpsi), "in_cone": True,
            "blocks_iff_psi_lt_45": blocks, "vertical_evasion_in_cone": evasion_ok}

def main():
    cases, c3cases, n_flush, n_infeasible = [], [], 0, 0
    for td in TD:
        for r in REL:
            tg = td * (1 + r) if r > -1 else None
            if tg is None or tg <= 0:
                continue
            if tg == td:
                n_flush += 1
                continue
            rec = check_pair(td, tg)
            if rec is None:
                continue
            if not rec["g_gt_d"]:
                n_infeasible += 1
            cases.append(rec)
    for td in [F(1, 100), F(1, 10)]:
        for tpsi in [F(1, 1000), F(1, 10), F(1, 3), F(2, 5)]:
            c3cases.append(check_c3(td, tpsi))
    out = {"what": "A48 Lemma C1 (R1 strict step) + C3 cone facts, exact Fractions",
           "parametrization": "(cos,sin)=((1-t^2)/(1+t^2), 2t/(1+t^2)), rational t",
           "n_cases": len(cases), "n_flush_excluded": n_flush,
           "n_g_lt_d_infeasible_cert": n_infeasible,
           "claims": ["cone iff g>=d", "flush iff g==d", "exact 3-row stationarity",
                      "lam_ab>0 iff g>d", "u in (0,1)", "C3 cone + psi<45 + no vertical evasion"],
           "verdict": "PASS", "cases": cases, "c3_cases": c3cases}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w"), indent=1)
    print("PASS r1_bridge:", len(cases), "pair cases,", len(c3cases), "C3 cases")

if __name__ == "__main__":
    main()
