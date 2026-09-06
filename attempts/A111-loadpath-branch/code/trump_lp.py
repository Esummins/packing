"""A111 canary / T1 finding: how far is each shadow's LOAD PATH from Trump's, and does any YES
region of the branch contain Trump?

Two different questions, kept apart:

  (1) PROXIMITY of the load paths.  For each shadow and each element of D4, the best injection of
      the shadow's box squares into Trump's eleven squares (max centre distance in the inf-norm,
      then max tilt deviation).  The smallest (r, rho) at which the boxes alone contain a Trump
      image is r_T = max_i |c_i - c^T_{sigma(i)}|_inf, rho_T = max_i |theta_i - theta^T_{sigma(i)}|.

  (2) THE CANARY.  A YES leaf's hypothesis is "the class pins + one square in every box", so Trump
      endangers it only if some D4 image of Trump satisfies BOTH: a square within the class's slack
      pin box (half-width delta/sqrt2, delta = 1e-2, tilt exactly 0 -- A57's pin cores) of every
      pin, AND a square in every F_i, all distinct.  That is the test run here.

All poses are exact (A108's Q(sqrt2) S07, the gallery's S02, A03's Trump); the drawn overlay is
geometry-checked (worst pairwise SAT gap and worst wall gap printed on the figure).
"""
from __future__ import annotations

import itertools, json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a111lib as L
import t1_yes as T1

OUT = os.path.join(L.RES, "trump_loadpath.json")
PIN_TILT_TOL = 1e-9          # A57 pin boxes are th0 = th1 = 0


def trump():
    p = os.path.join(L.ROOT, "attempts", "A03-upper-reconstruct", "trump11_float.json")
    return json.load(open(p))["X"]


def tilt_dev(a_deg, b_deg):
    d = abs(a_deg - b_deg) % 90.0
    return min(d, 90.0 - d)


def best_match(box_names, cbn, P):
    best = None
    for perm in itertools.permutations(range(len(P)), len(box_names)):
        rmax = tmax = 0.0
        pairs = []
        for n, j in zip(box_names, perm):
            x, y, t = cbn[n]
            X, Y, T = P[j]
            r = max(abs(X - x), abs(Y - y))
            dt = tilt_dev(math.degrees(t) % 90.0, math.degrees(T) % 90.0)
            rmax = max(rmax, r); tmax = max(tmax, dt)
            pairs.append(dict(box=n, trump=j, dx=round(X - x, 6), dy=round(Y - y, 6),
                              dtheta_deg=round(dt, 4)))
        key = (max(rmax, tmax / 90.0), rmax, tmax)
        if best is None or key < best[0]:
            best = (key, rmax, tmax, pairs, list(perm))
    return best


def canary(tag, cls, variant, r, rho, slack=T1.PIN_SLACK):
    """Does some D4 image of Trump satisfy the class pins AND every box?"""
    pn = T1.CLASS_PINS[cls]
    ext = T1.anchors(tag, pn) if variant == "lpa" else ()
    s, names, cfg, slots, free, box_names, B = T1.make_boxes(tag, r, rho, extra=ext)
    X = trump()
    hits = []
    for op, f in L.d4_ops(L.SHAT).items():
        P = [f(x, y, t) for (x, y, t) in X]
        # which square can serve each pin (tilt must be 0 mod 90 and the centre inside the pin box)
        need = {}
        ok = True
        for p in pn:
            ax, ay = T1.slot_affine(p)
            px = ax[0] + ax[1] * L.SHAT
            py = ay[0] + ay[1] * L.SHAT
            cand = [j for j, (x, y, t) in enumerate(P)
                    if abs(x - px) <= slack and abs(y - py) <= slack
                    and min((math.degrees(t) % 90.0), 90.0 - (math.degrees(t) % 90.0)) <= 1e-6]
            if not cand:
                ok = False; break
            need["pin:" + p] = cand
        if not ok:
            continue
        for n in box_names:
            b = B[n]
            cand = []
            for j, (x, y, t) in enumerate(P):
                td = math.degrees(t) % 90.0
                if (b["x0"] <= x <= b["x1"] and b["y0"] <= y <= b["y1"]
                        and any(b["th0"] <= td + o <= b["th1"] for o in (-90.0, 0.0, 90.0))):
                    cand.append(j)
            if not cand:
                ok = False; break
            need["box:" + n] = cand
        if not ok:
            continue
        keys = list(need)
        for perm in itertools.permutations(range(len(P)), len(keys)):
            if all(perm[i] in need[keys[i]] for i in range(len(keys))):
                hits.append(dict(op=op, assign=dict(zip(keys, perm))))
                break
    return dict(shadow=tag, cls=cls, variant=variant, r=r, rho=rho, boxes=box_names,
                contains_trump=bool(hits), hits=hits)


def proximity(tag, cls, variant):
    pn = T1.CLASS_PINS[cls]
    ext = T1.anchors(tag, pn) if variant == "lpa" else ()
    s, names, cfg, slots, free, box_names, B = T1.make_boxes(tag, 0.0, 0.0, extra=ext)
    cbn = {n: cfg[names.index(n)] for n in box_names}
    X = trump()
    rows = []
    for op, f in L.d4_ops(L.SHAT).items():
        P = [f(x, y, t) for (x, y, t) in X]
        key, rmax, tmax, pairs, perm = best_match(box_names, cbn, P)
        rows.append(dict(op=op, r_T=round(rmax, 6), rho_T=round(tmax, 4), pairs=pairs))
    rows.sort(key=lambda d: (d["r_T"], d["rho_T"]))
    return dict(shadow=tag, cls=cls, variant=variant, boxes=box_names, shadow_side=s,
                best=rows[0], all_ops=rows)


def svg(prox02):
    s, names, cfg, slots, free, lp, B = T1.make_boxes("S02", 0.0, 0.0)
    op = prox02["best"]["op"]
    f = L.d4_ops(L.SHAT)[op]
    P = [f(x, y, t) for (x, y, t) in trump()]
    wp = min(L.sat_gap(P[i][:2], P[i][2], P[j][:2], P[j][2])
             for i in range(11) for j in range(i + 1, 11))
    ww = min(min(L.wall_gaps(q[0], q[1], q[2], L.SHAT).values()) for q in P)
    wp2, ww2 = L.worst_gap(s, cfg)
    sc, ox, oy, W, H = 150.0, 40.0, 40.0, 700, 700

    def Q(x, y, side):
        return ox + sc * x, oy + sc * (side - y)
    body = ['<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#000" '
            'stroke-width="1.5"/>' % (ox, oy, sc * s, sc * s)]
    for i, (x, y, t) in enumerate(cfg):
        pts = " ".join("%.1f,%.1f" % Q(a, b, s) for a, b in L.corners(x, y, t))
        col = "#c33" if names[i] in ("f1", "f2", "f3") else ("#999" if names[i] == "f0" else "#36c")
        body.append('<polygon points="%s" fill="%s" fill-opacity="0.30" stroke="%s" '
                    'stroke-width="1.2"/>' % (pts, col, col))
        body.append('<text x="%.1f" y="%.1f" font-size="10" text-anchor="middle">%s</text>'
                    % (Q(x, y, s)[0], Q(x, y, s)[1], names[i]))
    for (x, y, t) in P:
        pts = " ".join("%.1f,%.1f" % Q(a, b, L.SHAT) for a, b in L.corners(x, y, t))
        body.append('<polygon points="%s" fill="none" stroke="#080" stroke-width="1.3" '
                    'stroke-dasharray="5,3"/>' % pts)
    lines = [
        "A111 T1: S02's load path IS Trump's load path (D4 element %s). Solid = S02 at side "
        "%.6f (red f1 f2 f3 = load-bearing, grey f0 = strut, blue = slot squares)." % (op, s),
        "Dashed = Trump at s-hat = %.6f under %s. The three matched centres differ by <= %.4f "
        "(inf-norm) and the tilts by %.3f deg (48.4351 vs 90 - 40.1819 = 49.8181)."
        % (L.SHAT, op, prox02["best"]["r_T"], prox02["best"]["rho_T"]),
        "So boxes of radius (r >= %.4f, rho >= %.3f deg) on the load path alone hold a Trump image: "
        "the branch cannot be about the load path." % (prox02["best"]["r_T"], prox02["best"]["rho_T"]),
        "What separates the two grains is the SLOT skeleton -- S02 carries BR(0,1) and TL(0,0), "
        "this Trump image carries BL(2,0) and TR(0,0) instead -- and the class pins.",
        "Geometry check: S02 worst pair SAT %.1e / worst wall %.1e; Trump image %.1e / %.1e."
        % (wp2, ww2, wp, ww)]
    for i, t in enumerate(lines):
        body.append('<text x="%.1f" y="%.1f" font-size="11">%s</text>'
                    % (ox, oy + sc * s + 16 + 15 * i, t))
    out = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">'
           '<rect width="100%%" height="100%%" fill="#fff"/>%s</svg>' % (W, H, W, H, "".join(body)))
    p = os.path.join(L.RES, "s02_is_trump.svg")
    open(p, "w", encoding="utf-8").write(out)
    return dict(path=os.path.relpath(p, L.ROOT).replace("\\", "/"),
                trump_worst_pair=wp, trump_worst_wall=ww,
                s02_worst_pair=wp2, s02_worst_wall=ww2)


def main():
    prox, cans = [], []
    for tag, cls in (("S02", "k5_11"), ("S02", "k5_16"), ("S07", "trump5")):
        for variant in ("lp", "lpa"):
            pr = proximity(tag, cls, variant)
            prox.append(pr)
            print("PROX %s/%s/%s boxes=%s -> op=%s r_T=%.5f rho_T=%.4f deg"
                  % (tag, cls, variant, pr["boxes"], pr["best"]["op"], pr["best"]["r_T"],
                     pr["best"]["rho_T"]), flush=True)
            for (r, rho) in ((0.02, 2.0), (0.05, 5.0), (0.1, 10.0), (0.2, 20.0)):
                c = canary(tag, cls, variant, r, rho)
                cans.append(c)
                print("  CANARY %s/%s/%s r=%.2f rho=%4.1f  Trump satisfies pins+boxes: %s %s"
                      % (tag, cls, variant, r, rho, c["contains_trump"],
                         [h["op"] for h in c["hits"]]), flush=True)
    fig = svg(prox[0])
    print("figure:", fig, flush=True)
    json.dump(dict(proximity=prox, canaries=cans, figure=fig), open(OUT, "w"), indent=1)


if __name__ == "__main__":
    main()
