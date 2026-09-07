"""A107 drawing: per-shadow SVG in the gen_a57_lp.py / gen_pinwheel_k7_svg.py conventions.
Panel 1 = the raw LP dual support of the representative node (overlaps allowed, reported as numbers).
Panel 2 = the snapped shadow (slot squares named, free squares f0..fn) at the certified side s0.
Panel 3 = the minimised packing at s* (contacts ringed, tilts labelled).  Every drawn square is
containment-checked; panels 2/3 are additionally overlap-checked."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shadowlib as L
import minimise as M

S0 = L.S0
SHAT = L.SHAT

def esc(t):
    return str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def text(x, y, t, size=11, col='#222', bold=False, anchor='start'):
    b = ' font-weight="bold"' if bold else ''
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{col}" text-anchor="{anchor}"{b}>{esc(t)}</text>'

def poly(ox, oy, sc, P, fill, stroke, op=0.6, w=1.5):
    pts = ' '.join(f'{ox + x * sc:.1f},{oy - y * sc:.1f}' for x, y in P)
    return f'<polygon points="{pts}" fill="{fill}" fill-opacity="{op:.2f}" stroke="{stroke}" stroke-width="{w}"/>'

def frame(ox, oy, sc, s):
    out = [f'<rect x="{ox}" y="{oy - s * sc:.1f}" width="{s * sc:.1f}" height="{s * sc:.1f}" fill="none" stroke="#000" stroke-width="2.2"/>']
    for (x0, y0) in [(0, 0), (s - 1, 0), (0, s - 1), (s - 1, s - 1)]:
        out.append(f'<rect x="{ox + x0 * sc:.1f}" y="{oy - (y0 + 1) * sc:.1f}" width="{sc}" height="{sc}" fill="none" stroke="#bbb" stroke-width="1" stroke-dasharray="4,3"/>')
    return out

# gallery v2 (PI, 2026-09-07): the left panel no longer encodes tilt.  One sequential scale carries
# the dual weight y and nothing else - pale yellow at y -> 0, dark orange at y = 1 - and the
# hypothesis squares get a colour used nowhere else in the gallery.
HYP_FILL, HYP_STROKE = '#00e5ff', '#000000'

def wcol(y, dark=False):
    """Sequential yellow->orange ramp on the dual weight y."""
    y = 0.0 if y is None else max(0.0, min(1.0, float(y)))
    h = 46.0 - 22.0 * y
    l = (88.0 - 46.0 * y) - (22.0 if dark else 0.0)
    return f'hsl({h:.0f},92%,{max(l,12.0):.0f}%)'

def lattice_free(free, s, dtol=1e-3, atol=0.05):
    """Free squares that sit ON a lattice cell (within dtol of its centre and atol degrees of axis).
    A121 found the gallery drawing these red as if they were free; they are snapped slot squares."""
    out = {}
    for i, (cx, cy, th) in enumerate(free):
        nm = L.snap(cx, cy, th, s, dtol=dtol, atol=atol)
        if nm:
            out[i] = nm
    return out

def panel_lp(ox, oy, sc, title, cores, sup, weights=None):
    """Raw LP dual support: hypothesis squares bright cyan with a heavy black outline and an 'H';
    every dual-support placement on ONE sequential scale by its weight y."""
    out = [text(ox, oy - S0 * sc - 26, title, 12, bold=True)]
    out += frame(ox, oy, sc, S0)
    bad = 0
    for k, (cx, cy, th) in enumerate(sup):
        P = L.corners(cx, cy, th)
        if not all(-1e-6 <= x <= S0 + 1e-6 and -1e-6 <= y <= S0 + 1e-6 for x, y in P):
            bad += 1
            continue
        w = 1.0 if weights is None else float(weights[k])
        out.append(poly(ox, oy, sc, P, wcol(w), wcol(w, True), 0.85, 1.0))
        if w < 0.95:                       # print y inside the faint squares only
            out.append(text(ox + cx * sc, oy - cy * sc + 3, f'{w:.2f}', 8, '#5d4037', False, 'middle'))
    for (cx, cy, th) in cores:             # drawn last so the hypothesis is never buried
        P = L.corners(cx, cy, th)
        out.append(poly(ox, oy, sc, P, HYP_FILL, HYP_STROKE, 0.75, 3.0))
        out.append(text(ox + cx * sc, oy - cy * sc + 4, 'H', 11, '#000', True, 'middle'))
    allsq = list(cores) + list(sup)
    g = min([L.sat_gap(allsq[i][:2], allsq[i][2], allsq[j][:2], allsq[j][2])
             for i in range(len(allsq)) for j in range(i + 1, len(allsq))] or [0.0])
    out.append(text(ox, oy + 16, f'{len(cores)} hypothesis square(s) H (cyan) + {len(sup)} dual-support '
                                 f'placements, fill = dual weight y; worst pairwise SAT gap {g:+.4f} '
                                 f'(LP rows are grid cells of pitch 0.192, so representatives overlap); '
                                 f'outside container: {bad}', 8.5, '#444'))
    return out, g

def panel_pack(ox, oy, sc, title, sub, s, free, slots, ring=True):
    """A real packing: slot squares blue+named, free squares red+f-indexed with tilts."""
    out = [text(ox, oy - S0 * sc - 26, title, 12, bold=True),
           text(ox, oy - S0 * sc - 10, sub, 9.5, '#444')]
    out += frame(ox, oy, sc, s)
    fx = M.slot_centres(slots, s)
    allsq = [(f[0], f[1], f[2]) for f in free] + [(p[0], p[1], 0.0) for p in fx]
    names = [f'f{i}' for i in range(len(free))] + list(slots)
    polys = [L.corners(*q) for q in allsq]
    exc = max([max(-x, x - s, -y, y - s) for P in polys for x, y in P] or [0.0])
    assert exc <= 1e-5, f'containment violated by {exc:.2e}'
    m = min([L.sat_gap(allsq[i][:2], allsq[i][2], allsq[j][:2], allsq[j][2])
             for i in range(len(allsq)) for j in range(i + 1, len(allsq))] or [0.0])
    latt = lattice_free(free, s)
    for i, P in enumerate(polys):
        isf = i < len(free)
        onlat = isf and i in latt
        # a free square sitting ON a lattice cell is a snapped slot square: draw it blue like the
        # others and give it its cell name.  Its f-index is kept so review.csv rows stay valid.
        fill = '#90caf9' if (not isf or onlat) else '#ef9a9a'
        stroke = '#1565c0' if (not isf or onlat) else '#c62828'
        out.append(poly(ox, oy, sc, P, fill, stroke, 0.6))
        cx, cy, th = allsq[i]
        out.append(text(ox + cx * sc, oy - cy * sc + 4, names[i], 9.5, '#000', True, 'middle'))
        if onlat:
            out.append(text(ox + cx * sc, oy - cy * sc + 15, latt[i], 8, '#0d47a1', True, 'middle'))
        elif isf:
            out.append(text(ox + cx * sc, oy - cy * sc + 15, f'{math.degrees(L.tmod(th)):.2f}°', 8, '#333', False, 'middle'))
    if ring:
        for i in range(len(allsq)):
            for j in range(i + 1, len(allsq)):
                if i >= len(free) and j >= len(free):
                    continue
                if L.sat_gap(allsq[i][:2], allsq[i][2], allsq[j][:2], allsq[j][2]) < 1e-6:
                    A, B = polys[i], polys[j]
                    best = (9, None)
                    for X, Y in ((A, B), (B, A)):
                        for v in X:
                            for k in range(4):
                                p, q = Y[k], Y[(k + 1) % 4]
                                ex, ey = q[0] - p[0], q[1] - p[1]
                                Ln = ex * ex + ey * ey
                                t = max(0.0, min(1.0, ((v[0] - p[0]) * ex + (v[1] - p[1]) * ey) / Ln))
                                f = (p[0] + t * ex, p[1] + t * ey)
                                dd = math.hypot(v[0] - f[0], v[1] - f[1])
                                if dd < best[0]:
                                    best = (dd, f)
                    f = best[1]
                    out.append(f'<circle cx="{ox + f[0] * sc:.1f}" cy="{oy - f[1] * sc:.1f}" r="4.5" fill="none" stroke="#2e7d32" stroke-width="2"/>')
    out.append(text(ox, oy + 16, f'min pairwise SAT separation {m:+.2e}; worst containment excursion '
                                 f'{exc:+.2e}; container side {s:.6f}'
                                 + (f'; {len(latt)} free square(s) sit ON a lattice cell and are drawn as '
                                    f'slot squares: ' + ', '.join(f'f{i}={n}' for i, n in sorted(latt.items()))
                                    if latt else ''), 8.5, '#444'))
    return out, m, latt

LEGEND = ('LEGEND  |  LEFT panel = the raw LP dual support: fill = dual weight y on one scale '
          '(pale yellow y->0, dark orange y=1; the number is printed inside faint squares), '
          'bright cyan + heavy black outline + H = a hypothesis square, overlaps are LP grid-cell '
          'representatives.  |  RIGHT panel = the minimised packing at s*: blue = slot square '
          '(named cell), red = free square (f-index + tilt), green ring = contact at gap < 1e-6.')

def legend(x, y):
    return [text(x, y, LEGEND, 9, '#333')]

def tilt_panel(ox, oy, w, h, curve, s_star, th_star):
    pts = [(d['tilt_deg'], d['s']) for d in curve if d['s'] is not None]
    if not pts:
        return []
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0, x1 = min(xs), max(xs); y0, y1 = min(ys + [s_star]), max(ys)
    if x1 - x0 < 1e-9: x1 = x0 + 1
    if y1 - y0 < 1e-9: y1 = y0 + 1e-3
    X = lambda v: ox + (v - x0) / (x1 - x0) * w
    Y = lambda v: oy - (v - y0) / (y1 - y0) * h
    out = [f'<rect x="{ox}" y="{oy - h}" width="{w}" height="{h}" fill="none" stroke="#888"/>',
           text(ox, oy - h - 8, 'side minimum vs the common tilt of the free squares', 10, '#222', True)]
    d = ' '.join(('M' if i == 0 else 'L') + f'{X(p[0]):.1f},{Y(p[1]):.1f}' for i, p in enumerate(sorted(pts)))
    out.append(f'<path d="{d}" fill="none" stroke="#c62828" stroke-width="1.8"/>')
    out.append(f'<line x1="{X(x0):.1f}" y1="{Y(SHAT):.1f}" x2="{X(x1):.1f}" y2="{Y(SHAT):.1f}" stroke="#1565c0" stroke-dasharray="4,3"/>')
    out.append(text(X(x1), Y(SHAT) - 3, ' s-hat', 8, '#1565c0', anchor='end'))
    out.append(f'<circle cx="{X(th_star):.1f}" cy="{Y(s_star):.1f}" r="3.5" fill="#2e7d32"/>')
    out.append(text(ox, oy + 12, f'{x0:.2f}°', 8, '#444'))
    out.append(text(ox + w, oy + 12, f'{x1:.2f}°', 8, '#444', anchor='end'))
    out.append(text(ox - 4, oy, f'{y0:.5f}', 8, '#444', anchor='end'))
    out.append(text(ox - 4, oy - h, f'{y1:.5f}', 8, '#444', anchor='end'))
    return out

def write_svg(path, body, W, H):
    doc = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Segoe UI, sans-serif" style="background:#fff">'] + body + ['</svg>']
    open(path, 'w', encoding='utf-8').write('\n'.join(doc))
    import xml.dom.minidom
    xml.dom.minidom.parse(path)
    return path
