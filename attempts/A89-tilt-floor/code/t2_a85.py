"""A89 / T2 TASK D: A85's LP rows and the BL blocker-box census under the
tilt-floor deletion  Z(theta_0) = (0, theta_0) union (90 - theta_0, 90).

D1  attempts/A85-k0-route/results/a85_lp_samples.jsonl (24 records, 12 distinct
    node tags; a85_lp_plan.json lists all 26 planned nodes) -- group, boxes,
    verdict; then per candidate theta_0 which FAILED nodes carry a blocker box
    that meets Z(theta_0) partly / entirely.  S1-INT boxes are interior cells,
    NOT blocker boxes: reported separately, flagged 'interior: lemma not
    applicable'.

D2  a85_reach_BL.json variant sigma_closed_7 (678 cover boxes, 644 sound) and
    a85_pairs_BL.json (33 656 surviving unordered pairs at level 2).
    Parametrisation confirmed by reading corner85.py: T_EDGES are edges in
    t = tan(theta/2), t in {0, 1/8, 1/4, 3/8, 5/11, 3/5, 7/9, 1} -> theta in
    [0, 90) via theta = 2*atan(t); cover_sigma additionally bisects theta at the
    DEGREE midpoint, so the realised cover has 9 theta bins, not 7.

Usage: python t2_a85.py
"""
from __future__ import annotations

import json
import math
import os
import re
import sys
import time
from fractions import Fraction as Fr

import a89lib as L

A85 = os.path.join(L.ATT, 'A85-k0-route')
sys.path.insert(0, os.path.join(A85, 'code'))
RES85 = os.path.join(A85, 'results')

from caselp import Box, t_lo, t_hi                            # noqa: E402
from pinguard import cores_meet                               # noqa: E402
import corner85 as C85                                        # noqa: E402

OUT = os.path.join(L.RESULTS, 't2_a85_zone.json')
T0S = (0.5, 1.0, 1.7347, 2.0, 5.0, 10.0, 15.0)
CORNER_GROUPS = ('S1-COR', 'S2', 'S3', 'S4', 'S5')


# ------------------------------------------------------------------ zone maths
def zone_overlap_deg(th0, th1, t0):
    """|[th0,th1] cap ((0,t0) u (90-t0,90))| in degrees."""
    a = max(0.0, min(th1, t0) - max(th0, 0.0))
    b = max(0.0, min(th1, 90.0) - max(th0, 90.0 - t0))
    return a + b


def zone_overlap_t(th0, th1, t0):
    """the same overlap measured in t = tan(theta/2)."""
    def tt(d):
        return math.tan(math.radians(d) / 2.0)
    lo, hi = tt(th0), tt(th1)
    a = max(0.0, min(hi, tt(t0)) - max(lo, 0.0))
    b = max(0.0, min(hi, tt(90.0)) - max(lo, tt(90.0 - t0)))
    return a + b


def zone_class(th0, th1, t0):
    ov = zone_overlap_deg(th0, th1, t0)
    if ov <= 0.0:
        return 'disjoint'
    return 'entirely' if ov >= (th1 - th0) - 1e-12 else 'partly'


def clip_zone(th0, th1, t0):
    """the surviving theta range after deleting Z(t0); None if it vanishes."""
    lo = max(th0, t0) if th0 < t0 else th0
    hi = min(th1, 90.0 - t0) if th1 > 90.0 - t0 else th1
    if hi - lo <= 1e-12:
        return None
    return lo, hi


# --------------------------------------------------------------------- D1
def d1():
    recs = [json.loads(ln) for ln in
            open(os.path.join(RES85, 'a85_lp_samples.jsonl')) if ln.strip()]
    plan = json.load(open(os.path.join(RES85, 'a85_lp_plan.json')))
    nodes = {}
    for r in recs:
        t = r['tag']
        d = nodes.setdefault(t, {'tag': t, 'n_records': 0})
        d['n_records'] += 1
        if r.get('group'):
            d['group'] = r['group']
            d['level'] = r.get('level')
            d['near_far'] = r.get('near_far')
            d['k'] = r.get('k')
            d['ghost'] = r.get('ghost')
            d['boxes'] = r['boxes']
            d['node'] = r.get('node')
            d['eps_geo'] = r.get('eps_geo')
        d['verdict'] = r.get('verdict', d.get('verdict'))
        d['tau'] = r.get('tau', d.get('tau'))
        d['lp_s'] = r.get('lp_s', d.get('lp_s'))
    for p in plan['plan']:
        if p['tag'] not in nodes:
            nodes[p['tag']] = {'tag': p['tag'], 'group': p['group'],
                               'level': p.get('level'), 'near_far': p.get('near_far'),
                               'k': p.get('k'), 'ghost': p.get('ghost'),
                               'boxes': None, 'verdict': 'not-run', 'n_records': 0}
    out = []
    for t in sorted(nodes):
        d = nodes[t]
        v = d.get('verdict') or 'not-run'
        st = ('PASS' if v.startswith('PASS') else
              'FAIL' if v.startswith('FAIL') else
              'refused' if v.startswith('refused') else
              'not-run' if v == 'not-run' else v)
        d['verdict_class'] = st
        d['is_blocker_node'] = d.get('group') in CORNER_GROUPS
        d['interior_note'] = ('interior: lemma not applicable'
                              if d.get('group') == 'S1-INT' else None)
        bl = []
        for k, b in enumerate(d.get('boxes') or []):
            bl.append({'k': k, 'th0': b['th0'], 'th1': b['th1'],
                       'width_deg': b['th1'] - b['th0'],
                       'x': [b['x0'], b['x1']], 'y': [b['y0'], b['y1']]})
        d['box_theta'] = bl
        d['zone'] = {}
        for t0 in T0S:
            cls = [zone_class(b['th0'], b['th1'], t0) for b in bl]
            d['zone']['%g' % t0] = {
                'per_box': cls,
                'n_partly': cls.count('partly'), 'n_entirely': cls.count('entirely'),
                'any_intersecting': bool(any(c != 'disjoint' for c in cls)),
                'all_entirely': bool(cls and all(c == 'entirely' for c in cls))}
        out.append(d)

    table = {}
    for t0 in T0S:
        key = '%g' % t0
        fails = [d for d in out if d['verdict_class'] == 'FAIL']
        bf = [d for d in fails if d['is_blocker_node']]
        infi = [d for d in fails if d.get('group') == 'S1-INT']
        hit = [d['tag'] for d in bf if d['zone'][key]['any_intersecting']]
        ent = [d['tag'] for d in bf if d['zone'][key]['n_entirely'] > 0]
        unres = [d for d in out if d['verdict_class'] in ('FAIL', 'refused', 'not-run')]
        ub = [d for d in unres if d['is_blocker_node']]
        uhit = [d['tag'] for d in ub if d['boxes'] and d['zone'][key]['any_intersecting']]
        allb = [d for d in out if d['is_blocker_node'] and d['boxes']]
        ahit = [d['tag'] for d in allb if d['zone'][key]['any_intersecting']]
        table[key] = {
            'n_unresolved_nodes_FAIL_or_refused_or_notrun': len(unres),
            'n_unresolved_blocker_nodes': len(ub),
            'unresolved_blocker_nodes_zone_intersecting': uhit,
            'all_run_blocker_nodes_zone_intersecting': ahit,
            'n_failed_nodes': len(fails),
            'n_failed_blocker_nodes': len(bf),
            'failed_blocker_nodes': [d['tag'] for d in bf],
            'n_failed_interior_nodes': len(infi),
            'failed_interior_nodes_lemma_not_applicable': [d['tag'] for d in infi],
            'failed_blocker_nodes_zone_intersecting_partly_or_entirely': hit,
            'failed_blocker_nodes_with_a_box_entirely_in_zone': ent,
            'frac_failed_blocker_nodes_touched':
                (len(hit) / len(bf)) if bf else None}
    counts = {}
    for d in out:
        k = '%s/%s' % (d.get('group'), d['verdict_class'])
        counts[k] = counts.get(k, 0) + 1
    return {'n_distinct_node_tags_with_records':
            sum(1 for d in out if d['n_records'] > 0),
            'n_planned_nodes': len(plan['plan']),
            'group_verdict_counts': counts,
            'theta0_table': table, 'nodes': out}


# --------------------------------------------------------------------- D2
def stream_pairs(path):
    """(i, j) of every surviving_level2 entry, without loading the 50 MB file."""
    pat = re.compile(r'"i":\s*(\d+),\s*"j":\s*(\d+),\s*"sense_i"')
    out = []
    tail = ''
    with open(path) as f:
        while True:
            chunk = f.read(1 << 22)
            if not chunk:
                break
            buf = tail + chunk
            last = 0
            for m in pat.finditer(buf):
                out.append((int(m.group(1)), int(m.group(2))))
                last = m.end()
            tail = buf[max(last, len(buf) - 200):]
    return out


def d2(do_e=True):
    t0w = time.time()
    R = json.load(open(os.path.join(RES85, 'a85_reach_BL.json')))
    V = R['variants']['sigma_closed_7']
    rows = [r for r in V['rows'] if r['sound']]
    boxes = [Box.from_json(r['box']) for r in rows]
    n = len(boxes)
    res = {'variant': 'sigma_closed_7', 'n_cover_boxes': V['counts']['cover'],
           'n_sound_boxes': n, 'w_widen': R['w_widen'], 'a': R['a'],
           'rect': R['rect'], 'w_box': R['w_box'], 'a_min': R['a_min'],
           't_edges': V['t_edges'],
           'theta_bins_deg': sorted(set((round(b.th0, 6), round(b.th1, 6))
                                        for b in boxes)),
           'n_theta_bins': len(set((round(b.th0, 6), round(b.th1, 6))
                                   for b in boxes))}
    res['t_parametrisation_confirmed'] = {
        'source': 'attempts/A85-k0-route/code/corner85.py',
        'T_EDGES_in_t_tan_half_theta': ['0', '1/8', '1/4', '3/8', '5/11', '3/5',
                                        '7/9', '1'],
        'deg_of_t': 'theta = 2*atan(t), theta in [0, 90)',
        'edges_deg': [C85._deg_of_t(x) for x in C85.T_EDGES],
        'cover_sigma_extra_split': 'theta bisected at the DEGREE midpoint when '
                                   'min(a(b), a(sigma b)) < a_min, so the realised '
                                   'cover has 9 theta bins',
        'sigma_closed_check': R['sigma_closed_check']['closed']}

    pairs = stream_pairs(os.path.join(RES85, 'a85_pairs_BL.json'))
    res['n_pairs_level2_streamed'] = len(pairs)
    res['n_pairs_reported_by_a85'] = None
    with open(os.path.join(RES85, 'a85_pairs_BL.json')) as f:
        head = f.read(1 << 20)
    m = re.search(r'"n_pair":\s*\{[^}]*"level2":\s*(\d+)', head, re.S)
    if m:
        res['n_pairs_reported_by_a85'] = int(m.group(1))

    per_t0 = {}
    for t0 in T0S:
        cls = [zone_class(b.th0, b.th1, t0) for b in boxes]
        touched = set(k for k, c in enumerate(cls) if c != 'disjoint')
        inside = set(k for k, c in enumerate(cls) if c == 'entirely')
        vol_deg = sum((b.x1 - b.x0) * (b.y1 - b.y0) * (b.th1 - b.th0) for b in boxes)
        del_deg = sum((b.x1 - b.x0) * (b.y1 - b.y0)
                      * zone_overlap_deg(b.th0, b.th1, t0) for b in boxes)
        vol_t = sum((b.x1 - b.x0) * (b.y1 - b.y0)
                    * (math.tan(math.radians(b.th1) / 2)
                       - math.tan(math.radians(b.th0) / 2)) for b in boxes)
        del_t = sum((b.x1 - b.x0) * (b.y1 - b.y0)
                    * zone_overlap_t(b.th0, b.th1, t0) for b in boxes)
        ext_deg = sum(b.th1 - b.th0 for b in boxes)
        extdel_deg = sum(zone_overlap_deg(b.th0, b.th1, t0) for b in boxes)
        ext_t = sum(math.tan(math.radians(b.th1) / 2)
                    - math.tan(math.radians(b.th0) / 2) for b in boxes)
        extdel_t = sum(zone_overlap_t(b.th0, b.th1, t0) for b in boxes)
        one = sum(1 for (i, j) in pairs if i in touched or j in touched)
        both = sum(1 for (i, j) in pairs if i in touched and j in touched)
        one_in = sum(1 for (i, j) in pairs if i in inside or j in inside)
        both_in = sum(1 for (i, j) in pairs if i in inside and j in inside)
        per_t0['%g' % t0] = {
            'a_boxes': {
                'n_sound': n,
                'n_zone_intersecting': len(touched),
                'frac_zone_intersecting': len(touched) / n,
                'n_entirely_inside_zone': len(inside),
                'frac_entirely_inside_zone': len(inside) / n},
            'b_tilt_volume_deleted': {
                'xytheta_volume_frac_deg': del_deg / vol_deg,
                'xytheta_volume_frac_t': del_t / vol_t,
                'tilt_extent_frac_deg_unweighted': extdel_deg / ext_deg,
                'tilt_extent_frac_t_unweighted': extdel_t / ext_t},
            'c_pairs': {
                'n_pairs': len(pairs),
                'n_at_least_one_member_zone_intersecting': one,
                'frac_at_least_one': one / len(pairs) if pairs else None,
                'n_both_members_zone_intersecting': both,
                'frac_both': both / len(pairs) if pairs else None},
            'd_pairs_entirely_inside': {
                'n_at_least_one_member_bin_entirely_in_zone': one_in,
                'frac_at_least_one': one_in / len(pairs) if pairs else None,
                'n_both_members_bin_entirely_in_zone': both_in,
                'frac_both': both_in / len(pairs) if pairs else None,
                'note': 'a bin lies ENTIRELY inside Z(theta_0) only when it is '
                        'narrower than theta_0; the realised partition has 9 bins '
                        'whose end bins are [0, 7.125017] and [82.874984, 90], so '
                        'this is empty for every theta_0 <= 7.125017'}}
    res['per_theta0'] = per_t0

    # ---- (e) refine the end bins at theta_0, drop the sub-bin inside the zone,
    #          then re-run the level-0 pair prune (P1 cores_meet / P2 maxdist<1).
    if do_e:
        ecc = {}
        for t0 in T0S:
            t1 = time.time()
            clipped = []
            nclip = 0
            for b in boxes:
                cz = clip_zone(b.th0, b.th1, t0)
                if cz is None:
                    clipped.append(None)
                    continue
                if abs(cz[0] - b.th0) > 1e-12 or abs(cz[1] - b.th1) > 1e-12:
                    nclip += 1
                    clipped.append(Box(b.x0, b.x1, b.y0, b.y1, cz[0], cz[1]))
                else:
                    clipped.append(b)
            cores = [None if b is None else b.core() for b in clipped]
            dead = kept = 0
            why = {'vacuous': 0, 'maxdist<1': 0, 'cores_meet': 0}
            for (i, j) in pairs:
                bi, bj = clipped[i], clipped[j]
                if bi is None or bj is None:
                    dead += 1
                    why['vacuous'] += 1
                    continue
                r = C85.pruned(bi, bj, cores[i], cores[j])
                if r is None:
                    kept += 1
                else:
                    dead += 1
                    why[r] += 1
            ecc['%g' % t0] = {
                'n_boxes_clipped': nclip,
                'n_boxes_emptied': sum(1 for b in clipped if b is None),
                'n_pairs_in': len(pairs),
                'n_pairs_core_contradictory_after_refine_level0': dead,
                'n_pairs_surviving_after_refine_level0': kept,
                'frac_killed': dead / len(pairs) if pairs else None,
                'reason_counts': why,
                'secs': time.time() - t1}
            print('  (e) theta0=%g clipped=%d killed=%d/%d (%.4f) %.1fs'
                  % (t0, nclip, dead, len(pairs),
                     dead / max(1, len(pairs)), time.time() - t1), flush=True)
        res['e_refined_level0_prune'] = ecc
        res['e_note'] = ('approximation as licensed by the brief: end bins clipped '
                         'to [theta_0, bin1] (mirrored at 90), then the LEVEL-0 '
                         'prune (corner85.pruned = P1 pinguard.cores_meet or '
                         'P2 max centre distance < 1) re-run on the 33 656 '
                         'level-2 survivors.  Level 0 is weaker than the level-2 '
                         'refinement that produced the survivors, so these counts '
                         'are a LOWER bound on what the refined census kills.')
    res['secs'] = time.time() - t0w
    return res


def main():
    t0 = time.time()
    print('free commit %.0f MB' % L.free_commit_mb(), flush=True)
    out = {'D1_lp_rows': d1()}
    print('D1 done', flush=True)
    out['D2_BL_census'] = d2()
    json.dump(out, open(OUT, 'w'), indent=1, default=str)
    print(json.dumps(out['D1_lp_rows']['theta0_table'], indent=1, default=str),
          flush=True)
    print(json.dumps({k: v['a_boxes'] | v['b_tilt_volume_deleted'] | v['c_pairs']
                      | {'d_' + kk: vv for kk, vv in v['d_pairs_entirely_inside'].items()
                         if kk != 'note'}
                      for k, v in out['D2_BL_census']['per_theta0'].items()},
                     indent=1, default=str), flush=True)
    print('-> %s   %.1f s' % (OUT, time.time() - t0), flush=True)


if __name__ == '__main__':
    main()
