"""A237 Lemma TILT-MIN, tested (docs/proofs/pocket_waste.md s.1).  For every doubly-met corner of the ring
rand_0_0569|t20, the 193 HELD / CROWD four-crowds of A217 and Trump's TL corner (corner frame: u, v = distances from
the two walls, the open box (0,1)^2):
  (a) ONE-TILTED: some meeter is tilted;
  (b) a FLAT meeter touching a wall at offset delta along it (A = [delta, 1+delta] x [0, 1] in the frame with that
      wall as the floor) with a tilted partner of tilt theta in (0, 90) satisfies  sin(theta) <= delta  (the exact
      curve: Theorem B's clause (W) at zeta = theta) and the partner's lowest point is at height
      >= 1 - (delta - sin theta) tan theta  (its depth below the box's top is at most that);
  (c) DEPTH-BUDGET: d_A + d_B <= 1 for the two meeters (d = the infinity-depth 1 - min_Q max(u, v));
  (d) the tilts of the tilted meeters against the witness's imposed tilt floor tmin_deg (HELD) -- how many sit AT it.
    python tiltmin237.py  -> results/tiltmin237.jsonl (one row per corner) + a summary on stdout
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
try:
    import psutil
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    psutil.Process().cpu_affinity(list(range(16)))
except Exception:
    pass
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A236-ring-capacity', 'code'))
import band236 as BD                                                   # noqa: E402

ATT = os.path.abspath(os.path.join(HERE, '..'))
ATTS = os.path.abspath(os.path.join(ATT, '..'))
WIT = os.path.join(ATTS, 'A217-torque-probe', 'results', 'witnesses217.jsonl')
SURVEY = os.path.join(ATTS, 'A226-one-flush', 'results', 'survey226.jsonl')
OUT = os.path.join(ATT, 'results', 'tiltmin237.jsonl')
TOL = 1e-6


def frame_verts(p, s, c):
    """vertices of the square in the corner frame (u, v) of c."""
    V = BD.verts(p)
    if c == 'BL':
        return V
    if c == 'BR':
        return np.array([(s - x, y) for x, y in V])
    if c == 'TR':
        return np.array([(s - x, s - y) for x, y in V])
    return np.array([(x, s - y) for x, y in V])


def depth(V):
    """infinity-depth 1 - min over the square of max(u, v): min over the boundary (the min of a convex function of
    ... no: max(u, v) is convex, its min over a convex polygon is attained anywhere; sample the edges finely)."""
    best = 1e9
    for i in range(4):
        a, b = V[i], V[(i + 1) % 4]
        for t in np.linspace(0.0, 1.0, 401):
            q = a + t * (b - a)
            best = min(best, max(q[0], q[1]))
    return max(0.0, 1.0 - best)


def flat_offset(V):
    """for a flat square in the frame: which wall it touches (u = 0 or v = 0) and its offset along that wall;
    None if it touches neither."""
    u0, v0 = V[:, 0].min(), V[:, 1].min()
    if v0 <= TOL:
        return 'floor', float(u0)
    if u0 <= TOL:
        return 'wall', float(v0)
    return None, None


def tilt_in_frame(V, wall):
    """the tilt theta in (0, 90) of the partner in the frame whose floor is the flat meeter's wall: the angle of
    the edge leaving its lowest vertex to the right."""
    if wall == 'wall':
        V = np.array([(y, x) for x, y in V])
    i0 = int(np.argmin(V[:, 1]))
    nb = [V[(i0 + 1) % 4] - V[i0], V[(i0 - 1) % 4] - V[i0]]
    e = max(nb, key=lambda d: d[0])
    return math.degrees(math.atan2(e[1], e[0])) % 90.0, float(V[:, 1].min())


def corner_row(label, src, poses, s, c, tmin=None):
    ms = BD.meeters(poses, s, c)
    if len(ms) < 2:
        return None
    V = {i: frame_verts(poses[i], s, c) for i in ms}
    d = {i: depth(V[i]) for i in ms}
    fl = {i: BD.is_flush(poses[i][2]) for i in ms}
    row = {'label': label, 'src': src, 's': s, 'corner': c, 'meeters': ms, 'depths': {str(i): d[i] for i in ms},
           'flush': {str(i): bool(fl[i]) for i in ms}, 'n_flat': sum(fl.values()), 'one_tilted': bool(sum(fl.values()) < len(ms)),
           'depth_sum_max_pair': float(max(d[i] + d[j] for i in ms for j in ms if i < j)), 'tmin_deg': tmin,
           'tilts': {str(i): math.degrees(BD.phi_of(poses[i][2])) for i in ms}}
    row['depth_budget_ok'] = bool(row['depth_sum_max_pair'] <= 1.0 + 1e-9)
    pairs = []
    for a in ms:
        if not fl[a]:
            continue
        wall, delta = flat_offset(V[a])
        if wall is None:
            pairs.append({'flat': a, 'hover': True})
            continue
        for b in ms:
            if b == a or fl[b]:
                continue
            th, low = tilt_in_frame(V[b], wall)
            thr = math.radians(th)
            bound_low = 1.0 - (delta - math.sin(thr)) * math.tan(thr)
            pairs.append({'flat': a, 'partner': b, 'wall': wall, 'delta': delta, 'theta_deg': th,
                          'sin_le_delta': bool(math.sin(thr) <= delta + 1e-7), 'sin_theta': math.sin(thr),
                          'partner_low': low, 'low_bound': bound_low, 'low_ok': bool(low >= bound_low - 1e-7),
                          'theta_max_deg': math.degrees(math.asin(min(1.0, delta)))})
    row['pairs'] = pairs
    row['tiltmin_ok'] = bool(all(p.get('sin_le_delta', True) and p.get('low_ok', True) for p in pairs))
    tilted = [math.degrees(BD.phi_of(poses[i][2])) for i in ms if not fl[i]]
    row['min_tilt_deg'] = min(tilted) if tilted else None
    row['at_floor'] = bool(tmin is not None and tilted and min(tilted) <= tmin + 0.05)
    return row


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    rows = []
    for l in open(WIT, encoding='utf-8'):
        w = json.loads(l)
        if w['n2'] == 4 and w['cls'] in ('HELD', 'CROWD'):
            poses, s = [(w['z'][3 * i], w['z'][3 * i + 1], w['z'][3 * i + 2]) for i in range(11)], w['z'][-1]
            for c in BD.CORNERS:
                r = corner_row(w['wid'], w['cls'], poses, s, c, w.get('tmin_deg'))
                if r:
                    r['rid'] = w['rid']
                    rows.append(r)
    for l in open(SURVEY, encoding='utf-8'):
        r = json.loads(l)
        if r['n'] == 11:
            poses = [tuple(p) for p in r['squares']]
            for c in BD.CORNERS:
                rr = corner_row('trump', 'record', poses, r['side'], c)
                if rr:
                    rows.append(rr)
    with open(OUT, 'w', encoding='utf-8') as fh:
        for r in rows:
            fh.write(json.dumps(r) + '\n')
    n = len(rows)
    print('corners', n, 'one_tilted', sum(r['one_tilted'] for r in rows), 'tiltmin_ok', sum(r['tiltmin_ok'] for r in rows),
          'depth_budget_ok', sum(r['depth_budget_ok'] for r in rows))
    pairs = [p for r in rows for p in r['pairs'] if 'partner' in p]
    hov = sum(1 for r in rows for p in r['pairs'] if p.get('hover'))
    print('flat-wall pairs', len(pairs), 'hovering flat meeters', hov, 'sin<=delta', sum(p['sin_le_delta'] for p in pairs),
          'low_ok', sum(p['low_ok'] for p in pairs))
    if pairs:
        sl = sorted(p['theta_max_deg'] - p['theta_deg'] for p in pairs)
        print('slack theta_max - theta: min %.3f median %.3f' % (sl[0], sl[len(sl) // 2]))
    held = [r for r in rows if r['src'] == 'HELD']
    print('HELD corners', len(held), 'min tilt at the imposed floor', sum(bool(r['at_floor']) for r in held))
    ds = sorted(r['depth_sum_max_pair'] for r in rows)
    print('depth sum: max %.4f median %.4f' % (ds[-1], ds[len(ds) // 2]))
    print('wrote', OUT)


if __name__ == '__main__':
    main()
