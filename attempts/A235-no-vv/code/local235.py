"""A235 -- the complete local test (Theorem SO, A219's second219 candidates: every rotation of every square about
every active contact point, both senses, and the eigen-directions of the reduced Hessian; selection per pair by the
best axis; completion by LP; v2; curve check) on every HELD / CROWD witness that carries a loadable tilted VV contact,
in the BOUNDED variant (all active rows: the problem the witness is a local optimum of).  A witness that is FJ under
every consistent selection (select235) AND has no second-order saddle here survives every local test we have.
    python local235.py   -> results/local235.jsonl
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vv235 as V             # noqa: E402
import stress234 as ST        # noqa: E402
import rows219 as R           # noqa: E402
import second219 as S2        # noqa: E402

OUT = os.path.join(V.ATT, 'results', 'local235.jsonl')


def main():
    ST.set_priority()
    t0 = time.time()
    res = []
    with open(OUT, 'w', encoding='utf-8') as f:
        for l in open(ST.WIT, encoding='utf-8'):
            raw = json.loads(l)
            if raw['cls'] not in ('HELD', 'CROWD'):
                continue
            w = ST.from_w217(raw)
            w['rid'] = raw['rid']
            cen, _ = V.analyse(w)
            if not any(e['loadable'] for e in cen['vv']):
                continue
            rows, z = R.witness_rows(raw)
            _, A, _ = R.system(z, rows)
            lam, lam0 = R.feasible(A)
            o = {'wid': raw['wid'], 'rid': raw['rid'], 'cls': raw['cls'], 's': float(z[R.S_IDX]), 'lam0': lam0,
                 'vv_pairs': [e['pair'] for e in cen['vv'] if e['loadable']]}
            for var in ('bounded', 'core'):
                r = S2.test_variant(z, rows, lam, var)
                r.pop('modes', None)
                o[var] = r
            o['t_s'] = round(time.time() - t0, 1)
            res.append(o)
            f.write(json.dumps(o, default=float) + '\n')
            b = o['bounded']
            print('%s %s VV %s | bounded: stationary %s, modes %d (strut %d), saddle %s (verified %s), not-KKT-other-sel %s, not-FJ-other-sel %s, min v2 %s' % (
                raw['wid'], raw['cls'], o['vv_pairs'], b['stationary'], b.get('n_modes', 0), b.get('n_strut_modes', 0),
                b.get('saddle_second_order'), b.get('saddle_verified'), b.get('first_order_other_selection'),
                b.get('not_fj_other_selection'), ('%.3g' % b['min_v2']) if 'min_v2' in b else '-'), flush=True)
    print('%d witnesses, %.0f s' % (len(res), time.time() - t0))
    for cls in ('HELD', 'CROWD'):
        rs = [o for o in res if o['cls'] == cls]
        b = [o['bounded'] for o in rs]
        print('  %-5s %d | stationary %d | with zero modes %d | saddle %d (verified %d) | not KKT under the mode selection %d (not FJ %d)' % (
            cls, len(rs), sum(x['stationary'] for x in b), sum(x.get('n_modes', 0) > 0 for x in b),
            sum(bool(x.get('saddle_second_order')) for x in b), sum(bool(x.get('saddle_verified')) for x in b),
            sum(bool(x.get('first_order_other_selection')) for x in b), sum(bool(x.get('not_fj_other_selection')) for x in b)))


if __name__ == '__main__':
    main()
