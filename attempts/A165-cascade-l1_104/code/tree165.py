"""A165 -- assemble the CASE TREE record `results/cascade165.jsonl`.

One line per case of the tree.  Every line carries

  node      the case id, e.g. `l1_104/C2/TR(17,42)`
  level     0 root, 1 one corner conditioned, 2 two corners conditioned
  roles     the named squares of the case and their boxes
  forced_by the leaf + certificate that forces the case to exist (or to be branched)
  verdict   ALIVE | DEAD(C, <leaf>) | DEAD(LP) | DEAD(LP, certificate pending) | UNDECIDED
  evidence  the numbers behind the verdict

and, for the TR cases, a CLASSIFICATION of the two meeters against the PI's reading of step (a)
("a deep meeter up-right of H and a shallow meeter up-left of H along the top wall").

    python code/tree165.py --cell l1_104 --depth 8
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cas165 as K                                               # noqa: E402
import cascade165 as CS                                          # noqa: E402
import guardline as GL                                           # noqa: E402
from caselp import Box                                           # noqa: E402


def classify(b, corner):
    """Where in the corner's approach does this cover box sit, and how deep can it reach?

    `side`  TOP / RIGHT (BOTTOM / LEFT at the lower corners) / DIAGONAL, by the sign of the
            mid-centre offset along the corner diagonal.
    `depth` the largest penetration of the square into the widened corner cell over the box,
            measured along the cell's two normals (an UPPER bound: mid-box + h_max).
    `band_top` / `band_right`  whether the box's certified minchord on the wall line
            y (resp. x) = s0 - 1 - w is >= 1 -- the PI's "carries a chord >= 1".
    """
    X0, X1, Y0, Y1 = K.corner_cell(corner)
    mx, my = 0.5 * (b.x0 + b.x1), 0.5 * (b.y0 + b.y1)
    hmax = 0.5 * max(abs(math.cos(math.radians(t))) + abs(math.sin(math.radians(t)))
                     for t in (b.th0, 45.0 if b.th0 <= 45.0 <= b.th1 else b.th0, b.th1))
    if corner == "TR":
        du, dv = (b.x1 + hmax) - X0, (b.y1 + hmax) - Y0          # depth past the cell's x0 / y0
        a1, a2 = K.S0 - mx, K.S0 - my                            # distance to the right / top wall
        side = "TOP" if a2 < a1 - 0.05 else ("RIGHT" if a1 < a2 - 0.05 else "DIAG")
    elif corner == "TL":
        du, dv = X1 - (b.x0 - hmax), (b.y1 + hmax) - Y0
        a1, a2 = mx, K.S0 - my
        side = "TOP" if a2 < a1 - 0.05 else ("LEFT" if a1 < a2 - 0.05 else "DIAG")
    elif corner == "BL":
        du, dv = X1 - (b.x0 - hmax), Y1 - (b.y0 - hmax)
        a1, a2 = mx, my
        side = "BOTTOM" if a2 < a1 - 0.05 else ("LEFT" if a1 < a2 - 0.05 else "DIAG")
    else:                                                         # BR
        du, dv = (b.x1 + hmax) - X0, Y1 - (b.y0 - hmax)
        a1, a2 = K.S0 - mx, my
        side = "BOTTOM" if a2 < a1 - 0.05 else ("RIGHT" if a1 < a2 - 0.05 else "DIAG")
    yline = GL.Line("h", CS.Fr(int(round((K.S0 - 1.0 - K.W0) * 100000)), 100000))
    xline = GL.Line("v", CS.Fr(int(round((K.S0 - 1.0 - K.W0) * 100000)), 100000))
    return dict(side=side, depth_x=round(du, 4), depth_y=round(dv, 4),
                mid=[round(mx, 4), round(my, 4)], tilt=[b.th0, b.th1],
                band_top=bool(GL.minchord_box(b, yline)["lo"] >= 1),
                band_right=bool(GL.minchord_box(b, xline)["lo"] >= 1),
                minchord_top=round(GL.minchord_box(b, yline)["lo_float"], 4),
                minchord_right=round(GL.minchord_box(b, xline)["lo_float"], 4))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", default="l1_104")
    ap.add_argument("--depth", type=int, default=8)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    cov = json.load(open(CS.cover_path(a.cell, a.depth), encoding="utf-8"))
    H = Box(*cov["boxes"][0])
    OB = {c: [Box(*b) for b in cov["covers"][c]["open"]] for c in K.CORNERS}
    PR = {}
    for c in K.CORNERS:
        p = CS.pairs_path(a.cell, a.depth, c)
        PR[c] = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None
    rp = None
    p = os.path.join(CS.RES, "rowprod_%s.json" % CS.tag(a.cell, a.depth))
    if os.path.exists(p):
        rp = json.load(open(p, encoding="utf-8"))
    geom, lp = {}, {}
    p = CS.geom_path(a.cell, a.depth, "TR")
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8"):
            d = json.loads(ln)
            geom[tuple(d["pair"])] = d
    p = os.path.join(CS.RES, "lp3_%s_TR.jsonl" % CS.tag(a.cell, a.depth))
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8"):
            d = json.loads(ln)
            lp[tuple(d["pair"])] = d

    out = a.out or os.path.join(CS.RES, "cascade165.jsonl")
    fh = open(out, "a", encoding="utf-8")
    n = 0

    def emit(rec):
        nonlocal n
        rec["cell"] = a.cell
        rec["depth0"] = a.depth
        fh.write(json.dumps(rec, default=str) + "\n")
        n += 1

    # ---- C0 the root
    emit(dict(node="%s/C0" % a.cell, level=0,
              roles=dict(H=K.bx_json(H)),
              forced_by=["A115 record %s (tau = budget, converged)" % a.cell],
              verdict="ALIVE",
              evidence=dict(tau=cov["tau"], budget=cov["budget"],
                            s0=K.S0, w=cov["w"], r6_gap=cov["r6_gap"])))

    # ---- C1 the structural facts
    emit(dict(node="%s/C1-structure" % a.cell, level=0, roles=dict(H=K.bx_json(H)),
              forced_by=["k0_route.md sec 3 Lemma K0-FREE (teleport) + sec 4.2 K0-BLOCKED",
                         "k0_route.md sec 4.1 Lemma K0-WIDEN (pad w)",
                         "A150 notes/composition.md (R6): s0 - 2(1+w) - sqrt2 > 0",
                         "A161 chordlane.box_misses_cell_exact  ->  M(c)"],
              verdict="ALIVE",
              evidence=dict(M_exact={c: cov["M_exact"][c]["misses"] for c in K.CORNERS},
                            M_a141={c: cov["M"][c]["excluded"] for c in K.CORNERS},
                            n_corner_meeters=8,
                            H_is_a_meeter=[c for c in K.CORNERS
                                           if not cov["M_exact"][c]["misses"]],
                            free_squares_left=(11 - 1 - 8 if all(
                                cov["M_exact"][c]["misses"] for c in K.CORNERS) else None),
                            covers={c: cov["covers"][c]["n_open"] for c in K.CORNERS})))

    # ---- C2 the TR cases
    if PR["TR"]:
        cls = [classify(b, "TR") for b in OB["TR"]]
        pairs = [tuple(q) for q in PR["TR"]["pairs"]]
        emit(dict(node="%s/C2-TR-branching" % a.cell, level=1, roles={},
                  forced_by=["A141 polylane.lane_cover (complete prefix-code cover)",
                             "A118 sec 1.2(ii) always-overlap pair prune",
                             "A141 sec 3/sec 5 shared-rational-point (same square) prune"],
                  verdict="BRANCH",
                  evidence=dict(n_cover=len(OB["TR"]), n_pairs_raw=PR["TR"]["n_pairs_raw"],
                                n_after_ovl=PR["TR"]["n_after_ovl"],
                                n_same_square=PR["TR"]["n_same_square"],
                                n_cases=len(pairs),
                                sides={s: sum(1 for c in cls if c["side"] == s)
                                       for s in ("TOP", "RIGHT", "DIAG")},
                                band_top_boxes=sum(1 for c in cls if c["band_top"]),
                                band_right_boxes=sum(1 for c in cls if c["band_right"]),
                                pair_side_classes={
                                    k: v for k, v in sorted(
                                        _count(("%s+%s" % tuple(sorted((cls[i]["side"],
                                                                        cls[j]["side"]))))
                                               for i, j in pairs).items(),
                                        key=lambda kv: -kv[1])},
                                pair_band_classes={
                                    k: v for k, v in sorted(
                                        _count(("%d band-top of 2" %
                                                (int(cls[i]["band_top"]) + int(cls[j]["band_top"])))
                                               for i, j in pairs).items(),
                                        key=lambda kv: -kv[1])})))
        for (i, j) in pairs:
            gg = geom.get((i, j))
            lprec = lp.get((i, j))
            verdict, ev = "UNDECIDED", {}
            if gg and gg.get("row_kill"):
                verdict = "DEAD(C, chord row A144 LINE-1)"
            elif gg and gg.get("area_kill"):
                verdict = "DEAD(C, uncoverable area A164/A89 Lemma ID)"
            elif lprec:
                if lprec.get("kills_converged"):
                    verdict = ("DEAD(LP)" if lprec.get("certified") == "PASS"
                               else "DEAD(LP, certificate pending)")
                elif lprec.get("kills"):
                    verdict = "LP-dead unconverged (kill candidate)"
                else:
                    verdict = "ALIVE(LP)"
                ev = dict(tau=lprec.get("tau"), eta=lprec.get("eta"),
                          converged=lprec.get("converged"), certified=lprec.get("certified"),
                          wall_s=lprec.get("wall_s"))
            if gg:
                ev.update(row_min_rhs=gg["row_min_rhs"], rows={k: v["rhs_f"]
                                                              for k, v in gg["rows"].items()},
                          area_U=gg.get("area_U"), B0=CS.B0)
            emit(dict(node="%s/C2/TR(%d,%d)" % (a.cell, i, j), level=1,
                      roles=dict(H=K.bx_json(H), TR_a=K.bx_json(OB["TR"][i]),
                                 TR_b=K.bx_json(OB["TR"][j])),
                      budget=11 - 3,
                      forced_by=["K0-BLOCKED at TR with M(TR) = %s"
                                 % ("0 (A161 exact SAT)" if cov["M_exact"]["TR"]["misses"]
                                    else ">= 1"),
                                 "A141 cover box %d and %d" % (i, j)],
                      verdict=verdict, evidence=ev,
                      classify=dict(TR_a=cls[i], TR_b=cls[j])))

    # ---- C3 the four-wall chord-row product
    if rp:
        emit(dict(node="%s/C3-rowproduct" % a.cell, level=2, roles={},
                  forced_by=["A144 LINE-1/LINE-2 guard row on each of the four wall strips",
                             "(R6): the two crowds a wall sees are disjoint sets of squares"],
                  verdict="BRANCH",
                  evidence=dict(walls=rp["walls"], four_cycle=rp.get("four_cycle"),
                                n_cases=rp["n_cases"], nlines=rp["nlines"],
                                n_certs=len(rp.get("certs", [])))))
        for ct in rp.get("certs", []):
            emit(dict(node="%s/C3/%s-%s-%s" % (a.cell, ct["wall"], ct["case1"], ct["case2"]),
                      level=2,
                      roles=dict(boxes=ct["boxes"]),
                      budget=11 - len(ct["boxes"]),
                      forced_by=["A144 LINE-1 on the %s wall line %s" % (ct["wall"],
                                                                        ct["row"]["off"])],
                      verdict="DEAD(C, chord row A144 LINE-1)",
                      evidence=dict(row=ct["row"], exact_rhs_negative=ct["exact_rhs_negative"])))
    fh.close()
    print("wrote %d case lines -> %s" % (n, out), flush=True)


def _count(it):
    d = {}
    for v in it:
        d[v] = d.get(v, 0) + 1
    return d


if __name__ == "__main__":
    main()
