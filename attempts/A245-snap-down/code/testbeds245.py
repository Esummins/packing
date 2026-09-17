"""A245 testbeds: (a) A244's certified 12-stuck candidates (all at S >= 4.00002), (b) the window / contact /
jutting rings of A239 and A226's rattler rings (8-9 squares, S = 3.877 .. 4.15, NOT 12-stuck), (c) the 193
HELD / CROWD four-crowds of A217 (S >= 4.0014).  Every configuration is a list of poses (cx, cy, theta mod
90 deg) with its side; the tag says which family."""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
A244 = os.path.join(ROOT, 'attempts', 'A244-twelve-stuck', 'results')
RINGS239 = os.path.join(ROOT, 'attempts', 'A239-rings-below-4', 'results', 'rings239.jsonl')
RING226 = os.path.join(ROOT, 'attempts', 'A226-one-flush', 'results', 'ring11_226.jsonl')
WIT217 = os.path.join(ROOT, 'attempts', 'A217-torque-probe', 'results', 'witnesses217.jsonl')


def _norm(poses):
    return [(float(x), float(y), float(t) % (math.pi / 2)) for x, y, t in poses]


def _from_z(z):
    return _norm([(z[3 * i], z[3 * i + 1], z[3 * i + 2]) for i in range(11)]), float(z[33])


def a244():
    out, seen = [], set()
    for name in ('twelve244_main.jsonl', 'twelve244_fresh.jsonl'):
        p = os.path.join(A244, name)
        if not os.path.exists(p):
            continue
        for line in open(p, encoding='utf-8'):
            r = json.loads(line)
            if not r.get('ok') or r['rid'] in seen:
                continue
            seen.add(r['rid'])
            poses, s = _from_z(r['z'])
            out.append({'rid': r['rid'], 'tag': 'a244', 'poses': poses, 's': s,
                        'supply': r.get('supply'), 'meeters': r.get('meeters')})
    out.sort(key=lambda c: c['s'])
    return out


def rings():
    out = []
    if os.path.exists(RINGS239):
        for line in open(RINGS239, encoding='utf-8'):
            r = json.loads(line)
            out.append({'rid': 'a239:' + r['label'], 'tag': 'ring', 'poses': _norm(r['poses']),
                        's': float(r['S'])})
    if os.path.exists(RING226):
        for k, line in enumerate(open(RING226, encoding='utf-8')):
            r = json.loads(line)
            poses = r.get('poses') or r.get('ring')
            out.append({'rid': 'a226:S%.2f_eps%.2f' % (r['S'], r['eps']), 'tag': 'ring',
                        'poses': _norm(poses), 's': float(r['S'])})
    return out


def four_crowds():
    out = []
    for line in open(WIT217, encoding='utf-8'):
        w = json.loads(line)
        if w['n2'] == 4 and w['cls'] in ('HELD', 'CROWD'):
            poses, s = _from_z(w['z'])
            out.append({'rid': w['wid'], 'tag': 'crowd', 'poses': poses, 's': s, 'cls': w['cls'],
                        'meeters': w.get('meeters')})
    out.sort(key=lambda c: c['rid'])
    return out


def all_configs(which=('a244', 'ring', 'crowd')):
    out = []
    if 'a244' in which:
        out += a244()
    if 'ring' in which:
        out += rings()
    if 'crowd' in which:
        out += four_crowds()
    return out


if __name__ == '__main__':
    for c in all_configs():
        print(c['tag'], c['rid'], len(c['poses']), round(c['s'], 5))
