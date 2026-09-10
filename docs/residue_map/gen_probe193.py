"""A193 pages: probe193_<class>.svg -- the frame of the class (pins, the forced cells thin dashed: window-forced
dashed, s0-only forced dotted, the meeter windows), the pins-only root LP's dual support with its guard lines, and
the deepest assignment leaf's windows + guard-line LP support with the roles' hulls.  Drawing rules of
gen_a57_lp.py: hypothesis squares only at ADMISSIBLE poses (every drawn support square is checked for containment
and the count of inadmissible ones is printed), opacity = dual weight, times printed.  Read-only on A193's results.

    python gen_probe193.py [corners4 k4_05]
"""
import json, math, os, sys
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
A193 = os.path.join(R, 'attempts', 'A193-highk-probes')
S0 = 969271 / 250000
S = 120                                   # px per unit
PAD = 34


def sq(cx, cy, th):
    c, s_ = math.cos(th), math.sin(th)
    return [(cx + 0.5 * (dx * c - dy * s_), cy + 0.5 * (dx * s_ + dy * c)) for dx, dy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]


def admissible(P):
    return all(-1e-9 <= x <= S0 + 1e-9 and -1e-9 <= y <= S0 + 1e-9 for x, y in P)


def esc(t):
    return str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def text(x, y, t, size=11, col='#222', bold=False, anchor='start'):
    b = ' font-weight="bold"' if bold else ''
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{col}" text-anchor="{anchor}"{b}>{esc(t)}</text>'


def rows(path):
    out = []
    if os.path.exists(path):
        for l in open(path, encoding='utf-8'):
            if l.strip():
                out.append(json.loads(l))
    return out


def frame_panel(ox, oy, fr, pins, title):
    """ox, oy = the panel's top-left in px; the container drawn with y up."""
    X = lambda x: ox + x * S
    Y = lambda y: oy + (S0 - y) * S
    out = [text(ox, oy - 8, title, 12, bold=True),
           f'<rect x="{X(0):.1f}" y="{Y(S0):.1f}" width="{S0 * S:.1f}" height="{S0 * S:.1f}" fill="none" stroke="#000" stroke-width="2"/>']
    for (cx, cy) in pins:
        P = sq(cx, cy, 0.0)
        out.append('<polygon points="%s" fill="#90caf9" fill-opacity="0.6" stroke="#1565c0" stroke-width="1.5"/>' %
                   ' '.join(f'{X(x):.1f},{Y(y):.1f}' for x, y in P))
    for c in fr:
        # the OPEN slot box of the cell in the container frame (unit cell at the corner's offsets)
        corner, i, j = c['cell'][:2], int(c['cell'][3]), int(c['cell'][5])
        u0, v0 = i, j
        x0 = u0 if corner in ('BL', 'TL') else S0 - u0 - 1
        y0 = v0 if corner in ('BL', 'BR') else S0 - v0 - 1
        dash = '5,3' if c.get('fc_window') else ('2,3' if c.get('fc_s0_only') else '1,4')
        col = '#c62828' if c.get('fc_window') else ('#ef6c00' if c.get('fc_s0_only') else '#9e9e9e')
        out.append(f'<rect x="{X(x0):.1f}" y="{Y(y0 + 1):.1f}" width="{S:.1f}" height="{S:.1f}" fill="none" stroke="{col}" stroke-width="1" stroke-dasharray="{dash}"/>')
        out.append(text(X(x0) + 3, Y(y0 + 1) + 11, '%s %s' % (c['cell'], c.get('extension') or ''), 8, col))
    return out


def support_panel(ox, oy, pk, lines, title, sub, hulls=None, pins=()):
    X = lambda x: ox + x * S
    Y = lambda y: oy + (S0 - y) * S
    out = [text(ox, oy - 20, title, 12, bold=True), text(ox, oy - 7, sub, 9, '#444'),
           f'<rect x="{X(0):.1f}" y="{Y(S0):.1f}" width="{S0 * S:.1f}" height="{S0 * S:.1f}" fill="none" stroke="#000" stroke-width="2"/>']
    for (cx, cy) in pins:
        P = sq(cx, cy, 0.0)
        out.append('<polygon points="%s" fill="#90caf9" fill-opacity="0.35" stroke="#1565c0" stroke-width="1"/>' %
                   ' '.join(f'{X(x):.1f},{Y(y):.1f}' for x, y in P))
    for L in lines or []:
        if L.get('z', 0) <= 1e-6:
            continue
        o, off = L['orient'], float(L['off'])
        if o == 'h':
            out.append(f'<line x1="{X(0):.1f}" y1="{Y(off):.1f}" x2="{X(S0):.1f}" y2="{Y(off):.1f}" stroke="#2e7d32" stroke-width="1.2" stroke-dasharray="6,2"/>')
            out.append(text(X(S0) + 3, Y(off) + 3, 'z=%.3f' % L['z'], 8, '#2e7d32'))
        else:
            out.append(f'<line x1="{X(off):.1f}" y1="{Y(0):.1f}" x2="{X(off):.1f}" y2="{Y(S0):.1f}" stroke="#2e7d32" stroke-width="1.2" stroke-dasharray="6,2"/>')
            out.append(text(X(off) - 8, Y(S0) - 3, 'z=%.3f' % L['z'], 8, '#2e7d32'))
    pk = [p for p in pk if float(p[3]) > 1e-6]                 # the dual SUPPORT: positive weight only
    ys = [float(p[3]) for p in pk] or [1.0]
    ymax = max(ys) or 1.0
    bad = 0
    for p in pk:
        cx, cy, th, w = float(p[0]), float(p[1]), float(p[2]), float(p[3])
        P = sq(cx, cy, th)
        if not admissible(P):
            bad += 1
            continue                                          # drawing rule: admissible poses only
        op = 0.15 + 0.7 * (w / ymax)
        out.append('<polygon points="%s" fill="#ef9a9a" fill-opacity="%.2f" stroke="#b71c1c" stroke-width="0.8"/>' %
                   (' '.join(f'{X(x):.1f},{Y(y):.1f}' for x, y in P), op))
    for k, h in (hulls or {}).items():                        # the roles' centre hulls, drawn ON TOP (thin, no fill)
        if k.startswith('P'):
            continue
        x0, x1, y0, y1 = h[0], h[1], h[2], h[3]
        out.append(f'<rect x="{X(x0):.1f}" y="{Y(y1):.1f}" width="{(x1 - x0) * S:.1f}" height="{(y1 - y0) * S:.1f}" fill="none" stroke="#1b5e20" stroke-width="1.6"/>')
        out.append(text(X(x0) + 2, Y(y1) + 9, '%s [%.0f-%.0f deg]' % (k, h[4], h[5]), 8, '#1b5e20', bold=True))
    out.append(text(ox, Y(0) + 14, '%d support placements drawn (opacity = dual weight, sum %.3f); %d inadmissible NOT drawn' % (len(pk) - bad, sum(ys) if pk else 0, bad), 9, '#444'))
    return out


def page(cls):
    rs = rows(os.path.join(A193, 'results', 'probe193_%s.jsonl' % cls))
    fr = next((r for r in rs if r['kind'] == 'frame'), None)
    root = next((r for r in rs if r['kind'] == 'root_lp'), None)
    leaves = [r for r in rs if r['kind'] == 'leaf_lp']
    search = ([r for r in rs if r['kind'] == 'search'] or [None])[-1]
    certs = {r.get('node'): r for r in rows(os.path.join(A193, 'results', 'probe193_certify.jsonl')) if r.get('cls') == cls and r.get('node')}
    nrs = [r for r in rs if r['kind'] == 'noroom']
    if fr is None:
        print(cls, 'no frame row'); return
    pins = [tuple(p) for p in fr['pins']]
    W = 3 * (S0 * S + 60) + PAD
    H = S0 * S + 150
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" font-family="Helvetica, Arial, sans-serif">',
           f'<rect width="{W:.0f}" height="{H:.0f}" fill="#fff"/>',
           text(PAD, 20, 'A193 probe -- %s (%s): frame, pins-only root LP with guard lines, deepest assignment leaf' % (cls, 'k4_13' if cls == 'corners4' else cls), 14, bold=True)]
    oy = 60
    nw = sum(1 for c in fr['cells'] if c.get('fc_window')); ns = sum(1 for c in fr['cells'] if c.get('fc_s0_only'))
    out += frame_panel(PAD, oy, fr['cells'], pins, 'frame: %d pins, %d cells forced on the window (dashed), %d at s0 only (dotted)' % (len(pins), nw, ns))
    ox2 = PAD + S0 * S + 60
    if root:
        sub = 'tau %.4f / budget %s, %s, %d active lines, LP %.0f s [K1: tau* >= 7 while k5_11/k5_16 roots are alive]' % (
            root.get('tau') or 0, root.get('budget'), 'converged' if root.get('converged') else 'NOT converged', root.get('n_active') or 0, root.get('wall_s') or 0)
        try:                                                   # the FULL dual support (the jsonl row is capped at 200 rows)
            rl = json.load(open(os.path.join(A193, 'results', 'lpres_root_%s.json' % cls), encoding='utf-8'))
            rpk = [[q['cx'], q['cy'], q['theta'], q['y']] for q in (rl.get('packing') or [])]
        except Exception:
            rpk = root.get('packing_rows') or []
        out += support_panel(ox2, oy, rpk, root.get('z'), 'root LP: pins only + guard lines', sub, pins=pins)
    ox3 = ox2 + S0 * S + 60
    if leaves:
        best = min(leaves, key=lambda r: (r.get('tau') or 99) - (r.get('budget_v4') or 0))
        lp = {}
        try:
            lp = json.load(open(os.path.join(R, best['lpres']), encoding='utf-8'))
        except Exception:
            pass
        hulls = {}
        for k, ps in (lp.get('roles_pieces') or {}).items():
            hulls[k] = [min(p[0] for p in ps), max(p[1] for p in ps), min(p[2] for p in ps), max(p[3] for p in ps), min(p[4] for p in ps), max(p[5] for p in ps)]
        cv = certs.get(best['node'], {}).get('certified')
        sub = 'tau %.4f / b4 %s, %s, %d roles (%d cored), %d free, %d active lines, LP %.0f s%s' % (
            best.get('tau') or 0, best.get('budget_v4'), 'converged' if best.get('converged') else 'NOT converged', best.get('n_roles') or 0,
            best.get('n_cores') or 0, best.get('free') or 0, best.get('n_active') or 0, best.get('wall_s') or 0, ('; v5 ' + cv) if cv else '')
        out += support_panel(ox3, oy, best.get('packing_rows') or [], best.get('z'), 'leaf LP: windows + guard lines (' + best['label'][-48:] + ')', sub, hulls=hulls, pins=pins)
    else:
        out.append(text(ox3, oy - 8, 'no complete assignment leaf reached' + (' (%s)' % search.get('leaf') if search else ''), 12, bold=True))
    y = oy + S0 * S + 40
    if search:
        sm = search.get('summary') or {}
        out.append(text(PAD, y, 'assignment search: %s -- %d multibox nodes, %.0f s geometry, leaves dead %d / alive %d / undecided %d; %s' % (
            search.get('verdict'), search.get('n_nodes') or 0, search.get('compute_s') or 0, sm.get('dead', 0), sm.get('alive', 0), sm.get('undecided', 0), (search.get('leaf') or '')[:90]), 10, '#222'))
        y += 14
    if nrs:
        out.append(text(PAD, y, 'no-room leaf at %d complete leaves: %s' % (len(nrs), '; '.join('%s (%.0f s, %s)' % (r.get('verdict'), r.get('seconds') or 0, (r.get('reason') or '')[:60]) for r in nrs[:3])), 10, '#222'))
        y += 14
    out.append(text(PAD, y, 'kills are [C under v5 ONLY]; s0-only forced cells make a kill an s0 statement (window form = A57 G1 [P]); generated by docs/residue_map/gen_probe193.py', 9, '#666'))
    out.append('</svg>')
    p = os.path.join(R, 'docs', 'residue_map', 'probe193_%s.svg' % cls)
    open(p, 'w', encoding='utf-8').write('\n'.join(out))
    print('wrote', p)


if __name__ == '__main__':
    for cls in (sys.argv[1:] or ['corners4', 'k4_05']):
        page(cls)
