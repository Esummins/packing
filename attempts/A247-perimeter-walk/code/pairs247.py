"""A247 -- the PAIR TABLE: for every pair of designated cell-sets that two squares of a walk can
carry, the certified verdict of the two-square branch-and-bound (bb247) on a side range.

Pair kinds (canonical under D4 and relabelling, geo247.tuple_key):
  MM-same  two meeters of one corner (BL): {BL00} + subsets of BL's four slots      (136 raw)
  MM-adj   a meeter of BL and a meeter of BR                                       (256 raw)
  MM-opp   a meeter of BL and a meeter of TR (expected feasible; run for completeness)
  MF       a meeter of BL and a free square (any window)                            (768 raw)
  FF       two free squares                                                         (1176 raw)
Every INFEASIBLE row is a certificate: no two interior-disjoint unit squares in [0, s]^2 with
s in the range carry those designated sets with meeting depth >= eta (free squares avoiding the
open corner boxes).  FEASIBLE rows carry an exactly verified rational witness.
    python pairs247.py --range window|corpus --eta 1e-2 --budget 3000000 [--kinds MM-same,MF] [--shard k/n]
Resume: the same command (rows already in results/pairs247_<range>_<eta>.jsonl are skipped);
stop: touch logs/STOP.
"""
import argparse
import itertools
import json
import os
import time

import bb247 as B
import geo247 as G

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
RANGES = {'window': (G.S_LO, G.SHAT), 'corpus': (G.S_LO, 4.5), 'to4': (G.SHAT, 3.999)}


def realisable(catalogue):
    """the D4-orbit keys of the single-square sets the catalogue found FEASIBLE (None = all)."""
    if not catalogue:
        return None
    ok = set()
    for line in open(catalogue):
        r = json.loads(line)
        if r.get('kind') in ('M', 'F') and r['status'] == 'FEASIBLE':
            ok.add((r['kind'], tuple(r['orbit'])))
    return ok


def orbit_key(cells):
    return min(tuple(sorted(m[c] for c in cells)) for m in G.D4)


def pair_problems(kinds, catalogue=None):
    ok = realisable(catalogue)

    def keep(kind, cells):
        return ok is None or (kind, orbit_key(cells)) in ok
    M_BL = [('M', 'BL', c) for c in G.meeter_sets('BL') if keep('M', c)]
    M_BR = [('M', 'BR', c) for c in G.meeter_sets('BR') if keep('M', c)]
    M_TR = [('M', 'TR', c) for c in G.meeter_sets('TR') if keep('M', c)]
    F = [('F', c) for c in G.free_sets() if keep('F', c)]
    raw = []
    if 'MM-same' in kinds:
        raw += [(a, b) for a, b in itertools.combinations_with_replacement(M_BL, 2)]
    if 'MM-adj' in kinds:
        raw += [(a, b) for a in M_BL for b in M_BR]
    if 'MM-opp' in kinds:
        raw += [(a, b) for a in M_BL for b in M_TR]
    if 'MF' in kinds:
        raw += [(a, b) for a in M_BL for b in F]
    if 'FF' in kinds:
        raw += [(a, b) for a, b in itertools.combinations_with_replacement(F, 2)]
    seen = {}
    for a, b in raw:
        k = G.tuple_key([a, b])
        if k not in seen:
            seen[k] = (a, b)
    return seen


def load_done(path):
    done = {}
    if os.path.exists(path):
        for line in open(path):
            r = json.loads(line)
            done[r['key']] = r
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--range', default='window', choices=list(RANGES))
    ap.add_argument('--eta', type=float, default=1e-2)
    ap.add_argument('--budget', type=int, default=3_000_000)
    ap.add_argument('--hmin', type=float, default=1e-5)
    ap.add_argument('--kinds', default='MM-same,MM-adj,MM-opp,MF,FF')
    ap.add_argument('--shard', default='0/1')
    ap.add_argument('--eta-avoid', type=float, default=None, help='avoid level (default = eta); a gap makes the searches decisive')
    ap.add_argument('--exact', action='store_true', help='exact cell-sets (avoid every other reachable cell)')
    ap.add_argument('--catalogue', default='', help='exact catalogue jsonl: only its FEASIBLE sets enter the table')
    ap.add_argument('--only-status', default='', help='rerun only keys whose status in a previous file is this (e.g. BUDGET)')
    a = ap.parse_args()
    try:
        import sys
        sys.path.insert(0, os.path.join(ATT, '..', 'A244-twelve-stuck', 'code'))
        from search244 import belownormal
        belownormal()
    except Exception:
        pass
    os.makedirs(os.path.join(ATT, 'results'), exist_ok=True)
    os.makedirs(os.path.join(ATT, 'logs'), exist_ok=True)
    out = os.path.join(ATT, 'results', 'pairs247_%s%s_%g.jsonl' % (a.range, '_exact' if a.exact else '', a.eta))
    stop = os.path.join(ATT, 'logs', 'STOP')
    lf = open(os.path.join(ATT, 'logs', 'pairs247_%s%s_%g_%s.log' % (a.range, '_exact' if a.exact else '', a.eta, a.shard.replace('/', 'of'))), 'a')

    def log(t):
        lf.write(time.strftime('%H:%M:%S ') + t + '\n')
        lf.flush()

    probs = pair_problems(a.kinds.split(','), os.path.join(ATT, a.catalogue) if a.catalogue and not os.path.isabs(a.catalogue) else a.catalogue)
    def rank(k):
        nf = k.count('F:')
        if nf == 0:
            return 0 if k.split(' | ')[0][2:4] == k.split(' | ')[1][2:4] else 1
        return 1 + nf
    keys = sorted(probs, key=lambda k: (rank(k), k))       # MM-same, MM-adj/opp, MF, FF
    k, n = map(int, a.shard.split('/'))
    keys = [x for i, x in enumerate(keys) if i % n == k]
    done = load_done(out)
    if a.only_status:
        keys = [x for x in keys if x in done and done[x]['status'] == a.only_status]
        done = {x: r for x, r in done.items() if x not in keys}
    log('%d pair problems (%s), %d done, eta %g, range %s, budget %d' % (len(keys), a.kinds, len(done), a.eta, a.range, a.budget))
    t0 = time.time()
    for i, key in enumerate(keys):
        if key in done:
            continue
        if os.path.exists(stop):
            log('STOP')
            break
        specs = probs[key]
        prob = B.problem_of(list(specs), RANGES[a.range], eta=a.eta, exact=a.exact, eta_avoid=a.eta_avoid)
        t = time.time()
        r = B.solve(prob, hmin=a.hmin, budget_boxes=a.budget, stop=stop)
        row = {'key': key, 'specs': [list(s) if s[0] == 'F' else [s[0], s[1], list(s[2])] for s in specs],
               'status': r['status'], 'eta': a.eta, 'eta_avoid': prob['eta_avoid'], 'range': a.range, 'exact': a.exact, 's': list(RANGES[a.range]),
               'boxes': r['processed'], 'undecided': r['undecided'], 'seconds': round(time.time() - t, 2),
               'witness': r['witness'], 'how': (r['witness'] or {}).get('how', 'bb'), 'undecided_boxes': r['undecided_boxes'][:3]}
        with open(out, 'a') as f:
            f.write(json.dumps(row) + '\n')
        log('%4d/%d %-11s %8d boxes %6.1fs  %s' % (i + 1, len(keys), r['status'], r['processed'], time.time() - t, key))
    log('done in %.0f s' % (time.time() - t0))


if __name__ == '__main__':
    main()
