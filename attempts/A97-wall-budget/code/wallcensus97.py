"""wallcensus97.py -- A97 T3: box-level footprint tests of Lemma WALL-F on A85's census.

For every SOUND BL reach-cover box (a85_reach_BL.json, sigma_closed_7, 644 boxes) compute a
SOUND LOWER bound phi_lb on the square's footprint (docs/proofs/wall_budget.md, Lemma WALL-F:
the interior chord on the line at distance h0 = 1/sqrt2 from the wall) on the two wall lines of
the BL corner, x = h0 (left wall) and y = h0 (bottom wall), uniformly over the box:

    y_min = cy - h(theta),  h = (cos+sin)/2   ->  y_min <= y1 - h_min(theta range)
    t     = h0 - y_min      ->  t_lb = h0 - y1 + h_min
    phi(t, tau) = 0 (t <= 0); min(2t/sin 2tau, 1/cos tau) (t > 0, tau = tilt in (0,45]); 1 (tau = 0)
    phi_lb = min(2 t_lb / sin 2 tau_max, 1/cos tau_min)   (t_lb > 0),  else 0.

Then over the 7 044 realisable pairs (realise85.pairs.json) report the fraction whose two
members' footprints on one wall line sum to > s0 - 2 = 1.877084 (dead as the crowd adjacent to
a JAM corner along that corner's NICK wall, or along the pusher wall under P-ON), and to
>= 2 (both members unit-footprint), per line and on either line; plus the JAM strata's own
footprints as a self-check (S: 1 on both lines; N: 1 on the nick line).

One process, no BLAS.  Writes attempts/A97-wall-budget/results/wallcensus97.json.
"""
from __future__ import annotations
import os, json, math
for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_v] = '1'

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
RES85 = os.path.join(ROOT, 'attempts', 'A85-k0-route', 'results')
OUT = os.path.join(HERE, '..', 'results')
S0 = 969271 / 250000
H0 = 1 / math.sqrt(2)


def tilt_range(th0, th1):
    """tilt = dist(theta, 90Z) over theta in [th0, th1] degrees."""
    pts = [th0, th1] + [k * 90.0 for k in range(-1, 3) if th0 <= k * 90.0 <= th1] \
        + [k * 90.0 + 45.0 for k in range(-1, 3) if th0 <= k * 90.0 + 45.0 <= th1]
    vals = []
    for p in pts:
        r = p % 90.0
        vals.append(min(r, 90.0 - r))
    return min(vals), max(vals)


def h_min(th0, th1):
    """min over [th0, th1] of (|cos|+|sin|)/2 -- attained at the endpoint nearest to 90Z."""
    tmin, _ = tilt_range(th0, th1)
    t = math.radians(tmin)
    return (math.cos(t) + math.sin(t)) / 2


def phi_lb(cmax, th0, th1):
    """sound lower bound on the footprint of every pose in the box with centre-coordinate
    (perpendicular to the wall) <= cmax and theta in [th0, th1]."""
    t_lb = H0 - cmax + h_min(th0, th1)
    if t_lb <= 0:
        return 0.0
    tmin, tmax = tilt_range(th0, th1)
    f2 = 1 / math.cos(math.radians(tmin))
    if tmax <= 1e-12:
        return min(1.0, f2)
    f1 = 2 * t_lb / math.sin(math.radians(2 * tmax))
    return min(f1, f2)


def main():
    R = json.load(open(os.path.join(RES85, 'a85_reach_BL.json'), encoding='utf-8'))
    rows = [r for r in R['variants']['sigma_closed_7']['rows'] if r['sound']]
    boxes = {k: r['box'] for k, r in enumerate(rows)}   # pairs index the SOUND list positionally (A89 verify_box_index)
    assert len(boxes) == 644
    P = json.load(open(os.path.join(RES85, 'realise85.pairs.json'), encoding='utf-8'))['surviving']
    C = json.load(open(os.path.join(RES85, 'cases85.json'), encoding='utf-8'))
    # per-box footprints on the two lines
    fx, fy = {}, {}
    for i, b in boxes.items():
        fx[i] = phi_lb(b['x1'], b['th0'], b['th1'])   # left wall line x = h0
        fy[i] = phi_lb(b['y1'], b['th0'], b['th1'])   # bottom wall line y = h0
    nb_unit_x = sum(1 for i in boxes if fx[i] >= 1 - 1e-12)
    nb_unit_y = sum(1 for i in boxes if fy[i] >= 1 - 1e-12)
    nb_zero_x = sum(1 for i in boxes if fx[i] == 0)
    # pair stats
    thr = S0 - 2
    n = len(P)
    cnt = dict(sum_x_gt_thr=0, sum_y_gt_thr=0, either_gt_thr=0, both_lines_gt_thr=0,
               sum_x_ge2=0, sum_y_ge2=0, either_ge2=0, any_member_unit_x=0, any_member_unit_y=0,
               sum_x_plus_y_gt=0)
    labels = {}
    try:
        with open(os.path.join(RES85, 'cases85.pairs.jsonl'), encoding='utf-8') as fh:
            for line in fh:
                r = json.loads(line)
                labels[(r['i'], r['j'])] = r.get('label', r.get('case'))
    except Exception:
        pass
    per_label = {}
    for (i, j) in P:
        sx = fx[i] + fx[j]; sy = fy[i] + fy[j]
        cnt['sum_x_gt_thr'] += sx > thr
        cnt['sum_y_gt_thr'] += sy > thr
        cnt['either_gt_thr'] += (sx > thr or sy > thr)
        cnt['both_lines_gt_thr'] += (sx > thr and sy > thr)
        cnt['sum_x_ge2'] += sx >= 2 - 1e-12
        cnt['sum_y_ge2'] += sy >= 2 - 1e-12
        cnt['either_ge2'] += (sx >= 2 - 1e-12 or sy >= 2 - 1e-12)
        cnt['any_member_unit_x'] += (fx[i] >= 1 - 1e-12 or fx[j] >= 1 - 1e-12)
        cnt['any_member_unit_y'] += (fy[i] >= 1 - 1e-12 or fy[j] >= 1 - 1e-12)
        lab = labels.get((i, j), labels.get((j, i), '?'))
        d = per_label.setdefault(lab, dict(n=0, either_gt_thr=0, either_ge2=0, min_sx=9, min_sy=9,
                                           max_sx=0, max_sy=0))
        d['n'] += 1; d['either_gt_thr'] += (sx > thr or sy > thr)
        d['either_ge2'] += (sx >= 2 - 1e-12 or sy >= 2 - 1e-12)
        d['min_sx'] = min(d['min_sx'], sx); d['min_sy'] = min(d['min_sy'], sy)
        d['max_sx'] = max(d['max_sx'], sx); d['max_sy'] = max(d['max_sy'], sy)
    out = dict(attempt='A97 wallcensus97 -- Lemma WALL-F footprint lower bounds on the A85 census',
               s0=S0, h0=H0, threshold_adjacent_to_jam=thr, n_boxes=len(boxes), n_pairs=n,
               boxes=dict(unit_footprint_left=nb_unit_x, unit_footprint_bottom=nb_unit_y,
                          zero_footprint_left=nb_zero_x),
               pairs={k: v for k, v in cnt.items()},
               pairs_frac={k: v / n for k, v in cnt.items()},
               per_label=per_label,
               note='phi_lb is a SOUND lower bound (uniform over the box) on the interior chord at '
                    'distance 1/sqrt2 from the wall; a pair with sum > s0-2 on a line cannot be the '
                    'crowd of the corner adjacent (along that line) to a JAM corner nicked on that '
                    'wall (footprint 2 + 1/cos(alpha) - 1 + sum > s0), nor, under P-ON, adjacent along '
                    'the pusher wall.  Labels from cases85.pairs.jsonl (priority partition).')
    os.makedirs(OUT, exist_ok=True)
    json.dump(out, open(os.path.join(OUT, 'wallcensus97.json'), 'w'), indent=1)
    print(json.dumps({k: out[k] for k in ('boxes', 'pairs', 'pairs_frac', 'per_label')}, indent=1))


if __name__ == '__main__':
    main()
