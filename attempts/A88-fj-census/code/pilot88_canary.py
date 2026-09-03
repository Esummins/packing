"""pilot88_canary.py -- A88 T3 pilot: the TRUMP CANARY (A76 Lemma K).

The per-structure certificate for Trump's support must NOT exclude the region
containing z-hat.  The correct output is "one isolated root at s = s-hat
(Krawczyk contracts), no other root with s <= s-hat_hi": Krawczyk IDENTIFIES
z-hat, it never excludes it.

Method (p88_fj.follow_point): descend the branch-and-bound always into the
child that CONTAINS z-hat, running every leaf test on the way.  If ANY test
(HC4, a-structure, a-sigma, Farkas, Krawczyk) ever discharges that box, the
test is unsound and the canary FAILS.  Otherwise the descent ends when the
epsilon-inflated Krawczyk test certifies exactly one root; the root box is then
refined and its s-enclosure compared with s-hat.

The same descent is run on the A87 genuine FJ structures as a control (with the
s window widened to cover their sigma, which lies above s-hat).

Writes results/pilot88_canary.json.
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
import p88_fj as FJ                                  # noqa: E402

RES = os.path.abspath(os.path.join(HERE, '..', 'results'))
A87 = os.path.abspath(os.path.join(HERE, '..', '..', 'A87-drain-flow',
                                   'results', 'cp87_fj_polished.jsonl'))
OUT = os.path.join(RES, 'pilot88_canary.json')

S_HAT = 3.877083590022814
S_HAT_HI = 3.877084


def point_of(tag):
    if tag.startswith('trump'):
        z, _ = T.load_trump()
        return [float(x) for x in z]
    for line in open(A87):
        r = json.loads(line)
        if r['tag'] == tag:
            return [float(T.str_frac(x)) for x in r['z_polished']]
    return None


def run_one(st, z, s_lo, s_hi, ztol=FJ.ZTOL):
    rec = FJ.follow_point(st, z, s_lo=s_lo, s_hi=s_hi, max_depth=400,
                          ztol=ztol)
    out = {k: v for k, v in rec.items()
           if k not in ('log', 'final_box', 'sel')}
    out['ztol'] = ztol
    out['log_tail'] = rec.get('log', [])[-2:]
    if rec.get('status') == 'ISOLATED':
        box = rec['final_box']
        sel = rec['sel']
        ki, trace = FJ.refine_root(st, box, sel)
        js = st.ix[('s',)]
        if ki:
            sb = ki['root_box'][js]
            out['refined'] = {
                'root_s_box': sb,
                'root_box_maxwidth': max(y - x for x, y in ki['root_box']),
                'ratio': ki['ratio'], 'cond': ki['cond'],
                'contains_s_hat': bool(sb[0] <= S_HAT <= sb[1]),
                's_hat': S_HAT,
                's_hat_minus_root_mid': S_HAT - 0.5 * (sb[0] + sb[1]),
                'trace': trace}
    return out


def main():
    sts = {}
    for l in open(os.path.join(RES, 'pilot88_structs.jsonl')):
        st = S.struct_from_json(json.loads(l))
        sts[st.tag] = st

    out = {'note': 'float interval arithmetic with outward padding '
                   '(p88_iv); a COST/behaviour measurement, NOT a certificate '
                   'and NOT a verdict about s(11).',
           's_hat': S_HAT, 's_hat_hi': S_HAT_HI}

    for tag in ('trump_1e-06', 'trump_1e-09'):
        st = sts[tag]
        z = point_of(tag)
        out[tag] = run_one(st, z, 3.82, S_HAT_HI)
        print(tag, out[tag]['status'],
              out[tag].get('refined', {}).get('root_s_box'),
              'contains s-hat',
              out[tag].get('refined', {}).get('contains_s_hat'), flush=True)

    ctl = {}
    for tag in sorted(sts):
        if tag.startswith('trump'):
            continue
        st = sts[tag]
        z = point_of(tag)
        sig = float(z[33])
        # the A87 points satisfy their active rows only to the extraction
        # tolerance, so the descent must carry that same row-activity slack
        ztol = 4.0 * float(st.extra.get('tol', 1e-6))
        r = run_one(st, z, min(3.82, sig - 0.05), max(S_HAT_HI, sig + 0.001),
                    ztol=ztol)
        r['row_activity_tol'] = st.extra.get('tol')
        r['tight'] = st.extra.get('tight')
        r['sigma'] = sig
        ctl[tag] = {k: v for k, v in r.items() if k != 'log_tail'}
        print('control %-6s tight=%-5s sigma %.6f  %-14s %s'
              % (tag, st.extra.get('tight'), sig, r['status'],
                 (r.get('refined') or {}).get('root_s_box')), flush=True)
    out['controls_A87'] = ctl
    out['any_canary_fail'] = any(
        (v.get('status') == 'CANARY_FAIL')
        for k, v in list(out.items()) + list(ctl.items())
        if isinstance(v, dict))
    json.dump(out, open(OUT, 'w'), indent=1)
    print('wrote', OUT)


if __name__ == '__main__':
    main()
