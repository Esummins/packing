#!/usr/bin/env python3
"""A47 leg (a): collect work/sstar/*.result.json into results/sstar_lemma.json + a coverage audit.

Coverage audit: the PASSing parameter boxes must cover the whole declared domain
   y0 in [Y0_MIN, Y0_MAX],  b in [max(0, y0-1), y0].
The audit is done on the exact rational rectangle decomposition: it checks that the union of the
PASSing rectangles contains every rectangle of the reference grid (param_boxes at the finest step
occurring among the results), and names the uncovered part if not.
"""
import glob
import json
import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import sstar_geom as G  # noqa: E402

WORK = os.path.join(ROOT, "work", "sstar")


def load_all():
    recs = []
    for p in sorted(glob.glob(os.path.join(WORK, "*.result.json"))):
        with open(p) as fh:
            recs.append(json.load(fh))
    return recs


def rect(r):
    return tuple(F(x) for x in r["box"])


_AREA = {}


def obstacle_area(box):
    if box not in _AREA:
        try:
            ob = G.build_obstacle(box)
            _AREA[box] = float(sum(G.poly_area(ob[n]["verts"]) for n in G.PIECES))
        except Exception:
            _AREA[box] = None
    return _AREA[box]


def covered(sub, boxes):
    """is rectangle `sub` covered by the union of `boxes` (all axis-aligned, exact)?"""
    y0, y1, b0, b1 = sub
    for (a0, a1, c0, c1) in boxes:
        if a0 <= y0 and y1 <= a1 and c0 <= b0 and b1 <= c1:
            return True
    return False


REPORT = """# A47 leg (a) -- the s* exception lemma (A47-G-a1).  Verdict: {verdict}

## Statement certified
s* = 2 sqrt2+1 is (Thm T1 + `results/t1_span_check.json`) the ONLY side in the live window
[3.82, s0] at which a flush-free thin chain can span the container; the chain is then [45,0,45]:
D_L = diamond |x-sqrt2/2|+|y-y0| <= sqrt2/2, U = [sqrt2,sqrt2+1]x[b,b+1], D_R = mirror of D_L.
LEMMA.  For every y0 in [sqrt2/2, sqrt2+1/2] (up-down symmetry half) and every b in
[max(0,y0-1), y0]  (b >= 0 since U lies in the container), there are NO 8 closed unit squares with
pairwise disjoint interiors inside [0,s*]^2 whose interiors all miss C(y0,b) -- so the s* exception
structure admits no 11-packing completion.

## Soundness chain (each link machine-checked or elementary)
1. Suppose 8 such squares exist.  Scale by lambda = {lam} > 1 about the origin and shrink each image
   about its centre back to side 1: two convex sets with disjoint interiors are line-separated and
   the lambda-square has support radius >= 1/2, so the shrunk squares are PAIRWISE DISJOINT CLOSED
   unit squares, lying in [0,lambda s*]^2 subset [0,s']^2, s' = {sp} (checked: lambda*(2 R2HI+1) <=
   s'), each still missing int(lambda C).
2. Per parameter box B, `sstar_geom.build_obstacle` builds a rational C_shr(B) = P_L u P_U u P_R and
   PROVES exactly (Fractions, no sampling) that every vertex of every piece satisfies every
   half-plane of lambda*C(y0,b) with slack >= delta = {delta} for EVERY (y0,b) in B: the right-hand
   sides are affine in the parameter and carry sqrt2 with a fixed sign, so the worse endpoint with
   sqrt2 -> R2LO/R2HI ({r2lo}, {r2hi}) is a certified rational bound.  So C_shr is inside
   int(lambda C) -- the relaxation only ENLARGES the container and SHRINKS the obstacle.
3. Per box a rational measure mu = sum w_i delta_(p_i) is checked EXACTLY by `verify_measure_obs.py`
   (the audited A08 branch-and-bound, integer core imported verbatim): every placement box is
   COVERED (certified mass >= 1) or EXEMPT -- a rational p with p in P (exact half-plane test) and p
   in Q(c,theta) for EVERY placement of the box (the same exact interval predicate as for atoms), so
   int(Q) meets int(lambda C) and Q is none of the 8.
4. Hence each of the 8 disjoint squares has mu >= 1: 8 <= total mass < 8, contradiction.

## Method (producer; NOT trusted -- only the verifier is)
LP  min sum w  s.t. mass >= 1 on a grid of admissible non-exempt placements (an atom counts only if
inside Q shrunk by eps = {eps}, the robustness margin); cutting plane against a fine float scan;
then a loop against the EXACT verifier -- each failing placement box is patched by ROBUST rows (only
atoms guaranteed inside for the WHOLE cell count) on a lattice ALIGNED with the verifier's own box
tree, so a failing box can never straddle two cells.  Weights rounded UP, safety factor {scale}.
The producer's exemption rule is strictly weaker than the verifier's, so it never drops a row the
verifier cannot discharge.

## Per-y0 summary ({npass}/{nrec} parameter boxes PASS; total mass must be < 8)
| y0 window | b boxes | max total | min total | max LP | verify boxes (max) |
|---|---|---|---|---|---|
{table}

Worst margin over all boxes: 8 - {maxtot} = {margin}.

## Gaps / caveats
{gaps}
"""


def write_report(out, recs, good, bad, gaps):
    rows = {}
    for r in recs:
        k = (r["box_float"][0], r["box_float"][1])
        rows.setdefault(k, []).append(r)
    lines = []
    for k in sorted(rows):
        rs = rows[k]
        tot = [x.get("total_float") for x in rs if x.get("total_float")]
        lp = [x.get("lp_total") for x in rs if x.get("lp_total")]
        vb = [x.get("verify_boxes") or 0 for x in rs]
        lines.append(f"| [{k[0]:.4f}, {k[1]:.4f}] | {len(rs)} | {max(tot):.4f} | {min(tot):.4f} | "
                     f"{max(lp):.4f} | {max(vb)} |")
    maxtot = max((r.get("total_float", 0) for r in good), default=0)
    gtxt = "None -- the declared parameter domain is fully covered by PASSing boxes."
    ap = os.path.join(ROOT, "work", "sstar", "audit.json")
    if os.path.exists(ap):
        with open(ap) as fh:
            au = json.load(fh)
        gtxt += (f"  Final audit: all {au['n_certs']} certificates re-verified in fresh processes "
                 f"(obstacle containment proof re-run from the parameter box) and spot-checked by "
                 f"the independent random-placement test: all_pass = {au['all_pass']}.")
    if bad or gaps:
        gtxt = ""
        for r in bad:
            gtxt += (f"- NOT PASS: y0 in [{r['box'][0]},{r['box'][1]}], b in [{r['box'][2]},"
                     f"{r['box'][3]}]: {r.get('result')} (total {r.get('total_float')}, "
                     f"LP {r.get('lp_total')})\n")
        if gaps:
            gtxt += f"- {len(gaps)} uncovered reference cells; first few:\n"
            for b in gaps[:6]:
                gtxt += f"  - y0 in [{b[0]},{b[1]}], b in [{b[2]},{b[3]}]\n"
    txt = REPORT.format(
        verdict=out["verdict"], lam=str(G.LAM), sp=str(G.SP), delta=str(G.DELTA),
        r2lo=str(G.R2LO), r2hi=str(G.R2HI),
        eps=recs[0].get("eps", "1/128"), scale=recs[0].get("scale", "102/100"),
        npass=len(good), nrec=len(recs), table="\n".join(lines),
        maxtot=f"{maxtot:.4f}", margin=f"{8 - maxtot:.4f}", gaps=gtxt.rstrip() or "None.")
    p = os.path.join(ROOT, "results", "sstar_report.md")
    with open(p, "w") as fh:
        fh.write(txt)
    print("->", p, f"({len(txt.splitlines())} lines)")


def main():
    recs = load_all()
    good = [r for r in recs if r.get("result") == "PASS"]
    bad = [r for r in recs if r.get("result") not in ("PASS",)]
    gboxes = [rect(r) for r in good]
    # ---- exact coverage audit on the arrangement generated by ALL box edges
    ycuts = sorted({G.Y0_MIN, G.Y0_MAX} | {F(r["box"][0]) for r in recs} | {F(r["box"][1]) for r in recs})
    ycuts = [y for y in ycuts if G.Y0_MIN <= y <= G.Y0_MAX]
    bcuts = sorted({F(0)} | {F(r["box"][2]) for r in recs} | {F(r["box"][3]) for r in recs}
                   | {G.Y0_MAX, G.Y0_MIN - 1, G.Y0_MAX - 1})
    bcuts = [b for b in bcuts if F(0) <= b <= G.Y0_MAX]
    gaps = []
    for i in range(len(ycuts) - 1):
        y0, y1 = ycuts[i], ycuts[i + 1]
        for j in range(len(bcuts) - 1):
            b0, b1 = bcuts[j], bcuts[j + 1]
            # Does this cell meet the INTERIOR of the domain {max(0,y0-1) < b < y0}?  Testing only
            # those cells is enough: the b-interval of the domain has positive length for every y0
            # in range, so the domain is the closure of its interior, and a finite union of CLOSED
            # boxes containing the interior contains the closure.
            if b0 >= y1 or b1 <= max(F(0), y0 - 1):
                continue
            if not covered((y0, y1, b0, b1), gboxes):
                gaps.append((y0, y1, b0, b1))

    out = {
        "lemma": ("For every (y0,b) with y0 in [sqrt2/2, sqrt2+1/2] and b in [max(0,y0-1), y0], "
                  "no 8 unit squares with pairwise disjoint interiors fit in [0,s*]^2 while avoiding "
                  "the interiors of the chain C(y0,b) = D_L u U u D_R.  Certified by monotone "
                  "rational relaxation (container [0,s']^2, s'=383/100; obstacle C_shr contained in "
                  "lambda*C, lambda=10001/10000) + A08-style exact measure certificates with "
                  "obstacle exemption, total mass < 8 on every parameter box."),
        "constants": {"s_prime": str(G.SP), "lambda": str(G.LAM), "delta": str(G.DELTA),
                      "sqrt2_lo": str(G.R2LO), "sqrt2_hi": str(G.R2HI),
                      "y0_domain": [str(G.Y0_MIN), str(G.Y0_MAX)]},
        "audit": (json.load(open(os.path.join(ROOT, "work", "sstar", "audit.json")))
                  if os.path.exists(os.path.join(ROOT, "work", "sstar", "audit.json")) else None),
        "n_boxes": len(recs), "n_pass": len(good), "n_not_pass": len(bad),
        "verdict": "PROVED (full declared parameter domain)" if (not bad and not gaps)
                   else "PARTIAL",
        "uncovered_reference_cells": [[str(x) for x in b] for b in gaps],
        "max_total": max((r.get("total_float", 0) for r in good), default=None),
        "boxes": sorted(
            [{"y0": r["box"][:2], "b": r["box"][2:], "y0_f": r["box_float"][:2],
              "b_f": r["box_float"][2:], "result": r.get("result"),
              "lp_total": round(r.get("lp_total", 0), 5) if r.get("lp_total") else None,
              "total": r.get("total"), "total_float": r.get("total_float"),
              "obstacle_shrink": {"delta": r.get("delta"), "eps_geo": r.get("eps"),
                                  "rho_lp": r.get("rho"),
                                  "area": obstacle_area(rect(r))},
              "atoms": r.get("n_atoms"), "verify_boxes": r.get("verify_boxes"),
              "verify_exempt": r.get("verify_exempt"), "eps": r.get("eps"), "rho": r.get("rho"),
              "scale": r.get("scale"), "refine_level": r.get("refine_level"),
              "time_s": round(r.get("time_s", 0), 1),
              "note": r.get("note") or r.get("error")}
             for r in recs], key=lambda z: (z["y0_f"][0], z["b_f"][0])),
    }
    p = os.path.join(ROOT, "results", "sstar_lemma.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as fh:
        json.dump(out, fh, indent=1)
    write_report(out, recs, good, bad, gaps)
    print(f"{len(recs)} boxes, {len(good)} PASS, {len(bad)} not; gaps: {len(gaps)}")
    print(f"max total over PASSing boxes: {out['max_total']}")
    for r in bad:
        print("  NOT PASS:", r["box"], r.get("result"), r.get("total_float"), r.get("lp_total"))
    print("->", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
