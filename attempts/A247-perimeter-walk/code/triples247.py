"""A247 task 3 -- per-walk geometry: the TRIPLE tests.  Every walk in the list has all its
pairs feasible (or undecided); the next bounded sub-problem is a triple of its squares whose
cell-sets touch (three squares of one corner region: the corner's two meeters and a third
square sharing a cell with them, or three squares along one wall).  A triple certified
INFEASIBLE by the three-square branch-and-bound (10 dims + s, exact form, level eta) kills
every walk containing it.  Triples are ordered by the number of walks they would kill.
    python triples247.py --walks results/walks247_window_exact_0.05.jsonl --eta 0.05 [--budget 600000] [--top N]
Resumable (rows in results/triples247_<tag>.jsonl are skipped); stop: touch logs/STOP.
Also: --three-in-box runs THREE-IN-BOX (three meeters of one corner box) alone.
"""
import argparse
import collections
import itertools
import json
import os
import time

import bb247 as B
import geo247 as G

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
WINDOW = (G.S_LO, G.SHAT)


def walk_squares(rec):
    """the eleven specs of a walk row."""
    out = []
    for c, d1, d2 in rec['corners']:
        for d in (d1, d2):
            out.append(('M', c, tuple(['%s00' % c] + list(d))))
    for f in rec['free']:
        if f:
            out.append(('F', tuple(f)))
    return out


def touching(sp1, sp2):
    """two specs whose reach (the N_c containing them) overlap."""
    def reach(sp):
        cells = sp[2] if sp[0] == 'M' else sp[1]
        r = set()
        for c in G.CORNERS:
            if set(cells) <= set(G.NBR[c]):
                r |= set(G.NBR[c])
        return r
    return bool(reach(sp1) & reach(sp2))


def triples_of(walks):
    """canonical triple keys -> (specs, number of walks containing it, walk indices)."""
    out = {}
    for wi, rec in enumerate(walks):
        sq = walk_squares(rec)
        for a, b, c in itertools.combinations(range(len(sq)), 3):
            t = (sq[a], sq[b], sq[c])
            if not (touching(t[0], t[1]) and touching(t[1], t[2]) and touching(t[0], t[2])):
                continue
            k = G.tuple_key(list(t))
            if k not in out:
                out[k] = [t, set()]
            out[k][1].add(wi)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--walks', default='')
    ap.add_argument('--eta', type=float, default=0.05)
    ap.add_argument('--budget', type=int, default=600_000)
    ap.add_argument('--top', type=int, default=0, help='run only the N most valuable triples (0 = all)')
    ap.add_argument('--eta-avoid', type=float, default=None)
    ap.add_argument('--three-in-box', action='store_true')
    ap.add_argument('--tag', default='')
    a = ap.parse_args()
    try:
        import sys
        sys.path.insert(0, os.path.join(ATT, '..', 'A244-twelve-stuck', 'code'))
        from search244 import belownormal
        belownormal()
    except Exception:
        pass
    stop = os.path.join(ATT, 'logs', 'STOP')
    tag = a.tag or ('window_exact_%g' % a.eta)
    out = os.path.join(ATT, 'results', 'triples247_%s.jsonl' % tag)
    lf = open(os.path.join(ATT, 'logs', 'triples247_%s.log' % tag), 'a')

    def log(t):
        lf.write(time.strftime('%H:%M:%S ') + t + '\n')
        lf.flush()
    done = {}
    if os.path.exists(out):
        for line in open(out):
            r = json.loads(line)
            done[r['key']] = r
    jobs = []
    if a.three_in_box:
        t = (('M', 'BL', ('BL00',)), ('M', 'BL', ('BL00',)), ('M', 'BL', ('BL00',)))
        jobs.append((G.tuple_key(list(t)) + ' [monotone]', t, 0, False))
    if a.walks:
        walks = [json.loads(l) for l in open(os.path.join(ATT, a.walks) if not os.path.isabs(a.walks) else a.walks)]
        walks = [w for w in walks if w.get('kind') != 'summary']
        tr = triples_of(walks)
        log('%d walks, %d distinct touching triples' % (len(walks), len(tr)))
        order = sorted(tr.items(), key=lambda kv: -len(kv[1][1]))
        if a.top:
            order = order[:a.top]
        jobs += [(k, v[0], len(v[1]), True) for k, v in order]
    killed = set()
    for i, (key, specs, nw, exact) in enumerate(jobs):
        if key in done:
            if done[key]['status'] == 'INFEASIBLE' and a.walks:
                killed |= tr[key][1] if key in tr else set()
            continue
        if os.path.exists(stop):
            log('STOP')
            break
        prob = B.problem_of(list(specs), WINDOW, eta=a.eta, exact=exact, eta_avoid=a.eta_avoid)
        t = time.time()
        r = B.solve(prob, hmin=1e-5, budget_boxes=a.budget, stop=stop)
        row = {'key': key, 'specs': [list(s) if s[0] == 'F' else [s[0], s[1], list(s[2])] for s in specs],
               'status': r['status'], 'eta': a.eta, 'eta_avoid': prob['eta_avoid'], 'exact': exact, 'walks': nw, 'boxes': r['processed'],
               'undecided': r['undecided'], 'seconds': round(time.time() - t, 2), 'witness': r['witness'],
               'how': (r['witness'] or {}).get('how', 'bb')}
        with open(out, 'a') as f:
            f.write(json.dumps(row) + '\n')
        if r['status'] == 'INFEASIBLE' and a.walks and key in tr:
            killed |= tr[key][1]
        log('%4d/%d %-11s %8d boxes %6.1fs walks %5d  %s' % (i + 1, len(jobs), r['status'], r['processed'],
                                                              time.time() - t, nw, key))
    if a.walks:
        log('walks killed by triples: %d of %d' % (len(killed), len(walks)))


if __name__ == '__main__':
    main()
