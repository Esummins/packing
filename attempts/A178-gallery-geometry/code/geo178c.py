"""A178 -- the SHARP corner requirement when H may itself be a corner meeter (forced_corners.md
section 5(h)): the two-meeter requirement at an unpinned forced corner as a case split, each case
a multibox node, the corner DEAD iff every case dies.

  (two-free)  H is not a meeter: two free meeters in distinct Lemma A2 cells, both lonely-clipped
              (the six cases of geo178's corner step).
  (H-meets)   H is a meeter and one free meeter T (lonely-clipped) exists.  "H is a meeter" is
              consumed through a COVER of H's box: the box is cut into nx x ny x nt sub-boxes, a
              sub-box that provably misses the widened corner box (A161's exact test) is dropped,
              and every other sub-box is one case {pins, H = sub-box, T in the corner window}.  A
              sub-box is a superset of its meeting poses, so each case over-approximates and the
              union of cases covers the H-meets branch [T].  What the cover buys: a localised H
              has a LARGER K' (an intersection over fewer poses), which clips T harder -- and T's
              survivors, once localised, get a non-empty K' that clips H back (the cascade the
              whole-box role never starts, notes/c0_Y1033.md).
"""
import time

import geo178 as G


def _split_box(b, nx, ny, nt):
    out = []
    for a in range(nx):
        for c in range(ny):
            for t in range(nt):
                out.append((b[0] + (b[1] - b[0]) * a / nx, b[0] + (b[1] - b[0]) * (a + 1) / nx,
                            b[2] + (b[3] - b[2]) * c / ny, b[2] + (b[3] - b[2]) * (c + 1) / ny,
                            b[4] + (b[5] - b[4]) * t / nt, b[4] + (b[5] - b[4]) * (t + 1) / nt))
    return out


def corner_sharp(pinroles, hnames, hull, item, nsub=4, refine=2, log=print, label="", grid=(3, 3, 2)):
    """-> dict(alive, subcases, h_hull_union, seconds, leaf)."""
    t0 = time.time()
    sub, alive_hulls = [], []
    # ---- (two-free): the six Lemma A2 cell pairs, both roles lonely-clipped
    n_alive_pairs = 0
    for sp in G.A2_PAIRS:
        rb = G.role_boxes_for(item, sp)
        roles = dict(pinroles)
        for k in hnames:
            roles[k] = tuple(hull[k])
        roles.update(rb)
        nd, info = G.run_node(roles, corners={k: item["corner"] for k in rb}, nsub=nsub, refine=refine,
                              label=label + "/sharp:" + item["cell"] + ":two-free:%s+%s" % sp)
        sub.append(dict(case="two-free:%s+%s" % sp, dead=info.get("dead"), kept=info.get("kept"),
                        k_area=info.get("k_area"), seconds=info["seconds"]))
        if not info["dead"]:
            n_alive_pairs += 1
            alive_hulls.append({k: G.hull_of(nd, k) for k in hnames})
    # ---- (H-meets): a cover of H's box, one case per sub-box that may meet the corner box
    hk = hnames[0]                       # the sharp test covers the FIRST H; other H roles ride along
    subs = _split_box(hull[hk], *grid)
    n_cases, n_alive_H, n_dropped = 0, 0, 0
    rb = G.role_boxes_for(item, None)
    for sb in subs:
        roles = dict(pinroles)
        for k in hnames:
            roles[k] = tuple(hull[k])
        roles[hk] = sb
        roles.update(rb)
        # drop the sub-box if it provably misses the widened corner box (exact test on the box)
        nd0 = G.MB.Node({hk: sb})
        m = nd0.misses_cell(tuple(item["wbox"]))
        if m[hk]["misses"]:
            n_dropped += 1
            continue
        n_cases += 1
        nd, info = G.run_node(roles, corners={k: item["corner"] for k in rb}, nsub=nsub, refine=refine,
                              label=label + "/sharp:" + item["cell"] + ":H-meets:%d" % n_cases)
        if not info["dead"]:
            n_alive_H += 1
            alive_hulls.append({k: G.hull_of(nd, k) for k in hnames})
    sub.append(dict(case="H-meets", n_sub=len(subs), n_dropped=n_dropped, n_cases=n_cases, n_alive=n_alive_H))
    alive = n_alive_pairs > 0 or n_alive_H > 0
    log("      sharp %s: two-free %d/6 alive; H-meets %d of %d sub-boxes may meet, %d alive -> %s" % (
        item["cell"], n_alive_pairs, n_cases, len(subs), n_alive_H, "ALIVE" if alive else "DEAD"))
    hu = None
    if alive_hulls:
        hu = {}
        for k in hnames:
            hs = [h[k] for h in alive_hulls]
            hu[k] = [min(h[0] for h in hs), max(h[1] for h in hs), min(h[2] for h in hs), max(h[3] for h in hs),
                     min(h[4] for h in hs), max(h[5] for h in hs)]
    return dict(alive=alive, subcases=sub, h_hull_union=hu, seconds=round(time.time() - t0, 1),
                leaf=None if alive else "sharp corner requirement at %s: no A2 pair and no H-meets sub-box survives" % item["cell"])
