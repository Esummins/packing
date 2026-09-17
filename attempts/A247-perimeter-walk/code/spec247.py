"""A247: from square SPECS to a bb247 problem.  A spec is ('M', corner, cells) -- a meeter of
that corner, c00 among its cells -- or ('F', cells) -- a free square -- or ('P', cells) -- a plain
square (required cells only).  Monotone form: required cells only, a free square avoiding the
four boxes.  EXACT form: every square requires exactly its cells and avoids (depth <= eta_avoid)
every other cell of the neighbourhoods N_c that contain its set (a free square avoids the boxes too).
"""
import geo247 as G


def problem_of(specs, s_range, eta=0.0, exact=False, eta_avoid=None):
    """specs: list of ('M', corner, cells) / ('F', cells) / ('P', cells).  Monotone (exact=False):
    a meeter requires its cells (c00 among them), a free square requires its cells and avoids
    the four boxes (depth <= eta), a plain square requires its cells.  EXACT: every square
    requires exactly its cells and avoids (depth <= eta) every other cell of the neighbourhoods
    N_c that contain its set (a free square avoids the boxes too)."""
    sq = []
    for sp in specs:
        cells = list(sp[2] if sp[0] == 'M' else sp[1])
        if exact:
            reach = set()
            for c in G.CORNERS:
                if set(cells) <= set(G.NBR[c]):
                    reach |= set(G.NBR[c])
            avoid = set(reach) - set(cells)
            if sp[0] == 'F':
                avoid |= set(G.BOXES)
            sq.append({'kind': sp[0], 'corner': sp[1] if sp[0] == 'M' else None, 'req': cells,
                       'avoid': sorted(avoid, key=G.RING.index)})
        elif sp[0] == 'M':
            sq.append({'kind': 'M', 'corner': sp[1], 'req': cells, 'avoid': []})
        elif sp[0] == 'P':
            sq.append({'kind': 'P', 'req': cells, 'avoid': []})
        else:
            sq.append({'kind': 'F', 'req': cells, 'avoid': list(G.BOXES)})
    order = []
    for i in range(len(sq)):
        for j in range(i + 1, len(sq)):
            if sq[i]['req'] == sq[j]['req'] and sq[i]['avoid'] == sq[j]['avoid']:
                order.append((i, j))
    return {'squares': sq, 's': tuple(s_range), 'eta': eta, 'eta_avoid': eta if eta_avoid is None else eta_avoid,
            'order': order, 'specs': specs, 'exact': exact}
