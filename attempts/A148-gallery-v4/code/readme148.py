"""A148 -- the review sheet: docs/shadows/<set>/README.md and the docs/shadows.md Part V block.

    set PYTHONDONTWRITEBYTECODE=1 && python code/readme148.py --set k0v4
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))

S0 = 969271.0 / 250000.0

HEAD = """# {title}

One page per node, in the **v4 three-panel form**.  Every page answers the same question first —
*can the remaining squares fit in the white space?* — and only then shows the LP.

| panel | what it is |
|---|---|
| **G — GEOMETRY: what is still free** (largest) | the container at s0, the hypothesis squares with their certified cores, and the **feasible-centre region**: the set of centres where one further unit square can still be placed at SOME tilt, interior-disjoint from every pin's exact core and from K'(B) of every conditioned square.  **Green = certified free; grey STIPPLE = undecided (clearance within the Lipschitz margin) and NOT feasible; white = certified blocked.**  Pockets narrower than 1 are a separate object, hatched with grey DIAGONAL lines and the width printed; A144 guard lines are drawn thin with their chord sum and rhs; each corner/slot carries A141's K' lane verdict with BOTH bounds (`ub` certified, `lb` sampled) and `M`, plus the WITNESSED free meeters from A157's screen and A141's two-crowd witness drawn as thin black outlines with how far each reaches into the cell; A131's exact pin-clip is the orange box inside the black centre box.  **Nothing in panel G comes from an LP.** |
| **S — the LP support** (medium) | the dual support of the node's latest record, fill = dual weight on one sequential scale (A107 v2), the certified cores outlined, and every column whose square overlaps a core drawn **red dashed**: those are impossible under the hypothesis, and each is labelled with whether it ALSO overlaps an exact pin core (pin geometry alone excludes it, inside the frozen certificate schema) or only K'(B) (which needs the polygon-core clause).  The squares here overlap each other — that is the relaxation's slack, not a packing. |
| **N — nearest real packing** (small) | A107's minimised shadow or A128's polished near-packing, the container at its own s* with s0 overlaid dashed and a banner saying whether it is realisable at s0.  These are the square names used everywhere else. |

**Soundness of the green region.**  The region is computed on a grid of pitch ≤ 0.02 × 36 tilts, and
both verdicts carry the Lipschitz margin `m = pitch·√2/2 + (√2/2)·(Δθ/2)` (SAT depth between convex
sets is 1-Lipschitz in the centre and (√2/2)-Lipschitz in the tilt).  So **GREEN is a certified
inner approximation** — every point of a green cell admits a feasible tilt — and **WHITE a certified
outer one** — no point of a white cell admits any tilt.  Sampled confirmation per page: 10⁴ centres
drawn uniformly in the green cells and 10⁴ in the blocked cells, tested at 360 tilts with an
independent SAT ({green_hits} and {blocked_hits} hits over the whole set).  An independent
re-verification (edge crossing + strict point-in-polygon, no separating axis anywhere in it) is
`attempts/A148-gallery-v4/code/verify148.py`; its result is
`attempts/A148-gallery-v4/results/verify148_{which}.json`.

**The disk bound — the shortcut this gallery is for.**  A unit square contains the disk of radius
1/2 about its centre, so the centres of the `budget` remaining squares carry pairwise disjoint
half-unit disks inside the container, and each centre lies in (green ∪ undecided).  Hence

>  `budget  ≤  area( (green ∪ undecided) ⊕ B(1/2)  ∩  [0,s0]² ) / (π/4)`

which is a **sound upper bound on how many more squares the node can hold, read straight off the
drawing**.  `n_max < budget` is a geometric kill with no LP at all.  The column is in the table.

{extra}
## The table

{table}

## What to look for, per node

{looks}

## Files

`review_{which}.csv` is the review sheet (every automatic column filled, the four `PI_*` columns
empty).  The generator is `attempts/A148-gallery-v4/code/{{gallery148,geo148,data148}}.py`; the
per-page facts are `attempts/A148-gallery-v4/results/gallery148_{which}.json`.
"""


def short_look(r):
    bits = []
    d = r["disk"]
    if d["n_max"] < r["budget"]:
        bits.append(f"**DISK BOUND KILLS IT** ({d['n_max']} < {r['budget']})")
    nn = [p for p in r["pockets"] if p["gap"] < 1.0]
    if nn:
        bits.append("pockets < 1: " + ", ".join(f"`{p['to']}` {p['gap']:.3f}" for p in nn[:3]))
    hot = [t for t in r["lane_tags"] if t["verdict"].startswith("KILL")
           or "NEAR-MISS" in t["verdict"] or "LANE<=1" in t["verdict"]]
    if hot:
        bits.append("lane: " + ", ".join(f"`{t['cell']}` {t['verdict']}" for t in hot))
    g = r["guard"][0] if r["guard"] else None
    if g and g["rhs"] <= 0.15:
        bits.append(f"guard line `{g['tag']}` chord sum {g['chord_sum']:.4f} (rhs {g['rhs']:.4f})")
    if r["t5"]["dead"]:
        bits.append("**T5⁗ DEAD**")
    if not bits:
        bits.append("nothing free: no pocket under 1, no lane ≤ 1, no tight guard line, disk "
                    f"bound {d['n_max']} ≥ budget {r['budget']}")
    return "; ".join(bits)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", dest="which", default="k0v4")
    ap.add_argument("--title", default=None)
    a = ap.parse_args()
    summ = json.load(open(os.path.join(BASE, "results", f"gallery148_{a.which}.json"),
                          encoding="utf-8"))
    out = os.path.join(ROOT, "docs", "shadows", a.which)
    rows = ["| node | level | s\\* of panel N | family | green area | green+undec. | disk bound "
            "n\\_max (budget) | narrowest pocket | pockets < 1 | lane tags (hot) | tightest guard "
            "rhs | leaves run |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    looks = []
    for r in summ:
        nn = [p for p in r["pockets"] if p["gap"] < 1.0]
        hot = [t for t in r["lane_tags"] if t["verdict"].startswith("KILL")
               or "NEAR-MISS" in t["verdict"] or "LANE<=1" in t["verdict"]]
        g = r["guard"][0] if r["guard"] else {}
        leaves = []
        leaves.append("clip vacuous" if "VACUOUS" in r["clip_note"] else "clip")
        leaves.append("T5⁗ " + ("DEAD" if r["t5"]["dead"] else "alive"))
        leaves.append("lane " + ("kill" if any(t["verdict"].startswith("KILL")
                                               for t in r["lane_tags"]) else
                                 ("near-miss" if hot else "no kill")))
        leaves.append("guard " + ("CONTRADICTION" if g.get("rhs", 9) < 0 else "no kill"))
        rows.append(
            f"| [`{r['id']}`]({r['id']}.svg) | {r['level']} | {r['s_star']:.6f} | "
            f"{r['family']} | {r['grid']['area_green']:.3f} | {r['grid']['area_open']:.3f} | "
            f"**{r['disk']['n_max']}** ({r['budget']}) | "
            + (f"`{r['pockets'][0]['to']}` {r['pockets'][0]['gap']:.4f}" if r["pockets"]
               else "none") + f" | {len(nn)} | "
            + (", ".join(f"`{t['cell']}` {t['verdict']}" for t in hot) or "—") + " | "
            + (f"{g.get('rhs', 0):.4f} (`{g.get('tag')}`)" if g else "n/a") + " | "
            + ", ".join(leaves) + " |")
        looks.append(f"* **`{r['id']}`** — {short_look(r)}")
    gh = sum(r["sample"]["green"]["hits"] for r in summ)
    bh = sum(r["sample"]["blocked"]["hits"] for r in summ)
    title = a.title or (f"The k0 residue gallery v4 ({len(summ)} converged-alive k0_00 cells)"
                        if a.which == "k0v4" else
                        f"The A57 / A60 review gallery v4 ({len(summ)} nodes)")
    extra = ""
    if a.which == "a57v4" and os.environ.get("A148_EXTRA"):
        extra = os.environ["A148_EXTRA"] + "\n"
    if a.which == "k0v4":
        extra = ("**Population.**  A140's twelve converged-alive `k0_00` cells minus "
                 "`s3_far_BL389484_TR018470`, which A141's K' lane leaf killed on BL "
                 "(`attempts/A141-polycore-lane/results/polycore_lane_kills.jsonl`).  A141's "
                 "conditional-lane run (T5) closed no further cell of the eleven, so no page here "
                 "carries a KILLED banner.\n")
    txt = HEAD.format(title=title, which=a.which, table="\n".join(rows),
                      looks="\n".join(looks), green_hits=gh, blocked_hits=bh, extra=extra)
    open(os.path.join(out, "README.md"), "w", encoding="utf-8").write(txt)
    print("wrote", os.path.join(out, "README.md"), len(txt), "chars")


if __name__ == "__main__":
    main()
