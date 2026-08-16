"""
make_certificate.py -- build exact rational certificates for s(11) <= s_c from the 60-digit
solution in trump11_exact.json.

Recipe: lam = s_c / s*; scale every centre by lam about the origin (unit squares keep their
size, so every contact opens into a positive gap of order lam-1: wall gaps (lam-1)/2, pair
gaps >= (lam-1)*|centre separation along the contact normal| ~ lam-1).  Then round the
centres to denominator 10^k and replace t = tan(theta/2) by a continued-fraction convergent
with error < 10^-k, where 10^-k <= (lam-1)/10^4, so rounding cannot close a gap.  Uprights get
t = 0 exactly.  Validity never depends on this recipe: certs/verify_certificate.py re-checks
everything in Fraction arithmetic.

Outputs (in certs/):
  trump11_certificate.json         s_c = 3877084/10^6              (centre-tilt format)
  trump11_certificate_tight.json   s_c = s* + 1e-9 rounded up at 12 decimals = 3877083591023/10^12
  trump11_certificate_38771.json   s_c = 38771/10^4 (the survey's headline bound)
  trump11_certificate_int.json     all-integer corners over a common denominator D for the
                                   3877084/10^6 certificate (for the Lean checker, A06)
  trump11_certificate_tight_int.json  same for the tight one
"""
import json
import os
import sys
from decimal import Decimal, getcontext
from fractions import Fraction
from math import lcm

getcontext().prec = 80
HERE = os.path.dirname(os.path.abspath(__file__))
CERTS = os.path.join(HERE, '..', '..', 'certs')
sys.path.insert(0, CERTS)
from verify_certificate import verify  # noqa: E402

d = json.load(open(os.path.join(HERE, 'trump11_exact.json')))
s_star = Fraction(Decimal(d['s']))
t_exact = Fraction(Decimal(d['t_tan_half_theta']))
theta = Decimal(d['theta_rad'])


def convergent_below(x: Fraction, err: Fraction) -> Fraction:
    """Continued-fraction convergent p/q of x with |x - p/q| < err (smallest q by construction)."""
    a = []
    y = x
    h0, h1 = 0, 1
    k0, k1 = 1, 0
    while True:
        ai = y.numerator // y.denominator
        h0, h1 = h1, ai * h1 + h0
        k0, k1 = k1, ai * k1 + k0
        c = Fraction(h1, k1)
        if abs(c - x) < err:
            return c
        frac = y - ai
        if frac == 0:
            return c
        y = 1 / frac


def build(s_c: Fraction, tag: str):
    lam = s_c / s_star
    assert lam > 1
    k = 4
    while Fraction(1, 10 ** k) > (lam - 1) / 10 ** 4:
        k += 1
    DEN = 10 ** k
    t_r = convergent_below(t_exact, Fraction(1, DEN))
    squares = []
    for q in d['squares']:
        cx = Fraction(Decimal(q['cx'])) * lam
        cy = Fraction(Decimal(q['cy'])) * lam
        th = Decimal(q['theta'])
        if abs(th) < Decimal('1e-30'):
            t = Fraction(0)
        elif abs(th - theta) < Decimal('1e-30'):
            t = t_r
        else:
            raise SystemExit('unexpected angle')
        cxr = Fraction(round(cx * DEN), DEN)
        cyr = Fraction(round(cy * DEN), DEN)
        squares.append({'cx': str(cxr), 'cy': str(cyr), 't': str(t),
                        'center': [str(cxr), str(cyr)]})
    cert = {
        'format': 'centre-tilt',
        'description': f'Rational certificate that 11 unit squares fit in a square of side {s_c} '
                       f'(Trump 1979 packing: 6 uprights + 5 squares tilted by theta, tan(theta/2) = t). '
                       f'Squares: centre (cx,cy) and t = tan(theta/2); corners = centre + R(theta)(+-1/2,+-1/2) '
                       f'with cos = (1-t^2)/(1+t^2), sin = 2t/(1+t^2), all exact rationals.',
        'side': str(s_c), 'container_side': str(s_c),
        'squares': squares,
        'provenance': {
            'attempt': 'A03-upper-reconstruct',
            'source': 'attempts/A03-upper-reconstruct/trump11_exact.json (60-digit Gauss-Newton solution of the contact system)',
            's_star': d['s'], 'theta_deg': d['theta_deg'], 't_exact': d['t_tan_half_theta'],
            's_star_minimal_polynomial': 's^8-20s^7+178s^6-842s^5+1923s^4-496s^3-6754s^2+12420s-6865',
            't_minimal_polynomial': '5t^8-10t^7-2t^6+14t^5+12t^4-6t^3+2t^2+2t-1 (t=tan(theta/2), theta=+40.18 deg CCW; equivalently p(-t)=0 with p=5t^8+10t^7-2t^6-14t^5+12t^4+6t^3+2t^2-2t-1)',
            'construction': f'centres scaled by lam = s_c/s* = 1 + {float(lam-1):.3e}, rounded to 10^-{k}; '
                            f't replaced by convergent {t_r} (error {float(abs(t_r-t_exact)):.1e})',
            'verifier': 'certs/verify_certificate.py (stdlib Fraction arithmetic only)',
        },
    }
    path = os.path.join(CERTS, f'trump11_certificate{tag}.json')
    json.dump(cert, open(path, 'w'), indent=1)
    print('wrote', path, ' lam-1 =', float(lam - 1), ' DEN =', DEN, ' t =', t_r)
    ok = verify(cert)
    assert ok
    return cert


def to_int(cert, tag):
    """All-integer corner version: corners as integers over one common denominator D."""
    side = Fraction(cert['side'])
    corners = []
    for q in cert['squares']:
        cx, cy, t = Fraction(q['cx']), Fraction(q['cy']), Fraction(q['t'])
        den = 1 + t * t
        c, s = (1 - t * t) / den, 2 * t / den
        h = Fraction(1, 2)
        pts = [(cx + c * bx - s * by, cy + s * bx + c * by) for bx, by in [(-h, -h), (h, -h), (h, h), (-h, h)]]
        corners.append(pts)
    D = side.denominator
    for pts in corners:
        for x, y in pts:
            D = lcm(D, x.denominator, y.denominator)
    S = side * D
    assert S.denominator == 1
    out = {
        'format': 'integer-corners',
        'description': cert['description'] + f'  All-integer version: coordinates are integers over the '
                       f'common denominator D; container is [0, side_D/D]^2; each square lists its 4 corners '
                       f'in counter-clockwise order; |P1-P0|^2 = D^2 exactly (unit square).',
        'D': D, 'denominator': D,
        'side_D': int(S), 'container_side': f'{int(S)}/{D}', 'side': f'{int(S)}/{D}',
        'squares': [{'corners': [[int(x * D), int(y * D)] for x, y in pts]} for pts in corners],
        'provenance': cert['provenance'],
    }
    path = os.path.join(CERTS, f'trump11_certificate{tag}_int.json')
    json.dump(out, open(path, 'w'), indent=1)
    print('wrote', path, ' D =', D, f'({len(str(D))} digits)')
    ok = verify(out)
    assert ok
    return out


if __name__ == '__main__':
    c1 = build(Fraction(3877084, 10 ** 6), '')
    to_int(c1, '')
    tight_side = Fraction(3877083591023, 10 ** 12)     # s* + 1e-9 rounded up at 12 decimals
    assert tight_side > s_star + Fraction(1, 10 ** 9)
    c2 = build(tight_side, '_tight')
    to_int(c2, '_tight')
    c3 = build(Fraction(38771, 10 ** 4), '_38771')
