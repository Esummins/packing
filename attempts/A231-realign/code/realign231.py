"""A231 the ANCHORED re-alignment after a corner swap (docs/proofs/realign.md).  From a corner-swapped four-crowd
(inputs231: settled slot square S at corner c, leftover L, same side s0):
  0. SHRINK: the fixed-tilt side minimum over the centres with S pinned to its slot (alternating LP, axes free)
     -> s_lp0 <= s0 (the swapped packing is feasible), configuration p0;
  1. GRAINS at p0: G_h = the contact component of S among the tilted squares of handedness h (for every h that
     touches S), G_comp = the component of S among ALL tilted squares, G_all = every tilted square;
  2. the anchored move of G: its members rotate toward their own alignment ('+' -> 0, '-' -> 90; diamonds -> 0),
     everything else keeps its tilt, S stays pinned flush; at each of 20 steps the side is minimised over the centres:
     A = the contacts of p0 keep their separating axis (lean contacts slide), B = every axis re-selected.
  Per path: the side trajectory, blocked-at + the blocking pairs, s_min / t_min / the grain's tilts there, the
  endpoint (flush / kink / start / blocked), the HORN (flush-side: the first step lowers the side; kink-side: raises it).
    python realign231.py [--only WID] [--src 193|win40|a226] [--resume] [--steps 20]   -> results/realign231.jsonl
"""
import json
import math
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
try:
    import psutil
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    psutil.Process().cpu_affinity(list(range(16)))
except Exception:      # noqa: BLE001
    pass
import geomn231 as GN         # noqa: E402
import inputs231 as IN        # noqa: E402

ATT = os.path.abspath(os.path.join(HERE, '..'))
REPO = os.path.abspath(os.path.join(ATT, '..', '..'))
OUT = os.path.join(ATT, 'results', 'realign231.jsonl')
TOL = 1e-7
EPS = 1e-6


def schedule(th0, t, members):
    th = np.array(th0, float) % (math.pi / 2)
    out = th.copy()
    for i in members:
        h = GN.handedness(th[i])
        if h == 'F':
            continue
        out[i] = th[i] * (1 - t) if h in ('+', 'D') else math.pi / 2 - (math.pi / 2 - th[i]) * (1 - t)
    return out


def component(cont, start, allowed):
    adj = {}
    for (i, j) in cont:
        if i in allowed and j in allowed:
            adj.setdefault(i, set()).add(j)
            adj.setdefault(j, set()).add(i)
    seen, stack = {start}, [start]
    while stack:
        a = stack.pop()
        for b in adj.get(a, ()):
            if b not in seen:
                seen.add(b)
                stack.append(b)
    return seen


def grain_sets(poses, S):
    cont = GN.contacts(poses)
    hand = [GN.handedness(p[2]) for p in poses]
    tilted = {i for i in range(len(poses)) if hand[i] != 'F'}
    nb = {j if i == S else i for (i, j) in cont if S in (i, j)}
    hs = sorted({hand[i] for i in nb if i in tilted and hand[i] != 'D'})
    out = {}
    for h in hs:
        out['g' + h] = sorted(component(cont, S, tilted_h(tilted, hand, h) | {S}) - {S})
    out['comp'] = sorted(component(cont, S, tilted | {S}) - {S})
    out['all'] = sorted(tilted)
    return out, hand, cont, sorted(nb)


def tilted_h(tilted, hand, h):
    return {i for i in tilted if hand[i] in (h, 'D')}


def blockers(poses, th_new, members):
    p2 = [(p[0], p[1], float(th_new[i])) for i, p in enumerate(poses)]
    g = GN.pair_gaps(p2)
    out = [[i, j, round(v, 5)] for (i, j), v in g.items() if v < -1e-9 and (i in members or j in members)]
    return sorted(out, key=lambda x: x[2])[:6]


def path(poses, S, corner, G, steps, keep):
    th0 = np.array([p[2] for p in poses])
    fixed = GN.contacts(poses) if keep else {}
    rec = {'t': [], 's': [], 'blocked_at': None, 'blockers': None, 'free_feasible_at_block': None, 'frames': {}}
    cur, sched = poses, []
    for k in range(steps + 1):
        t = k / steps
        th = schedule(th0, t, G)
        sched.append(th)
        p, s, sel, it = GN.fixed_tilt_min(cur, th, fixed, {S: corner})
        if p is None:
            rec['blocked_at'] = t
            rec['blockers'] = blockers(cur, th, G)
            if keep:
                pb, sb, _, _ = GN.fixed_tilt_min(cur, th, {}, {S: corner})
                rec['free_feasible_at_block'] = pb is not None
            break
        rec['t'].append(round(t, 4)); rec['s'].append(round(s, 7))
        cur = p
        rec['frames'][str(round(t, 4))] = [list(map(float, q)) for q in cur]
    if rec['s']:
        ss = rec['s']
        k_min = int(np.argmin(ss))
        rec.update({'s_lp0': ss[0], 's_end': ss[-1], 's_min': ss[k_min], 't_min': rec['t'][k_min],
                    'tilts_at_min_deg': sorted({round(GN.phi_deg(sched[k_min][i]), 2) for i in G}),
                    'monotone': bool(all(ss[i + 1] <= ss[i] + TOL for i in range(len(ss) - 1))),
                    'max_uptick': round(max([ss[i + 1] - ss[i] for i in range(len(ss) - 1)] + [0.0]), 7)})
        first = ss[1] - ss[0] if len(ss) > 1 else 0.0
        rec['horn'] = 'flush-side' if first < -TOL else ('kink-side' if first > TOL else 'flat')
        if rec['blocked_at'] is not None:
            rec['endpoint'] = 'blocked'
        elif k_min == len(ss) - 1:
            rec['endpoint'] = 'flush'
        elif k_min == 0:
            rec['endpoint'] = 'start'
        else:
            rec['endpoint'] = 'kink'
    keep_keys = {'0.0', '1.0', str(rec.get('t_min'))}
    rec['frames'] = {k: v for k, v in rec['frames'].items() if k in keep_keys}
    return rec


def run_case(case, steps):
    t0 = time.time()
    p, s0, S, c = case['poses'], case['s0'], case['S'], case['corner']
    out = {'key': IN.key_of(case), 'src': case['src'], 'wid': case['wid'], 'rid': case['rid'], 'n': case['n'],
           'corner': c, 's0': s0, 'swap': case['swap'], 'S': S, 'L': case['L']}
    if p is None or S is None:
        out['status'] = 'no swap'
        return out
    ok, gap, wall = GN.check(p, s0)
    out['swap_check'] = [bool(ok), gap, wall]
    p0, s_lp0, _, _ = GN.fixed_tilt_min(p, np.array([q[2] for q in p]), {}, {S: c})
    if p0 is None:
        out['status'] = 'shrink infeasible'
        return out
    out.update({'status': 'ok', 's_lp0': round(s_lp0, 7), 'shrink_improves': bool(s_lp0 < s0 - EPS)})
    gs, hand, cont, nb = grain_sets(p0, S)
    out.update({'hand': hand, 'S_neighbours': nb, 'grains': gs, 'L_in_comp': case['L'] in gs['comp'],
                'phi_deg': [round(GN.phi_deg(q[2]), 3) for q in p0]})
    out['paths'] = {}
    for name, G in gs.items():
        if not G:
            out['paths'][name] = {'members': [], 'note': 'no tilted member'}
            continue
        if name != 'comp' and G == gs['comp']:
            out['paths'][name] = {'members': G, 'note': 'same as comp'}
            continue
        for var, keep in (('A', True), ('B', False)):
            r = path(p0, S, c, G, steps, keep)
            r['members'] = G
            r['L_in_G'] = case['L'] in G
            r['L_blocks'] = bool(r['blockers'] and any(case['L'] in b[:2] for b in r['blockers']))
            if r.get('s'):
                r['improved'] = bool(r['s_min'] < s0 - EPS)
                r['realign_improves'] = bool(r['s_min'] < s_lp0 - EPS)
            if not (name == 'comp' and var == 'A'):
                r.pop('frames', None)
            out['paths'][name + var] = r
    out['secs'] = round(time.time() - t0, 2)
    return out


def commit(path_, msg):
    try:
        subprocess.run(['git', 'add', path_], cwd=REPO, check=False)
        subprocess.run(['git', 'commit', '-q', '-m', msg + '\n\nCo-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>',
                        '--', path_], cwd=REPO, check=False, capture_output=True)
    except Exception as e:      # noqa: BLE001
        print('commit failed', e, flush=True)


def main():
    argv = sys.argv
    only = argv[argv.index('--only') + 1] if '--only' in argv else None
    src = argv[argv.index('--src') + 1] if '--src' in argv else None
    steps = int(argv[argv.index('--steps') + 1]) if '--steps' in argv else 20
    done = set()
    if '--resume' in argv and os.path.exists(OUT):
        done = {json.loads(l)['key'] for l in open(OUT, encoding='utf-8')}
    cases = IN.all_cases() if src is None else {'193': IN.cases_193, 'win40': IN.cases_win40, 'a226': IN.cases_a226}[src]()
    rel = os.path.relpath(OUT, REPO).replace('\\', '/')
    n = 0
    for case in cases:
        if (only and case['wid'] != only) or IN.key_of(case) in done:
            continue
        rec = run_case(case, steps)
        with open(OUT, 'a', encoding='utf-8') as f:
            f.write(json.dumps(rec) + '\n')
        n += 1
        pa = rec.get('paths', {}).get('compA', {})
        print(rec['key'], rec['status'], 's0 %.5f' % rec['s0'], 'lp0', rec.get('s_lp0'), 'comp',
              pa.get('members'), pa.get('horn'), pa.get('endpoint'), pa.get('s_min'), rec.get('secs'), flush=True)
        if n % 25 == 0:
            commit(rel, 'A231 realign: %s' % rec['key'])
    commit(rel, 'A231 realign: final rows')


if __name__ == '__main__':
    main()
