"""A217 hunt, part 2: the crowd-forced meeters -- direction of the pull vs the wall, sign of its torque vs chi."""
import json, os, math, collections
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..', 'results')
T = [json.loads(l) for l in open(os.path.join(RES, 'torque217.jsonl'))]
W = {json.loads(l)['wid']: json.loads(l) for l in open(os.path.join(RES, 'witnesses217.jsonl'))}
WALL_UV = {'BL': {'x=0': 'u', 'y=0': 'v'}, 'BR': {'x=s': 'u', 'y=0': 'v'}, 'TR': {'x=s': 'u', 'y=s': 'v'}, 'TL': {'x=0': 'u', 'y=s': 'v'}}
c_dir = collections.Counter(); c_tor = collections.Counter(); c_pair = collections.Counter(); rows_out = []
for t in T:
    if t['cls'] != 'CROWD' or 'arrows' not in t: continue
    w = W[t['wid']]
    cr = [a for a in t['arrows'] if a['kind'] == 'crowd']
    for a in cr:
        cn = a['corner']; e = t['corners'][cn]
        m = [mm for mm in e['members'] if mm['i'] == a['i']][0]
        walls = m['walls']
        coord = 'u' if abs(a['f'][0]) > 0 and cn in ('BL', 'TL') and a['f'][0] != 0 else None
        # recover the row coordinate from the force direction in the frame
        M = {'BL': ((1, 0), (0, 1)), 'BR': ((-1, 0), (0, 1)), 'TR': ((-1, 0), (0, -1)), 'TL': ((1, 0), (0, -1))}[cn]
        fu = M[0][0] * a['f'][0] + M[0][1] * a['f'][1]; fv = M[1][0] * a['f'][0] + M[1][1] * a['f'][1]
        coord = 'u' if abs(fu) > abs(fv) else 'v'
        wall_uv = [WALL_UV[cn][x] for x in walls]
        kind = 'toward its own wall' if coord in wall_uv else ('along its wall toward the corner' if wall_uv else 'no wall')
        c_dir[kind] += 1
        tb = m['tau_bound_frame']; chi = m['chi']
        c_tor[('chi=%+d' % chi, 'crowd torque sign %+d' % (1 if tb > 1e-9 else (-1 if tb < -1e-9 else 0)))] += 1
        other = [mm for mm in e['members'] if mm['i'] != a['i']]
        c_pair[(kind, 'other meeter walls=%s' % (other[0]['walls'] if other else '?'), 'other loaded' if other and other[0]['W'] > 1e-9 else 'other unloaded')] += 1
        rows_out.append((t['wid'], round(t['s'], 4), cn, a['i'], walls, round(m['tilt_frame_deg'], 1), coord, round(a['lam'], 3), round(tb, 4), chi))
print('crowd pull direction:', dict(c_dir))
print('crowd torque sign vs chi:', dict(c_tor))
print('pairs:'); [print('  ', k, v) for k, v in sorted(c_pair.items(), key=lambda kv: -kv[1])]
print('sample rows (wid, s, corner, sq, walls, tilt_frame, coord, lam, tau_crowd_frame, chi):')
for r in rows_out[:16]: print('  ', r)
