"""pilot88_extract.py -- A88: build the (b) + (c) support structures.

(b) genuine k0 FJ points from A87 (attempts/A87-drain-flow/results/
    cp87_fj_polished.jsonl).  TIGHT survivors (survivor_tight, FJ at tol 1e-6)
    are the certified set; the six lowest (sigma 3.8868) are LOOSE mid-drain
    probes that pass the cone test only at tol 1e-4/1e-3 -- kept, labelled, as
    near-rigid COST probes only.
(c) Trump's structure (t3lib.load_trump + A22 cert cross-check) -- the CANARY.

Writes attempts/A88-fj-census/results/pilot88_structs.jsonl.
"""
from __future__ import annotations

import json
import os
import sys

os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import t3lib as T                                    # noqa: E402
import p88_struct as S                                 # noqa: E402
import p88_census as CL                                # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
A87 = os.path.join(ROOT, 'attempts', 'A87-drain-flow', 'results',
                   'cp87_fj_polished.jsonl')
OUT = os.path.join(HERE, '..', 'results', 'pilot88_structs.jsonl')

LOOSE = ['o006', 'o000', 'o002', 'o004', 'o003', 'o011']
TIGHT_LOW = ['o012', 'o018', 'o025', 'o026', 'o028']
FAM40 = ['o034', 'o036', 'o042', 'o044', 'o048', 'o057', 'o070', 'o085']


# ---- copied from attempts/A87-drain-flow/code/jobs87.py::active_rows_at_point
def active_rows_at_point(z, tol=1e-6):
    pt = [T._to_iv(x) for x in z]
    ab = T.test_ab(pt)
    info = {'point_infeasible': ab['infeasible'], 'point_reason': ab['reason']}
    if ab['infeasible']:
        info['min_gap'] = ab.get('min_gap')
        return None, info
    info['min_gap'] = ab['min_gap']
    info['min_clear'] = ab['min_clear']
    rows = []
    for i in range(11):
        for c in range(4):
            for w in T.WALLS:
                r = T.wall_row(i, c, w)
                if abs(float(T.row_value(pt, r).a)) <= tol:
                    rows.append(r)
    info['n_wall_active'] = len(rows)
    contact_pairs = [p for p, v in ab['pairs'].items() if v[1] <= tol]
    info['n_contact_pairs'] = len(contact_pairs)
    nsel = 0
    n_nosel = 0
    for (i, j) in sorted(contact_pairs):
        got = False
        for o, p in ((i, j), (j, i)):
            if got:
                break
            for e in range(4):
                if got:
                    break
                for k in range(4):
                    rr = [T.sep_row(o, e, p, k)] + [T.dom_row(o, e, p, k, m)
                                                    for m in range(4) if m != k]
                    vals = [T.row_value(pt, r) for r in rr]
                    if all(float(v.a) >= -tol for v in vals):
                        add = [r for r, v in zip(rr, vals)
                               if abs(float(v.a)) <= tol]
                        rows += add
                        nsel += len(add)
                        got = True
                        break
        if not got:
            n_nosel += 1
    info['n_sel_active'] = nsel
    info['n_pairs_no_consistent_selection'] = n_nosel
    return rows, info


def build(tag, z, tol, extra):
    rows, info = active_rows_at_point(z, tol)
    if rows is None:
        return None, info
    loaded = S.loaded_squares(rows)
    thetas = {i: float(z[3 * i + 2]) for i in range(11)}
    cls, reps, pinned, order = S.tilt_classes(thetas, loaded)
    ex = dict(extra)
    ex['tol'] = tol
    ex['active_info'] = {k: v for k, v in info.items() if k != 'pairs'}
    # the t3lib DOMINANCE side conditions of each selected sep row.  Those that
    # are themselves active came back as EQUALITY rows from
    # active_rows_at_point; the rest are genuine g >= 0 side conditions and are
    # carried as inequalities, exactly as the census records are read.  Their
    # sign convention is validated in pilot88_selftest (every rebuilt row is
    # strictly positive at the realising point).
    eqkeys = {T.row_key(r) for r in rows}
    ex['n_ineq'] = 0
    ineq = [r for r in CL.dominance_of(rows) if T.row_key(r) not in eqkeys]
    ex['n_ineq'] = len(ineq)
    st = S.Structure(tag, rows, cls, reps, pinned, order, ex, ineq=ineq)
    return st, info


def main():
    out = []
    recs = [json.loads(l) for l in open(A87)]
    by = {r['tag']: r for r in recs}

    for tag in LOOSE + TIGHT_LOW + FAM40:
        r = by.get(tag)
        if r is None:
            print('MISSING', tag); continue
        tight = bool(r.get('survivor_tight'))
        fj = r['final'].get('fj') or {}
        tol = 1e-6 if tight else float(fj.get('tol', 1e-4))
        z = [T.str_frac(x) for x in r['z_polished']]
        extra = {'source': 'A87', 'sigma': r['final']['sigma'],
                 'tight': tight,
                 'label': 'certified-FJ(tol 1e-6)' if tight
                          else 'loose (not certified FJ)',
                 'rank': fj.get('rank'), 'rank33': fj.get('rank33'),
                 'rattlers': fj.get('n_rattlers'),
                 'm_a87': fj.get('m_active')}
        st, info = build(tag, z, tol, extra)
        if st is None:
            print('INFEASIBLE POINT', tag, info); continue
        out.append(st)
        print(tag, 'k_H', st.k_H, 'm', st.m, 'chi', st.chi, 'D', st.D,
              'cls', st.n_cls, 'free', len(st.free_cls), 'tight', tight)

    # ---- (c) Trump: the canary
    z, _ = T.load_trump()
    cert = T.load_a22_cert()
    for tol in (1e-9, 1e-6):
        st, info = build('trump_%g' % tol, z, tol,
                         {'source': 'A22/A03', 'sigma': float(z[33]),
                          'tight': True, 'label': 'Trump (canary)',
                          'rank': 34, 'rattlers': 0,
                          'a22_n_constraints': len(cert['constraints'])})
        if st is None:
            print('TRUMP INFEASIBLE', tol, info); continue
        out.append(st)
        print(st.tag, 'k_H', st.k_H, 'm', st.m, 'chi', st.chi, 'D', st.D,
              'cls', st.n_cls, 'free', len(st.free_cls),
              'a22_rows', len(cert['constraints']))

    with open(OUT, 'w') as f:
        for st in out:
            f.write(json.dumps(S.struct_to_json(st)) + '\n')
    print('wrote', OUT, len(out))


if __name__ == '__main__':
    main()
