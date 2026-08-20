"""Phase 3: Krawczyk operator for the square system F = (g_k)_{k in S} on a
box around the 60-digit point.  K(B) = -Y F(c) + (I - Y [J](B)) [-r,r]^34
(offsets from centre c).  K(B) strictly inside (-r,r)^34  =>  exactly one
zero of F in B (existence by Brouwer/Krawczyk, uniqueness by contraction).
All interval arithmetic: mpmath.iv (outward rounded)."""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a22lib import *
from fractions import Fraction
from mpmath import mp, iv

mp.dps = 80
iv.dps = 80

z0, ex = load_z0()
cons = curated_constraints(ex)
certs = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    'results', 'farkas_certs.json')))
S = certs['S']

# ---- Y = rational rounding of inverse Jacobian at the centre
zm = z_point(mp, z0)
A = mp.zeros(NV, NV)
for r, k in enumerate(S):
    for kk, v in grad_g(mp, zm, cons[k]).items():
        A[r, kk] = v
Yr = mp.inverse(A)
QY = 10 ** 30
Yfrac = [[Fraction(int(mp.floor(Yr[i, j] * QY + mp.mpf('0.5'))), QY)
          for j in range(NV)] for i in range(NV)]

def K_op(radius):
    """radius: Fraction. Returns (ok, maxratio, K intervals)."""
    B = z_box(z0, radius)
    zc = z_point(iv, z0)          # tight enclosure of the rational centre
    Fc = [eval_g(iv, zc, cons[k]) for k in S]
    # sparse interval Jacobian rows over B
    Jrows = [grad_g(iv, B, cons[k]) for k in S]
    Yiv = [[cnum(iv, Yfrac[i][j]) for j in range(NV)] for i in range(NV)]
    rad = cnum(iv, radius)
    dbox = iv.mpf([(-rad).a, rad.b])
    ok = True
    maxratio = 0.0
    Kout = []
    for i in range(NV):
        # -(Y Fc)_i
        acc = iv.mpf(0)
        for r in range(NV):
            acc += Yiv[i][r] * Fc[r]
        Ki = -acc
        # (I - Y J)_i . dbox, row by row: M_ij = delta_ij - sum_r Y_ir Jrows[r][j]
        for j in range(NV):
            m = iv.mpf(1) if i == j else iv.mpf(0)
            s = iv.mpf(0)
            for r in range(NV):
                v = Jrows[r].get(j)
                if v is not None:
                    s += Yiv[i][r] * v
            m = m - s
            Ki += m * dbox
        Kout.append(Ki)
        hi = max(abs(float(Ki.a)), abs(float(Ki.b)))
        ratio = hi / float(radius)
        maxratio = max(maxratio, ratio)
        if not (Ki.a > (-rad).a and Ki.b < rad.b):
            ok = False
    return ok, maxratio, Kout

results = {}
for expo, rr in [('1e-3', Fraction(1, 1000)), ('3e-4', Fraction(3, 10000)),
                 ('1e-4', Fraction(1, 10 ** 4)), ('1e-5', Fraction(1, 10 ** 5)),
                 ('1e-6', Fraction(1, 10 ** 6))]:
    t0 = time.time()
    ok, ratio, _ = K_op(rr)
    print('radius %-6s  K(B) in int(B): %-5s  max|K|/r = %.6f   (%.1fs)'
          % (expo, ok, ratio, time.time() - t0))
    results[expo] = {'ok': ok, 'ratio': ratio}

json.dump({'Y_denominator': QY, 'results': results},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'results', 'krawczyk_scan.json'), 'w'), indent=1)

# push larger radii
for expo, rr in [('2e-3', Fraction(2, 1000)), ('4e-3', Fraction(4, 1000)),
                 ('6e-3', Fraction(6, 1000)), ('8e-3', Fraction(8, 1000)),
                 ('1e-2', Fraction(1, 100))]:
    ok, ratio, _ = K_op(rr)
    print('radius %-6s  K(B) in int(B): %-5s  max|K|/r = %.6f' % (expo, ok, ratio))

# tight enclosure of z-hat: K applied at small radius gives |offset| <= max|K|
ok, ratio, Kout = K_op(Fraction(1, 10 ** 6))
w = max(max(abs(float(Ki.a)), abs(float(Ki.b))) for Ki in Kout)
print('first-pass enclosure half-width around centre:', w)
# iterate: new radius = slightly above w
r2 = Fraction(int(w * Fraction(10 ** 62)) + 1, 10 ** 62)
ok2, ratio2, Kout2 = K_op(r2)
w2 = max(max(abs(float(Ki.a)), abs(float(Ki.b))) for Ki in Kout2)
print('pass2: ok', ok2, 'half-width', w2)
