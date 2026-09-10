"""A199 -- the corner chain (seal199 part 2): run_corner / run_page.  Every step's test and result is recorded; the
certificate is the list.  Sound at every step (docs/proofs/corner_seal.md section 4)."""
import math
import time

import seal199 as S

SIDE = 0.70                                  # < 1/sqrt2: a closed cell of this side holds at most one centre (Lemma A1)


def _fbox(win, th=(0.0, 90.0)):
    return (float(win[0]) - 1e-9, float(win[1]) + 1e-9, float(win[2]) - 1e-9, float(win[3]) + 1e-9, th[0], th[1])


def _restrict(box, win):
    x0, x1 = max(box[0], float(win[0])), min(box[1], float(win[1]))
    y0, y1 = max(box[2], float(win[2])), min(box[3], float(win[3]))
    if x0 > x1 or y0 > y1:
        return None
    return (x0, x1, y0, y1, box[4], box[5])


def _cells(rect, side=SIDE):
    x0, x1, y0, y1 = rect
    nx = max(1, int(math.ceil((x1 - x0) / side - 1e-12)))
    ny = max(1, int(math.ceil((y1 - y0) / side - 1e-12)))
    return [(x0 + (x1 - x0) * a / nx, x0 + (x1 - x0) * (a + 1) / nx, y0 + (y1 - y0) * b / ny, y0 + (y1 - y0) * (b + 1) / ny)
            for a in range(nx) for b in range(ny)]


def further_cases(r2, hn, gh, boxA, winA, s, fine, max_pairs=40):
    """F provably misses A: A's two meeters are {H, G} or {G, G'} (F stays as an obstacle).  -> (alive, record)."""
    out = dict(HG=None, GG=None)
    # (HG): H restricted to A's meeter window, one free G
    rH = dict(r2)
    ok = True
    for k in hn:
        rr = _restrict(r2[k], winA)
        if rr is None:
            ok = False
        else:
            rH[k] = rr
    if ok:
        rH["G"] = tuple(gh)
        nd, info = S.run_node(rH, s, fine[0], fine[1])
        hm = (not info["dead"]) and all(S.pieces_miss(nd.boxes[k], boxA)[0] for k in hn)
        out["HG"] = dict(dead=info["dead"], H_misses_A=hm, seconds=info["seconds"])
        if not info["dead"] and not hm:
            return True, out
    else:
        out["HG"] = dict(vacuous="H box outside A's window")
    # (GG'): two free meeters in distinct Lemma-A1 cells of G's hull
    cells = _cells(tuple(gh[:4]))
    pairs = [(i, j) for i in range(len(cells)) for j in range(i + 1, len(cells))]
    alive = 0
    tested = 0
    for (i, j) in pairs:
        if tested >= max_pairs:
            out["GG"] = dict(n_cells=len(cells), n_pairs=len(pairs), note="pair budget exhausted: ALIVE untested")
            return True, out
        r3 = dict(r2)
        ci, cj = cells[i], cells[j]
        r3["G"] = (ci[0], ci[1], ci[2], ci[3], gh[4], gh[5])
        r3["G2"] = (cj[0], cj[1], cj[2], cj[3], gh[4], gh[5])
        nd, info = S.run_node(r3, s, fine[0], fine[1])
        tested += 1
        if not info["dead"]:
            alive += 1
            break
    out["GG"] = dict(n_cells=len(cells), n_pairs=len(pairs), tested=tested, alive=alive)
    return alive > 0, out


def run_corner(pg, corner, Bcell, Acell, s, lam, nsub=4, refine=2, depth=8, fine=(8, 4), log=print, grid=(2, 2, 2)):
    T0 = time.time()
    steps = []
    swap = Bcell.endswith("(1,0)")
    roles = S.page_roles(pg, s, lam)
    hn = [k for k in roles if k.startswith("H")]
    nd0, i0 = S.run_node(roles, s, nsub, refine)
    steps.append(dict(step="base", **i0))
    if i0["dead"]:
        return dict(verdict="DEAD", leaf="base node EmptyBox(%s)" % i0["dead"], steps=steps, seconds=round(time.time() - T0, 1))
    cB, iB, jB = S.cell_of(Bcell)
    cA, iA, jA = S.cell_of(Acell)
    boxB, boxA = S.cell_box(cB, iB, jB, s, lam), S.cell_box(cA, iA, jA, s, lam)
    winA = S.window(boxA, s)
    hB = all(S.pieces_miss(nd0.boxes[k], boxB)[0] for k in hn)
    t = time.time()
    obst = [nd0.boxes[k].obstacle("poly") for k in roles]
    pcs, frac, nt = S.reach(S.window(boxB, s), obst, boxB, s, depth, nsub)
    steps.append(dict(step="reach", cell=Bcell, n_pieces=len(pcs), vol_frac=round(frac, 6), n_tests=nt,
                      hull=S.hull(pcs) if pcs else None, H_misses_B=hB, seconds=round(time.time() - t, 1)))
    log("    %s/%s: reach %d pieces (vol %.4f) hull %s; H misses B: %s" % (
        corner, Bcell, len(pcs), frac, [round(v, 3) for v in S.hull(pcs)] if pcs else None, hB))
    if not pcs:
        return dict(verdict="DEAD", leaf="no free meeter of %s (Theorem FC needs one)" % Bcell, steps=steps, seconds=round(time.time() - T0, 1))
    ss = S.seal_summary(pcs, cB, s, swap)
    steps.append(dict(step="seal", cell=Bcell, **ss))
    log("    SEAL: q_y %s phi %s x_r<= %.4f deep-regime all %s (margin %.3f) chord>= %.3f" % (
        [round(v, 3) for v in ss["qy"]], [round(v, 1) for v in ss["phi"]], ss["xr_max"], ss["deep_all"], ss["deep_margin_min"], ss["chord_min"]))
    cases = []
    for sb in S.sub_boxes(pcs, *grid):
        t = time.time()
        r2 = dict(roles)
        r2["F"] = tuple(sb)
        nd1, i1 = S.run_node(r2, s, nsub, refine)
        case = dict(F_box=[round(v, 4) for v in sb], node=i1)
        if i1["dead"]:
            case["dead"] = "EmptyBox(%s) in {pins, H, F}" % i1["dead"]
            cases.append(case)
            log("      F %s: DEAD (%s)" % (case["F_box"], i1["dead"]))
            continue
        hA = all(S.pieces_miss(nd1.boxes[k], boxA)[0] for k in hn)
        fA = S.pieces_miss(nd1.boxes["F"], boxA)[0]
        case["H_misses_A"], case["F_misses_A"] = hA, fA
        r3 = dict(r2)
        for k in r2:
            r3[k] = tuple(i1["hull"][k]) if k in hn or k == "F" else r2[k]
        r3["G"] = _fbox(winA)
        nd2, i2 = S.run_node(r3, s, fine[0], fine[1])
        case["G_node"] = dict(dead=i2["dead"], seconds=i2["seconds"], hull_G=i2.get("hull", {}).get("G"), kept=i2.get("kept"))
        g_dead = bool(i2["dead"])
        if g_dead and (hA or fA):
            case["dead"] = "EmptyBox(G): no free meeter of %s besides F; %s" % (Acell, "H misses A" if hA else "F misses A")
        elif g_dead:
            case["dead"] = None
            case["open"] = "A's meeters would be {F, H}: both can meet A (not excluded)"
        elif fA:
            alive, rec = further_cases(r3, hn, i2["hull"]["G"], boxA, winA, s, fine)
            case["further"] = rec
            case["dead"] = None if alive else "F misses A; (HG) and (GG') cases all dead"
        else:
            case["dead"] = None
            case["open"] = "G survives and F can meet A: case {F, G} open"
        case["seconds"] = round(time.time() - t, 1)
        cases.append(case)
        log("      F %s: %s  [H misses A %s, F misses A %s, G %s] %.0fs" % (case["F_box"], "DEAD" if case["dead"] else "alive",
                                                                            hA, fA, "dead" if g_dead else "alive", case["seconds"]))
    steps.append(dict(step="cases", n=len(cases), n_dead=sum(1 for c in cases if c["dead"]), cases=cases))
    dead = all(c["dead"] for c in cases)
    return dict(verdict="DEAD" if dead else "ALIVE", leaf=("corner seal at %s: F (free meeter of %s) leaves %s without a second meeter"
                                                          % (corner, Bcell, Acell)) if dead else None,
                steps=steps, seconds=round(time.time() - T0, 1))


def run_page(page, s=None, lam=None, log=print, stop_first=True, **kw):
    s = S.S0 if s is None else s
    lam = S.Fr(1) if lam is None else lam
    pg = S.load_page(page)
    corners = S.seal_corners(pg)
    out = dict(page=page, cls=pg["cls"], record=pg["record"], s=float(s), lam=float(lam), pad0=float(S.pad(0, lam)),
               corners=[c for c in corners], runs=[], verdict="ALIVE" if corners else "N/A", kill=None)
    if not corners:
        out["leaf"] = "no pinned corner with both neighbours forced"
        return out
    T0 = time.time()
    for (c, B, A) in corners:
        log("  %s: corner %s, F meets %s, A = %s" % (page, c, B, A))
        r = run_corner(pg, c, B, A, s, lam, log=log, **kw)
        r["corner"], r["B"], r["A"] = c, B, A
        out["runs"].append(r)
        if r["verdict"] == "DEAD":
            out["verdict"], out["kill"], out["leaf"] = "DEAD", dict(corner=c, B=B, A=A), r["leaf"]
            if stop_first:
                break
    out["seconds"] = round(time.time() - T0, 1)
    return out
