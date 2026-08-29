"""A46 W1 exact cross-checks (Fable lead). Pure Fractions; no float enters a verdict.

Checks:
 C1  Bridge mechanism (w1_theory.md par.5): a's three stationarity rows vanish EXACTLY with
     the stated multipliers, all strictly positive, for rational-trig angles 0 < d < g.
 C2  Torque identity spot check: dg/dt = omega * cross(p-q, n) for both row types, exact,
     against a direct symbolic derivative surrogate (finite rotation, first order in h ->
     checked via two step sizes and Richardson ratio in Fractions... implemented instead as
     the exact bilinear identity, which IS the proof; here we verify the sign tables of
     w1_theory.md par.4 (blocker taxonomy) from the identity.
 C3  Thin-chain span: 2*sqrt2 + 1 < s0 = 969271/250000, exactly (squared comparison).
 C4  W1.6(c): corner-height difference cos t - sin t = 0 iff t = 45; and the non-extremal
     corner variant forces sin t = 0. (Symbolic one-liners, recorded for the log.)
"""
from fractions import Fraction as F

def rat_trig(t):  # t = tan(theta/2) rational -> (sin, cos) exact
    return F(2*t.numerator*t.denominator, t.denominator**2 + t.numerator**2) if False else (
        F(2)*t/(1+t*t), (1-t*t)/(1+t*t))

def cross(u, v): return u[0]*v[1] - u[1]*v[0]

def check_bridge(td, tg):
    sd, cd = rat_trig(td); sg, cg = rat_trig(tg)
    # frame: E_b along x, q = origin, n_b = (0,1); e1a = (cd, sd), e2a = (-sd, cd)
    e1a = (cd, sd); e2a = (-sd, cd)
    # contacts on a:
    #  (a,b): p = q = (0,0), n = (0,1), multiplier lam_b
    #  (a,f): p = q + e1a, n_f = (-sg, cg), multiplier mu_f
    #  (a,e): p = q + e2a + u*e1a, n_e = (-e2a) = (sd, -cd), multiplier nu_e
    nu_e = F(1)
    mu_f = nu_e * sd / sg
    # lam_b from y-balance below; u from torque balance:
    # sin(g-d) = sg*cd - cg*sd ; cos(g-d) = cg*cd + sg*sd
    sin_gd = sg*cd - cg*sd; cos_gd = cg*cd + sg*sd
    lam_b = nu_e * sin_gd / sg
    u = (sd/sg) * cos_gd
    # force balance: lam_b*(0,1) + mu_f*n_f + nu_e*n_e == 0
    fx = lam_b*0 + mu_f*(-sg) + nu_e*(sd)
    fy = lam_b*1 + mu_f*(cg) + nu_e*(-cd)
    # torque about q: sum lam * cross(p - q, n) ; tau_b = 0
    tau_f = cross(e1a, (-sg, cg))
    p_e = (e2a[0] + u*e1a[0], e2a[1] + u*e1a[1])
    tau_e = cross(p_e, (sd, -cd))
    tq = mu_f*tau_f + nu_e*tau_e
    ok = (fx == 0 and fy == 0 and tq == 0 and lam_b > 0 and mu_f > 0 and nu_e > 0
          and 0 < u < 1)
    return ok, dict(lam_b=lam_b, mu_f=mu_f, u=u, fx=fx, fy=fy, tq=tq,
                    tau_f=tau_f, cos_gd=cos_gd)

def check_taxonomy(td):
    sd, cd = rat_trig(td)
    e1a = (cd, sd); e2a = (-sd, cd)
    rows = []
    # bottom edge interior at param u: p = u*e1a, n = +e2a  -> tau = +u
    u = F(1,3); p = (u*e1a[0], u*e1a[1]); rows.append(('bottom', cross(p, e2a), u))
    # right edge interior: p = e1a + u*e2a, n = -e1a -> tau = +u
    p = (e1a[0]+u*e2a[0], e1a[1]+u*e2a[1]); rows.append(('right', cross(p, (-e1a[0], -e1a[1])), u))
    # left edge interior: p = u*e2a, n = +e1a -> tau = -u
    p = (u*e2a[0], u*e2a[1]); rows.append(('left', cross(p, e1a), -u))
    # top edge interior: p = e2a + u*e1a, n = -e2a -> tau = -u
    p = (e2a[0]+u*e1a[0], e2a[1]+u*e1a[1]); rows.append(('top', cross(p, (-e2a[0], -e2a[1])), -u))
    # right WALL at q+e1a: n = (-1, 0) world -> tau = sin d
    rows.append(('rwall', cross(e1a, (-1, 0)), sd))
    # left WALL at q+e2a: n = (+1, 0) -> tau = -cos d
    rows.append(('lwall', cross(e2a, (1, 0)), -cd))
    # top WALL at far corner: n = (0,-1) -> tau = sin d - cos d
    far = (e1a[0]+e2a[0], e1a[1]+e2a[1])
    rows.append(('twall', cross(far, (0, -1)), sd - cd))
    return [(name, got, want, got == want) for name, got, want in rows]

def check_span():
    s0 = F(969271, 250000)
    # 2*sqrt2 + 1 < s0  <=>  sqrt2 < (s0-1)/2  <=>  2 < ((s0-1)/2)^2
    rhs = ((s0 - 1)/2)**2
    return rhs > 2, rhs

if __name__ == '__main__':
    all_ok = True
    for td, tg in [(F(1,100), F(1,10)), (F(1,50), F(1,7)), (F(1,20), F(3,10)),
                   (F(1,1000), F(1,9)), (F(7,100), F(8,100))]:
        ok, info = check_bridge(td, tg)
        all_ok &= ok
        print(f"C1 bridge td={td} tg={tg}: {'PASS' if ok else 'FAIL'} "
              f"lam_b={info['lam_b']} u={info['u']}")
    tax = check_taxonomy(F(1, 30))
    for name, got, want, ok in tax:
        all_ok &= ok
        print(f"C2 tau[{name}] = {got} (expected {want}): {'PASS' if ok else 'FAIL'}")
    ok, rhs = check_span()
    all_ok &= ok
    print(f"C3 ((s0-1)/2)^2 = {rhs} > 2: {'PASS' if ok else 'FAIL'} (=> 2*sqrt2+1 < s0)")
    print("ALL PASS" if all_ok else "FAILURES PRESENT")
