"""A187 -- the ranked table (notes/basin_map.md) and the one-page map
(docs/residue_map/basin_map.svg) from results/basin_map187.json.  READ-ONLY on everything else.

Drawing rules follow docs/residue_map/gen_a57_lp.py: plain SVG, no library, s0 container as a heavy
black square, thin dashed = certified basin boxes, thin outlines = the alive pages' hypothesis
boxes, colour = containment.

    python report187.py
"""
from __future__ import annotations

import json, math, os, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RES = os.path.abspath(os.path.join(HERE, "..", "results"))
NOTES = os.path.abspath(os.path.join(HERE, "..", "notes"))
S0 = 969271.0 / 250000.0

D = json.load(open(os.path.join(RES, "basin_map187.json"), encoding="utf-8"))
PAGES = D["pages"]
BINV = D["basins"]

import sys
sys.path.insert(0, HERE)
import basin187 as B                                    # noqa: E402  (map_box, load_basins)

BASINS = B.load_basins()


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, t, size=11, col="#222", bold=False, anchor="start"):
    b = ' font-weight="bold"' if bold else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{col}" '
            f'text-anchor="{anchor}"{b}>{esc(t)}</text>')


def colour(p):
    g = p.get("growth_needed")
    if g is None:
        return "#9e9e9e", "no basin in this frame"
    if p["contained"]:
        return "#2e7d32", "inside"
    if g < 2.0:
        return "#ef6c00", "gap < 2x"
    return "#c62828", "far"


# ------------------------------------------------------------------ the map
SC = 108.0                       # px per unit
PAD_L, PAD_T = 58, 74
CELL_W = S0 * SC + 108
CELL_H = S0 * SC + 128


def basin_key_of(p):
    b = p.get("nearest_basin") or {}
    return (b.get("tag"), b.get("cls"))


def panel(ox, oy, tag, cls, pages, note=""):
    """one minimiser-family panel: the certified basin boxes + the alive pages' hypothesis boxes."""
    out = []
    W = S0 * SC
    entries = BASINS.get((tag, cls), []) if tag else []
    inv = BINV.get(f"{tag}|{cls}") if tag else None
    s_star = (inv or {}).get("s_star")
    head = (f"{tag} in the {cls} frame" if tag else f"the {cls} frame — NO CERTIFIED BASIN")
    out.append(text(ox, oy - 40, head, 13.5, "#000", True))
    sub = (f"basin: {len(entries)} certified box set(s) from {', '.join((inv or {}).get('srcs', []))}"
           f"; minimiser s* = {s_star:.6f} > s0 = {S0:.6f}" if entries else
           "no local certificate exists for any minimiser of this frame")
    out.append(text(ox, oy - 25, sub, 9.5, "#444"))
    out.append(text(ox, oy - 12, note or f"{len(pages)} ALIVE page(s) drawn", 9.5, "#666"))
    out.append(f'<rect x="{ox}" y="{oy}" width="{W:.1f}" height="{W:.1f}" fill="none" '
               f'stroke="#000" stroke-width="2"/>')

    def rect(x0, x1, y0, y1, stroke, sw, dash="", op=1.0, fill="none"):
        return (f'<rect x="{ox + x0 * SC:.1f}" y="{oy + (S0 - y1) * SC:.1f}" '
                f'width="{(x1 - x0) * SC:.1f}" height="{(y1 - y0) * SC:.1f}" fill="{fill}" '
                f'stroke="{stroke}" stroke-width="{sw}"{dash} stroke-opacity="{op}"/>')

    # every certified box of every entry, thin dashed; then the union per named square, heavier
    byname = collections.defaultdict(list)
    for e in entries:
        for b in e["boxes"]:
            byname[b[0]].append(b)
            out.append(rect(b[1], b[2], b[3], b[4], "#1565c0", 0.4,
                            ' stroke-dasharray="3,2"', 0.30))
    for nm, bs in sorted(byname.items()):
        x0 = min(b[1] for b in bs); x1 = max(b[2] for b in bs)
        y0 = min(b[3] for b in bs); y1 = max(b[4] for b in bs)
        out.append(rect(x0, x1, y0, y1, "#0d47a1", 1.2, ' stroke-dasharray="6,3"', 0.9))
        out.append(text(ox + 0.5 * (x0 + x1) * SC, oy + (S0 - y1) * SC - 3, nm, 8.5,
                        "#0d47a1", True, "middle"))
        # the minimiser's own pose (the basin's anchor) as a small cross
        ax = sum(b[8 - 1] for b in bs) / len(bs)
        ay = sum(b[9 - 1] for b in bs) / len(bs)
        out.append(f'<circle cx="{ox + ax * SC:.1f}" cy="{oy + (S0 - ay) * SC:.1f}" r="2.2" '
                   f'fill="#0d47a1"/>')

    # the alive pages' hypothesis boxes
    for p in pages:
        bx = p["box_frame"]
        col, _ = colour(p)
        out.append(rect(bx[0], bx[1], bx[2], bx[3], col, 1.1, "", 0.95))
        lbl = p["nid"].replace("k5_11_interior_", "").replace("k5_16_interior_", "")
        lbl = lbl.replace("trump5_j0_", "")
        # label only the pages the basin could plausibly reach; the 'far' cluster is dense and
        # its labels would overprint each other into illegibility.
        if p["contained"] or (p.get("growth_needed") or 9) < 2.0:
            out.append(text(ox + 0.5 * (bx[0] + bx[1]) * SC, oy + (S0 - bx[3]) * SC - 2.5,
                            lbl, 6.4, col, False, "middle"))
    ins = sum(1 for p in pages if p["contained"])
    near = sum(1 for p in pages if not p["contained"] and (p.get("growth_needed") or 9) < 2.0)
    far = len(pages) - ins - near
    out.append(text(ox, oy + W + 15,
                    f"pages: {ins} inside / {near} gap < 2x / {far} far", 9.5, "#333"))
    if entries:
        gs = [p["growth_needed"] for p in pages if p.get("growth_needed") is not None]
        if gs:
            out.append(text(ox, oy + W + 28,
                            f"growth this basin would need: median {sorted(gs)[len(gs)//2]:.2f}x, "
                            f"max {max(gs):.2f}x", 9.5, "#333"))
    return out


def draw():
    # a panel per (basin tag, frame) that owns pages, plus the frames with no basin
    groups = collections.OrderedDict()
    for key in (("S02", "k5_11"), ("S02", "k5_16"), ("S02", "trump5"), ("S07", "trump5")):
        groups[key] = []
    for p in PAGES:
        k = basin_key_of(p)
        if k == (None, None):
            k = (None, p["frame"])
        groups.setdefault(k, []).append(p)
    for key in (("S33", "k6_07"), ("S38", "k6_21")):
        groups.setdefault(key, [])

    order = sorted(groups.items(), key=lambda kv: (-len(kv[1]), str(kv[0])))
    ncol = 3
    W = int(PAD_L + ncol * CELL_W + 380)
    nrow = (len(order) + ncol - 1) // ncol
    H = int(PAD_T + nrow * CELL_H + 150)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif">',
           f'<rect width="{W}" height="{H}" fill="#fff"/>']
    out.append(text(PAD_L, 30, "A187 — the basin containment map of the alive residue", 19,
                    "#000", True))
    n_basin_frame = sum(1 for p in PAGES if p.get("growth_needed") is not None)
    n_in = sum(1 for p in PAGES if p["contained"])
    n_own = sum(1 for p in PAGES if p["basin_own_frame"])
    n_cons = sum(1 for p in PAGES if p.get("consumer_inside_any"))
    out.append(text(PAD_L, 51,
                    f"{len(PAGES)} ALIVE gallery pages (52 a57v4 + 11 k0v4) against every certified "
                    f"local certificate.  {n_own} pages have a basin for their OWN nearest minimiser "
                    f"in their own class frame; {n_in} have their conditioned box inside a certified "
                    f"basin box; {n_cons} have their A107 representative configuration inside a "
                    f"certified N (the A116/A151/A160/A163 consumer test).  "
                    f"{len(PAGES) - n_basin_frame} pages sit in a frame with no basin at all.",
                    10.5, "#333"))
    for i, (key, pages) in enumerate(order):
        r, c = divmod(i, ncol)
        ox = PAD_L + c * CELL_W
        oy = PAD_T + r * CELL_H + 46
        note = ""
        if key[0] and not pages:
            note = "no ALIVE page sits in this frame (A163's problem, one frame further out)"
        out += panel(ox, oy, key[0], key[1], pages, note)

    # legend + the orphan minimisers
    lx = PAD_L + ncol * CELL_W + 14
    ly = PAD_T + 60
    out.append(text(lx, ly, "LEGEND", 12, "#000", True))
    for k, (col, lab, why) in enumerate([
            ("#2e7d32", "inside", "the page's conditioned box lies inside a certified basin box"),
            ("#ef6c00", "gap < 2x", "the basin box would have to grow by < 2x to swallow it"),
            ("#c62828", "far", "growth >= 2x on some coordinate"),
            ("#9e9e9e", "no basin", "no certified basin exists in this page's class frame")]):
        y = ly + 18 + 26 * k
        out.append(f'<rect x="{lx}" y="{y - 9}" width="16" height="11" fill="none" '
                   f'stroke="{col}" stroke-width="1.6"/>')
        out.append(text(lx + 22, y, lab, 10, col, True))
        out.append(text(lx + 22, y + 11, why, 8, "#666"))
    y = ly + 18 + 26 * 4 + 6
    out.append(f'<rect x="{lx}" y="{y - 9}" width="16" height="11" fill="none" stroke="#0d47a1" '
               f'stroke-width="1.2" stroke-dasharray="6,3"/>')
    out.append(text(lx + 22, y, "certified basin box (union over entries)", 9, "#0d47a1"))
    out.append(text(lx + 22, y + 11, "faint dashes = the individual certified box sets; "
                                     "dot = the minimiser's own pose", 8, "#666"))

    y += 44
    out.append(text(lx, y, "MINIMISERS WITH NO BASIN", 12, "#000", True))
    out.append(text(lx, y + 14, "(pages clustering on them — the census route)", 9, "#666"))
    cnt = collections.Counter(p["family"] for p in PAGES if not p["basin_own_frame"])
    for k, (fam, n) in enumerate(cnt.most_common()):
        out.append(text(lx, y + 32 + 14 * k, f"{fam:<6} {n:>3} page(s)"
                        + ("   [basin exists in another frame: "
                           + ", ".join(next(p["basin_other_frames"] for p in PAGES
                                            if p["family"] == fam)) + "]"
                           if any(p["family"] == fam and p["basin_other_frames"] for p in PAGES)
                           else ""), 9.5, "#333"))
    out.append(text(PAD_L, H - 30,
                    "A CAVEAT ON 'inside': a certified N asks for a square in EACH of its boxes; an "
                    "alive page conditions ONE square.  Box containment is therefore NECESSARY for the "
                    "LocalCompose YES leaf to cover the page, not sufficient — the other boxes are what "
                    "the NO children (A120/A136) still have to supply.", 9.5, "#555"))
    out.append(text(PAD_L, H - 16,
                    "A187, 2026-09-09.  Sources: docs/shadows/STATUS.md; A148 gallery records; "
                    "A107 struct_op/cfg; basins A119/A125/A160/A163.  Read-only.", 9, "#888"))
    out.append("</svg>")
    p = os.path.join(ROOT, "docs", "residue_map", "basin_map.svg")
    open(p, "w", encoding="utf-8").write("\n".join(out))
    print("wrote", p, len(order), "panels")


# ------------------------------------------------------------------ the ranked table
def table():
    L = []
    n_basin_frame = sum(1 for p in PAGES if p.get("growth_needed") is not None)
    n_in = sum(1 for p in PAGES if p["contained"])
    n_own = sum(1 for p in PAGES if p["basin_own_frame"])
    n_cons = sum(1 for p in PAGES if p.get("consumer_inside_any"))
    n_near = sum(1 for p in PAGES if not p["contained"]
                 and (p.get("growth_needed") is not None) and p["growth_needed"] < 2.0)
    L.append("# A187 — the basin containment map of the alive residue\n")
    L.append(f"Generated {D['generated']} by `attempts/A187-basin-map/code/basin187.py` + "
             f"`report187.py`; data `results/basin_map187.json`; map "
             f"`docs/residue_map/basin_map.svg`.  Read-only on every other attempt.\n")
    L.append("## 0. The headline\n")
    L.append(f"| | pages | of {len(PAGES)} |")
    L.append("|---|---|---|")
    L.append(f"| ALIVE gallery pages (52 `a57v4` + 11 `k0v4`) | {len(PAGES)} | 100 % |")
    L.append(f"| in a class frame that has **any** certified basin | {n_basin_frame} | "
             f"{100.0*n_basin_frame/len(PAGES):.0f} % |")
    L.append(f"| whose **own** nearest minimiser has a basin **in that frame** | {n_own} | "
             f"{100.0*n_own/len(PAGES):.0f} % |")
    L.append(f"| whose conditioned box is **inside** a certified basin box | {n_in} | "
             f"{100.0*n_in/len(PAGES):.0f} % |")
    L.append(f"| within a **2x growth** of a certified basin box | {n_in + n_near} | "
             f"{100.0*(n_in+n_near)/len(PAGES):.0f} % |")
    L.append(f"| whose A107 representative configuration is inside a certified N "
             f"(A116/A151/A160/A163 consumer) | {n_cons} | {100.0*n_cons/len(PAGES):.0f} % |")
    L.append("")
    L.append(f"**[M] The residue is not basin-shaped.**  All 52 A57/A60 pages live in a frame "
             f"(`k5_11`, `k5_16`, `trump5`) that owns the S02 pinwheel basin, but only {n_own} of "
             f"the {len(PAGES)} pages minimise to a configuration that has a certified basin in "
             f"their own frame at all — the other {len(PAGES) - n_own} cluster on a minimiser with "
             f"no local certificate there.  Where a page's box does fit a certified box it is "
             f"usually the WRONG minimiser's basin (a coincidence of position, not of family), so "
             f"the honest measure of how much of the residue is basin-shaped is the consumer "
             f"column: **{n_cons} of {len(PAGES)} pages = "
             f"{100.0*n_cons/len(PAGES):.0f} %**.  All seven sit inside the S02 pinwheel basin and "
             f"all seven are `k5_11` / `k5_16` pages; only three of them are S02 pages themselves "
             f"(`k5_16` Y0054, Y0380, Y1110), the other four minimise to S10, S36 and S01 and land "
             f"in S02's basin anyway.\n")

    L.append("## 1. Pages ranked by the growth the nearest certified basin would need\n")
    L.append("`growth` = max over (centre x, centre y, tilt) and over the two SIDES of the "
             "minimiser's own pose of (the reach the basin box would need) / (the reach it has) "
             "-- per side, because the certified windows are asymmetric -- minimised over every "
             "certified box of every entry in the page's frame.  `growth <= 1` = already contained.  `gap` = how far the page's "
             "box sticks out, per coordinate.  `own?` = is the matched basin the basin of the "
             "page's OWN nearest packing.  `cons` = the A116 consumer verdict on the page's A107 "
             "representative configuration.  `sup` = fraction of LP support weight inside the "
             "matched basin's boxes.\n")
    L.append("| # | page | class | family | s\\* | basin matched | growth | gap x | gap y | gap tilt (deg) | own? | cons | sup |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    rows = sorted(PAGES, key=lambda p: (p.get("growth_needed") is None,
                                        p.get("growth_needed") or 9e9))
    for i, p in enumerate(rows, 1):
        b = p.get("nearest_basin") or {}
        g = p.get("growth_needed")
        L.append("| %d | `%s` | `%s` | `%s` | %s | %s | %s | %.3f | %.3f | %.1f | %s | %s | %s |" % (
            i, p["nid"], p["cls"], p["family"],
            ("%.6f" % p["s_N"]) if p.get("s_N") else "—",
            (f"`{b['tag']}` / `{b['cls']}` ({b['entry'][:34]}…)" if b else "— none in frame"),
            ("**%.2f**" % g) if (g is not None and p["contained"]) else
            (("%.2f" % g) if g is not None else "—"),
            b.get("gap_x", 0.0), b.get("gap_y", 0.0), b.get("gap_t_deg", 0.0),
            "yes" if (p.get("own_basin_fit") and b and
                      p["own_basin_fit"]["entry"] == b.get("entry")) else "no",
            "YES" if p.get("consumer_inside_any") else "no",
            ("%.2f" % b["support_frac"]) if b.get("support_frac") is not None else "—"))
    L.append("")

    L.append("## 2. Minimisers ranked by how many alive pages cluster on them\n")
    L.append("| minimiser | s\\* | ALIVE pages | frames those pages live in | certified basin? |")
    L.append("|---|---|---|---|---|")
    fam = collections.Counter(p["family"] for p in PAGES)
    have = collections.defaultdict(set)
    for k in BASINS:
        have[k[0]].add(k[1])
    for f, n in fam.most_common():
        frames = sorted({p["frame"] for p in PAGES if p["family"] == f})
        s = next((p["s_family"] for p in PAGES if p["family"] == f and p.get("s_family")), None)
        if f in have:
            got = "**yes** — " + ", ".join(sorted(have[f]))
            if not (have[f] & set(frames)):
                got += "  *(but not in any frame an alive page lives in)*"
        else:
            got = "**none**"
        L.append("| `%s` | %s | %d | %s | %s |" % (
            f, ("%.6f" % s) if s else "—", n, ", ".join(f"`{x}`" for x in frames), got))
    L.append("")

    L.append("## 3. Pages with no nearby minimiser at all — the drain-census route\n")
    orph = [p for p in PAGES if not p["basin_own_frame"]]
    noframe = [p for p in PAGES if p.get("growth_needed") is None]
    L.append(f"**[M] {len(orph)} of {len(PAGES)} pages** minimise to a configuration that has no "
             f"certified basin in their class frame; **{len(noframe)}** of those (the whole `k0_00` "
             f"lane) sit in a frame with no basin of any minimiser, so containment cannot even be "
             f"tested there — `k0_00` has no pins, so no local certificate of the "
             f"`CLASS_PINS` form applies to it at all.  These are the census candidates.\n")
    L.append("| page | class | family (nearest packing) | s\\* | why no basin |")
    L.append("|---|---|---|---|---|")
    for p in sorted(orph, key=lambda p: (p["frame"], p["family"], p["nid"])):
        why = ("no basin in the `k0_00` frame (no class pins)" if p["frame"] == "k0_00"
               else (f"`{p['family']}` has a basin only in " +
                     ", ".join(f"`{x}`" for x in p["basin_other_frames"])
                     if p["basin_other_frames"]
                     else f"`{p['family']}` has no local certificate anywhere"))
        L.append("| `%s` | `%s` | `%s` | %s | %s |" % (
            p["nid"], p["cls"], p["family"],
            ("%.6f" % p["s_N"]) if p.get("s_N") else "—", why))
    L.append("")

    L.append("## 4. What would have to grow, and by how much\n")
    for key in sorted(BASINS):
        pages = [p for p in PAGES if (p.get("nearest_basin") or {}).get("tag") == key[0]
                 and (p.get("nearest_basin") or {}).get("cls") == key[1]]
        gs = sorted(p["growth_needed"] for p in pages if p.get("growth_needed") is not None)
        inv = BINV.get(f"{key[0]}|{key[1]}", {})
        if not gs:
            L.append(f"* **`{key[0]}` / `{key[1]}`** — {inv.get('n_entries', 0)} certified box "
                     f"sets; **no alive page sits in this frame**.")
            continue
        L.append(f"* **`{key[0]}` / `{key[1]}`** — {inv.get('n_entries')} certified box sets "
                 f"({', '.join(inv.get('srcs', []))}); {len(gs)} alive pages match it; "
                 f"growth needed: min {gs[0]:.2f}x, median {gs[len(gs)//2]:.2f}x, max "
                 f"{gs[-1]:.2f}x; {sum(1 for g in gs if g <= 1.0)} already contained, "
                 f"{sum(1 for g in gs if 1.0 < g < 2.0)} within 2x.")
    L.append("")
    L.append("## 5. Soundness\n")
    L.append("**[S] Box containment is NECESSARY, not sufficient.**  A certified N asks for a square "
             "in *each* of its boxes (plus the class pins in their slack cores); an alive page "
             "conditions *one* square (62 of the 63 pages have exactly one conditioned box; "
             "`f1_L10_0003` has two).  A page whose box lies inside a basin box is therefore a page "
             "the LocalCompose YES leaf *can* cover once the other boxes are supplied by the NO "
             "children (A120/A136) — not a page that is already dead.  The kill that follows from "
             "containment alone is the consumer column (`cons`), which is A116/A151/A160/A163's own "
             "test and is reproduced here byte-for-byte on the shared cases.\n")
    L.append("**[M] Control.**  `k5_16_interior_Y1110` reproduces A163's consumer slack "
             "0.01311 exactly, and `k5_16_interior_Y0054` / `Y0380` / `Y0230` reproduce A163's "
             "greedy-cover membership.\n")
    p = os.path.join(NOTES, "basin_map.md")
    open(p, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("wrote", p)


if __name__ == "__main__":
    # attach the frame-mapped hypothesis box to each page for the drawing
    for p in PAGES:
        p["box_frame"] = p.get("box_frame") or [0, 0, 0, 0]
    draw()
    table()
