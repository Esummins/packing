"""A218 -- the k0 COUNT tested on A217's witnesses: at every doubly-met open corner of every witness,
who pushes whom (in the corner frame), whether the two meeters press on each other (Lemma PUSH's
hypothesis), which squares HOLD a meeter (a loaded push with a component toward the corner), whether a
holder is a meeter of some corner, and the per-witness count |meeters| + |non-meeter holders|.
    python count218.py [--kept]      # --kept: only witnesses217.jsonl (486); default: all search files
Writes results/count218.jsonl (one record per doubly-met open corner) and results/count218.md.
"""
import argparse
import collections
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
A217 = os.path.abspath(os.path.join(HERE, '..', '..', 'A217-torque-probe', 'code'))
sys.path.insert(0, A217)
import geom217 as G          # noqa: E402
import stress217 as S        # noqa: E402
import crowd217 as C         # noqa: E402
import collect217 as K       # noqa: E402

RES = os.path.abspath(os.path.join(HERE, '..', 'results'))
EPS = 1e-6          # multipliers below this are LP noise (the one 5e-8 "exception" of the first run)
GENUINE = ('SETTLED', 'K0FREE', 'BOXK0')
WALL_U = {'BL': 'x=0', 'BR': 'x=s', 'TR': 'x=s', 'TL': 'x=0'}     # the corner's u-wall (u = 0)
WALL_V = {'BL': 'y=0', 'BR': 'y=0', 'TR': 'y=s', 'TL': 'y=s'}


def analyse(r):
    z = np.array(r['z'])
    tmin = None if r.get('tmin_deg') is None else math.radians(r['tmin_deg'])
    extra = None
    if r.get('crowd_delta') is not None:
        extra = C.active_crowd_fixed(z, r['designated'], r['crowd_delta'])
    return z, S.analyse(z, tmin=tmin, extra_active=extra)


def force_graph(a):
    """F[(c, b)] = total loaded force ON square b FROM square c (global frame); walls[b][wall] = load;
    pulls[b] = external crowd pulls on b (list of (corner, f))."""
    F = collections.defaultdict(lambda: np.zeros(2))
    walls = collections.defaultdict(lambda: collections.defaultdict(float))
    pulls = collections.defaultdict(list)
    for ar in a['arrows']:
        f = np.array(ar['f'])
        if ar['kind'] == 'edge':
            F[(ar['j'], ar['i'])] += f
            F[(ar['i'], ar['j'])] -= f
        elif ar['kind'] == 'wall':
            walls[ar['i']][ar['wall']] += ar['lam']
        elif ar['kind'] == 'crowd':
            pulls[ar['i']].append((ar['corner'], f))
    return F, walls, pulls


def corner_record(w, a, F, walls, pulls, cn, meet_all):
    cx, cy, th, s = G.unpack(np.array(w['z']))
    M, _, det = G.corner_frame(cn, s)
    meet = a['corners'][cn]['meeters']
    rec = {'wid': w['wid'], 'cls': w['cls'], 's': w['s'], 'corner': cn, 'meeters': meet, 'members': []}
    for b in meet:
        others = [x for x in meet if x != b]
        wu = walls[b].get(WALL_U[cn], 0.0) > EPS
        wv = walls[b].get(WALL_V[cn], 0.0) > EPS
        m = {'i': b, 'tilt_frame_deg': math.degrees(((th[b] if det == 1 else -th[b]) % (math.pi / 2))),
             'touch_u': wu, 'touch_v': wv, 'loaded': False, 'partner_push': [], 'holders': [], 'pulls': []}
        tot = np.zeros(2)
        for c in range(G.N):
            if c == b:
                continue
            f = M @ F[(c, b)]                      # force on b from c, corner frame
            if np.abs(f).max() <= EPS:
                continue
            tot += f
            m['loaded'] = True
            n = f / np.linalg.norm(f)
            ent = {'c': int(c), 'fu': float(f[0]), 'fv': float(f[1])}
            if c in others:
                ent['push_out'] = bool(n[0] > EPS or n[1] > EPS)
                ent['along_ok'] = bool((not wv or n[0] > EPS) and (not wu or n[1] > EPS))
                m['partner_push'].append(ent)
            elif f[0] < -EPS or f[1] < -EPS:
                ent['meeter_of'] = [k for k, v in meet_all.items() if c in v]
                ent['along_wall'] = bool((wv and f[0] < -EPS) or (wu and f[1] < -EPS))
                m['holders'].append(ent)
        if wu or wv:
            m['loaded'] = True
        for corner, f in pulls.get(b, []):
            ff = M @ f
            m['pulls'].append({'corner': corner, 'fu': float(ff[0]), 'fv': float(ff[1]),
                               'along_wall': bool((wv and ff[0] < -EPS) or (wu and ff[1] < -EPS))})
        m['partner_loaded'] = any(abs(p['fu']) + abs(p['fv']) > EPS for p in m['partner_push'])
        rec['members'].append(m)
    return rec


def tally(recs, wit_by):
    out = []
    for cls in ('SETTLED', 'K0FREE', 'BOXK0', 'HELD', 'CROWD'):
        R = [r for r in recs if r['cls'] == cls]
        if not R:
            continue
        mem = [m for r in R for m in r['members']]
        d = collections.OrderedDict()
        d['doubly-met open corners'] = len(R)
        d['corners with the two meeters pressing on each other (A-B loaded)'] = sum(
            1 for r in R if any(m['partner_loaded'] for m in r['members']))
        d['meeters'] = len(mem)
        d['meeters carrying no load at all (rattler meeters)'] = sum(1 for m in mem if not m['loaded'])
        d['meeters touching a corner wall (loaded)'] = sum(1 for m in mem if m['touch_u'] or m['touch_v'])
        d['meeters touching BOTH corner walls'] = sum(1 for m in mem if m['touch_u'] and m['touch_v'])
        pp = [p for m in mem for p in m['partner_push']]
        d['loaded partner pushes'] = len(pp)
        d['  ... with a positive frame component (Lemma PUSH (i))'] = sum(1 for p in pp if p['push_out'])
        d['  ... along the touched wall away from the corner (Lemma PUSH (ii))'] = sum(1 for p in pp if p['along_ok'])
        pm = [m for m in mem if m['partner_loaded']]
        d['meeters pushed by their partner'] = len(pm)
        d['  ... having a holder'] = sum(1 for m in pm if m['holders'])
        d['  ... having a holder that is no meeter of any corner'] = sum(
            1 for m in pm if any(not h['meeter_of'] for h in m['holders']))
        d['  ... having an along-wall holder'] = sum(1 for m in pm if any(h['along_wall'] for h in m['holders']))
        d['  ... pulled externally instead (CROWD/HELD)'] = sum(1 for m in pm if m['pulls'])
        hm = [h for m in mem for h in m['holders']]
        d['holder relations'] = len(hm)
        d['  ... holder is a meeter of another corner'] = sum(1 for h in hm if h['meeter_of'])
        d['  ... along the touched wall'] = sum(1 for h in hm if h['along_wall'])
        d['pulled meeters (external crowd rows)'] = sum(1 for m in mem if m['pulls'])
        d['  ... pull along the touched wall'] = sum(1 for m in mem if any(p['along_wall'] for p in m['pulls']))
        d['  ... pulled meeter also has a square holder'] = sum(1 for m in mem if m['pulls'] and m['holders'])
        # per-witness count
        cnt = []
        for wid, rs in wit_by.items():
            if rs[0]['cls'] != cls:
                continue
            meet = set(b for r in rs for b in r['meeters'])
            hold = set(h['c'] for r in rs for m in r['members'] for h in m['holders'] if not h['meeter_of'])
            npull = sum(1 for r in rs if any(m['pulls'] for m in r['members']))
            cnt.append((len(rs), len(meet), len(hold), npull))
        n2s = sorted(set(c[0] for c in cnt))
        for n2 in n2s:
            cc = [c for c in cnt if c[0] == n2]
            d['witnesses with n2 = %d: |meeters| + |non-meeter holders| min/max' % n2] = '%d: %d / %d' % (
                len(cc), min(c[1] + c[2] for c in cc), max(c[1] + c[2] for c in cc))
            if cls in ('CROWD', 'HELD'):
                d['  n2 = %d: |meeters| + |non-meeter holders| + corners pulled, min' % n2] = min(
                    c[1] + c[2] + c[3] for c in cc)
        out.append((cls, d))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--kept', action='store_true')
    args = ap.parse_args()
    if args.kept:
        ws = [json.loads(l) for l in open(os.path.join(A217, '..', 'results', 'witnesses217.jsonl'))]
    else:
        ws = K.load_witnesses()
        for r in ws:                                   # stable id: the run id (the search files grow)
            r['wid'] = r.get('wid') or r['rid']
    recs, wit_by = [], collections.OrderedDict()
    for w in ws:
        if w['n2'] == 0:
            continue
        try:
            z, a = analyse(w)
        except Exception as e:                    # noqa
            print('skip', w['wid'], repr(e))
            continue
        if a['fj'] == 'INFEASIBLE':
            continue
        F, walls, pulls = force_graph(a)
        meet_all = {cn: a['corners'][cn]['meeters'] for cn in G.CORNER_NAMES}
        for cn in G.CORNER_NAMES:
            e = a['corners'][cn]
            if e['settled'] is not None or len(e['meeters']) < 2:
                continue
            rec = corner_record(w, a, F, walls, pulls, cn, meet_all)
            recs.append(rec)
            wit_by.setdefault(w['wid'], []).append(rec)
    os.makedirs(RES, exist_ok=True)
    with open(os.path.join(RES, 'count218.jsonl'), 'w') as f:
        for r in recs:
            f.write(json.dumps(r) + '\n')
    lines = ['# A218 count test on A217 witnesses (%s; %d doubly-met open corners in %d witnesses)\n' % (
        'kept 486' if args.kept else 'all search files', len(recs), len(wit_by))]
    for cls, d in tally(recs, wit_by):
        lines.append('\n## %s\n' % cls)
        for k, v in d.items():
            lines.append('- %s: %s' % (k, v))
    open(os.path.join(RES, 'count218.md'), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
