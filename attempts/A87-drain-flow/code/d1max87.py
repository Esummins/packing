"""d1max87.py -- A87 chore: DOES A DEEP JAM SURVIVE ANCHORING?

PI target: a lemma bounding the DEEPER intruder's depth d1 at a corner from
ABOVE.  The mechanism is Lemma JAM-0 (docs/proofs/tilt_floor_k0.md s5.1) read
backwards: an axis-aligned deeper intruder Q at offset g = max(a, b) has
depth d1 = 1 - g exactly, so

    d1 > 1 - g*   <=>   g < g*   ==>   partner N has sin(tilt N) <= g,
                                       depth(N) <= g^2 / sqrt(1 - g^2).

i.e. a very deep intruder CONFINES its partner to a g*-sliver and forces it
near-flush.  By A89-G1 / tilt_floor_k0 s5.2 such a near-flush partner is
flush-LOCKED only if it carries a presser within r <= eps of its top vertex u
PLUS a side pusher on its far edge (the K > 0 branch of the s5.2 multiplier
computation; with K = 0 the wall is unloaded and the presser must sit exactly
at t_P = r, codimension 1, or the partner is unloaded and TF-U moves it).

This module MEASURES, on the anchored corpora, whether such locked deep jams
actually occur and what they cost.

Part A -- CORNER CENSUS.  For every corner with >= 2 intruders in
  (1) attempts/A87-drain-flow/results/d2front87.json  candidates (anchored arm
      per_cap_anchored / own_side_anchored, and the raw arm for contrast),
  (2) attempts/A87-drain-flow/results/k0dir87.polish.jsonl  rows carrying an
      exact K0-BLOCKED z (k0dir87.deep.jsonl stores no configuration vector --
      only the 4 polished exact-K0-BLOCKED rows persist a z),
  (3) attempts/A87-drain-flow/results/cp87_fj_polished.jsonl  survivors
      (the 167 certified FJ points; K0-FREE overall, but their two-intruder
      corners are real anchored crowds),
  (4) Trump's exact certificate (attempts/A03-upper-reconstruct),
report: d1, d2, tilt of the deeper D and of the partner P, whether P obeys
JAM-0's bound at g = 1 - d1, whether D is retreat-blocked (A90 t3_90
analyse_square RETREATABLE, verbatim) and by which contacts, and -- for
near-flush partners (tilt < 6 deg) -- whether a presser (pair contact within
0.05 of P's top vertex u, pressing along the wall toward the corner) and a
side pusher (pair contact pushing P into the wall it hugs) exist, with the
supplying square classified as

    other_corner_intruder | pin (non-intruder touching a container wall)
                          | free_square (non-intruder, no wall contact)

ANCHORING is applied PER CORNER (the 167 FJ points are K0-FREE, so
d2front87's global ANCHORED predicate, which demands 8 intruders, cannot fire
on them):  corner_anchored := neither intruder is A90-RETREATABLE AND the
shallower has no constant-side rotation toward flush that reduces its depth
(d2front87.rot_toward_flush_free, verbatim).

Part B -- PAIR CENSUS.  For A85's realisable surviving pair boxes
(attempts/A85-k0-route/results/realise85.pairs.json, indices into the 644
sound BL cover boxes of a85_reach_BL.json/sigma_closed_7), with A89
t2b_depth's box depth bound, the fraction of pairs whose DEEPER member can
host d1 >= 0.9 and whose PARTNER box lies entirely inside JAM-0's tilt bound
arcsin(1 - 0.9) = 5.7392 deg -- i.e. how much of the census a lemma
"d1 <= 0.9 at the selected minimiser" would delete.  Both the plain depth
bound (t2b_depth part 1) and A85's WALL-AWARE depth_ub_wall are reported.

Canary: Trump's TL corner must come out anchored with d1 = 0.168321 (and
d2 = 0.155475), i.e. NOT a deep jam.

One process, OMP_NUM_THREADS=1.  Writes only results/d1max87.* and
notes/d1max87.md.
Usage: python d1max87.py [canary|A|B|all]
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import json
import math
import time
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
A87 = os.path.abspath(os.path.join(HERE, '..'))
ATT = os.path.abspath(os.path.join(A87, '..'))
A85 = os.path.join(ATT, 'A85-k0-route')
A89 = os.path.join(ATT, 'A89-tilt-floor')
A90 = os.path.join(ATT, 'A90-nocrit-blocked')
for _p in (HERE, os.path.join(A85, 'code'), os.path.join(A89, 'code'),
           os.path.join(A90, 'code')):
    sys.path.insert(0, _p)

import cp85                    # noqa: E402
import t3_90 as A             # noqa: E402  (A90's retreat/lock engine, verbatim)
import d2front87 as D2        # noqa: E402  (rot_toward_flush_free, verbatim)
import t2b_reach as TB        # noqa: E402

RESULTS = os.path.join(A87, 'results')
NOTES = os.path.join(A87, 'notes')
LOGS = os.path.join(A87, 'logs')
for _d in (RESULTS, NOTES, LOGS):
    os.makedirs(_d, exist_ok=True)

OUT_JS = os.path.join(RESULTS, 'd1max87.json')
OUT_JL = os.path.join(RESULTS, 'd1max87.jsonl')
OUT_CEN = os.path.join(RESULTS, 'd1max87.census.json')
OUT_CAN = os.path.join(RESULTS, 'd1max87.canary.json')
OUT_MD = os.path.join(NOTES, 'd1max87.md')
LOG = os.path.join(RESULTS, 'd1max87.log')   # writes stay under results/

NEAR_FLUSH_DEG = 6.0        # the brief's near-flush cut for the partner
EPS_PRESS = 0.05            # "presser within eps of the partner's top vertex"
N_DOT = 0.1                 # a force counts as pressing/pushing above this
D1_STAR = 0.9               # the census hypothesis "d1 <= 0.9"
G_STAR = 1.0 - D1_STAR      # JAM-0 offset it implies
TILT_STAR_DEG = math.degrees(math.asin(G_STAR))     # 5.7391704...

_fh = open(LOG, 'a')


def log(*a):
    m = ' '.join(str(v) for v in a)
    print(m, flush=True)
    _fh.write(m + '\n')
    _fh.flush()


def jam0_depth_bound(g):
    if g >= 1.0:
        return float('inf')
    return g * g / math.sqrt(1.0 - g * g)


def jam0_tilt_bound_deg(g):
    if g >= 1.0:
        return 90.0
    return math.degrees(math.asin(g))


# ------------------------------------------------------------------ corpora
def _z_to_cths(z):
    zz = np.array([float(Fraction(v)) if isinstance(v, str) else float(v)
                   for v in z], float)
    return A.unpack_z(zz)


def corpus_d2front():
    """d2front87.json certified candidates: anchored arm and raw arm."""
    out = []
    p = os.path.join(RESULTS, 'd2front87.json')
    if not os.path.exists(p):
        return out
    d = json.load(open(p))
    blocks = []
    for k, v in d.get('per_cap_anchored', {}).items():
        blocks.append(('anchored_cap_' + k, True, v))
    blocks.append(('anchored_own_side', True, d.get('own_side_anchored', {})))
    for k, v in d.get('per_cap', {}).items():
        blocks.append(('raw_cap_' + k, False, v))
    blocks.append(('raw_own_side', False, d.get('own_side', {})))
    seen = {}
    for lbl, anch, blk in blocks:
        for c in (blk or {}).get('candidates', []) or []:
            z = c.get('z')
            if not z:
                continue
            key = tuple(z)
            if key in seen:
                # keep the anchored provenance if any block claims it
                if anch:
                    seen[key]['arm_anchored'] = True
                    seen[key]['labels'].append(lbl)
                continue
            rec = {'source': 'd2front87', 'label': lbl, 'labels': [lbl],
                   'arm_anchored': bool(anch),
                   'sigma': c.get('sigma_certified_upper'),
                   'z': z, 'extra': {kk: c.get(kk) for kk in
                                     ('n_block_certified', 'disjoint_certified',
                                      'min_pair_gap_lower')}}
            seen[key] = rec
            out.append(rec)
    return out


def corpus_k0dir():
    out = []
    p = os.path.join(RESULTS, 'k0dir87.polish.jsonl')
    if not os.path.exists(p):
        return out
    for line in open(p):
        if not line.strip():
            continue
        r = json.loads(line)
        z = r.get('z_polished')
        if not z:
            continue
        out.append({'source': 'k0dir87.polish', 'label': r['tag'],
                    'arm_anchored': None, 'sigma': r.get('sigma_polished'),
                    'z': z,
                    'extra': {'exact_K0_BLOCKED': r.get('exact_K0_BLOCKED'),
                              'exact_n_block': r.get('exact_n_block'),
                              'genuine': r.get('genuine')}})
    return out


def corpus_fj167():
    out = []
    p = os.path.join(RESULTS, 'cp87_fj_polished.jsonl')
    for line in open(p):
        if not line.strip():
            continue
        r = json.loads(line)
        z = r.get('z_polished')
        # the CERTIFIED 167 are exactly the survivor_tight rows
        if not z or not r.get('survivor_tight'):
            continue
        out.append({'source': 'fj167', 'label': r['tag'],
                    'arm_anchored': None, 'sigma': r.get('sigma_polished'),
                    'z': z,
                    'extra': {'survivor_tight': r.get('survivor_tight'),
                              'kind': r.get('kind')}})
    return out


def corpus_trump():
    p = os.path.join(ATT, 'A03-upper-reconstruct', 'trump11_exact.json')
    d = json.load(open(p))
    s = float(d['s'])
    z = []
    for sq in d['squares']:
        z += [float(sq['cx']), float(sq['cy']), float(sq['theta'])]
    z.append(s)
    return [{'source': 'trump', 'label': 'trump11', 'arm_anchored': None,
             'sigma': s, 'z': [repr(v) for v in z],
             'extra': {'exact': True}}]


# --------------------------------------------------- presser / side pusher
def _partner_geometry(P, cn, C, TH, cst):
    """In corner cn's frame: P's deepest vertex v, the wall strip it dips into,
    and P's TOP VERTEX u (JAM-0 s5.2's u = v + (-sin a, cos a) in the left-strip
    case; the x<->y mirror in the bottom strip)."""
    fr = cst[cn]['frame']
    V = A.verts(C[P], TH[P])
    W = A.to_frame(V, fr)                    # 4 x 2, corner frame
    f = [max(p[0], p[1]) for p in W]
    kv = int(np.argmin(f))
    v = W[kv]
    strip = 'left' if v[0] < v[1] else 'bottom'
    nb = [W[(kv + 1) % 4], W[(kv + 3) % 4]]
    if strip == 'left':
        u = nb[0] if nb[0][1] > nb[1][1] else nb[1]
    else:
        u = nb[0] if nb[0][0] > nb[1][0] else nb[1]
    return fr, W, v, u, strip


def press_report(P, D, cn, C, TH, s, cst, pcs, wcs, intr_all):
    """Does the near-flush partner P carry a presser within EPS_PRESS of its top
    vertex u AND a side pusher into the wall it hugs?  s5.2's K > 0 branch."""
    fr, W, v, u, strip = _partner_geometry(P, cn, C, TH, cst)
    rows = A.contacts_on(P, pcs, wcs)
    pressers, pushers, others = [], [], []
    for r in rows:
        ptf = A.to_frame(np.asarray(r['pt'], float), fr)[0]
        nf = A.vec_to_frame(np.asarray(r['n'], float), fr)
        dist_u = float(np.hypot(ptf[0] - u[0], ptf[1] - u[1]))
        if strip == 'left':
            press_c, push_c = -float(nf[1]), -float(nf[0])
        else:
            press_c, push_c = -float(nf[0]), -float(nf[1])
        item = {'kind': r['kind'], 'other': (int(r['other'])
                                             if r['kind'] == 'pair'
                                             else r['other']),
                'type': r['type'], 'gap': float(r['gap']),
                'dist_to_top_vertex': dist_u,
                'press_component': press_c, 'push_component': push_c,
                'pt_frame': [float(ptf[0]), float(ptf[1])],
                'n_frame': [float(nf[0]), float(nf[1])]}
        if r['kind'] == 'pair':
            item['supplier'] = classify_supplier(int(r['other']), D, P, cn,
                                                 cst, wcs, TH, intr_all)
        if r['kind'] == 'pair' and dist_u <= EPS_PRESS and press_c > N_DOT:
            pressers.append(item)
        elif r['kind'] == 'pair' and push_c > N_DOT:
            pushers.append(item)
        else:
            others.append(item)
    dpress = [it['dist_to_top_vertex'] for it in pressers + pushers + others
              if it['kind'] == 'pair' and it['press_component'] > N_DOT]
    return {'strip': strip,
            'deep_vertex_frame': [float(v[0]), float(v[1])],
            'top_vertex_frame': [float(u[0]), float(u[1])],
            'n_pressing_pair_contacts': len(dpress),
            'min_dist_pressing_contact_to_top_vertex':
                (min(dpress) if dpress else None),
            'eps_press': EPS_PRESS,
            'has_presser': bool(pressers), 'has_side_pusher': bool(pushers),
            'FLUSH_LOCK_MENU': bool(pressers and pushers),
            'pressers': pressers, 'side_pushers': pushers,
            'other_rows': others, 'n_contacts': len(rows)}


def classify_supplier(q, D, P, cn, cst, wcs, TH, intr_all):
    corners_where = [c for c in A.CORNERS if q in cst[c]['intruders']]
    walls = sorted({w['wall'] for w in wcs if w['i'] == q})
    if q == D:
        role = 'partner_D_same_corner'
    elif corners_where:
        role = ('same_corner_intruder' if cn in corners_where
                else 'other_corner_intruder')
    elif walls:
        role = 'pin'
    else:
        role = 'free_square'
    return {'sq': int(q), 'role': role, 'intruder_at': corners_where,
            'walls': walls, 'tilt_deg': math.degrees(A.tilt_of(TH[q])),
            'axis_aligned': bool(A.tilt_of(TH[q]) < 1e-7)}


# ------------------------------------ sharper local test: is the dip HELD at all?
# d2front87's anchoring filter tests (i) A90 cardinal CLUSTER translations and
# (ii) a pure rotation of the shallower toward flush about one of its contacts.
# Neither covers s5.2's own escape motion, which is a rotation about the top
# vertex u COMBINED with a slide along the wall.  This probe is a superset: over
# the full 3-dof rigid motion space of the single square Q (dx, dy, dtheta), is
# there a constant-side motion that strictly reduces Q's intrusion depth at
# corner cn while the whole packing stays feasible?
LOCAL_STEPS = (3e-3, 3e-4, 3e-5)
_LOCAL_DIRS = None


def local_dirs(m=720):
    global _LOCAL_DIRS
    if _LOCAL_DIRS is None:
        rng = np.random.default_rng(20260904)
        v = rng.normal(size=(m, 3))
        v /= np.linalg.norm(v, axis=1, keepdims=True)
        ax = []
        for a in (1.0, -1.0):
            ax += [[a, 0, 0], [0, a, 0], [0, 0, a], [a, a, 0], [a, -a, 0]]
        _LOCAL_DIRS = np.vstack([np.array(ax, float)
                                 / np.linalg.norm(np.array(ax, float), axis=1,
                                                  keepdims=True), v])
    return _LOCAL_DIRS


def local_free(Q, cn, C, TH, s, cst, rot_scale=1.0):
    """3-dof single-square probe.  Returns (free, witness)."""
    fr = cst[cn]['frame']
    d0 = float(cst[cn]['depth'][Q])
    if d0 <= 0.0:
        return False, None
    for st in LOCAL_STEPS:
        for u in local_dirs():
            C2 = C.copy()
            TH2 = TH.copy()
            C2[Q] = C[Q] + st * np.array([u[0], u[1]])
            TH2[Q] = TH[Q] + st * rot_scale * u[2]
            x2 = cp85.pack(C2, TH2, s)
            ov, cv = cp85.feasibility(x2)
            if ov > -1e-12 or cv > -1e-12:
                continue
            dn = float(A.depth_arg(A.verts(C2[Q], TH2[Q]), fr)[0])
            if dn < d0 - 1e-12:
                return True, {'step': st, 'dir': [float(t) for t in u],
                              'depth_before': d0, 'depth_after': dn}
    return False, None


# ------------------------------------------------------------ corner census
def analyse_config(rec, want_rot=True):
    C, TH, s = _z_to_cths(rec['z'])
    x = cp85.pack(C, TH, s)
    bbox = A.tight_bbox_of(C, TH)
    cst = A.corner_state(C, TH, bbox)
    pcs = A.all_pair_contacts(C, TH)
    wcs = A.wall_contacts(C, TH, s)
    intr_all = {c: list(cst[c]['intruders']) for c in A.CORNERS}
    ov, cv = cp85.feasibility(x)
    try:
        glob_anch = bool(D2.anchored_report(x, want_clusters=True)['ANCHORED'])
    except Exception:                                     # noqa: BLE001
        glob_anch = None
    n_block = [int(cst[c]['n_block']) for c in A.CORNERS]
    rows = []
    for cn in A.CORNERS:
        intr = list(cst[cn]['intruders'])
        if len(intr) < 2:
            continue
        dep = np.array([float(cst[cn]['depth'][q]) for q in intr])
        order = list(np.argsort(-dep))
        Dq, Pq = intr[order[0]], intr[order[1]]
        d1, d2 = float(dep[order[0]]), float(dep[order[1]])
        aD = A.analyse_square(Dq, cn, C, TH, s, bbox, cst, pcs, wcs, True)
        aP = A.analyse_square(Pq, cn, C, TH, s, bbox, cst, pcs, wcs, True)
        tD = math.degrees(A.tilt_of(TH[Dq]))
        tP = math.degrees(A.tilt_of(TH[Pq]))
        g = max(0.0, 1.0 - d1)
        tb, db = jam0_tilt_bound_deg(g), jam0_depth_bound(g)
        rotfree, rotwit = (False, None)
        if want_rot:
            try:
                rotfree, rotwit = D2.rot_toward_flush_free(
                    x, Pq, cn, C, TH, s, cst, A.contacts_on(Pq, pcs, wcs))
            except Exception as ex:                       # noqa: BLE001
                rotfree, rotwit = False, {'error': repr(ex)[:160]}
        lfD, lwD = local_free(Dq, cn, C, TH, s, cst)
        lfP, lwP = local_free(Pq, cn, C, TH, s, cst)
        near_flush = bool(tP < NEAR_FLUSH_DEG)
        pr = (press_report(Pq, Dq, cn, C, TH, s, cst, pcs, wcs, intr_all)
              if near_flush else None)
        corner_anchored = bool((not aD.get('RETREATABLE'))
                               and (not aP.get('RETREATABLE'))
                               and (not rotfree))
        blockers = {}
        for lbl, cl in (aD.get('clusters') or {}).items():
            blockers[lbl] = {'cluster_size': cl['size'],
                             'wall_anchored': cl['wall_anchored'],
                             'wall_hits': cl['wall_hits'],
                             'intruder_anchored': cl['intruder_anchored'],
                             'intruder_hits': cl['intruder_hits'],
                             'blocking': sorted({q['other'] for q in cl['sides']
                                                 if q['blocking']},
                                                key=lambda t: str(t)),
                             'free': cl['free']}
        # external squares consumed by this corner's lock
        ext = set()
        if pr:
            for it in pr['pressers'] + pr['side_pushers']:
                if isinstance(it['other'], int) and it['other'] not in (Dq, Pq):
                    ext.add(int(it['other']))
        ext_retreat = set()
        for lbl in aD.get('cardinals', []):
            cl = (aD.get('clusters') or {}).get(lbl)
            if not cl:
                continue
            for q in cl['sides']:
                if q['blocking'] and isinstance(q['other'], int) \
                        and q['other'] not in (Dq, Pq):
                    ext_retreat.add(int(q['other']))
        rows.append({
            'source': rec['source'], 'label': rec['label'],
            'arm_anchored': rec.get('arm_anchored'),
            'config_ANCHORED_d2front': glob_anch, 'n_block': n_block,
            'sigma': float(s), 'corner': cn,
            'n_intruders': len(intr), 'intruders': [int(q) for q in intr],
            'deeper': int(Dq), 'partner': int(Pq),
            'd1': d1, 'd2': d2,
            'tilt_deeper_deg': tD, 'tilt_partner_deg': tP,
            'deeper_axis_aligned': bool(tD < 1e-7),
            'jam0_g': g, 'jam0_tilt_bound_deg': tb, 'jam0_depth_bound': db,
            'partner_within_jam0_tilt': bool(tP <= tb + 1e-12),
            'partner_within_jam0_depth': bool(d2 <= db + 1e-12),
            'partner_within_jam0': bool(tP <= tb + 1e-12 and d2 <= db + 1e-12),
            'jam0_hypothesis_literal': bool(tD < 1e-7),
            'deeper_RETREATABLE': bool(aD.get('RETREATABLE')),
            'partner_RETREATABLE': bool(aP.get('RETREATABLE')),
            'deeper_LOCKED': bool(aD.get('LOCKED')),
            'partner_LOCKED': bool(aP.get('LOCKED')),
            'deeper_cardinals': aD.get('cardinals'),
            'deeper_n_contacts': aD.get('n_contacts'),
            'partner_n_contacts': aP.get('n_contacts'),
            'partner_rot_to_flush_free': bool(rotfree),
            'partner_rot_witness': rotwit,
            'deeper_local3dof_free': bool(lfD), 'deeper_local3dof_wit': lwD,
            'partner_local3dof_free': bool(lfP), 'partner_local3dof_wit': lwP,
            'corner_anchored': corner_anchored,
            'corner_anchored_strict': bool(corner_anchored and not lfD
                                           and not lfP),
            'near_flush_partner': near_flush,
            'deeper_blocking_contacts': blockers,
            'press': pr,
            'external_squares_press': sorted(ext),
            'external_squares_retreat_block': sorted(ext_retreat),
            'n_external_squares': len(ext | ext_retreat),
            'external_squares': sorted(ext | ext_retreat),
            'feas_overlap': ov, 'feas_container': cv,
        })
    return rows


# ------------------------------------------------------------------ canary
def canary():
    rec = corpus_trump()[0]
    rows = analyse_config(rec)
    tl = [r for r in rows if r['corner'] == 'TL']
    out = {'trump_corners_with_2plus_intruders':
           [{k: r[k] for k in ('corner', 'intruders', 'deeper', 'partner',
                               'd1', 'd2', 'tilt_deeper_deg',
                               'tilt_partner_deg', 'corner_anchored',
                               'deeper_RETREATABLE', 'partner_RETREATABLE',
                               'partner_within_jam0')} for r in rows],
           'expected_TL': {'d1': 0.168321, 'd2': 0.155475}}
    ok = False
    if tl:
        r = tl[0]
        ok = (abs(r['d1'] - 0.168321) < 2e-5 and abs(r['d2'] - 0.155475) < 2e-5)
        out['TL'] = {'d1': r['d1'], 'd2': r['d2'],
                     'squares': [r['deeper'], r['partner']],
                     'corner_anchored': r['corner_anchored'],
                     'deep_jam': bool(r['d1'] > 1.0 - G_STAR)}
    out['CANARY_OK'] = bool(ok and tl and not (tl[0]['d1'] > 1.0 - G_STAR))
    json.dump(out, open(OUT_CAN, 'w'), indent=1, default=str)
    log('CANARY', json.dumps(out.get('TL'), default=str), 'OK', out['CANARY_OK'])
    return out


# ---------------------------------------------------------------- part A run
def part_A():
    t0 = time.time()
    recs = (corpus_d2front() + corpus_k0dir() + corpus_fj167() + corpus_trump())
    log('part A: %d configurations' % len(recs))
    allrows = []
    nerr = 0
    with open(OUT_JL, 'w') as fo:
        for k, rec in enumerate(recs):
            try:
                rows = analyse_config(rec)
            except Exception as ex:                       # noqa: BLE001
                nerr += 1
                log('  ERROR %s %s: %r' % (rec['source'], rec['label'], ex))
                continue
            for r in rows:
                fo.write(json.dumps(r, default=str) + '\n')
            allrows += rows
            if (k + 1) % 25 == 0:
                log('  %d/%d configs, %d corner rows, %.0fs'
                    % (k + 1, len(recs), len(allrows), time.time() - t0))
    log('part A: %d corner rows (>=2 intruders), %d config errors, %.0fs'
        % (len(allrows), nerr, time.time() - t0))
    return allrows, recs, nerr


D1_BINS = [(0.0, 0.1), (0.1, 0.2), (0.2, 0.3), (0.3, 0.5), (0.5, 0.7),
           (0.7, 0.9), (0.9, 0.99), (0.99, 1.01)]
T_BINS = [(0.0, 1e-7), (1e-7, 0.1), (0.1, 1.0), (1.0, 6.0), (6.0, 15.0),
          (15.0, 45.1)]


def joint(rows):
    tab = {}
    for a, b in D1_BINS:
        for c, d in T_BINS:
            tab['d1[%g,%g) x tilt[%g,%g)' % (a, b, c, d)] = 0
    for r in rows:
        for a, b in D1_BINS:
            if a <= r['d1'] < b:
                for c, d in T_BINS:
                    if c <= r['tilt_partner_deg'] < d:
                        tab['d1[%g,%g) x tilt[%g,%g)' % (a, b, c, d)] += 1
                        break
                break
    return {k: v for k, v in tab.items() if v}


def summarise_A(rows):
    anch = [r for r in rows if r['corner_anchored']]
    qual = [r for r in anch
            if (not r['deeper_RETREATABLE']) and r['near_flush_partner']]
    locked = [r for r in qual if r['press'] and r['press']['FLUSH_LOCK_MENU']]
    by_cfg = {}
    for r in qual:
        by_cfg.setdefault((r['source'], r['label']), []).append(r)
    by_cfg_locked = {}
    for r in locked:
        by_cfg_locked.setdefault((r['source'], r['label']), []).append(r)
    qs = [r for r in qual if r['corner_anchored_strict']]
    out = {
        'n_corner_rows': len(rows),
        'STRICT_3dof': {
            'n_corner_anchored_strict': sum(1 for r in rows
                                            if r['corner_anchored_strict']),
            'n_qualifying_strict': len(qs),
            'max_d1_qualifying_strict': max((r['d1'] for r in qs), default=None),
            'n_deeper_local3dof_free_among_qualifying':
                sum(1 for r in qual if r['deeper_local3dof_free']),
            'n_partner_local3dof_free_among_qualifying':
                sum(1 for r in qual if r['partner_local3dof_free']),
            'rows': [{k: r[k] for k in ('source', 'label', 'corner', 'sigma',
                                        'd1', 'd2', 'tilt_partner_deg',
                                        'deeper_local3dof_free',
                                        'partner_local3dof_free')}
                     for r in sorted(qual, key=lambda r: -r['d1'])]},
        'n_by_source': {s: sum(1 for r in rows if r['source'] == s)
                        for s in sorted({r['source'] for r in rows})},
        'n_corner_anchored': len(anch),
        'n_anchored_by_source': {s: sum(1 for r in anch if r['source'] == s)
                                 for s in sorted({r['source'] for r in anch})},
        'joint_d1_x_partner_tilt_ANCHORED': joint(anch),
        'joint_d1_x_partner_tilt_ALL': joint(rows),
        'max_d1_all_rows': max((r['d1'] for r in rows), default=None),
        'max_d1_anchored': max((r['d1'] for r in anch), default=None),
        'max_d1_anchored_retreatblocked_nearflush':
            max((r['d1'] for r in qual), default=None),
        'n_qualifying_corners': len(qual),
        'n_qualifying_configs': len(by_cfg),
        'n_configs_with_TWO_qualifying_corners':
            sum(1 for v in by_cfg.values() if len(v) >= 2),
        'configs_with_TWO_qualifying_corners':
            ['%s/%s (%d corners)' % (a, b, len(v))
             for (a, b), v in by_cfg.items() if len(v) >= 2],
        'sigma_of_qualifying_corners': sorted(round(r['sigma'], 6)
                                              for r in qual),
        'min_sigma_qualifying': min((r['sigma'] for r in qual), default=None),
        'n_qualifying_at_sigma_le_shat': sum(1 for r in qual
                                             if r['sigma'] <= 3.877084),
        'n_qualifying_deep_d1_gt_0.9': sum(1 for r in qual if r['d1'] > 0.9),
        'min_sigma_qualifying_deep_d1_gt_0.9':
            min((r['sigma'] for r in qual if r['d1'] > 0.9), default=None),
        'n_configs_globally_ANCHORED': None,
        'n_flush_lock_menu_corners': len(locked),
        'n_configs_with_TWO_flush_lock_menu_corners':
            sum(1 for v in by_cfg_locked.values() if len(v) >= 2),
        'max_d1_flush_lock_menu': max((r['d1'] for r in locked), default=None),
        'external_squares_consumed': {
            'per_qualifying_corner': sorted(r['n_external_squares']
                                            for r in qual),
            'mean': (sum(r['n_external_squares'] for r in qual) / len(qual))
            if qual else None,
            'max': max((r['n_external_squares'] for r in qual), default=None),
        },
        'jam0': {
            'n_partner_within_jam0_tilt': sum(1 for r in rows
                                              if r['partner_within_jam0_tilt']),
            'n_partner_within_jam0_depth': sum(1 for r in rows
                                               if r['partner_within_jam0_depth']),
            'n_rows_deeper_axis_aligned': sum(1 for r in rows
                                              if r['deeper_axis_aligned']),
            'n_axis_aligned_deeper_violating_jam0':
                sum(1 for r in rows if r['deeper_axis_aligned']
                    and not r['partner_within_jam0']),
        },
        'top_anchored_by_d1': [
            {k: r[k] for k in ('source', 'label', 'corner', 'sigma', 'd1', 'd2',
                               'tilt_deeper_deg', 'tilt_partner_deg',
                               'deeper_RETREATABLE', 'partner_RETREATABLE',
                               'near_flush_partner', 'n_external_squares',
                               'external_squares', 'config_ANCHORED_d2front')}
            for r in sorted(anch, key=lambda r: -r['d1'])[:15]],
        'qualifying_rows': [
            {k: r[k] for k in ('source', 'label', 'corner', 'sigma', 'd1', 'd2',
                               'tilt_deeper_deg', 'tilt_partner_deg',
                               'deeper_axis_aligned', 'partner_within_jam0',
                               'n_external_squares', 'external_squares',
                               'config_ANCHORED_d2front')}
            | {'has_presser': (r['press'] or {}).get('has_presser'),
               'has_side_pusher': (r['press'] or {}).get('has_side_pusher'),
               'FLUSH_LOCK_MENU': (r['press'] or {}).get('FLUSH_LOCK_MENU'),
               'n_pressing_pair_contacts':
                   (r['press'] or {}).get('n_pressing_pair_contacts'),
               'min_dist_presser_to_top_vertex':
                   (r['press'] or {}).get(
                       'min_dist_pressing_contact_to_top_vertex'),
               'supplier_roles': sorted({
                   it['supplier']['role']
                   for it in ((r['press'] or {}).get('pressers', []) +
                              (r['press'] or {}).get('side_pushers', []))
                   if it.get('supplier')})}
            for r in sorted(qual, key=lambda r: -r['d1'])[:40]],
    }
    return out


# ---------------------------------------------------------------- part B
def part_B():
    t0 = time.time()
    R, V, brows, boxes = TB.load_boxes()
    pairs = json.load(open(os.path.join(A85, 'results',
                                        'realise85.pairs.json')))['surviving']
    bx = json.load(open(os.path.join(A85, 'results', 'realise85.boxes.json')))
    duw = bx['depth_ub_wall']
    n = len(boxes)
    log('part B: %d sound boxes, %d realisable surviving pairs' % (n, len(pairs)))

    # (i) plain depth upper bound (A89 t2b_depth part 1, recomputed here)
    dub = np.zeros(n)
    dlb = np.zeros(n)
    NTH = 2001
    LIP = math.sqrt(2.0) / 2.0
    for k, b in enumerate(boxes):
        th = np.linspace(math.radians(b.th0), math.radians(b.th1), NTH)
        sl = LIP * (th[1] - th[0]) / 2.0 if NTH > 1 else 0.0
        f0 = TB.f_minmax_np(TB.verts_np(np.full(NTH, b.x0),
                                        np.full(NTH, b.y0), th))
        f1 = TB.f_minmax_np(TB.verts_np(np.full(NTH, b.x1),
                                        np.full(NTH, b.y1), th))
        dub[k] = 1.0 - (float(f0.min()) - sl)
        dlb[k] = 1.0 - (float(f1.max()) + sl)

    # (ii) does the WHOLE theta range of a box lie inside JAM-0's tilt bound?
    def tilt_range_deg(b):
        lo, hi = b.th0, b.th1
        ts = np.linspace(lo, hi, 4001)
        tl = np.array([math.degrees(A.tilt_of(math.radians(t))) for t in ts])
        return float(tl.min()), float(tl.max())

    trange = [tilt_range_deg(b) for b in boxes]
    inside = np.array([trange[k][1] <= TILT_STAR_DEG for k in range(n)])
    meets = np.array([trange[k][0] <= TILT_STAR_DEG for k in range(n)])
    dubw = np.array([(duw[k] if duw[k] is not None else -1e9) for k in range(n)])

    # what fraction of each box's theta cell survives JAM-0's tilt clause?
    def band_frac(b):
        ts = np.linspace(b.th0, b.th1, 20001)
        tl = np.array([math.degrees(A.tilt_of(math.radians(t))) for t in ts])
        return float((tl <= TILT_STAR_DEG).mean())

    bfrac = np.array([band_frac(b) for b in boxes])

    def census(deep_ub, name):
        deep = deep_ub >= D1_STAR
        nd = int(deep.sum())
        hit = 0
        hit_depth = 0
        for i, j in pairs:
            a = (deep[i] and inside[j])
            b_ = (deep[j] and inside[i])
            if a or b_:
                hit += 1
            # additionally require the partner box to obey JAM-0's DEPTH bound
            db = jam0_depth_bound(G_STAR)
            a2 = (deep[i] and inside[j] and deep_ub[j] <= db)
            b2 = (deep[j] and inside[i] and deep_ub[i] <= db)
            if a2 or b2:
                hit_depth += 1
        # refinements: a pair with a deep-capable member at all; JAM-0's own
        # kills (partner cell disjoint from the band, or partner FORCED deeper
        # than the sliver); and the theta-measure a d1<=0.9 lemma would shave.
        db = jam0_depth_bound(G_STAR)
        n_deepmember = 0
        n_jam0_tilt_kill = 0
        n_jam0_depth_kill = 0
        shave = 0.0
        for i, j in pairs:
            live = []
            if deep[i]:
                live.append((i, j))
            if deep[j]:
                live.append((j, i))
            if not live:
                continue
            n_deepmember += 1
            if all(not meets[q] for _p, q in live):
                n_jam0_tilt_kill += 1
            if all(dlb[q] > db for _p, q in live):
                n_jam0_depth_kill += 1
            shave += max(0.0, 1.0 - max(bfrac[q] for _p, q in live))
        return {'bound': name, 'n_boxes_can_host_d1_ge_0.9': nd,
                'frac_boxes': nd / n,
                'n_pairs': len(pairs),
                'n_pairs_with_a_deep_capable_member': n_deepmember,
                'frac_pairs_with_a_deep_capable_member':
                    n_deepmember / len(pairs) if pairs else 0.0,
                'n_pairs_deep_member_and_partner_box_inside_jam0_tilt': hit,
                'frac_pairs': hit / len(pairs) if pairs else 0.0,
                'n_pairs_also_partner_box_inside_jam0_depth': hit_depth,
                'frac_pairs_depth': hit_depth / len(pairs) if pairs else 0.0,
                'n_pairs_killed_by_jam0_tilt_clause_alone': n_jam0_tilt_kill,
                'n_pairs_killed_by_jam0_depth_clause_alone': n_jam0_depth_kill,
                'theta_measure_shaved_from_partner_cells_pair_equivalents':
                    shave,
                'frac_of_census_shaved': shave / len(pairs) if pairs else 0.0}

    out = {'n_sound_boxes': n, 'n_realisable_surviving_pairs': len(pairs),
           'D1_STAR': D1_STAR, 'G_STAR': G_STAR,
           'jam0_tilt_bound_deg': TILT_STAR_DEG,
           'jam0_depth_bound': jam0_depth_bound(G_STAR),
           'n_boxes_theta_range_entirely_within_jam0_tilt': int(inside.sum()),
           'n_boxes_theta_range_meeting_jam0_tilt_band': int(meets.sum()),
           'theta_cells': sorted({(round(b.th0, 4), round(b.th1, 4))
                                  for b in boxes}),
           'finest_theta_cell_width_deg': min(b.th1 - b.th0 for b in boxes),
           'note_granularity':
               'the cover s finest theta cell is 7.125 deg wide, WIDER than '
               'JAM-0 s bound arcsin(0.1) = 5.7392 deg, so NO cell can lie '
               'entirely inside the band: the "entirely within" count is 0 by '
               'cell granularity, not by geometry.  One bisection of the two '
               'extreme cells [0,7.125] and [82.875,90] would make the clause '
               'able to bite.',
           'depth_ub_plain': {'max': float(dub.max()), 'n_ge_0.9':
                              int((dub >= D1_STAR).sum())},
           'depth_lb_plain': {'max': float(dlb.max()), 'n_ge_0.9':
                              int((dlb >= D1_STAR).sum())},
           'depth_ub_wall_A85': {'max': float(dubw.max()),
                                 'n_ge_0.9': int((dubw >= D1_STAR).sum()),
                                 'n_None': sum(1 for v in duw if v is None)},
           'census_plain_ub': census(dub, 't2b_depth plain depth_ub'),
           'census_wall_ub': census(dubw, 'A85 realise85 depth_ub_wall'),
           'census_forced_lb': census(dlb, 'depth_LB (box FORCED to d1>=0.9)'),
           'secs': time.time() - t0}
    json.dump(out, open(OUT_CEN, 'w'), indent=1, default=str)
    log('part B done %.0fs' % (time.time() - t0))
    return out


# ------------------------------------------------------------------- main
def main(argv):
    what = argv[1] if len(argv) > 1 else 'all'
    t0 = time.time()
    res = {'attempt': 'A87 chore d1max87: deep jams in ANCHORED configurations',
           'near_flush_deg': NEAR_FLUSH_DEG, 'eps_press': EPS_PRESS,
           'n_dot_threshold': N_DOT, 'D1_STAR': D1_STAR,
           'jam0_tilt_bound_at_g_star_deg': TILT_STAR_DEG,
           'jam0_depth_bound_at_g_star': jam0_depth_bound(G_STAR)}
    if what in ('canary', 'all', 'A'):
        res['canary'] = canary()
    if what in ('A', 'all'):
        rows, recs, nerr = part_A()
        res['part_A'] = summarise_A(rows)
        cfgs = {}
        for r in rows:
            cfgs[(r['source'], r['label'])] = r['config_ANCHORED_d2front']
        res['part_A']['n_configs_globally_ANCHORED'] = sum(
            1 for v in cfgs.values() if v)
        res['part_A']['globally_ANCHORED_configs'] = [
            '%s/%s' % k for k, v in cfgs.items() if v]
        res['part_A']['n_configs'] = len(recs)
        res['part_A']['n_config_errors'] = nerr
        res['part_A']['n_configs_by_source'] = {
            s: sum(1 for r in recs if r['source'] == s)
            for s in sorted({r['source'] for r in recs})}
    if what in ('B', 'all'):
        res['part_B'] = part_B()
    res['secs'] = time.time() - t0
    json.dump(res, open(OUT_JS, 'w'), indent=1, default=str)
    log(json.dumps(res, indent=1, default=str)[:8000])
    return res


if __name__ == '__main__':
    main(sys.argv)
