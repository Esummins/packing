"""A258 task 3 [M]: NORMALISE the corpus rings by the NORMAL-CELL exchange W -> T = s1 + sec(phi) e, wall by wall.

Corpus: A253's 48 ring + poker rows (`mintilt253_curve.jsonl`: common-tilt slice, tau 0.1 .. 26 deg, three sides,
each with its pinned poker), A249's C2 rings (`twotilted249_ring2.json`, sup-margin rows with margin > 0) and
A255's all-ADJ controls (`ringsense255.jsonl`, pattern ++++++++).  Per ring and per wall:
  s1 = the wall toucher meeting the START box, W = the one meeting the END box, T = s1 + sec(phi_1) * e_wall;
  M(T) = the squares other than s1 whose interior meets int T.  The exchange is AVAILABLE iff M(T) is a subset of {W}.
Two passes: (K) poker KEPT -- which walls are locked by the poker;  (R) poker REMOVED -- all walls exchange?
After pass (R): the ring's (a_w, phi_w), membership of D / D' (geo258.in_D), the full packing check, and the
SEATED poker (geo258.seated) with the Hall minimum of ring + seated poker.
Output results/norm258.jsonl + a printed summary.
"""
import json
import math
import os
import sys

import numpy as np

import geo258 as G

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
OUT = os.path.abspath(os.path.join(HERE, '..', 'results', 'norm258.jsonl'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A253-min-tilt', 'code'))
EW = [(1, 0), (0, 1), (-1, 0), (0, -1)]


def to_wall(w, s, P):
    x, y = P[:, 0], P[:, 1]
    if w == 0:
        return np.stack([x, y], 1)
    if w == 1:
        return np.stack([y, s - x], 1)
    if w == 2:
        return np.stack([s - x, s - y], 1)
    return np.stack([s - y, x], 1)


def wall_pair(sq, s, w, tol=1e-6):
    """(index of s1, index of W) among sq: touchers of wall w meeting the start / end box."""
    tch = [i for i, Q in enumerate(sq) if to_wall(w, s, Q)[:, 1].min() < tol]
    cl = G.cells(s)
    s1 = [i for i in tch if G.depth(sq[i], cl[('C', w)]) > 1e-9]
    W = [i for i in tch if G.depth(sq[i], cl[('C', (w + 1) % 4)]) > 1e-9]
    return (s1[0] if len(s1) == 1 else None), (W[0] if len(W) == 1 else None)


def tilt_of(Q, w, s):
    P = to_wall(w, s, Q)
    k = int(np.argmin(P[:, 1]))
    e = P[(k + 1) % 4] - P[k]
    th = math.atan2(e[1], e[0]) % (math.pi / 2)
    phi = ((th + math.pi / 4) % (math.pi / 2)) - math.pi / 4
    return phi, float(P[:, 0].min())


def normalise(sq, s, keep):
    """one pass over the four walls; sq[:8] the ring, sq[8:] extra squares (kept iff keep)."""
    cur = [Q.copy() for Q in (sq if keep else sq[:8])]
    info = []
    for w in range(4):
        i1, iW = wall_pair(cur[:8], s, w)
        if i1 is None or iW is None or i1 == iW:
            info.append(dict(wall=w, status='NO-PAIR'))
            continue
        phi, a = tilt_of(cur[i1], w, s)
        T = cur[i1] + (1.0 / math.cos(phi)) * np.array(EW[w], float)
        M = [j for j, Q in enumerate(cur) if j != i1 and G.depth(Q, T) > 1e-9]
        shift = float(np.dot(cur[iW].mean(0) - T.mean(0), EW[w]))
        rec = dict(wall=w, phi_deg=phi / G.DEG, a=a, T_in=G.contain_margin(T, s), M=M, W=iW,
                   W_minus_T_along_wall=shift, dtilt_deg=(tilt_of(cur[iW], w, s)[0] - phi) / G.DEG)
        if G.contain_margin(T, s) >= -1e-12 and set(M) <= {iW}:
            cur[iW] = T
            rec['status'] = 'EXCHANGED'
        else:
            rec['status'] = 'LOCKED by %s' % [j for j in M if j != iW]
        info.append(rec)
    return cur, info


def load():
    import geom253 as G3
    import geom248 as G8
    rows = []
    p = os.path.join(ROOT, 'attempts', 'A253-min-tilt', 'results', 'mintilt253_curve.jsonl')
    for ln in open(p, encoding='utf-8'):
        r = json.loads(ln)
        if r.get('stage') != 'joint' or r.get('M', -1) <= 0:
            continue
        s = float(r['side'])
        x = G3.x_of(r['tau_deg'] * G.DEG, [int(ch) for ch in r['sigma']], r['deltas'])
        sq = [np.array(V, float) for V in G3.polys(x, s)] + [np.array(G8.verts(list(r['pose'])), float)]
        rows.append(('A253 tau=%g s=%s' % (r['tau_deg'], r['side']), s, sq))
    p = os.path.join(ROOT, 'attempts', 'A255-common-sense', 'results', 'ringsense255.jsonl')
    for ln in open(p, encoding='utf-8'):
        r = json.loads(ln)
        if r['pattern'] == '++++++++' and r['sup_margin'] > 0:
            sq = [np.array(V, float) for V in G3.W.ring_polys(list(r['x']), r['s'], False)[0]]
            rows.append(('A255 control s=%g' % r['s'], r['s'], sq))
    return rows


def main():
    rows = load()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    tally = dict(n=0, kept_locked_walls=0, kept_exchanged=0, removed_all4=0, in_D=0, in_Dprime=0, packing=0,
                 seated_stuck=0)
    with open(OUT, 'w', encoding='utf-8') as f:
        for name, s, sq in rows:
            curK, infoK = normalise(sq, s, True)
            curR, infoR = normalise(sq, s, False)
            rec = dict(name=name, s=s, kept=infoK, removed=infoR)
            tally['n'] += 1
            tally['kept_locked_walls'] += sum(1 for i in infoK if i['status'].startswith('LOCKED'))
            tally['kept_exchanged'] += sum(1 for i in infoK if i['status'] == 'EXCHANGED')
            if all(i['status'] == 'EXCHANGED' for i in infoR):
                tally['removed_all4'] += 1
                a = [i['a'] for i in infoR]
                phi = [i['phi_deg'] * G.DEG for i in infoR]
                cm, pg = G.check_packing(curR, s)
                rebuilt = G.ring(s, a, phi)
                dev = max(float(np.abs(np.sort(P, 0) - np.sort(Q, 0)).max())
                          for P in rebuilt for Q in [min(curR, key=lambda Z: np.abs(Z.mean(0) - P.mean(0)).sum())])
                rec.update(a=a, phi_deg=[p / G.DEG for p in phi], D=G.in_D(s, a, phi, True),
                           Dprime=G.in_D(s, a, phi, False), contain=cm, pair_gap=pg, rebuild_dev=dev,
                           tooth=[G.tooth_terms(s, a[w], phi[w]) for w in range(4)])
                tally['in_D'] += rec['D'] > 0
                tally['in_Dprime'] += rec['Dprime'] > 0
                tally['packing'] += (cm >= -1e-9 and pg >= -1e-9)
                best = -9
                for w in range(4):
                    if min(rec['tooth'][w]) > 0:
                        nine = rebuilt + [G.seated(s, w, a[w], phi[w])]
                        c2, p2 = G.check_packing(nine, s)
                        if c2 >= -1e-9 and p2 >= -1e-9:
                            best = max(best, G.hall_min(nine, s, 1e-9)[0])
                rec['seated_hall'] = best
                tally['seated_stuck'] += best >= 1
                # the OTHER normalisation of a wall: s1 -> T' = W - sec(phi_W) e (the row pushed to the END corner)
                alt = -9
                for w in range(4):
                    sh = infoR[w]['W_minus_T_along_wall']
                    a2 = list(a)
                    a2[w] = a[w] + max(0.0, sh)
                    if G.in_D(s, a2, phi, False) > 0 and min(G.tooth_terms(s, a2[w], phi[w])) > 0:
                        nine = G.ring(s, a2, phi) + [G.seated(s, w, a2[w], phi[w])]
                        c2, p2 = G.check_packing(nine, s)
                        if c2 >= -1e-9 and p2 >= -1e-9:
                            alt = max(alt, G.hall_min(nine, s, 1e-9)[0])
                rec['seated_hall_alt'] = alt
                tally['seated_stuck_either'] = tally.get('seated_stuck_either', 0) + (max(best, alt) >= 1)
            f.write(json.dumps(rec) + '\n')
    print(json.dumps(tally))


if __name__ == '__main__':
    main()
