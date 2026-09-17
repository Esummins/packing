"""A244 pages (docs/residue_map/campaigns/A244-twelve-stuck/):

  twelve_stuck.svg  (A) the least-side CERTIFIED 12-stuck packing, all twelve border cells drawn
                        with their meeters;  (B) its BL corner magnified (the corner box and its
                        two wall slots, each meeter outlined);  (C) the 4-STUCK control at its own
                        least side, with the cells it FAILS marked;  (D) the closest thing the
                        probe found below 4.
  threshold244.svg  (E) best certified side vs restarts, 12-stuck and the 4-stuck control;
                    (F) the fixed-side probe: best residual vs side, with s-hat, 4 and 3 + sqrt2.

Every configuration panel is geometry-checked as drawn (containment + pairwise interior
disjointness, exact SAT) and the check is printed in that panel's note.
    python pages244.py
"""
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
sys.path.insert(0, HERE)
import cells244 as C          # noqa: E402
import draw244 as D           # noqa: E402

OUT = os.path.join(ROOT, 'docs', 'residue_map', 'campaigns', 'A244-twelve-stuck')
SHAT = 3.877084


def poses(z):
    return [(z[3 * i], z[3 * i + 1], z[3 * i + 2]) for i in range(11)]


def draw_config(pg, key, z, cells_fail=(), labels=True, cellnames=True):
    """draw a configuration into an ALREADY CREATED panel; returns (stuck report, geometry
    check)."""
    s = z[33]
    P = poses(z)
    ms = C.meeter_sets(z)
    for n in C.CELLS:
        r = C.cell_rect(n, s)
        bad = n in cells_fail
        pg.rect(key, r, '#ffd6d6' if bad else D.CELLFILL[n[2:]],
                D.RED if bad else '#c9c9c9', 1.3 if bad else 0.7, dash=None if bad else '3,2')
    meet = sorted({i for v in ms.values() for i in v})
    for i, p in enumerate(P):
        fill, stroke = (D.ORANGE, '#8a4a08') if i in meet else (D.BLUE, '#1c4470')
        pg.square(key, p, fill, stroke, 1.4,
                  label=('%d' % i) if labels else None, op=0.45)
    pg.frame(key, s)
    if cellnames:
        for n in C.CELLS:
            x0, x1, y0, y1 = C.cell_rect(n, s)
            q = pg._t(key, ((x0 + x1) / 2, (y0 + y1) / 2))
            pg.text(q[0], q[1] - 1, n, 7.0, '#555' if n not in cells_fail else D.RED,
                    anchor='middle')
            pg.text(q[0], q[1] + 8, ','.join(str(i) for i in ms[n]), 7.0,
                    '#222' if len(ms[n]) >= 2 else D.RED, anchor='middle')
    return C.stuck_report(z), D.check(P, s)


def page1(su):
    t0 = time.time()
    pg = D.Page(1180, 1010, 'A244 twelve-stuck')
    pg.text(24, 30, 'A244 -- 12-STUCK: every one of the twelve border cells met by two squares',
            17, '#111', weight='600')
    pg.text(24, 50, 'Cells: corner boxes c00 (amber), wall slots c01 up the wall (blue) and c10 '
                    'along the floor (green), in each corner frame.  Orange = a square meeting at '
                    'least one cell, blue = free.  Under each cell: its meeters.', 10.5, '#444')
    best = su.get('best_twelve')
    four = su.get('best_four')
    near = su.get('near_below4')
    y0 = 64
    if best:
        z = list(best['z'])
        z[33] = best['s_cert']
        pg.panel('A', 24, y0, 520, 520, z[33])
        st, chk = draw_config(pg, 'A', z)
        pg.note(24, y0 + 540, [
            '(A) WHAT IT IS: the least-side CERTIFIED 12-stuck packing of 11 unit squares, at '
            'side %.9f (= the raw optimum %.9f inflated by lam = %s so that every' % (
                z[33], best.get('s', best.get('side', float('nan'))), best['cert']['lam']),
            '    wall and pair gap is >= 0 in 40-digit interval arithmetic).  Crowd margin delta '
            '= %g; run %s.' % (best.get('delta', 0), best['rid']),
            '    GEOMETRY CHECK (this panel, as drawn): contained and pairwise interior-disjoint '
            '= %s, min wall gap %.2e, min pair gap %.2e; 12 of 12 cells doubly met,' % (
                chk[0], chk[1], chk[2]),
            '    worst second depth %.3e.  Fritz-John on the FREE rows (no crowd rows): residual '
            '%s; every meeter loaded: %s; LOCKED: %s.' % (
                st['worst_second_depth'], best.get('fj_free_res'),
                best.get('meeters_all_loaded'), best.get('locked')),
            '    The side is ABOVE 4 and therefore above s-hat = 3.877084 by %.6f.'
            % (z[33] - SHAT)])
        pg.panel('B', 590, y0 + 16, 300, 300, z[33], win=(-0.1, 2.5, -0.1, 2.5))
        draw_config(pg, 'B', z, labels=True)
        pg.text(590, y0 + 10, '(B) the BL corner magnified (BL00, BL01, BL10)', 11, '#111')
    if four:
        z4 = list(four['z'])
        z4[33] = four['s_cert']
        st4 = C.stuck_report(z4)
        fail = [c for c in C.CELLS if len(st4['meeters'][c]) < 2]
        pg.panel('C', 920, y0 + 16, 240, 240, z4[33])
        _, chk4 = draw_config(pg, 'C', z4, cells_fail=fail, labels=False, cellnames=False)
        pg.text(920, y0 + 10, '(C) the 4-STUCK control, %.6f' % z4[33], 11, '#111')
        pg.note(920, y0 + 276, [
            'CONTROL: corner boxes only.  %d of 12' % st4['n_doubly_met'],
            'cells doubly met; the %d cells in RED' % len(fail),
            'are singly met.  Check %s, gaps %.1e / %.1e.' % (chk4[0], chk4[1], chk4[2])], 8.6, 10.5)
    if near:
        z = list(near['z'])
        pg.panel('D', 590, y0 + 376, 320, 320, z[33])
        stn = C.stuck_report(z)
        fail = [c for c in C.CELLS if len(stn['meeters'][c]) < 2]
        _, chkn = draw_config(pg, 'D', z, cells_fail=fail, labels=False)
        pg.text(590, y0 + 370, '(D) the best the probe reached at side %.6f' % z[33], 11, '#111')
        pg.note(590, y0 + 712, [
            '(D) WHAT IT IS: the least-residual configuration the fixed-side probe reached BELOW '
            '4 (side %.6f).  It is NOT a packing: residual %.3e' % (z[33], near['residual']),
            '    (min wall gap %.2e, min pair gap %.2e, worst second depth %.2e).  %d of 12 cells '
            'doubly met.' % (near['min_wall_gap'], near['min_pair_gap'],
                             near['worst_second_depth'], stn['n_doubly_met'])], 9.0, 11.5)
    pg.text(24, 990, 'generated %s by code/pages244.py in %.1f s'
            % (time.strftime('%Y-%m-%d %H:%M'), time.time() - t0), 8.5, '#888')
    pg.save(os.path.join(OUT, 'twelve_stuck.svg'))


def axes(pg, x, y, w, h, xr, yr, xt, yt, xlab, ylab, ylog=False):
    pg.line(x, y + h, x + w, y + h, '#444', 1.2)
    pg.line(x, y, x, y + h, '#444', 1.2)

    def X(v):
        return x + w * (v - xr[0]) / (xr[1] - xr[0])

    def Y(v):
        if ylog:
            a, b = math.log10(yr[0]), math.log10(yr[1])
            return y + h - h * (math.log10(max(v, yr[0])) - a) / (b - a)
        return y + h - h * (v - yr[0]) / (yr[1] - yr[0])
    for v in xt:
        pg.line(X(v), y + h, X(v), y + h + 4, '#444', 1.0)
        pg.text(X(v), y + h + 15, ('%g' % v), 8.5, '#444', anchor='middle')
    for v in yt:
        pg.line(x - 4, Y(v), x, Y(v), '#444', 1.0)
        pg.text(x - 7, Y(v) + 3, ('%g' % v), 8.5, '#444', anchor='end')
    pg.text(x + w / 2, y + h + 32, xlab, 9.5, '#222', anchor='middle')
    pg.text(x, y - 8, ylab, 9.5, '#222')
    return X, Y


def page2(su):
    t0 = time.time()
    pg = D.Page(1180, 620, 'A244 threshold')
    pg.text(24, 30, 'A244 -- the 12-STUCK threshold: what the search bought', 17, '#111', weight='600')
    cw = [(k, v) for k, v in su['curve_twelve'] if v]
    cf = [(k, v) for k, v in su['curve_four'] if v]
    lo = min([v for _, v in cw + cf] + [3.99])
    hi = max([v for _, v in cw + cf] + [4.05])
    nmax = max([k for k, _ in su['curve_twelve'] + su['curve_four']] + [1])
    X, Y = axes(pg, 80, 80, 470, 420, (0, nmax), (lo - 0.002, hi + 0.002),
                [0, nmax // 4, nmax // 2, 3 * nmax // 4, nmax],
                [round(lo - 0.002 + i * (hi - lo + 0.004) / 4, 4) for i in range(5)],
                'restarts (descent runs, in file order)', 'best CERTIFIED side')
    for pts, col, lab in ((cw, D.ORANGE, '12-STUCK'), (cf, D.BLUE, '4-STUCK (control)')):
        if pts:
            pg.polyline([(X(k), Y(v)) for k, v in pts], col, 1.8)
            pg.text(X(pts[-1][0]) - 4, Y(pts[-1][1]) - 6, '%s  %.6f' % (lab, pts[-1][1]), 9.5, col,
                    anchor='end')
    for v, lab, col in ((4.0, 's = 4', '#666'), (SHAT, 's-hat = 3.877084', D.GREEN)):
        if lo - 0.002 <= v <= hi + 0.002:
            pg.line(80, Y(v), 550, Y(v), col, 1.0, '5,4')
            pg.text(84, Y(v) - 4, lab, 8.5, col)
    pg.text(80, 66, '(E) the descent: best certified side after k restarts', 11, '#111')
    agg = {}
    for k, v in su['probe'].items():
        mode, side = k.split('|')[0], float(k.split('|')[1])
        cur = agg.get((mode, side))
        agg[(mode, side)] = v['best'] if cur is None else min(cur, v['best'])
    pr = agg
    sides12 = sorted(s for (m, s) in pr if m == 'twelve')
    sides4 = sorted(s for (m, s) in pr if m == 'four')
    allsides = sides12 + sides4
    if allsides:
        xr = (min(allsides) - 0.02, max(allsides) + 0.02)
        X2, Y2 = axes(pg, 680, 80, 440, 420, xr, (1e-6, 1e-1),
                      [round(v, 3) for v in (xr[0], (xr[0] + xr[1]) / 2, xr[1])],
                      [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1],
                      'side s', 'best residual over the restarts (log)', ylog=True)
        for sd, col, lab in ((sides12, D.ORANGE, '12-STUCK'), (sides4, D.BLUE, '4-STUCK')):
            key = 'twelve' if col == D.ORANGE else 'four'
            pts = [(X2(s), Y2(max(pr[(key, s)], 1e-6))) for s in sd]
            if pts:
                pg.polyline(pts, col, 1.8)
                for (px, py) in pts:
                    pg.parts.append('<circle cx="%.2f" cy="%.2f" r="2.6" fill="%s"/>'
                                    % (px, py, col))
                pg.text(pts[0][0] + 6, pts[0][1] - 6, lab, 9.5, col)
        for v, lab, col in ((4.0, 's = 4', '#666'), (SHAT, 's-hat', D.GREEN),
                            (3 + math.sqrt(2), '3+sqrt2', '#8a4a08')):
            if xr[0] <= v <= xr[1]:
                pg.line(X2(v), 80, X2(v), 500, col, 1.0, '5,4')
                pg.text(X2(v) + 3, 92, lab, 8.5, col)
        pg.text(680, 66, '(F) the fixed-side probe: how close it got at each side', 11, '#111')
    pg.note(80, 545, [
        'EVIDENCE, NOT PROOF.  (E) is the running minimum of verify244\'s certified side over the '
        'descent runs; (F) is the least residual the fixed-side probe reached,',
        'residual = max(-min wall gap, -min pair gap, delta - min second depth, 0), so 0 means a '
        'delta-margin stuck packing EXISTS at that side and a positive value',
        'means only that %d restarts (%.2f CPU-h in total for this campaign) did not find one.'
        % (su['n_probes'], su['cpu_hours'])])
    pg.text(24, 600, 'generated %s by code/pages244.py in %.1f s'
            % (time.strftime('%Y-%m-%d %H:%M'), time.time() - t0), 8.5, '#888')
    pg.save(os.path.join(OUT, 'threshold244.svg'))


def main():
    os.makedirs(OUT, exist_ok=True)
    su = json.load(open(os.path.join(ATT, 'results', 'summary244.json'), encoding='utf-8'))
    pr = [json.loads(l) for l in open(os.path.join(ATT, 'results', 'probe244_below4.jsonl'),
                                      encoding='utf-8')] \
        if os.path.exists(os.path.join(ATT, 'results', 'probe244_below4.jsonl')) else []
    cand = [r for r in pr if r['side'] < 4.0 and 'z' in r]
    su['near_below4'] = min(cand, key=lambda r: r['residual']) if cand else None
    page1(su)
    page2(su)
    print('pages written to', OUT, flush=True)


if __name__ == '__main__':
    main()
