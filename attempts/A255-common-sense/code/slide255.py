"""A255 addendum: the CORPUS TEST of Lemma SLIDE-NORMAL, in its CELLS form.

For a TILTED wall toucher s1 (global tilt phi, |phi| in (FLAT, 45)) and a direction d = +-1 along its wall
the NORMAL CELL is  T_d(s1) := s1 + d * sec(phi) * (wall direction): the unit square of s1's tilt, touching the
same wall, edge-to-edge with s1 (contact length 1 - tan|phi|).  T is a (tilted) unit cell, so Lemma CELLS
(ring_swap.md s.1.3: "any poses") applies to Pi = {T}:
    |M(T)| = 0  FREE      any square teleports onto T                              (SWAP, |X| = 1)
    |M(T)| = 1  SLIDE     the one square D meeting T teleports onto T -- the PI's normalising slide, as an
                          exchange: no path needed; NORMAL if D already IS T (centre 1e-4, tilt 1e-3)
    |M(T)| >= 2 BLOCKED   the blockers are classified:
        W  touches the same wall (the "next wall square", the PI's (b))
        a  meets the cell c (c := the border cell met by s1 that reaches farthest in direction d) -- (a)
        U  neither: a square of the second layer / interior poking into T -- the PI's (c); flag `meets_c`
           would contradict the PI's claim "(c) can never be a second meeter of c": by construction U has
           meets_c False, so the claim is tested as:  is every non-wall blocker that meets c NOT 'above s1'
           (above := its centre is farther than 1 from the wall and inside s1's along-wall extent)?
    OUT  T is not inside the container.
    python slide255.py  -> results/slide255.jsonl, results/slide255_summary.json
"""
import collections
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import geo255 as G                                                    # noqa: E402
from local255 import sat_gap                                          # noqa: E402
from sense255 import corpora                                          # noqa: E402

OUT = os.path.join(ATT, 'results', 'slide255.jsonl')
SUM = os.path.join(ATT, 'results', 'slide255_summary.json')
WALLDIR = {'x0': (0.0, 1.0), 'x1': (0.0, 1.0), 'y0': (1.0, 0.0), 'y1': (1.0, 0.0)}


def wall_coords(p, wall, s):
    """(along, depth) of a point-like centre for the wall."""
    cx, cy = p[0], p[1]
    return {'x0': (cy, cx), 'x1': (cy, s - cx), 'y0': (cx, cy), 'y1': (cx, s - cy)}[wall]


def extreme_cell(i, wall, d, s, table):
    """among the border cells ON this wall met by square i, the one reaching farthest in direction d."""
    best, bk = None, None
    for k, ms in table.items():
        if i not in ms:
            continue
        R = G.cell_rect(k, s)
        on = {'x0': R[0] < 1e-9, 'x1': R[1] > s - 1e-9, 'y0': R[2] < 1e-9, 'y1': R[3] > s - 1e-9}[wall]
        if not on:
            continue
        lo, hi = (R[2], R[3]) if wall in ('x0', 'x1') else (R[0], R[1])
        v = hi if d > 0 else -lo
        if best is None or v > best:
            best, bk = v, k
    return bk


def records(poses, s):
    V = [G.corners_of(*p) for p in poses]
    table = G.meeter_table(poses, s, G.all_cells(s))
    tch = [G.touches(p[0], p[1], p[2], s) for p in poses]
    for i, p in enumerate(poses):
        sg = G.sense(p[2])
        if sg in (0, 'X'):
            continue
        for wall in sorted(tch[i]):
            if len(tch[i]) > 1:
                continue                                  # wedged / two-wall squares: alone (WEDGED-SEAL)
            sec = 1.0 / math.cos(math.radians(G.phi_deg(p[2])))
            a_i, _ = wall_coords(p, wall, s)
            hw = 0.5 * (abs(math.cos(p[2])) + abs(math.sin(p[2])))
            for d in (1, -1):
                wx, wy = WALLDIR[wall]
                T = (p[0] + d * sec * wx, p[1] + d * sec * wy, p[2])
                VT = G.corners_of(*T)
                rec = {'i': i, 'wall': wall, 'd': d, 'sense': sg, 'phi': round(G.phi_deg(p[2]), 4)}
                if VT.min() < -1e-7 or VT.max() > s + 1e-7:
                    rec['status'] = 'OUT'
                    yield rec
                    continue
                bl = [j for j in range(len(poses)) if j != i and -sat_gap(V[j], VT) > 1e-9]
                c = extreme_cell(i, wall, d, s, table)
                rec['cell'] = G.cell_name(c) if c else None
                rec['second_meeters'] = [j for j in (table[c] if c else []) if j != i]
                if not bl:
                    rec['status'] = 'FREE'
                elif len(bl) == 1:
                    q = poses[bl[0]]
                    same = math.hypot(q[0] - T[0], q[1] - T[1]) < 1e-4 and \
                        abs(G.phi_deg(q[2]) - G.phi_deg(T[2])) < 1e-3 * 57.3
                    rec['status'] = 'NORMAL' if same else 'SLIDE'
                    rec['slider_is_second_meeter'] = bool(c and bl[0] in table[c])
                    rec['slider_sense'] = G.sense(q[2])
                else:
                    rec['status'] = 'BLOCKED'
                    types = []
                    for j in bl:
                        al, dep = wall_coords(poses[j], wall, s)
                        above = dep > 1.0 and abs(al - a_i) < hw
                        t = 'W' if wall in tch[j] else ('a' if (c and j in table[c]) else 'U')
                        types.append({'j': j, 'type': t, 'above': bool(above), 'sense': G.sense(poses[j][2]),
                                      'meets_c': bool(c and j in table[c])})
                    rec['blockers'] = types
                yield rec


def main():
    tab = collections.defaultdict(collections.Counter)
    btab = collections.defaultdict(collections.Counter)
    claim = collections.Counter()
    with open(OUT, 'w') as f:
        for corpus, rid, s, poses in corpora():
            band = corpus + ('<4' if s < 4 - 1e-9 else '>=4')
            for r in records(poses, s):
                tab[band][r['status']] += 1
                if r['status'] == 'SLIDE':
                    tab[band]['SLIDE:' + ('second-meeter' if r['slider_is_second_meeter'] else 'other') +
                              (':same-sense' if r['slider_sense'] == r['sense'] else ':other-sense')] += 1
                if r['status'] == 'BLOCKED':
                    key = ''.join(sorted(b['type'] for b in r['blockers']))
                    btab[band][key] += 1
                    for b in r['blockers']:
                        if b['above']:
                            claim['above-blocker' + (' MEETS c' if b['meets_c'] else ' misses c')] += 1
                f.write(json.dumps({'corpus': corpus, 'rid': rid, 's': s, **r}) + '\n')
    out = {'status': {b: dict(t) for b, t in tab.items()}, 'blocked_types': {b: dict(t.most_common()) for b, t in btab.items()},
           'pi_claim_c': dict(claim)}
    json.dump(out, open(SUM, 'w'), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
