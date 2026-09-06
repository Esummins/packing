"""A109 -- exact check of the SOUND pad a_w = 1 on A57's G1 slab.

Lemma SLOT-CROWD + Lemma SLOT-SLIDE give, at a usable slot p of a packing of class S at side
m in the slab, two non-pin squares of depth d_p >= max(0, s-hat'_p - m), i.e. mu_p^{(m)} <= 1 - d.
Lemma B-YES-S then puts the dilated squares in F_p(a_w(m)) with

    a_w(m) = lambda (1 - d) + (lambda - 1)(1/sqrt2 + max(i,j)),   lambda = s0/m.

A single family that works for the WHOLE slab needs a_w >= sup over m in [m_lo, s0].  This script
evaluates that supremum exactly (Fractions) on a fine grid plus the two endpoints, separately for
a FULL-window slot (s-hat'_p = s0) and for the k6_23 slot (s-hat'_p = 3877/1000), and reports the
maximum.  Expected: FULL -> exactly 1 (attained at m = s0, monotone increasing);
k6_23 -> the sup over [m_lo, 3877/1000] is < 1 but the slot carries NO hypothesis on
(3877/1000, s0), so it cannot enter a slab-wide certificate at all.
"""
import sys, os
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import slotfam94 as SF

S0 = SF.S0
M_LO = SF.M_LO_G1
SQ2H = SF.SQ2H
K23 = SF.K6_23_TOP


def a_w(m, shat_p, c):
    lam = S0 / m
    d = max(Fr(0), shat_p - m)
    return lam * (1 - d) + (lam - 1) * c


def sweep(shat_p, c, n=20000, m_hi=None):
    hi = S0 if m_hi is None else m_hi
    best, arg = None, None
    for k in range(n + 1):
        m = M_LO + (hi - M_LO) * Fr(k, n)
        v = a_w(m, shat_p, c)
        if best is None or v > best:
            best, arg = v, m
    return best, arg


if __name__ == "__main__":
    print("s0     =", S0, "=", float(S0))
    print("m_lo   =", M_LO, "=", float(M_LO), " lambda_max =", float(S0 / M_LO))
    for cij, lab in ((SQ2H + 1, "max(i,j)=1"), (SQ2H, "max(i,j)=0")):
        b, m = sweep(S0, cij)
        print("FULL   %s : sup a_w = %s = %.12f at m = %.9f   (a_w at m_lo = %.9f)"
              % (lab, str(b), float(b), float(m), float(a_w(M_LO, S0, cij))))
        assert b <= 1, b
        b2, m2 = sweep(K23, cij, m_hi=K23)
        print("k6_23  %s : sup a_w over [m_lo, 3877/1000] = %.12f at m = %.9f "
              "(NO hypothesis on (3877/1000, s0) -- slot excluded from the slab certificate)"
              % (lab, float(b2), float(m2)))
    print("A109 SOUND pad used: %s = %.9f  (1 + 1e-5, a strict outer pad)"
          % (str(Fr(100001, 100000)), float(Fr(100001, 100000))))
