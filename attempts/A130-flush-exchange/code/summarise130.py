"""summarise130.py -- the T3 table (hold x move -> certified / not, radius, margin) from results/moves130.jsonl."""
import json, os, math
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
HERE = os.path.dirname(os.path.abspath(__file__)); A130 = os.path.dirname(HERE)
res = [json.loads(l) for l in open(os.path.join(A130, 'results', 'moves130.jsonl'), encoding='utf-8') if l.strip()]
a128 = {}
for l in open(os.path.join(os.path.dirname(os.path.dirname(A130)), 'attempts', 'A128-coupled-moves', 'results', 'moves128.jsonl'), encoding='utf-8'):
    if l.strip():
        o = json.loads(l); a128[o['packing']] = o

L = ['# T3 table -- hold x move (A130, results/moves130.jsonl)', '',
     'Box radius r in every pose coordinate and in the side; FIELD = Lemma BOX-FIELD-W over all eleven squares with the tilt-sign sub-box split and the contact-mode split (Lemma MODE), certified iff EVERY sub-box x mode piece is (each with its own field; vacuous pieces count as certified); ROT-W = the same with the single square; EX2 = Lemma EXCHANGE-2 (A128\'s re-fit + a finite opening motion of the untouched squares); A128 = the depth-1 exchange radius. Point tests at r = 1e-8: the weak-cone depth rate (Lemma ROT-W / FIELD with weak rows at the point; rates <= 1e-6 are at the near-packings\' residual) and, where the rate is <= 1e-6, the cone dimension (Lemma ISOLATED) and the second-order test (Lemma KINK). Sample = drawn -> tested -> hits over every certified piece.', '',
     '| packing | side | corner | subject sq (depth, tilt) | Gordan support at the point (single square) | point: weak-cone rate / isolated / 2nd order | FIELD box r (pieces cert/total at largest r tried) | ROT-W box r | sample | EX2 at corner (flush set, r, eps*, sample) | A128 exchange r |',
     '|---|---|---|---|---|---|---|---|---|---|---|']
summary = []
for o in res:
    nm = o['packing']; first = True
    held_all = True; anything = []
    for cn, cr in o['corners'].items():
        ex = cr.get('EX2', {})
        if 'tried' in ex:
            t0 = ex['tried'][0]
            exs = 'F=%s; ' % t0.get('flush_set')
            if ex.get('certified_radius') is not None:
                b = ex.get('best', {})
                exs += 'CERTIFIED r=%g eps*=%.2e sample %s' % (ex['certified_radius'], b.get('eps_star', 0), b.get('sample'))
                anything.append('%s EX2 r=%g' % (cn, ex['certified_radius']))
            else:
                exs += 'not certified at any r (%s)' % '; '.join('r=%g: %s' % (t['r'], t.get('verdict', '')[:60]) for t in ex['tried'])
        else:
            exs = ex.get('verdict', '-')
        e128 = (a128.get(nm, {}).get('exchange', {}) or {}).get(cn, {})
        r128 = e128.get('certified_radius')
        for q, sr in cr['subjects'].items():
            fb = sr['FIELD_box']; rw = sr['ROTW_box']
            frad = fb.get('certified_radius')
            if frad is None:
                fails = fb.get('fail', {})
                rr = sorted(fails, key=lambda x: -float(x))[0] if fails else None
                fstr = 'held (%s)' % ', '.join('r=%s' % k for k in sorted(fails, key=lambda x: -float(x)))
            else:
                fstr = 'CERTIFIED r=%g (%d/%d pieces, min strict %.2e)' % (frad, fb.get('subboxes_certified', 1), fb.get('subboxes', 1), fb.get('min_strict') or 0)
                anything.append('%s sq%s FIELD r=%g' % (cn, q, frad)); held_all = False
            wc = sr['weak_cone']
            pt = ('%.1e' % wc['max_depth_rate']) if wc['max_depth_rate'] >= 0 else 'no depth row (tangent, cannot intrude the 1e-8 box)'
            if wc['max_depth_rate'] < 0:
                so = None
            elif 'isolated' in wc:
                pt += ' / %s (cone extent %.1e)' % ('ISOLATED' if wc['isolated'] else 'flat dirs', wc.get('cone_extent', 0))
            so = sr.get('second_order') if wc['max_depth_rate'] >= 0 else None
            if so:
                pt += ' / ' + (so.get('verdict') or so.get('error', ''))[:70]
            samp = (fb.get('sample') if frad is not None else None) or (rw.get('sample') if rw.get('certified_radius') is not None else None)
            sstr = '%d -> %d -> %d' % (samp['drawn'], samp['tested'], samp['hits']) if samp else '-'
            gs = sr.get('ROT_gordan_support')
            gstr = ', '.join('%s %.2f' % (t, w) for t, w in gs) if gs else 'UNHELD at the point (no certificate)'
            if rw.get('certified_radius') is not None:
                anything.append('%s sq%s ROT-W r=%g' % (cn, q, rw['certified_radius'])); held_all = False
            L.append('| %s | %s | %s | sq%s (%.3g, %.2f deg) | %s | %s | %s | %s | %s | %s | %s |' % (
                nm if first else '', ('%.6f' % o['side']) if first else '', cn, q, sr['depth_point'], sr['tilt_deg'], gstr, pt, fstr,
                rw.get('certified_radius'), sstr, exs if q == list(cr['subjects'])[0] else '', r128 if q == list(cr['subjects'])[0] else ''))
            first = False
        if 'tried' in ex and ex.get('certified_radius') is not None:
            held_all = False
    summary.append((nm, o['side'], held_all, anything))
L += ['', '## Per-packing summary', '', '| packing | side | held under FIELD + ROT-W + EX2 on every box | certificates |', '|---|---|---|---|']
for nm, side, h, a in summary:
    L.append('| %s | %.6f | %s | %s |' % (nm, side, 'YES' if h else 'no', '; '.join(a) if a else '-'))
open(os.path.join(A130, 'results', 'table130.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('\n'.join(L[-len(summary) - 3:]))
