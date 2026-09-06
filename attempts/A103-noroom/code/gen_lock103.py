"""gen_lock103.py -- draw the (C) object of A103: the two sub-4 K0-BLOCKED packings with every intruder
labelled HELD (blue: Lemma ROT + Cor. 2 certificate exists) or UNHELD (red: a strictly opening, depth-
decreasing single-square motion exists; arrow = the LP direction, with its room), free squares grey.
Poses from A87's exact files (lock103's loader), verdicts from results/lock103.jsonl.  Every square is
geometry-checked (containment, pairwise SAT separation).  Output: results/lockmap103.svg."""
import json
import math
import os
import xml.dom.minidom

HERE = os.path.dirname(os.path.abspath(__file__))
A103 = os.path.dirname(HERE)
import lock103 as L  # noqa: E402

corpus = {c['name']: c for c in L.load_corpus()}
rows = {}
for line in open(os.path.join(A103, 'results', 'lock103.jsonl'), encoding='utf-8'):
    if line.strip():
        o = json.loads(line)
        rows[o['packing']] = o

S = 130


def esc(t):
    return str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def text(x, y, t, size=11, col='#222', bold=False, anchor='start'):
    b = ' font-weight="bold"' if bold else ''
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{col}" '
            f'text-anchor="{anchor}"{b}>{esc(t)}</text>')


red = ('#c62828', '#ef9a9a')
blue = ('#1565c0', '#90caf9')
grey = ('#555', '#e0e0e0')


def panel(ox, oy, name, title):
    c = corpus[name]
    s, P = c['side'], c['poses']
    o = rows[name]
    polys = [L.verts(*q) for q in P]
    assert all(-5e-9 <= x <= s + 5e-9 and -5e-9 <= y <= s + 5e-9 for p in polys for x, y in p)
    msep = min(L.sep(polys[i], polys[j]) for i in range(11) for j in range(i + 1, 11))
    assert msep >= -5e-9, msep
    status = {}
    for r in o['rows']:
        status[r['square']] = r
    out = [text(ox, oy - s * S - 28, title, 12.5, bold=True)]
    out.append(f'<rect x="{ox}" y="{oy - s * S:.1f}" width="{s * S:.1f}" height="{s * S:.1f}" '
               f'fill="none" stroke="#000" stroke-width="2.2"/>')
    corners = {'BL': (0, 0), 'BR': (s - 1, 0), 'TR': (s - 1, s - 1), 'TL': (0, s - 1)}
    for cn, (x0, y0) in corners.items():
        out.append(f'<rect x="{ox + x0 * S:.1f}" y="{oy - (y0 + 1) * S:.1f}" width="{S}" height="{S}" '
                   f'fill="none" stroke="#999" stroke-width="1" stroke-dasharray="4,3"/>')
    for i, p in enumerate(polys):
        r = status.get(i)
        col, fill = grey if r is None else (blue if r['held'] else red)
        pts = ' '.join(f'{ox + x * S:.1f},{oy - y * S:.1f}' for x, y in p)
        out.append(f'<polygon points="{pts}" fill="{fill}" fill-opacity="0.6" stroke="{col}" '
                   f'stroke-width="1.5"/>')
        t = math.degrees(P[i][2]) % 90
        t = min(t, 90 - t)
        out.append(text(ox + P[i][0] * S, oy - P[i][1] * S + 4, str(i), 11, '#000', True, 'middle'))
        out.append(text(ox + P[i][0] * S, oy - P[i][1] * S + 15, f'{t:.2f}°', 8, '#333', False,
                        'middle'))
        if r is not None and not r['held']:
            vx, vy, w = r['lp_dir']
            cx, cy = ox + P[i][0] * S, oy - P[i][1] * S
            n = math.hypot(vx, vy)
            if n > 0.05:
                ex, ey = cx + 0.35 * S * vx / n, cy - 0.35 * S * vy / n
                out.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" '
                           f'stroke="#b71c1c" stroke-width="2.5" marker-end="url(#arr)"/>')
            if abs(w) > 0.05:
                sw = 'CCW' if w > 0 else 'CW'
                out.append(text(cx, cy - 18, f'rot {sw}', 8.5, '#b71c1c', True, 'middle'))
    lines = []
    for cn in ('BL', 'BR', 'TR', 'TL'):
        rs = [r for r in o['rows'] if r['corner'] == cn]
        parts = []
        for r in sorted(rs, key=lambda r: -r['depth']):
            if r['held']:
                parts.append(f"sq{r['square']} d={r['depth']:.1e} HELD")
            else:
                cf = r['confirm'] or {}
                parts.append(f"sq{r['square']} d={r['depth']:.1e} UNHELD by {r['free_by']} "
                             f"(t*={r['lp_t']:.2g}, room {cf.get('travel_max', 0):.1e}, "
                             f"{'exits cell' if cf.get('exits_cell') else 'retracts %.0f%%' % (100 * (cf.get('retraction_fraction') or 0))})")
        lines.append(f'{cn}: ' + '; '.join(parts))
    y = oy + 20
    for ln in lines:
        out.append(text(ox, y, ln, 9.2, '#333'))
        y += 13
    out.append(text(ox, y, f'checks: containment, min pairwise SAT separation {msep:+.1e}; '
                    f'meeter counts ' + ' '.join(f"{k}:{v}" for k, v in o['meet_counts'].items()),
                    9, '#666'))
    y += 13
    return out, y


W = 2 * (int(4.0 * S) + 60) + 40
body = ['<defs><marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">'
        '<path d="M0,0 L8,4 L0,8 z" fill="#b71c1c"/></marker></defs>']
ymax = 0
for k, (name, title) in enumerate([
        ('record_s0115', 'record_s0115: side 3.9854837, K0-BLOCKED (exact), 7 of 8 intruders HELD'),
        ('floor_1e-03_d1em03_s0050', 'floor 1e-3 record: side 3.9907485, K0-BLOCKED(1e-3), 6 of 8 HELD')]):
    out, y = panel(30 + k * (int(4.0 * S) + 60), 60 + 4.0 * S, name, title)
    body += out
    ymax = max(ymax, y)
cap = [
    'blue = intruder HELD at first order (Lemma ROT + Cor. 2: its contact rows balance the virtual corner push; no strictly opening, depth-decreasing single-square motion);',
    'red = UNHELD (the LP direction is drawn: arrow = translation part, "rot" = rotation sense); grey = free squares. Contacts at gap < 1e-7, meet bar 1e-9 (A102 conventions).',
    'A103 (2026-09-06): no K0-BLOCKED packing on disk (12/12, sides 3.985-4.107) is held at all eight intruders; every one has an unheld SECOND meeter. Trump: 5/5 held (canary).',
    'The (C) object is therefore not a realised frame but the family RES-LOCK (all intruders held, side < 4), empty on the corpus; the fact that would finish is Conjecture LOCK-FREE (noroom.md s.7).']
for ln in cap:
    body.append(text(30, ymax + 16, ln, 9.5, '#444'))
    ymax += 14
H = int(ymax + 24)
doc = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
       f'font-family="Segoe UI, sans-serif" style="background:#fff">'] + body + ['</svg>']
outp = os.path.join(A103, 'results', 'lockmap103.svg')
open(outp, 'w', encoding='utf-8').write('\n'.join(doc))
xml.dom.minidom.parse(outp)
print('wrote', outp, W, H, 'xml ok')
