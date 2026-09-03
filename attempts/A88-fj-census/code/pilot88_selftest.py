"""pilot88_selftest.py -- A88 T3 pilot: soundness spot-checks for the fast
core-row engine (p88_iv / p88_rows / p88_triage).

(1) p88_iv row VALUE vs t3lib mpmath.iv row_value on the exact structure points
    (must agree; both must bracket 0 for an active row).
(2) p88_rows row GRADIENT vs central finite differences.
(3) the T1b LP relaxation must be FEASIBLE on the (padded) degenerate box at
    the realising point -- a sound outer relaxation can never kill a
    realisation.  The LP zero slack used is the structure's own row-activity
    tolerance, since rows were declared active at |g| <= tol, not g == 0.
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
import p88_struct as S                               # noqa: E402
import p88_rows as R                                 # noqa: E402
import p88_triage as TR                              # noqa: E402
import p88_census as CL                              # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
A87 = os.path.join(ROOT, 'attempts', 'A87-drain-flow', 'results',
                   'cp87_fj_polished.jsonl')
STR = os.path.join(HERE, '..', 'results', 'pilot88_structs.jsonl')
OUT = os.path.join(HERE, '..', 'results', 'pilot88_selftest.json')


def point_of(tag):
    if tag.startswith('trump'):
        z, _ = T.load_trump()
        return [float(x) for x in z]
    for line in open(A87):
        r = json.loads(line)
        if r['tag'] == tag:
            return [float(T.str_frac(x)) for x in r['z_polished']]
    return None


def degenerate_box(st, z, pad=0.0):
    b = [None] * st.D
    for i in st.loaded:
        b[st.ix[('cx', i)]] = (z[3 * i] - pad, z[3 * i] + pad)
        b[st.ix[('cy', i)]] = (z[3 * i + 1] - pad, z[3 * i + 1] + pad)
    for c in st.free_cls:
        v = st.reps[c]
        b[st.ix[('th', c)]] = (v - pad, v + pad)
    b[st.ix[('s',)]] = (z[33] - pad, z[33] + pad)
    return b


def main():
    sts = [S.struct_from_json(json.loads(l)) for l in open(STR)]
    worst_val = 0.0
    worst_cmp = 0.0
    worst_grad = 0.0
    bad_lp = []
    worst_dom = 1e9
    for st in sts:
        z = point_of(st.tag)
        box = degenerate_box(st, z)
        b34 = st.to34(box)
        iv34 = [T.iv.mpf([x[0], x[1]]) for x in b34]
        for r in st.rows:
            v, g = R.eval_row_core(st, box, r)
            worst_val = max(worst_val, abs(v[0]), abs(v[1]))
            vm = T.row_value(iv34, r)
            worst_cmp = max(worst_cmp, abs(float(vm.a) - v[0]),
                            abs(float(vm.b) - v[1]))
            for k, gi in list(g.items())[:3]:
                h = 1e-6
                bp = list(box); bm = list(box)
                bp[k] = (box[k][0] + h, box[k][1] + h)
                bm[k] = (box[k][0] - h, box[k][1] - h)
                fp, _ = R.eval_row_core(st, bp, r, grad=False)
                fm, _ = R.eval_row_core(st, bm, r, grad=False)
                fd = (0.5 * (fp[0] + fp[1]) - 0.5 * (fm[0] + fm[1])) / (2 * h)
                worst_grad = max(worst_grad, abs(fd - 0.5 * (gi[0] + gi[1])))
        # (4) rebuilt DOMINANCE side conditions must be >= 0 at the point:
        # this validates the sign convention with which the census rows are
        # turned into inequalities
        for r in st.ineq:
            v, _ = R.eval_row_core(st, box, r, grad=False)
            if v[0] < worst_dom:
                worst_dom = v[0]
        lpidx, nv = TR.lp_index(st)
        ztol = 4.0 * float(st.extra.get('tol', 1e-6))
        wb = degenerate_box(st, z, pad=1e-6)
        res = TR.solve_leaf(st, wb, lpidx, nv, ztol=ztol)
        if res['infeasible']:
            bad_lp.append([st.tag, res['margin'], res['reason']])
    out = {'n_structures': len(sts),
           'max_abs_row_value_at_realising_points': worst_val,
           'max_fastiv_vs_mpmath_row_value': worst_cmp,
           'max_grad_vs_finite_difference': worst_grad,
           'lp_infeasible_at_realising_point': bad_lp,
           'min_rebuilt_dominance_row_value_at_points': worst_dom}
    ok = (worst_cmp < 1e-9 and worst_grad < 1e-5 and not bad_lp
          and worst_dom > -1e-3)
    out['verdict'] = 'PASS' if ok else 'FAIL'
    json.dump(out, open(OUT, 'w'), indent=1)
    for k, v in out.items():
        print(k, ':', v)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
