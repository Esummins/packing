"""A260 minimal SVG helper (text is XML-escaped): panels with a world -> pixel map (y up), polygons, notes, a grey STIPPLE pattern for
undecided regions (never green), and a magnified inset (the same drawing calls at a larger scale, clipped)."""

from html import escape


class Panel:
    def __init__(self, x0, y0, wpx, hpx, wx0, wy0, wx1, wy1, clip_id=None):
        self.x0, self.y0, self.wpx, self.hpx = x0, y0, wpx, hpx
        self.wx0, self.wy0, self.wx1, self.wy1 = wx0, wy0, wx1, wy1
        self.k = min(wpx / (wx1 - wx0), hpx / (wy1 - wy0))
        self.items, self.clip_id = [], clip_id

    def pt(self, p):
        return (self.x0 + (p[0] - self.wx0) * self.k, self.y0 + self.hpx - (p[1] - self.wy0) * self.k)

    def poly(self, V, fill='none', stroke='#333', sw=1.0, op=1.0, dash=None):
        pts = ' '.join('%.2f,%.2f' % self.pt(p) for p in V)
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        self.items.append('<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="%s" stroke-width="%.2f"%s/>'
                          % (pts, fill, op, stroke, sw, d))

    def line(self, p, q, stroke='#333', sw=1.0, dash=None):
        a, b = self.pt(p), self.pt(q)
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        self.items.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="%.2f"%s/>'
                          % (a[0], a[1], b[0], b[1], stroke, sw, d))

    def path(self, pts, stroke='#333', sw=1.2):
        s = ' '.join('%.2f,%.2f' % self.pt(p) for p in pts)
        self.items.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.2f"/>' % (s, stroke, sw))

    def dot(self, p, r=3, fill='#000'):
        a = self.pt(p)
        self.items.append('<circle cx="%.2f" cy="%.2f" r="%.1f" fill="%s"/>' % (a[0], a[1], r, fill))

    def text(self, p, s, size=11, fill='#111', anchor='start'):
        a = self.pt(p)
        self.items.append('<text x="%.1f" y="%.1f" font-size="%d" fill="%s" text-anchor="%s">%s</text>'
                          % (a[0], a[1], size, fill, anchor, escape(s)))

    def frame(self, stroke='#000', sw=1.5):
        self.poly([(self.wx0, self.wy0), (self.wx1, self.wy0), (self.wx1, self.wy1), (self.wx0, self.wy1)],
                  stroke=stroke, sw=sw)

    def render(self):
        body = '\n'.join(self.items)
        if self.clip_id:
            return ('<clipPath id="%s"><rect x="%.1f" y="%.1f" width="%.1f" height="%.1f"/></clipPath>\n'
                    '<g clip-path="url(#%s)">\n%s\n</g>\n<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" '
                    'stroke="#b00" stroke-width="1.5"/>' % (self.clip_id, self.x0, self.y0, self.wpx, self.hpx,
                                                           self.clip_id, body, self.x0, self.y0, self.wpx, self.hpx))
        return body


def note(x, y, lines, size=11, width=0):
    out = []
    for i, ln in enumerate(lines):
        out.append('<text x="%.1f" y="%.1f" font-size="%d" fill="#111">%s</text>' % (x, y + i * (size + 3), size, escape(ln)))
    return '\n'.join(out)


def page(path, W, Hh, title, parts):
    head = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" font-family="sans-serif">\n'
            '<defs><pattern id="stip" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="6" '
            'fill="#eee"/><circle cx="2" cy="2" r="1" fill="#888"/></pattern></defs>\n'
            '<rect width="%d" height="%d" fill="#fff"/>\n<text x="12" y="20" font-size="14" font-weight="bold">%s</text>\n'
            % (W, Hh, W, Hh, W, Hh, escape(title)))
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(head + '\n'.join(parts) + '\n</svg>\n')
