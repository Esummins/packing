"""A189: the NO-ROOM leaf drawn on the node it was found on (c0_Y1033's STEP 34 node of A182).

Three panels, in the drawing rules of `gen_a57_lp.py` (S px per unit, black container, light-blue
pins, a note under every panel):

  (1) the node: the ten boxed roles' K' filled (A132: K' lies inside EVERY pose of the role), with
      each role's pose-window outlined -- the picture PI read as "10 squares placed";
  (2) certificate 1, the exact bisection: the CENTRE domain [1/2, s-1/2]^2 of an eleventh unit
      square, with every dropped piece hatched (each is certified "every pose here meets some
      core") and the open residue's pocket drawn solid;
  (3) certificate 2, the exact lane cover on the pocket: LANE = 0, i.e. no unit square meets the
      pocket's interior clear of the ten cores -- and every free pose's centre is in the pocket,
      so the node is DEAD.

Read-only on every attempt: it re-runs A189's own tool (`attempts/A189-noroom/code/noroom189.py`)
and reads its recorded certificate.
"""
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "attempts", "A189-noroom", "code"))
import noroom189 as NR                                             # A189 (which pulls in A171/A178)

S = 150                                                            # px per unit
CERT = os.path.join(ROOT, "attempts", "A189-noroom", "results", "certs",
                    "step34_regression.json")
OUT = os.path.join(HERE, "noroom_c0_Y1033.svg")
COL = ["#e53935", "#8e24aa", "#3949ab", "#00897b", "#f4511e", "#6d4c41",
       "#1e88e5", "#43a047", "#fdd835", "#d81b60"]


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, t, size=11, col="#222", bold=False, anchor="start"):
    b = ' font-weight="bold"' if bold else ""
    return ('<text x="%.1f" y="%.1f" font-size="%s" fill="%s" text-anchor="%s"%s>%s</text>'
            % (x, y, size, col, anchor, b, esc(t)))


def sq(cx, cy, th):
    c, s_ = math.cos(th), math.sin(th)
    return [(cx + 0.5 * (dx * c - dy * s_), cy + 0.5 * (dx * s_ + dy * c))
            for dx, dy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]


def frame(ox, oy, s0, title, note):
    out = [text(ox, oy - s0 * S - 30, title, 13, bold=True)]
    for i, ln in enumerate(note):
        out.append(text(ox, oy - s0 * S - 16 + 12 * i, ln, 9.5, "#444"))
    out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fff" stroke="#000" '
               'stroke-width="2"/>' % (ox, oy - s0 * S, s0 * S, s0 * S))
    return out


def main():
    cert = json.load(open(CERT, encoding="utf-8"))
    roles = NR.STEP34
    nd, bud = NR.build_node(roles, name="step34")
    s0 = float(nd.s)
    pieces, bc = NR.bisect_free(nd, bud)
    pk = cert["pockets"][0]
    lane = cert["lanes"][0]

    # the union (over tilt) of the surviving centre rects, and the pieces dropped at the LAST level
    open_rects = sorted({(float(r[0]), float(r[1]), float(r[2]), float(r[3])) for _, r in pieces})
    W = int(3 * s0 * S + 4 * 60)
    H = int(s0 * S + 190)
    oy = H - 40
    P = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">'
         % (W, H, W, H),
         '<rect width="%d" height="%d" fill="#fafafa"/>' % (W, H),
         '<defs><pattern id="hatch" width="6" height="6" patternTransform="rotate(45)" '
         'patternUnits="userSpaceOnUse"><line x1="0" y1="0" x2="0" y2="6" stroke="#9e9e9e" '
         'stroke-width="1.6"/></pattern></defs>',
         text(60, 26, "A189 -- the NO-ROOM leaf on c0_Y1033's STEP 34 node "
                      "(A182 recorded it UNDECIDED; it is DEAD by geometry, no LP)", 15, bold=True),
         text(60, 44, "Node: " + NR.STEP34_LABEL, 10, "#555"),
         text(60, 58, "Leaf [T]: with k = 10 roles boxed, the 11th unit square must lie in the "
                      "container with its interior clear of every K'; sum over the residue pockets "
                      "of LANE = %s < 1, so no such square exists." % cert["bound"], 10, "#555")]

    # ---- panel 1: the node ------------------------------------------------
    ox = 60
    P += frame(ox, oy, s0, "(1) the node: ten boxed roles, K' filled",
               ["K'(role) lies inside EVERY pose of that role (A132), so the 11th square's "
                "interior must miss all ten.",
                "thin outlines = a sample of the role's own poses; the five pins are axis-aligned "
                "unit squares."])
    for i, k in enumerate(nd.names):
        mb = nd.boxes[k]
        b = mb.ubox
        for (cx, cy, th) in [(float(b.x0), float(b.y0), 0.0), (float(b.x1), float(b.y1), 0.0)]:
            pts = " ".join("%.1f,%.1f" % (ox + x * S, oy - y * S) for x, y in sq(cx, cy, th))
            P.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="0.7" '
                     'stroke-opacity="0.5"/>' % (pts, COL[i % len(COL)]))
        V = [(float(x), float(y)) for x, y in mb.pc.verts] if len(mb.pc.verts) else []
        if len(V) >= 3:
            pts = " ".join("%.1f,%.1f" % (ox + x * S, oy - y * S) for x, y in V)
            P.append('<polygon points="%s" fill="%s" fill-opacity="0.55" stroke="%s" '
                     'stroke-width="1.2"/>' % (pts, COL[i % len(COL)], COL[i % len(COL)]))
            cx = sum(x for x, _ in V) / len(V); cy = sum(y for _, y in V) / len(V)
            P.append(text(ox + cx * S, oy - cy * S + 4, k, 10, "#fff", bold=True, anchor="middle"))
    P.append(text(ox, oy + 18, "s = %.6f; ten K' drawn, total area %.4f" %
                  (s0, sum(float(nd.boxes[k].pc.area()) for k in nd.names)), 9.5, "#444"))

    # ---- panel 2: the bisection -------------------------------------------
    ox = 60 + s0 * S + 60
    P += frame(ox, oy, s0, "(2) certificate 1: the exact bisection",
               ["centre domain [1/2, s-1/2]^2 of the 11th square, %d levels, %d t-sub-bins; every "
                "HATCHED piece is certified" % (bc["depth"], bud["tsub"]),
                "'every pose in it meets some core' by multibox's exact dead test -- %.4f %% of the "
                "root (centre x tilt) volume." % (100 * bc["dropped_fraction"])])
    P.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="url(#hatch)" '
             'stroke="#616161" stroke-width="1" stroke-dasharray="3,3"/>'
             % (ox + 0.5 * S, oy - (s0 - 0.5) * S, (s0 - 1) * S, (s0 - 1) * S))
    for (x0, x1, y0, y1) in open_rects:
        P.append('<rect x="%.1f" y="%.1f" width="%.2f" height="%.2f" fill="#ffb300" '
                 'fill-opacity="0.9" stroke="none"/>'
                 % (ox + x0 * S, oy - y1 * S, max(0.6, (x1 - x0) * S), max(0.6, (y1 - y0) * S)))
    P.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#e65100" '
             'stroke-width="2"/>' % (ox + pk[0] * S, oy - pk[3] * S,
                                     (pk[1] - pk[0]) * S, (pk[3] - pk[2]) * S))
    P.append(text(ox + pk[0] * S - 6, oy - pk[3] * S - 6, "pocket", 10, "#e65100", bold=True,
                  anchor="end"))
    P.append(text(ox, oy + 18, "open residue: %d pieces, centre x tilt volume %.6f of %.4f; one "
                  "connected pocket [%.3f, %.3f] x [%.3f, %.3f] (margin %.4f)"
                  % (bc["n_open"], bc["open_volume"], bc["root_volume"], pk[0], pk[1], pk[2], pk[3],
                     bud["margin"]), 9.5, "#444"))
    P.append(text(ox, oy + 31, "the right-wall slot between F1 and H: K'(F1) reaches y 1.873 and "
                  "K'(H) starts at y 1.870, a graze no piece representation can pin -- which is why "
                  "the bisection alone does not finish.", 9.5, "#444"))

    # ---- panel 3: the lane cover ------------------------------------------
    ox = 60 + 2 * (s0 * S + 60)
    P += frame(ox, oy, s0, "(3) certificate 2: the exact lane cover on the pocket",
               ["A141/A161's lane cover restricted to the node's cores: LANE(pocket) = %s "
                "(ok=%s, depth %s, %s leaves, %s s)."
                % (lane["lane"], lane.get("ok"), lane.get("depth"), lane.get("n_leaves"),
                   lane.get("seconds")),
                "A square whose centre lies in the closed pocket MEETS the pocket's interior, so "
                "LANE = 0 leaves the 11th square nowhere to be."])
    for i, k in enumerate(nd.names):
        V = [(float(x), float(y)) for x, y in nd.boxes[k].pc.verts]
        if len(V) >= 3:
            pts = " ".join("%.1f,%.1f" % (ox + x * S, oy - y * S) for x, y in V)
            P.append('<polygon points="%s" fill="#bdbdbd" fill-opacity="0.55" stroke="#757575" '
                     'stroke-width="1"/>' % pts)
    P.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#e65100" '
             'fill-opacity="0.30" stroke="#e65100" stroke-width="2"/>'
             % (ox + pk[0] * S, oy - pk[3] * S, (pk[1] - pk[0]) * S, (pk[3] - pk[2]) * S))
    cx, cy = 0.5 * (pk[0] + pk[1]), 0.5 * (pk[2] + pk[3])
    for th in (0.0, math.pi / 8, math.pi / 4):
        pts = " ".join("%.1f,%.1f" % (ox + x * S, oy - y * S) for x, y in sq(cx, cy, th))
        P.append('<polygon points="%s" fill="none" stroke="#e65100" stroke-width="1" '
                 'stroke-dasharray="5,4" stroke-opacity="0.8"/>' % pts)
    P.append(text(ox + cx * S, oy - cy * S - 4, "no pose fits", 10, "#bf360c", bold=True,
                  anchor="middle"))
    P.append(text(ox, oy + 18, "verdict %s: sum of pocket LANE = %s < %d free square(s); the node "
                  "dies with no LP and no certificate file to verify."
                  % (cert["verdict"], cert["bound"], cert["m"]), 9.5, "#444"))
    P.append(text(ox, oy + 31, "dashed outlines: three tilts of a unit square centred in the "
                  "pocket, each meeting a core -- the lane cover proves it for ALL of them.",
                  9.5, "#444"))

    P.append("</svg>")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(P))
    print("wrote", OUT, "(%d bytes)" % os.path.getsize(OUT))
    print("panel 2: %d open rects, dropped fraction %.6f" % (len(open_rects),
                                                             bc["dropped_fraction"]))


if __name__ == "__main__":
    main()
