"""A235 tests: (1) Lemma VV-AXES on random VV configurations of two non-parallel unit squares -- exactly one edge
of each square through the common vertex separates, and the pair is interior-disjoint near the contact iff
g_A >= 0 or g_B >= 0 (union, not intersection); (2) both VV rows are EXACTLY zero along finite rotations of
either square about the common vertex; (3) the inverted-pendulum curvature identities y^T H_A y = h_B,
y^T H_B y = 1/2 on the ring's 4|6; (4) Corollary NO-VV-IND against the census: a VV row outside the span of the
other rows carries no load in any multiplier (load range max = 0).
    python test235.py
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vv235 as V             # noqa: E402
import roll235 as RL          # noqa: E402
import stress234 as ST        # noqa: E402
import rows219 as R           # noqa: E402

HALF = np.array([(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)])
NHAT = np.array([(0.0, -1.0), (1.0, 0.0), (0.0, 1.0), (-1.0, 0.0)])


def square(c, th):
    Rm = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])
    return np.array(c) + HALF @ Rm.T, NHAT @ Rm.T


def sat_gaps(qA, nA, qB, nB):
    """per axis (owner, edge): min over the other's corners of the projection - 1/2 (>= 0: separating)."""
    cA, cB = qA.mean(0), qB.mean(0)
    out = {}
    for e in range(4):
        out[('A', e)] = float(((qB - cA) @ nA[e]).min() - 0.5)
        out[('B', e)] = float(((qA - cB) @ nB[e]).min() - 0.5)
    return out


def vv_config(rng):
    """A at the origin with tilt thA; B placed with its vertex kB on A's vertex kA, tilt thB such that the wedges
    are disjoint (relative angle in (90, 270) deg for the diagonal-wedge parametrisation)."""
    thA = rng.uniform(0, math.pi / 2)
    kA = rng.integers(4)
    qA, nA = square((0.0, 0.0), thA)
    P = qA[kA]
    # B's wedge at its vertex kB opens in the direction of its centre: centre = P + (sqrt2/2) * u, |u| = 1
    # A's wedge opens toward A's centre: direction dA = (0 - P) / |P|;  disjoint wedges: angle(u, dA) in (90, 270)
    dA = -P / np.linalg.norm(P)
    a0 = math.atan2(dA[1], dA[0])
    ang = a0 + math.radians(rng.uniform(95.0, 265.0))
    u = np.array([math.cos(ang), math.sin(ang)])
    cB = P + (math.sqrt(2) / 2) * u
    thB = (ang - math.radians(225.0)) % (math.pi / 2)   # the vertex at direction 225 deg from the centre is corner 0
    qB, nB = square(cB, thB)
    kB = int(np.argmin(np.linalg.norm(qB - P, axis=1)))
    assert np.linalg.norm(qB[kB] - P) < 1e-9
    return qA, nA, qB, nB, thA, thB, kA, kB, P


def test_vv_axes(n=400):
    rng = np.random.default_rng(1)
    for _ in range(n):
        qA, nA, qB, nB, thA, thB, kA, kB, P = vv_config(rng)
        if V.tilt_gap(thA, thB) < 1e-3:
            continue
        gaps = sat_gaps(qA, nA, qB, nB)
        sepA = [e for e in range(4) if abs(gaps[('A', e)]) < 1e-9]
        sepB = [e for e in range(4) if abs(gaps[('B', e)]) < 1e-9]
        assert len(sepA) == 1 and len(sepB) == 1, (sepA, sepB, gaps)
        assert max(v for v in gaps.values()) < 1e-9                         # touching: no axis strictly positive
        e, f = sepA[0], sepB[0]
        # the union: random small relative translations of B; disjoint (some axis >= 0) iff g_A >= 0 or g_B >= 0
        for _ in range(20):
            u = rng.normal(size=2) * 1e-3
            g2 = sat_gaps(qA, nA, qB + u, nB)
            disjoint = max(g2.values()) >= -1e-12
            union = g2[('A', e)] >= -1e-12 or g2[('B', f)] >= -1e-12
            assert disjoint == union, (u, g2)
    print('VV-AXES: exactly one separating edge per square, feasible set = union of the two half-spaces: ok (%d configs)' % n)


def test_exact_zero_along_rotation():
    rng = np.random.default_rng(2)
    for _ in range(100):
        qA, nA, qB, nB, thA, thB, kA, kB, P = vv_config(rng)
        gaps = sat_gaps(qA, nA, qB, nB)
        e = next(k for k in range(4) if abs(gaps[('A', k)]) < 1e-9)
        f = next(k for k in range(4) if abs(gaps[('B', k)]) < 1e-9)
        for om in (0.3, -0.3, 0.05):
            Rm = np.array([[math.cos(om), -math.sin(om)], [math.sin(om), math.cos(om)]])
            qB2, nB2 = P + (qB - P) @ Rm.T, nB @ Rm.T           # B rotated about P
            gA = (qB2[kB] - qA.mean(0)) @ nA[e] - 0.5
            gB = (qA[kA] - qB2.mean(0)) @ nB2[f] - 0.5
            assert abs(gA) < 1e-12 and abs(gB) < 1e-12, (gA, gB)
            qA2, nA2 = P + (qA - P) @ Rm.T, nA @ Rm.T           # A rotated about P
            gA = (qB[kB] - qA2.mean(0)) @ nA2[e] - 0.5
            gB = (qA2[kA] - qB.mean(0)) @ nB[f] - 0.5
            assert abs(gA) < 1e-12 and abs(gB) < 1e-12, (gA, gB)
    print('both VV rows are exactly zero along finite rotations of either square about P: ok')


def test_curvature_ring():
    raw = [json.loads(l) for l in open(ST.WIT, encoding='utf-8') if 'rand_0_0569|t20' in l][0]
    w = ST.from_w217(raw)
    cen, cts = V.analyse(w)
    e = next(x for x in cen['vv'] if x['pair'] == [4, 6])
    t = RL.contact_terms(w['z'], w['rows'], e['rowA'], e['rowB'], np.array(e['P']), 4, 6)
    assert abs(t['yj_HA_yj'] - t['h_B']) < 1e-9 and abs(t['yj_HB_yj'] - 0.5) < 1e-8
    assert abs(t['yi_HB_yi'] - t['h_A']) < 1e-9 and abs(t['yi_HA_yi'] - 0.5) < 1e-8
    assert t['h_B'] > 0 and t['h_A'] > 0
    print('ring 4|6: y^T H_A y = h_B = %.4f, y^T H_B y = 1/2 (inverted-pendulum terms, both positive): ok' % t['h_B'])


def test_no_vv_ind_against_census():
    rows = [json.loads(l) for l in open(os.path.join(V.ATT, 'results', 'census235.jsonl'), encoding='utf-8')]
    n_ind, n_dep, bad = 0, 0, []
    for o in rows:
        for e in o['vv']:
            if e['load_range'] is None:
                continue
            if not e['gA_in_span']:
                n_ind += 1
                if e['load_range'][1] > 1e-5:
                    bad.append((o['name'], e['pair'], 'A', e['load_range']))
            else:
                n_dep += 1
    assert not bad, bad
    print('NO-VV-IND vs census: %d VV rows outside the span carry no load (max over the polytope <= 1e-5), %d dependent: ok' % (n_ind, n_dep))


if __name__ == '__main__':
    ST.set_priority()
    test_vv_axes()
    test_exact_zero_along_rotation()
    test_curvature_ring()
    test_no_vv_ind_against_census()
