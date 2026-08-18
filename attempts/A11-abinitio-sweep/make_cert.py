#!/usr/bin/env python3
"""
make_cert.py -- turn a milp_pack.py result JSON into a rational 'centre-tilt' certificate
(certs/verify_certificate.py format) and verify it exactly.

Steps: re-solve the structure LP with a small slack (so every separation / containment is strictly
positive), then rationalise: t = tan(theta/2) rounded to 12 decimals, centres to 10 decimals, side
rounded UP to 9 decimals + 1e-9.  Then call the lab's exact verifier (stdlib Fractions).
Usage: python make_cert.py results/n11_0_trump.json [--slack 2e-7]
"""
import argparse
import json
import math
import os
import subprocess
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from milp_pack import Model, polish_lp  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('result')
    ap.add_argument('--slack', type=float, default=2e-7)
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    res = json.load(open(a.result))
    m = Model(res['n'], res['angles_deg'], s_max=float(math.ceil(math.sqrt(res['n']))) + 1.0, symbreak=False, com=False)
    p = polish_lp(m, res, slack=a.slack)
    if p is None:
        print('LP infeasible with slack'); sys.exit(1)
    s, sq = p
    side = F(math.ceil((s + 1e-9) * 1e9), 10 ** 9)
    squares = []
    for q in sq:
        t = F(str(round(math.tan(math.radians(q['theta_deg']) / 2), 12)))
        cx = F(str(round(q['cx'], 10)))
        cy = F(str(round(q['cy'], 10)))
        squares.append({'cx': str(cx), 'cy': str(cy), 't': str(t)})
    cert = {'format': 'centre-tilt',
            'description': f"A11 ab-initio sweep (A09 angle-lattice MILP) result: n={res['n']} lattice {res['angles_deg']} deg, "
                           f"structure {res.get('structure')}; rationalised (t=tan(theta/2) to 12 dp).",
            'side': str(side), 'squares': squares}
    out = a.out or a.result.replace('.json', '_cert.json')
    json.dump(cert, open(out, 'w'), indent=1)
    print(f'wrote {out}: side = {side} = {float(side):.10f}')
    r = subprocess.run([sys.executable, os.path.join(HERE, '..', '..', 'certs', 'verify_certificate.py'), out],
                       capture_output=True, text=True)
    print(r.stdout[-800:], r.stderr[-300:])
    sys.exit(r.returncode)


if __name__ == '__main__':
    main()
