"""A274: exact small-angle H1-H3 configurations violating (U4) / (U5) -- route R1 is dead.  Fractions throughout
(rational rotations tan(t/2)); H1-H3 by SAT on edge normals (witness273's functions, imported); the ring-condition
margins from ringdom271.conditions (float, informational).   python witness274.py -> results/witness274.json"""
import json, math, os, sys
from fractions import Fraction as F
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A273-disc-lemma', 'code'))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A271-ring-domain', 'code'))
import witness273 as W                                                # noqa: E402  rot, sq_low, interiors_meet
import ringdom271 as RD                                               # noqa: E402  conditions (float)
BOX = [(F(0), F(0)), (F(1), F(0)), (F(1), F(1)), (F(0), F(1))]


def config(hu, hv, tC, D, tX, xmin, tA, side):
    c, s = W.rot(tC); cp, sp = W.rot(tX); ca, sa = W.rot(tA)
    Ctop = hv + c + s
    xl = Ctop - D
    C = W.sq_low(hu + s, hv, (c, s)); X = W.sq_low(sp, xl, (cp, sp)); A = W.sq_low(xmin + sa, F(0), (ca, sa))
    Tu = [(x - hu, y) for x, y in C]
    xtop = max(y for _, y in X)
    H = dict(hu=hu > 0, hv=0 < hv < 1, C_meets_box=W.interiors_meet(C, BOX), A_quadrant=min(x for x, _ in A) >= 0,
             A_meets_box=W.interiors_meet(A, BOX), A_C_disjoint=not W.interiors_meet(A, C),
             X_top_gt=xtop > side - 1, X_top_le=xtop <= side, X_low_ge1=xl >= 1, X_meets_Tu=W.interiors_meet(X, Tu),
             X_C_disjoint=not W.interiors_meet(X, C), X_A_disjoint=not W.interiors_meet(X, A),
             side=F(382, 100) <= side <= W.SHAT_LO)
    q = [float(hu), float(hv), 2 * math.atan(float(tC)), float(xl), 2 * math.atan(float(tX)),
         float(xmin + sa), 2 * math.atan(float(tA)), float(side)]
    cond = {k: v for k, v in RD.conditions(q).items() if k in RD.COND or k in ('a_R', 'a_star', 'w_max', 'beta_deg')}
    return dict(params=dict(h_u=str(hu), h_v=str(hv), tan_half_theta=str(tC), theta_deg=q[2] / RD.DEG, D=str(D),
                            tan_half_phi=str(tX), phi_deg=q[4] / RD.DEG, x_min_A=str(xmin), tan_half_alpha=str(tA),
                            alpha_deg=q[6] / RD.DEG, side=str(side), X_low=str(xl), C_top=str(Ctop)),
                H1H3_exact=H, all_H1H3=all(H.values()), ring_conditions_float=cond)


def main():
    out = dict(
        W1_U4=config(F(1, 2), F(997, 1000), F(1, 229), F(1, 100), F(11, 252), F(97, 100), F(1, 286), F(385, 100)),
        W2_U5=config(F(1, 5), F(99, 100), F(0), F(1, 200), F(11, 252), F(19, 20), F(7, 15), F(385, 100)))
    for k, v in out.items():
        v['verdict'] = ('H1-H3 exact; ' + ', '.join(f'{c} {v["ring_conditions_float"][c]:+.4f}' for c in ('U3', 'U4', 'U5', 'U6', 'U8'))
                        if v['all_H1H3'] else 'NOT an H1-H3 configuration')
        print(k, v['verdict'])
    json.dump(out, open(os.path.join(HERE, '..', 'results', 'witness274.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
