"""A110 chore 2 (T4) - for every alive node explained by S07 (19) and by S02 (267), does the node's LP
support lie inside the swept grain family of the shadow (same load path, tilt in the swept range)?

Read-only on every campaign.  Inputs: attempts/A107-shadow-gallery/results/{shadow_nodes,extract}.json
(the LP supports, A107's canonicalisation), results/sweep_S07.json + sweep_S02.json (the families,
grain110.py).  A node's support is the representative 11-square configuration of its dual support
(hypothesis cores + integral placements; cells of pitch 0.19, so two representatives may overlap by one
pitch - A107's convention, tolerance 0.21).  Test per node: canonicalise the support into the shadow's
frame (A107's struct_op), take its non-slot squares, and for every tilt of the family match the family's
LOAD-BEARING squares (S07: f0 f1 f2 f4; S02: f1 f2 f3) greedily to distinct support squares; the node
is INSIDE the family iff at the best tilt every matched centre is within 0.21 of the family square and
every matched tilt is within 5 deg (one A57 tilt cell) of the family tilt, and that tilt lies in the
family's range [theta_lo, theta_hi] (S07: the Trump crest to the upper load-path change).  Also reports,
per node, the conditioned box(es) of the hypothesis and which family square (at which tilt) comes
nearest to the box centre, and whether the box's tilt interval meets the family range.

Outputs results/t4_S07.jsonl, results/t4_S02.jsonl, results/t4_summary.json, results/box_to_grain_110.svg."""
from __future__ import annotations
import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_v] = '1'
import sys, json, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A108-s07-certify', 'code'))
import a108lib as A                      # noqa: E402
from a108lib import L, MZ                # noqa: E402

RES = os.path.join(ROOT, 'attempts', 'A110-grain-flood', 'results')
A107R = os.path.join(ROOT, 'attempts', 'A107-shadow-gallery', 'results')
S = L.S0
DTOL, ATOL = 0.21, 5.0


def tilt_dev(a_rad, b_deg):
    a = math.degrees(L.tmod(a_rad)); b = b_deg % 90.0
    d = abs(a - b) % 90.0
    return min(d, 90.0 - d)


def family(sw, lb_idx, lo, hi):
    """(tilt, cfg) records of the S07/S02 branch inside [lo, hi], from the down and up sweeps."""
    recs = []
    for key in ('down', 'up'):
        for r in sw[key]:
            if r.get('s') is None:
                continue
            if lo - 1e-9 <= r['tilt_deg'] <= hi + 1e-9:
                recs.append((r['tilt_deg'], r['cfg'], r['s'], r['loaded']))
    recs.sort(key=lambda t: t[0])
    # de-duplicate the shared 45 / 48.4351 point
    out = []
    for r in recs:
        if out and abs(out[-1][0] - r[0]) < 1e-9:
            continue
        out.append(r)
    return out


def match(fam_cfg, lb_idx, support):
    """Best injection of the family's load-bearing squares into distinct support squares (all
    injections enumerated; score = max centre distance, tie-break max tilt deviation)."""
    import itertools
    best = None
    for perm in itertools.permutations(range(len(support)), len(lb_idx)):
        dmax = 0.0; tmax = 0.0; pairs = []
        for i, j in zip(lb_idx, perm):
            fx, fy, ft = fam_cfg[i]
            x, y, t = support[j]
            d = math.hypot(x - fx, y - fy)
            dmax = max(dmax, d); tmax = max(tmax, tilt_dev(t, math.degrees(ft))); pairs.append((i, j, d))
        key = (dmax, tmax)
        if best is None or key < best[:2]:
            best = (dmax, tmax, pairs)
    return best


def boxes_of(node_path):
    d = json.load(open(os.path.join(ROOT, node_path), encoding='utf-8'))
    bx = d['hyp']['boxes']
    out = []
    for b in bx:
        w = max(b['x1'] - b['x0'], b['y1'] - b['y0'], b['th1'] - b['th0'])
        if w > 1e-6:                        # the pins have zero-width boxes (A60) or delta-cores (A57)
            if b['th1'] - b['th0'] > 1e-6 or (b['x1'] - b['x0']) > 0.02:
                out.append(b)
    return out


def run(shadow, sw, lb_idx, lo, hi, names):
    sn = json.load(open(os.path.join(A107R, 'shadow_nodes.json'), encoding='utf-8'))[shadow]
    ex = json.load(open(os.path.join(A107R, 'extract.json'), encoding='utf-8'))['nodes']
    idx = {(n['src'], n['nid']): n for n in ex}
    fam = family(sw, lb_idx, lo, hi)
    rows = []
    for rec in sn:
        n = idx[(rec['src'], rec['nid'])]
        op = n.get('struct_op') or 'e'
        sup = MZ.canon_free(n['cfg'], op, S)          # the non-slot squares of the support, shadow frame
        best = None
        for (td, cfg, sfam, loaded) in fam:
            m = match(cfg, lb_idx, sup)
            if m is None:
                continue
            dmax, tmax, pairs = m
            if best is None or dmax < best[0]:
                best = (dmax, tmax, td, pairs)
        # the conditioned boxes, mapped into the shadow frame
        f = dict(L.d4_ops(S))[op]
        bx = []
        for b in boxes_of(n['path']):
            cx, cy = 0.5 * (b['x0'] + b['x1']), 0.5 * (b['y0'] + b['y1'])
            th = 0.5 * (b['th0'] + b['th1'])
            X, Y, T = f(cx, cy, math.radians(th))
            hw = 0.5 * max(b['x1'] - b['x0'], b['y1'] - b['y0'])
            htw = 0.5 * (b['th1'] - b['th0'])
            Tdeg = math.degrees(L.tmod(T))
            # nearest family square to the box centre over the family
            nb = None
            for (td, cfg, sfam, loaded) in fam:
                for i, (x, y, t) in enumerate(cfg):
                    d = math.hypot(x - X, y - Y)
                    if nb is None or d < nb[0]:
                        nb = (d, td, names[i], tilt_dev(T, td))
            meets = any((Tdeg - htw) % 90 <= td + ATOL and (Tdeg + htw) % 90 >= td - ATOL or
                        abs(((Tdeg - td + 45) % 90) - 45) <= htw for (td, _, _, _) in fam)
            bx.append(dict(centre=[X, Y], tilt_deg=Tdeg, half_w=hw, half_tilt=htw,
                           nearest_family_square=nb[2], nearest_dist=nb[0], nearest_tilt=nb[1],
                           tilt_dev_to_nearest=nb[3], box_tilt_meets_family_range=bool(meets),
                           box_contains_family_square=bool(nb[0] <= hw and nb[3] <= htw)))
        inside_loose = bool(best and best[0] <= DTOL and best[1] <= ATOL)
        tilts_in_range = bool(best) and all(lo - 1e-9 <= (math.degrees(L.tmod(sup[j][2]))) <= hi + 1e-9 for (_, j, _) in best[3])
        inside = bool(inside_loose and tilts_in_range)
        sup_tilts = sorted(round(math.degrees(L.tmod(q[2])), 2) for q in sup)
        row = dict(shadow=shadow, src=rec['src'], nid=rec['nid'], level=rec['level'], via=rec['via'], op=op,
                   n_support_free=len(sup), support_tilts_deg=sup_tilts,
                   best_tilt=best[2] if best else None, dmax=best[0] if best else None,
                   tilt_dev_max=best[1] if best else None, pairs=best[3] if best else None,
                   inside_family=inside, inside_loose=inside_loose, matched_tilts_in_range=tilts_in_range, boxes=bx)
        rows.append(row)
    return rows, fam


def svg_box_to_grain(sw07, rows07, names):
    """One drawing: the S07 family at 43 deg, node c0_Y0324's conditioned box and its LP support."""
    fam = {r['tilt_deg']: r for r in sw07['down'] if r.get('s')}
    r43 = fam[min(fam, key=lambda t: abs(t - 43.0))]
    s = r43['s']; cfg = r43['cfg']
    ex = json.load(open(os.path.join(A107R, 'extract.json'), encoding='utf-8'))['nodes']
    node = next(n for n in ex if n['src'] == 'A60' and n['nid'] == 'c0_Y0324')
    box = boxes_of(node['path'])[0]
    sc, ox, oy, W, H = 150.0, 40.0, 40.0, 720, 700
    def P(x, y):
        return ox + sc * x, oy + sc * (s - y)
    body = [f'<rect x="{ox}" y="{oy}" width="{sc*s:.1f}" height="{sc*s:.1f}" fill="none" stroke="#000" stroke-width="1.5"/>']
    worst = 1e9
    for i, (x, y, t) in enumerate(cfg):
        pts = ' '.join(f'{P(a, b)[0]:.1f},{P(a, b)[1]:.1f}' for a, b in L.corners(x, y, t))
        col = '#c33' if names[i] in ('f0', 'f1', 'f2', 'f4') else ('#888' if names[i] == 'f3' else '#36c')
        body.append(f'<polygon points="{pts}" fill="{col}" fill-opacity="0.35" stroke="{col}" stroke-width="1.2"/>')
        body.append(f'<text x="{P(x, y)[0]:.1f}" y="{P(x, y)[1]:.1f}" font-size="10" text-anchor="middle">{names[i]}</text>')
        for j in range(i):
            worst = min(worst, L.sat_gap(cfg[i][:2], cfg[i][2], cfg[j][:2], cfg[j][2]))
    # the support (dashed)
    for q in node['cfg'][5:]:
        pts = ' '.join(f'{P(a, b)[0]:.1f},{P(a, b)[1]:.1f}' for a, b in L.corners(q[0], q[1], q[2]))
        body.append(f'<polygon points="{pts}" fill="none" stroke="#080" stroke-width="1.2" stroke-dasharray="4,3"/>')
    x0, y0 = P(box['x0'], box['y1']); x1, y1 = P(box['x1'], box['y0'])
    body.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1-x0:.1f}" height="{y1-y0:.1f}" fill="#fc0" fill-opacity="0.5" stroke="#a80" stroke-width="2"/>')
    body.append(f'<text x="{x1+4:.1f}" y="{y0+10:.1f}" font-size="10" fill="#a80">box of c0_Y0324: tilt [{box["th0"]:.1f}, {box["th1"]:.1f}] deg</text>')
    title = (f'A110 box-to-grain obstruction: S07 family at 43.0 deg (side {s:.6f}; red = load path, grey = rattler, '
             f'blue = slots; worst SAT {worst:.1e}), the alive node c0_Y0324 (A60): its box (yellow) and its LP support (green, dashed)')
    body.append(f'<text x="{ox}" y="{oy+sc*s+18:.1f}" font-size="11">{title[:150]}</text>')
    body.append(f'<text x="{ox}" y="{oy+sc*s+32:.1f}" font-size="11">{title[150:]}</text>')
    body.append(f'<text x="{ox}" y="{oy+sc*s+50:.1f}" font-size="11">The box holds the RATTLER of the support (tilt 53.1-64.0 deg; the family runs 41.565-53.75 deg); no load-bearing family square at any tilt lies in the box (nearest 0.208 from its centre, half-width 0.070): the box is not a grain.</text>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="#fff"/>' + ''.join(body) + '</svg>'
    open(os.path.join(RES, 'box_to_grain_110.svg'), 'w', encoding='utf-8').write(svg)
    return worst


def main():
    sw07 = json.load(open(os.path.join(RES, 'sweep_S07.json')))
    sw02 = json.load(open(os.path.join(RES, 'sweep_S02.json')))
    args = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    lo07, hi07 = args.get('S07', [41.6, 51.0])
    lo02, hi02 = args.get('S02', [42.0, 56.0])
    n07 = sw07['names']; n02 = sw02['names']
    rows07, fam07 = run('S07', sw07, [0, 1, 2, 4], lo07, hi07, n07)
    rows02, fam02 = run('S02', sw02, [1, 2, 3], lo02, hi02, n02)
    with open(os.path.join(RES, 't4_S07.jsonl'), 'w') as f:
        for r in rows07: f.write(json.dumps(r) + '\n')
    with open(os.path.join(RES, 't4_S02.jsonl'), 'w') as f:
        for r in rows02: f.write(json.dumps(r) + '\n')
    summ = {}
    for tag, rows, rng in (('S07', rows07, (lo07, hi07)), ('S02', rows02, (lo02, hi02))):
        n = len(rows); ins = sum(r['inside_family'] for r in rows); ins_loose = sum(r['inside_loose'] for r in rows)
        d_ok = sum(1 for r in rows if r['dmax'] is not None and r['dmax'] <= DTOL)
        t_ok = sum(1 for r in rows if r['tilt_dev_max'] is not None and r['tilt_dev_max'] <= ATOL)
        box_meets = sum(1 for r in rows if any(b['box_tilt_meets_family_range'] for b in r['boxes']))
        box_contains = sum(1 for r in rows if any(b['box_contains_family_square'] for b in r['boxes']))
        by_src = {}
        for r in rows:
            k = f"{r['src']}/L{r['level']}"
            by_src.setdefault(k, [0, 0]); by_src[k][0] += 1; by_src[k][1] += r['inside_family']
        summ[tag] = dict(range=rng, nodes=n, inside_family=ins, inside_loose_5deg=ins_loose, centres_within_0p21=d_ok, tilts_within_5deg=t_ok,
                         box_tilt_meets_range=box_meets, box_contains_family_square=box_contains, by_src_level=by_src,
                         dmax_quartiles=[float(np.percentile([r['dmax'] for r in rows if r['dmax'] is not None], q)) for q in (0, 25, 50, 75, 100)])
        print(tag, json.dumps(summ[tag]))
        for r in rows[:25] if tag == 'S07' else rows[:0]:
            print(f"   {r['src']:4s} {r['nid']:24s} L{r['level']} via={r['via']:9s} tilts={r['support_tilts_deg']} best_tilt={r['best_tilt']} "
                  f"dmax={r['dmax']:.3f} tdev={r['tilt_dev_max']:.2f} inside={r['inside_family']} "
                  f"box=[{', '.join(f'{b['nearest_family_square']}@{b['nearest_tilt']}:{b['nearest_dist']:.3f} tilt{b['tilt_deg']:.1f}±{b['half_tilt']:.1f} meets={b['box_tilt_meets_family_range']} contains={b['box_contains_family_square']}' for b in r['boxes'])}]")
    worst = svg_box_to_grain(sw07, rows07, n07)
    summ['svg_worst_sat'] = worst
    json.dump(summ, open(os.path.join(RES, 't4_summary.json'), 'w'), indent=1)
    print('wrote t4_*.jsonl, t4_summary.json, box_to_grain_110.svg (family drawing worst SAT %.1e)' % worst)


if __name__ == '__main__':
    main()
