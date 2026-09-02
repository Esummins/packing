#!/usr/bin/env python3
"""emit_tube.py -- build / evaluate / sweep contraction-tube certificates (A83).

Certification-in-the-loop (A39 lab rule): every candidate (T, r_c, r_theta, r_s,
direction) is evaluated by the EXACT checker certs/verify_tube.py (imported as a
module -- the checker never imports this file), and a certificate JSON is written
only for candidates the checker PASSes.  omega / P / Y are A36's universal barrier
(G3_UNIVERSAL.json) and A22's pin system verbatim; the certificate adds the tube
geometry (T, r, v) and the list of strictly compressed rows.

Usage:
  python emit_tube.py --T 1/100 --rc 2/1250 --rt 21/10000 --rs 0 --mode slot --tag X
  python emit_tube.py --sweep sweep.json          # list of candidates -> results jsonl
"""
import argparse
import hashlib
import importlib.util
import json
import os
import sys
import time
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
A22 = os.path.join(ROOT, 'attempts', 'A22-local-rigidity', 'results', 'krawczyk_cert.json')
A36U = os.path.join(ROOT, 'attempts', 'A36-levers', 'results', 'a36_certs', 'G3_UNIVERSAL.json')
CERTS = os.path.join(ROOT, 'certs')
RESULTS = os.path.join(HERE, '..', 'results')

spec = importlib.util.spec_from_file_location('verify_tube', os.path.join(CERTS, 'verify_tube.py'))
VT = importlib.util.module_from_spec(spec)
spec.loader.exec_module(VT)

TRUMP5_PINS = [0, 1, 2, 3, 5]


def frac(s):
    return VT.frac(s)


def direction(z0, mode, pins):
    s0 = z0[VT.S_IDX]
    v = []
    for i in range(33):
        sq = i // 3
        if i % 3 == 2:
            v.append(Fraction(0))
        elif mode == 'slot' and sq in pins:
            x = z0[i]
            isR = any(abs(x - (s0 - a)) < Fraction(1, 10 ** 30)
                      for a in (Fraction(1, 2), Fraction(3, 2), Fraction(5, 2)))
            v.append(Fraction(1) if isR else Fraction(0))
        else:
            v.append(z0[i] / s0)
    v.append(Fraction(1))
    return v


def build(T, rc, rt, rs, mode, pins, K, om_src, tag):
    z0 = [frac(x) for x in K['z0']]
    v = direction(z0, mode, pins)
    om = list(om_src['omega_rational'])
    P = [k if k < 36 else (44 if k == 36 else 45) for k in K['S']]
    cert = {
        'format': VT.FORMAT,
        'name': tag,
        'T': VT.fs(T), 'r_c': VT.fs(rc), 'r_theta': VT.fs(rt), 'r_s': VT.fs(rs),
        'T_float': float(T), 'r_c_float': float(rc), 'r_theta_float': float(rt), 'r_s_float': float(rs),
        'direction_spec': {'mode': mode, 'pins': pins if mode == 'slot' else None,
                           'text': ('v = z0/s0 on every centre coordinate, 0 on tilts, 1 on s '
                                    '(pure scaling about the origin = pull-back of a dilation)'
                                    if mode == 'scale' else
                                    'pins %s ride their slot lines (v = beta in {0,1} per coordinate), '
                                    'free squares scale (v = z0/s0), tilts 0, s 1' % pins)},
        'direction_v': [VT.fs(x) for x in v],
        'P': P,
        'P_source': "A22 krawczyk_cert.json 'S', mapped 36->44, 37->45",
        'Y_source': "A22 krawczyk_cert.json 'Y', verbatim (loaded by the checker)",
        'omega_rational': om,
        'omega_source': 'A36 G3_UNIVERSAL.json omega_rational verbatim (universal rows 0..35 + 44, 45)',
        'strictly_compressed_rows': [],
        'a22_sha256': hashlib.sha256(open(A22, 'rb').read()).hexdigest(),
        'handover': {'target': 'A22 strict local optimality on box(z0, r_N)', 'r_N': K['r_N']},
        'coordinates': 'theta-frame (radians), A22 ordering: (cx_i, cy_i, theta_i)_{i<11}, s',
        'produced_by': 'attempts/A83-contraction-tube/code/emit_tube.py',
    }
    # strictly compressed rows: gamma_k lower bound > 0 (exact), computed with the checker's kernel
    cons = VT.build_constraints(K)
    r0 = frac(K['r_0'])
    pbox = VT.rad_box(z0, r0)
    strict = []
    for k in range(VT.NEXT3):
        if frac(om[k]) == 0:
            continue
        j, vs = VT.row_jet(pbox, cons[k], 1)
        acc = VT.IZERO
        for loc, gi in enumerate(vs):
            if v[gi] != 0:
                acc = acc + j.g[loc] * v[gi]
        if acc.lo > 0:
            strict.append(k)
    cert['strictly_compressed_rows'] = strict
    return cert


def evaluate(cert, K, nmax=4000, quiet=False):
    lines = []

    def log(s):
        lines.append(s)
        if not quiet:
            print(s)
    ck = VT.Check(log)
    st = VT.check_cert(dict(cert), K, ck, log, nmax=nmax, verbose=not quiet)
    st['fails'] = list(ck.fails)
    st['n_checks'] = ck.n
    st['PASS'] = not ck.fails
    return st


def finalize(cert, st):
    cert['claims'] = {k: st[k] for k in ('beta', 'kappa', 'kappa_eff', 'Hbar', 'q_vv', 'Hv_l1',
                                         'Hv_l1_tilts', 'eps_0', 'eps_w', 'g_max', 'X_max',
                                         'psi_Xmax', 'psi_over_Xmax', 'x_star', 'n_iter',
                                         'min_tangential', 'min_tangential_row',
                                         'min_depth_plus_half', 'min_gamma_loaded',
                                         'sum_omega_gamma', 'canary_wall_rows')}
    cert['claims_note'] = 'informational: the checker recomputes every quantity and gates on its own values'
    return cert


def run_one(T, rc, rt, rs, mode, pins, tag, K, om_src, write, quiet=False, nmax=4000):
    cert = build(T, rc, rt, rs, mode, pins, K, om_src, tag)
    st = evaluate(cert, K, nmax=nmax, quiet=quiet)
    row = dict(tag=tag, T=VT.fs(T), r_c=VT.fs(rc), r_theta=VT.fs(rt), r_s=VT.fs(rs), mode=mode,
               T_float=float(T), r_c_float=float(rc), r_theta_float=float(rt), r_s_float=float(rs),
               **{k: v for k, v in st.items() if k != 'name'})
    if write and st['PASS']:
        finalize(cert, st)
        if tag.startswith('regress'):
            # the A36 universal certificate as a T = 0 tube: the checker must reproduce
            # A70/A79's constants (gated by the checker when this field is present)
            cert['regression_targets'] = {'beta': 0.4352815659957499, 'Hbar': 7.9079039796968145,
                                          'kappa_eff': 19.315664098324593,
                                          'psi_over_Xmax': 0.9978097018969502}
        fn = os.path.join(CERTS, 'tube_%s.json' % tag)
        with open(fn, 'w') as f:
            json.dump(cert, f, indent=1)
        # re-verify FROM DISK after the JSON round trip (review suggestion 11)
        st2 = evaluate(json.load(open(fn)), K, nmax=nmax, quiet=True)
        assert st2['PASS'] and (st2['claims_max_rel_dev'] or 0) < 1e-9, (tag, st2['fails'])
        row['file'] = os.path.relpath(fn, ROOT)
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--T', default='0')
    ap.add_argument('--rc', default='3689/1000000')
    ap.add_argument('--rt', default=None)
    ap.add_argument('--rs', default=None)
    ap.add_argument('--mode', default='slot', choices=('scale', 'slot'))
    ap.add_argument('--pins', default='0,1,2,3,5')
    ap.add_argument('--tag', default=None)
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--sweep', default=None, help='json list of {T, rc, rt, rs, mode, tag}')
    ap.add_argument('--out', default=None, help='results jsonl (sweep)')
    ap.add_argument('--nmax', type=int, default=4000)
    ap.add_argument('--omega', default=A36U)
    a = ap.parse_args()
    K = json.load(open(A22))
    K['_sha256'] = hashlib.sha256(open(A22, 'rb').read()).hexdigest()
    om_src = json.load(open(a.omega))
    pins = [int(x) for x in a.pins.split(',')] if a.pins else []
    if a.sweep:
        cands = json.load(open(a.sweep))
        out = a.out or os.path.join(RESULTS, 'sweep.jsonl')
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, 'a') as fh:
            for c in cands:
                T, rc = frac(c['T']), frac(c['rc'])
                rt = frac(c.get('rt', c['rc']))
                rs = frac(c.get('rs', '0'))
                mode = c.get('mode', 'slot')
                tag = c.get('tag') or '%s_T%s_rc%s_rt%s' % (mode, c['T'], c['rc'], c.get('rt', c['rc']))
                tag = tag.replace('/', 'o')
                t0 = time.time()
                row = run_one(T, rc, rt, rs, mode, c.get('pins', pins), tag, K, om_src,
                              c.get('write', False), quiet=True, nmax=a.nmax)
                row['wall'] = round(time.time() - t0, 1)
                fh.write(json.dumps(row) + '\n')
                fh.flush()
                print('%-40s %s  beta=%.4f psi/X=%.4f x*=%.2e n=%d tan=%.5f(%s) %.1fs %s'
                      % (tag, 'PASS' if row['PASS'] else 'FAIL', row['beta'], row['psi_over_Xmax'],
                         row['x_star'], row['n_iter'], row['min_tangential'],
                         row['min_tangential_row'], row['wall'], row['fails'][:2]))
        return 0
    T, rc = frac(a.T), frac(a.rc)
    rt = frac(a.rt) if a.rt else rc
    rs = frac(a.rs) if a.rs is not None else Fraction(0)
    tag = a.tag or ('%s_T%s_rc%s_rt%s' % (a.mode, a.T, a.rc, a.rt or a.rc)).replace('/', 'o')
    row = run_one(T, rc, rt, rs, a.mode, pins, tag, K, om_src, a.write, nmax=a.nmax)
    print(json.dumps({k: v for k, v in row.items() if k not in ('fails',)}, indent=1, default=str))
    print('fails:', row['fails'])
    return 0 if row['PASS'] else 1


if __name__ == '__main__':
    sys.exit(main())
