"""A178 -- the TWO-MEETER requirement at a forced SLOT as a leaf test (forced_corners.md FC-slot,
FC-count; the PI's "cascade from the BR01 two-meeter requirement").

At a forced slot p the page's F has two distinct NON-pin meeters of the widened box B_p+.  The
non-pin squares are H and the free squares, so exactly one of two cases holds and both are
tested as multibox nodes:

  (H-meets)  H is a meeter and ONE free square B meets B_p+:  node {pins, H restricted to the
             poses whose centre lies in the meeter window of p, B in the window}.  H restricted
             is a SUPERSET of the meeting poses (a meeter's centre is in the window), so the node
             is a sound over-approximation of the case; EmptyBox kills it.
  (two-free) H is not a meeter and TWO distinct free squares B, B' meet B_p+.  Their centres are
             at l_inf distance >= 1/sqrt2 (Lemma A1).  First {pins, H, B} is normalised; every
             free meeter's pose survives that clip, so B' lies in hull(B) too.  hull(B)'s centre
             rect is cut into cells of side < 1/sqrt2; two centres 1/sqrt2 apart cannot share a
             cell, so the case is the union over UNORDERED PAIRS of DISTINCT cells (i, j) of the
             nodes {pins, H, B in cell_i, B' in cell_j} (tilts free).  No pair alive = dead; a hull
             narrower than 1/sqrt2 in both directions has one cell and no pair: dead outright.

The slot is ALIVE iff some sub-case is alive.  The union hull of H over the alive sub-cases is a
sound replacement for H (every packing of the page falls in one sub-case).
"""
import math

import geo178 as G

SQ2H = 0.70710678118654757


def _cells(rect, side=0.70):
    """cut [x0,x1]x[y0,y1] into an nx x ny grid with cell sides <= `side` (< 1/sqrt2)."""
    x0, x1, y0, y1 = rect
    nx = max(1, int(math.ceil((x1 - x0) / side - 1e-12)))
    ny = max(1, int(math.ceil((y1 - y0) / side - 1e-12)))
    out = []
    for a in range(nx):
        for b in range(ny):
            out.append((x0 + (x1 - x0) * a / nx, x0 + (x1 - x0) * (a + 1) / nx,
                        y0 + (y1 - y0) * b / ny, y0 + (y1 - y0) * (b + 1) / ny))
    return out


def _restrict(box, win):
    """the box with its centre rect intersected with the window rect; None if empty."""
    x0, x1 = max(box[0], win[0]), min(box[1], win[1])
    y0, y1 = max(box[2], win[2]), min(box[3], win[3])
    if x0 > x1 or y0 > y1:
        return None
    return (x0, x1, y0, y1, box[4], box[5])


def slot_pair_test(pinroles, hnames, hull, item, nsub=4, refine=2, log=print, max_pairs=40, label="", max_cells=6):
    """-> dict(alive, subcases=[...], h_hull_union, seconds).  `hull` = {H: box} of the case."""
    import time
    t0 = time.time()
    tag = item["cell"].replace("(", "").replace(",", "").replace(")", "")
    W = item["window"]
    win_box = (W[0], W[1], W[2], W[3], 0.0, 90.0)
    sub = []
    alive_hulls = []
    # ---- 1. one free meeter with H free (the clip every case shares)
    roles = dict(pinroles)
    for k in hnames:
        roles[k] = tuple(hull[k])
    roles["B_" + tag] = win_box
    nd, info = G.run_node(roles, nsub=nsub, refine=refine, label=label + "/pair:" + item["cell"] + ":one-free")
    sub.append(dict(case="one-free", dead=info.get("dead"), kept=info.get("kept"), seconds=info["seconds"]))
    if info["dead"]:
        log("      %s one-free DEAD (%s)" % (item["cell"], info["dead"]))
        return dict(alive=False, subcases=sub, seconds=round(time.time() - t0, 1), leaf="one free meeter impossible")
    hb = G.hull_of(nd, "B_" + tag)
    # ---- 2. (H-meets): H restricted to the window, one free meeter
    hm_alive = False
    rolesH = dict(pinroles)
    ok = True
    for k in hnames:
        r = _restrict(hull[k], W)
        if r is None:
            ok = False
        else:
            rolesH[k] = r
    if ok:
        rolesH["B_" + tag] = (hb[0], hb[1], hb[2], hb[3], hb[4], hb[5])
        ndH, infoH = G.run_node(rolesH, nsub=nsub, refine=refine, label=label + "/pair:" + item["cell"] + ":H-meets")
        # H restricted must still be able to MEET the box: A161's exact miss test says no -> vacuous
        vac = (not infoH["dead"]) and G.h_misses(ndH, item["wbox"])
        sub.append(dict(case="H-meets", dead=infoH.get("dead"), vacuous=vac, kept=infoH.get("kept"),
                        seconds=infoH["seconds"]))
        if not infoH["dead"] and not vac:
            hm_alive = True
            alive_hulls.append({k: G.hull_of(ndH, k) for k in hnames})
    else:
        sub.append(dict(case="H-meets", dead=None, vacuous=True, reason="H box outside the window"))
    # ---- 3. (two-free): pairs of distinct cells of hull(B)
    cells = _cells((hb[0], hb[1], hb[2], hb[3]))
    pairs = [(i, j) for i in range(len(cells)) for j in range(i + 1, len(cells))]
    n_alive_pairs = 0
    if len(cells) > max_cells:
        # a wide hull (the free meeter is not squeezed): the pair test cannot kill cheaply; ALIVE
        sub.append(dict(case="two-free", n_cells=len(cells), n_pairs=len(pairs), skipped="hull too wide: ALIVE untested",
                        hull_B=hb[:4]))
        n_alive_pairs = -1
        pairs = []
    elif not pairs:
        sub.append(dict(case="two-free", n_cells=len(cells), n_pairs=0, dead="no pair of cells"))
    else:
        tested = 0
        for (i, j) in pairs:
            if tested >= max_pairs:
                sub.append(dict(case="two-free", note="pair budget exhausted: treated as ALIVE", n_pairs=len(pairs)))
                n_alive_pairs += 1
                break
            roles2 = dict(pinroles)
            for k in hnames:
                roles2[k] = tuple(hull[k])
            ci, cj = cells[i], cells[j]
            roles2["B_" + tag] = (ci[0], ci[1], ci[2], ci[3], hb[4], hb[5])
            roles2["B2_" + tag] = (cj[0], cj[1], cj[2], cj[3], hb[4], hb[5])
            nd2, info2 = G.run_node(roles2, nsub=nsub, refine=refine, label=label + "/pair:" + item["cell"] + ":two-free:%d+%d" % (i, j))
            tested += 1
            if not info2["dead"]:
                n_alive_pairs += 1
                alive_hulls.append({k: G.hull_of(nd2, k) for k in hnames})
        sub.append(dict(case="two-free", n_cells=len(cells), n_pairs=len(pairs), n_alive_pairs=n_alive_pairs,
                        hull_B=hb[:4]))
    alive = hm_alive or n_alive_pairs != 0
    log("      %s: one-free alive (B hull %.2fx%.2f), H-meets %s, two-free %d/%d pairs alive -> %s" % (
        item["cell"], hb[1] - hb[0], hb[3] - hb[2], "ALIVE" if hm_alive else "dead", n_alive_pairs, len(pairs),
        "ALIVE" if alive else "DEAD"))
    hu = None
    if alive_hulls:
        hu = {}
        for k in hnames:
            hs = [h[k] for h in alive_hulls]
            hu[k] = [min(h[0] for h in hs), max(h[1] for h in hs), min(h[2] for h in hs), max(h[3] for h in hs),
                     min(h[4] for h in hs), max(h[5] for h in hs)]
    return dict(alive=alive, subcases=sub, h_hull_union=hu, seconds=round(time.time() - t0, 1),
                leaf=None if alive else "two-meeter requirement at %s: H-meets dead, no free pair" % item["cell"])
