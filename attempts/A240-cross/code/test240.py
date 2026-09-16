"""A240 tests (python test240.py; ~40 s).
 1. Lemma PARTNER-TORQUE: the torque of a loaded vertex-on-edge row on the VERTEX owner equals
    lam * (h_k x R(theta_o - theta_p) nu_e) -- a function of the tilt difference and the vertex/edge labels only --
    and on the EDGE owner equals lam * x, x the tangential coordinate of the contact along the owner's edge
    (position), on every loaded edge row of Trump + A217's witnesses; the corner closed forms of cross.md s.1
    (B owner: tau_A = -(cos d + sin d)/2 for d = phi_B - phi_A < 0, (cos d - sin d)/2 for d > 0; A owner: mirror).
 2. Lemma W: every loaded tilted wall row torques the square with sign -chi (all witnesses).
 3. Per-meeter torque balance closes (|sum| <= 5e-6, the LP's 1e-6 slack) at every doubly-met corner of cross240.jsonl.
 4. CROSS-PLANAR on the data: whenever the loaded LR and TB chains both exist they share a square or a square of
    one touches a square of the other (an unloaded contact) -- never neither.
 5. OPPOSE's refutation is reproducible: >= 200 locked same-handed corners, >= 30 at A217's deduplicated free FJ points, and at
    least one locked same-handed VE pair with both tilts >= 1 deg off flat.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A234-handedness', 'code'))
import stress234 as S          # noqa: E402
import geom217 as G            # noqa: E402
import cross240 as X           # noqa: E402

RES = os.path.join(HERE, '..', 'results', 'cross240.jsonl')
H = np.array([(-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5)])
NU = np.array([(0, -1.), (1, 0), (0, 1), (-1, 0)])


def R(a):
    return np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])


def cr(a, b):
    return float(a[0] * b[1] - a[1] * b[0])


def test_partner_torque(ws):
    worst_v = worst_e = 0.0
    n = 0
    corner_forms = 0
    for w in ws:
        if w['lam'] is None:
            continue
        z, rows, A, lam = w['z'], w['rows'], w['A'], w['lam']
        cx, cy, th, s, nn = S.unpack(z)
        q, nrm, c = S.verts(z), S.normals(z), np.stack([cx, cy], -1)
        for k, r in enumerate(rows):
            if r['kind'] != 'edge' or lam[k] <= 1e-7:
                continue
            p, kk, o, e = r['i'], r['corner'], r['j'], r['edge']
            worst_v = max(worst_v, abs(cr(H[kk], R(th[o] - th[p]) @ NU[e]) - A[k, 3 * p + 2]))
            t = np.array([-nrm[o, e][1], nrm[o, e][0]])
            x = float(t @ (q[p, kk] - c[o]))
            worst_e = max(worst_e, abs(x - A[k, 3 * o + 2]))
            n += 1
            # the corner closed form: a {NW, SE} joint with B the owner of its top edge (e = 2) and A's lowest
            # (k = 0) or rightmost (k = 1) vertex on it; d = phi_B - phi_A (owner minus vertex owner)
            d = th[o] - th[p]
            if e == 2 and kk in (0, 1):
                pred = -(math.cos(d) + math.sin(d)) / 2 if kk == 0 else (math.cos(d) - math.sin(d)) / 2
                assert abs(pred - A[k, 3 * p + 2]) < 1e-9
                corner_forms += 1
    assert worst_v < 1e-9 and worst_e < 1e-9, (worst_v, worst_e)
    print('1. PARTNER-TORQUE: vertex-owner torque = h_k x R(theta_o - theta_p) nu_e (err %.1e), edge-owner torque = tangential '
          'coordinate (err %.1e) on %d loaded edge rows; corner closed form checked on %d rows' % (worst_v, worst_e, n, corner_forms))


def test_lemma_w(ws):
    n = bad = 0
    for w in ws:
        if w['lam'] is None:
            continue
        z, rows, A, lam = w['z'], w['rows'], w['A'], w['lam']
        cx, cy, th, s, nn = S.unpack(z)
        for k, r in enumerate(rows):
            if r['kind'] != 'wall' or lam[k] <= 1e-7:
                continue
            chi, h, d = X.handed(th[r['i']] % (math.pi / 2))
            if chi == 0:
                continue
            # global torque sign: the wall torques toward alignment, sign -chi (Lemma W, every wall)
            n += 1
            if X.sgn(float(A[k, 3 * r['i'] + 2])) != -chi:
                bad += 1
    assert bad == 0, bad
    print('2. Lemma W: sign -chi on %d / %d loaded tilted wall rows' % (n - bad, n))


def test_records():
    rs = [json.loads(l) for l in open(RES, encoding='utf-8')]
    worst = 0.0
    same = same_fj = opp = 0
    same_ve_off = 0
    both = share = touch = 0
    for r in rs:
        if not r['has_stress']:
            continue
        for c in r['corners']:
            for m in c['members']:
                worst = max(worst, abs(m['tau_sum']))
            if c['locked']:
                if c['pair_frame'] == 'same':
                    same += 1
                    same_fj += r['name'].startswith('fj_')
                    if c['partner_type'] == 'VE' and min(min(m['tilt_frame_deg'], 90 - m['tilt_frame_deg']) for m in c['members']) >= 1.0:
                        same_ve_off += 1
                elif c['pair_frame'] == 'opposite':
                    opp += 1
        ch = r['chains']
        if ch['LR'] and ch['TB']:
            both += 1
            share += bool(ch['shared'])
            touch += (not ch['shared']) and bool(ch['touch_only'])
    assert worst <= 5e-6, worst      # the LP carries a 1e-6 slack on stationarity (stress234)
    print('3. torque balance closes at every meeter: max |sum| = %.1e' % worst)
    assert both == share + touch, (both, share, touch)
    print('4. CROSS-PLANAR on the data: LR and TB loaded chains share a square on %d and only TOUCH (an unloaded contact) on %d '
          'of the %d witnesses carrying both; never neither' % (share, touch, both))
    assert same >= 200 and same_fj >= 30 and same_ve_off >= 1 and opp < same / 10
    print('5. OPPOSE refuted: %d locked same-handed corners (%d at free FJ points; %d VE pairs with both tilts >= 1 deg off flat) '
          'against %d opposite-handed' % (same, same_fj, same_ve_off, opp))


if __name__ == '__main__':
    S.set_priority()
    ws = [S.trump()] + S.a217_witnesses()
    test_partner_torque(ws)
    test_lemma_w(ws)
    test_records()
    print('all A240 tests passed')
