"""A148 -- data access for the v4 pages.  No drawing, no geometry: only the records.

Reuses A140's `cells140` (the twelve converged-alive k0_00 cells and their A115 records, the A107
shadow index, A128's near-packings) and A142's `gallery142` loaders (the A57/A60 node index, the
A107 shadow families) verbatim, plus:

  A140  results/{t1_polycore,lane140,exactcore140,invitro140_s*}.json(l)   the K' measurement and
        the exact-axis-core / K'-pruned re-solves of the k0 cells
  A141  results/{t2_table.json,t4_slots.jsonl,t5_deep.jsonl,t5_split.jsonl,t5_twocrowd.json,
        polycore_lane_kills.jsonl}                                        the K' lane verdicts
  A142  results/population142.json                                        the subtree-cost model
  A144  results/offline144.jsonl                                          the stored guard rows
  A131  results/corpus131.jsonl                                           kept8 / the clip

READ-ONLY throughout.
"""
import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, ".."))
A107 = os.path.join(ATT, "A107-shadow-gallery")
A115 = os.path.join(ATT, "A115-k0-corner-rows")
A131 = os.path.join(ATT, "A131-pin-clip")
A140 = os.path.join(ATT, "A140-k0-residue-gallery")
A141 = os.path.join(ATT, "A141-polycore-lane")
A142 = os.path.join(ATT, "A142-a57-review-gallery")
A144 = os.path.join(ATT, "A144-guard-lines")
for _p in (os.path.join(A140, "code"), os.path.join(A142, "code"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np                                                   # noqa: E402
import polycore                                                      # noqa: E402
import cells140 as C140                                              # noqa: E402
import minimise as M                                                 # noqa: E402
import geo148 as G                                                   # noqa: E402

S0 = G.S0
SHAT = G.SHAT
KILLED_BY_A141 = "s3_far_BL389484_TR018470"
CORNER_CELL = {"BL": "BL(0,0)", "BR": "BR(0,0)", "TL": "TL(0,0)", "TR": "TR(0,0)"}


def _jl(p):
    out = []
    if not os.path.exists(p):
        return out
    for ln in open(p, encoding="utf-8"):
        ln = ln.strip()
        if ln:
            try:
                out.append(json.loads(ln))
            except Exception:                                        # noqa: BLE001
                pass
    return out


def _j(p, default=None):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else default


# ------------------------------------------------------------------ cached tables
_C = {}


def tbl(name):
    if name in _C:
        return _C[name]
    if name == "t1poly":
        v = {r["cell"]: r for r in (_j(os.path.join(A140, "results", "t1_polycore.json"),
                                       {}) or {}).get("twelve", [])}
    elif name == "exactcore140":
        v = {r["cell"]: r for r in _jl(os.path.join(A140, "results", "exactcore140.jsonl"))}
    elif name == "invitro140":
        v = {}
        for f in sorted(glob.glob(os.path.join(A140, "results", "invitro140_s*.jsonl"))):
            for r in _jl(f):
                v[r["cell"]] = r
    elif name == "lane140":
        v = _j(os.path.join(A140, "results", "lane140.json"), {}) or {}
    elif name == "a141_t2":
        v = (_j(os.path.join(A141, "results", "t2_table.json"), {}) or {}).get("table", {})
    elif name == "a141_slots":
        v = {}
        for r in _jl(os.path.join(A141, "results", "t4_slots.jsonl")) + \
                _jl(os.path.join(A141, "results", "t4_y0460.jsonl")):
            v.setdefault(r["nid"], []).append(r)
    elif name == "a141_a5760":
        v = {}
        for f in sorted(glob.glob(os.path.join(A141, "results", "t2_a5760_s*.jsonl"))):
            for r in _jl(f):
                v.setdefault(r.get("nid") or r.get("id"), []).append(r)
    elif name == "a141_deep":
        v = {}
        for f in ("t5_deep.jsonl", "t5_split.jsonl"):
            for r in _jl(os.path.join(A141, "results", f)):
                v.setdefault(r["cell"], []).append(r)
        for r in (_j(os.path.join(A141, "results", "t5_twocrowd.json"), []) or []):
            r = dict(r, kind="two-crowd")
            v.setdefault(r["cell"], []).append(r)
    elif name == "a141_kills":
        v = {}
        for r in _jl(os.path.join(A141, "results", "polycore_lane_kills.jsonl")):
            v.setdefault(r["nid"], []).append(r)
    elif name == "pop142":
        v = _j(os.path.join(A142, "results", "population142.json"), {}) or {}
    elif name == "a144":
        v = {r["id"]: r for r in _jl(os.path.join(A144, "results", "offline144.jsonl"))}
    elif name == "corpus131":
        v = {r["id"]: r for r in _jl(os.path.join(A131, "results", "corpus131.jsonl"))}
    else:
        raise KeyError(name)
    _C[name] = v
    return v


def cost_curve():
    return {int(k): float(v) for k, v in
            (tbl("pop142").get("cost_model", {}).get("C", {}) or {"5": 0.0}).items()}


def subtree_cost(level, kept8=1.0, n_open_desc=0):
    """A142's formula, for a node that is an ALIVE leaf of the emitted tree."""
    C = cost_curve()
    if n_open_desc:
        return 0.0
    return 8.0 * C.get(int(level) + 1, 0.0) * float(kept8 or 1.0)


# ------------------------------------------------------------------ the k0 population
def population(which):
    if which == "k0v4":
        return _k0_population()
    return _a57_population(which)


def _k0_population():
    out = []
    kills = tbl("a141_kills")
    t2 = tbl("a141_t2")
    for (name, lvl, src, fn, lanekey, alias) in C140.CELLS:
        if name == KILLED_BY_A141:
            continue                       # A140's twelve minus s3_far (A141 T1 killed it)
        meta, d = C140.load_cell(name)
        kc = (t2.get(name) or {}).get("kill_corners") or []
        banner, leafkill = "", ""
        if name in kills or kc:
            k = (kills.get(name) or [{}])[0]
            banner = (f"KILLED — K' LANE LEAF on {k.get('corner') or ', '.join(kc)}: "
                      f"LANE + M <= 1, K0-FREE (teleport)")
            leafkill = k.get("leaf") or "LANE_K' + M <= 1 (K0-FREE / teleport_packing)"
        out.append(dict(id=name, camp="k0", cls="k0_00", level=lvl, src=src,
                        record=meta["record"], boxes=d["hyp"]["boxes"],
                        packing=d.get("packing") or [],
                        tau=float(d.get("tau") or 0.0), budget=int(d.get("budget") or 0),
                        minmass=float(d.get("minmass") or 0.0),
                        converged=bool(d.get("converged")), alias=alias,
                        banner=banner, leafkill=leafkill, kept8=1.0, n_open_desc=0,
                        which="k0v4"))
    return out


def _a57_population(which):
    """the A57/A60 pages: A142's subtree-cost ranking, refreshed against the night's records."""
    import gallery142 as G142
    pop = tbl("pop142")
    out = []
    for key, camp, n in (("rank_a57", "A57", 40), ("rank_a60", "A60", 20)):
        for i, r in enumerate(pop.get(key, [])):
            if len(([x for x in out if x["camp"] == camp])) >= n:
                break
            try:
                d, path = G142.load_node(camp, r["id"])
            except Exception:                                        # noqa: BLE001
                continue
            boxes = d["hyp"]["boxes"]
            out.append(dict(id=r["id"], camp=camp, cls=r["cls"], level=r["level"],
                            src=f"{camp} {r['cls']}", record=path, boxes=boxes,
                            packing=d.get("packing") or [],
                            tau=float(d.get("tau") or 0.0),
                            budget=int(d.get("budget") or (11 - len(boxes))),
                            minmass=float(d.get("minmass") or 0.0),
                            converged=bool(d.get("converged")),
                            alias=None, banner="", leafkill="",
                            kept8=float(r.get("kept8") or 1.0),
                            n_open_desc=int(r.get("n_open_desc") or 0),
                            rank=i + 1, subtree_s=float(r.get("subtree_s") or 0.0),
                            verdict=r.get("verdict"), which=which))
    return out


# ------------------------------------------------------------------ per-node completion
def _lane_tags(node):
    tags = []
    if node["camp"] == "k0":
        rec = tbl("a141_t2").get(node["id"]) or {}
        for c, v in (rec.get("corners") or {}).items():
            cell = CORNER_CELL[c]
            try:
                (x, y) = M.slot_centres([cell], S0)[0]
            except Exception:                                        # noqa: BLE001
                continue
            vd = v.get("verdict") or "n/a"
            if v.get("lane_ub") is not None:
                vd += f" (LANE<={v['lane_ub']}, M={v.get('M')})"
            tags.append(dict(cell=cell, centre=[x, y], verdict=vd, source="A141 T2"))
        if not tags:
            for c, cell in CORNER_CELL.items():
                (x, y) = M.slot_centres([cell], S0)[0]
                tags.append(dict(cell=cell, centre=[x, y], verdict="n/a", source="none"))
        return tags
    seen = set()
    for r in tbl("a141_slots").get(node["id"], []):
        try:
            (x, y) = M.slot_centres([r["slot"]], S0)[0]
        except Exception:                                            # noqa: BLE001
            continue
        vd = r["verdict"] + (f" (LANE<={r['lane_ub']}, M={r.get('M')})"
                             if r.get("lane_ub") is not None else "")
        tags.append(dict(cell=r["slot"], centre=[x, y], verdict=vd, source="A141 T4 slots"))
        seen.add(r["slot"])
    for r in tbl("a141_a5760").get(node["id"], []):
        cell = r.get("slot") or CORNER_CELL.get(r.get("corner") or "", None)
        if not cell or cell in seen:
            continue
        try:
            (x, y) = M.slot_centres([cell], S0)[0]
        except Exception:                                            # noqa: BLE001
            continue
        vd = r.get("verdict") or "n/a"
        if r.get("lane_ub") is not None:
            vd += f" (LANE<={r['lane_ub']}, M={r.get('M')})"
        tags.append(dict(cell=cell, centre=[x, y], verdict=vd, source="A141 T2 (A57/A60)"))
        seen.add(cell)
    if not tags:
        for c, cell in CORNER_CELL.items():
            (x, y) = M.slot_centres([cell], S0)[0]
            tags.append(dict(cell=cell, centre=[x, y], verdict="n/a", source="none"))
    return tags[:8]


def _clip(node):
    """A131's exact pin clip.  k0_00 has NO pins, so the clip is vacuous there and the drawn
    'clipped box' is the original centre box; say so rather than drawing a fake."""
    npin = sum(1 for k in node["kinds"] if k["kind"] == "pin")
    if npin == 0:
        return {}, ("PIN-CLIP (A131): k0_00 has NO pins, so the pin clip is VACUOUS on this node "
                    "and the clipped centre box IS the original box (black dashed). The only "
                    "shrink available here is the other conditioned squares' K'.")
    import pinclip
    import gallery142 as G142
    from caselp import Box
    sl = G142.slots_for("A60" if node["camp"] == "A60" else "A57", node["id"])
    a_pin = min(float(k["a_exact"]) for k in node["kinds"] if k["kind"] == "pin")
    a_pin = pinclip.Fr(str(a_pin)).limit_denominator(10 ** 14)
    out, notes = {}, []
    for i, k in enumerate(node["kinds"]):
        if k["kind"] != "H":
            continue
        try:
            cl = pinclip.clip_node(k["box"], sl, nsub=8, a_pin=a_pin)
        except Exception as ex:                                      # noqa: BLE001
            notes.append(f"{node['onames'][i]}: clip refused ({str(ex)[:50]})")
            continue
        if cl.get("union_rect"):
            u = [float(v) for v in cl["union_rect"]]
            out[node["onames"][i]] = u
        notes.append(f"{node['onames'][i]}: keeps {float(cl['kept_vol']):.4f} of the box over 8 "
                     f"tilt sub-bins ({int(cl['n_empty'])} EMPTY), union box "
                     f"{float(cl['kept_union']):.4f}"
                     + ("  — EMPTY: DEAD by pin geometry" if cl.get("empty") else ""))
    return out, ("PIN-CLIP (A131, exact rationals at the A135 exact pin core a = "
                 f"{float(a_pin):.9f}, 8 tilt sub-bins; orange dashed inside the black centre "
                 f"box): " + "; ".join(notes))


def _t5(node):
    """the T5'''' (polygon-core) leaf: K' inside the container, K' pairwise interior-disjoint."""
    exc, pairs = -9e9, []
    for i, P in enumerate(node["obstacles"]):
        exc = max(exc, max(max(-x, x - S0, -y, y - S0) for x, y in P))
    Hs = [i for i, k in enumerate(node["kinds"]) if k["kind"] == "H"]
    for a in range(len(node["obstacles"])):
        for b in range(a + 1, len(node["obstacles"])):
            d = float(polycore.poly_poly_depth(np.array(node["obstacles"][a], float),
                                               np.array(node["obstacles"][b], float)))
            pairs.append((node["onames"][a], node["onames"][b], d))
    worst = max([p[2] for p in pairs]) if pairs else None
    dead = bool(exc > 0.0 or (worst is not None and worst > 0.0))
    return dict(excursion=float(exc), worst_pair=worst, pairs=pairs, dead=dead)


def _near(node):
    """panel N's geometry: A128's near-packing, else A107's minimised shadow, else raw support."""
    if node["camp"] == "k0":
        np_ = C140.a128_nearpack(node["id"])
        if np_ is not None:
            return ([tuple(map(float, q)) for q in np_["poses"]], float(np_["side"]), True,
                    f"A128 near-packing of the converged support, all 11 squares polished free; "
                    f"worst gap {np_['worst_gap']:+.1e}")
        sid, _ = C140.a107_shadow(node["alias"]) if node.get("alias") else (None, None)
        if sid:
            sh = C140.a107_shadow_geom(sid)
            poses = [tuple(map(float, f)) for f in sh["free"]] + \
                    [(x, y, 0.0) for (x, y) in M.slot_centres(sh["slots"], sh["s"])]
            return poses, float(sh["s"]), True, (
                f"A107 shadow {sid} minimised to s* = {sh['s']:.6f} (s* - s-hat {sh['ds']:+.6f}); "
                f"the cell enters {sid} through its A99/A38 alias {node['alias']}")
    else:
        import gallery142 as G142
        for sid in G142.shadow_families(node["id"]):
            sh = G142.shadow_geom(sid)
            if not sh:
                continue
            poses = [tuple(map(float, f)) for f in sh["free"]] + \
                    [(x, y, 0.0) for (x, y) in M.slot_centres(sh["slots"], sh["s"])]
            return poses, float(sh["s"]), True, (
                f"A107 shadow {sid} minimised to s* = {sh['s']:.6f} (s* - s-hat {sh['ds']:+.6f}), "
                f"{sh['nsquares']} squares, {sh['nfree']} free; {sh['nnodes']} nodes explained")
    pk = [p for p in node["packing"] if float(p.get("y", 0.0)) > 0.5]
    poses = [(float(p["cx"]), float(p["cy"]), float(p["theta"])) for p in pk]
    for k in node["kinds"]:
        if k["kind"] == "H":
            b = k["box"]
            poses.append((0.5 * (b.x0 + b.x1), 0.5 * (b.y0 + b.y1),
                          math.radians(0.5 * (b.th0 + b.th1))))
        else:
            poses.append((k["c"][0], k["c"][1], 0.0))
    return poses, S0, False, (
        "RAW integral dual support at s0 plus the hypothesis squares at their box centres: this "
        "node has neither an A107 shadow family nor a polished near-packing, so this is NOT a "
        "packing and NOT minimised — the overlaps are the relaxation's slack")


def _family(node):
    if node["camp"] == "k0":
        sid, _ = C140.a107_shadow(node["alias"]) if node.get("alias") else (None, None)
        return sid or "none"
    import gallery142 as G142
    return ";".join(G142.shadow_families(node["id"])) or "none"


def finish(node):
    """fill everything the page prints that is not geometry: the header, the two generated lines,
    panel S's and panel N's provenance, and the CSV/summary fields."""
    node["lane_tags"] = _lane_tags(node)
    node["clip"], node["clip_note"] = _clip(node)
    node["t5"] = _t5(node)
    node["poses"], node["s_star"], node["is_packing"], node["prov"] = _near(node)
    node["family"] = _family(node)
    node["subtree_s"] = node.get("subtree_s") or subtree_cost(
        node["level"], node.get("kept8", 1.0), node.get("n_open_desc", 0))

    # ---- panel S provenance: the latest record, and what has been re-solved on top of it
    ex = tbl("exactcore140").get(node["id"]) if node["camp"] == "k0" else None
    iv = tbl("invitro140").get(node["id"]) if node["camp"] == "k0" else None
    node["record_label"] = (f"stock LP record {os.path.basename(node['record'])} — tau "
                            f"{node['tau']:.9f} / budget {node['budget']}, minmass "
                            f"{node['minmass']:.3f}, converged {node['converged']}")
    bits = ["This is the STOCK LP support (the row filter was the AXIS core K(a)); the columns "
            "drawn red overlap a certified core K' and count as impossible."]
    if ex and ex.get("tau") is not None:
        bits.append(f"A140's EXACT-AXIS-CORE re-solve of this cell reached tau {ex['tau']:.6f} "
                    f"(eta {ex['eta']:+.2e}), converged {ex['converged']}, "
                    f"{ex.get('support')} support columns"
                    + (" — KILL" if ex.get("kills") else " — no kill")
                    + "; that run stored counts, not placements, so the support drawn here is "
                      "still the stock one.")
    if iv and iv.get("tau") is not None:
        bits.append(f"A140's K'-pruned in-vitro re-solve reached tau {iv['tau']:.6f} "
                    f"(eta {iv['eta']:+.4f}), converged {iv['converged']}"
                    + (" — LP-DEAD under K', certificate pending" if iv.get("kills_converged")
                       else (" — kill candidate, unconverged at the cap" if iv.get("kills")
                             else " — no kill")) + ".")
    node["support_note"] = " ".join(bits)

    # ---- the header
    node["headline"] = (f"{node['id']}  —  {node['cls']}, level {node['level']}  ({node['src']})")
    node["subline"] = (
        f"tau {node['tau']:.9f} / budget {node['budget']} = 11 - "
        f"{len(node['boxes'])} core(s)  (eta {node['tau'] - node['budget']:+.2e}), minmass "
        f"{node['minmass']:.3f}, converged {node['converged']}   |   family {node['family']}   |   "
        f"subtree cost {node['subtree_s']:.0f} s = {node['subtree_s'] / 3600.0:.2f} CPU-h "
        f"(A142's C(L) = pL*850 + pA*(300 + 8*C(L+1)), residual = 8*C(L+1)*kept8)   |   record "
        f"{node['record']}")

    # ---- WHAT TO LOOK FOR (generated from the geometry)
    look = []
    reg, disk = node["region"], node["disk"]
    if disk["n_max"] < node["budget"]:
        look.append(f"DISK BOUND KILLS IT: at most {disk['n_max']} more unit squares fit in the "
                    f"free centre region, budget is {node['budget']}")
    else:
        look.append(f"free centre region: green {reg.area_green():.3f} + undecided "
                    f"{reg.area_open() - reg.area_green():.3f} = {reg.area_open():.3f}, against "
                    f"{node['budget']} remaining squares x 1 unit of area = {node['budget']}; "
                    f"disk bound says at most {disk['n_max']} more squares fit")
    nn = [p for p in node["pockets"] if p["gap"] < 1.0]
    if nn:
        look.append(f"{len(nn)} pocket(s) narrower than 1 (nothing fits): "
                    + ", ".join(f"{p['to']} {p['gap']:.3f}" for p in nn[:4]))
    else:
        look.append(f"no pocket narrower than 1 (narrowest {node['pockets'][0]['to']} "
                    f"{node['pockets'][0]['gap']:.3f})")
    hot = [t for t in node["lane_tags"]
           if t["verdict"].startswith("KILL") or "NEAR-MISS" in t["verdict"]
           or "LANE<=1" in t["verdict"] or "LANE<=0" in t["verdict"]]
    if hot:
        look.append("lane: " + ", ".join(f"{t['cell']} {t['verdict']}" for t in hot))
    g = node["guard"][0] if node["guard"] else None
    if g and g["rhs"] <= 0.15:
        look.append(f"guard line {g['orient']}={g['off']:.4f} ({g['tag']}) has chord sum "
                    f"{g['chord_sum']:.4f} within 0.15 of s0 (rhs {g['rhs']:.4f})"
                    + (" — NEGATIVE rhs is an outright contradiction" if g["rhs"] < 0 else ""))
    elif g:
        look.append(f"no guard line within 0.15 of s0 (tightest rhs {g['rhs']:.4f} on "
                    f"{g['orient']}={g['off']:.4f})")
    node["look"] = "; ".join(look) + "."

    # ---- the geometric leaves already run
    lv = []
    lv.append("CLIP (A131): " + ("vacuous, k0_00 has no pins" if not node["clip"]
                                 and node["camp"] == "k0"
                                 else node["clip_note"].split("): ", 1)[-1][:180]))
    t5 = node["t5"]
    lv.append(f"T5'''' (polygon core): K' worst container excursion {t5['excursion']:+.2e}, worst "
              + (f"K'-K' pair depth {t5['worst_pair']:+.2e}" if t5["worst_pair"] is not None
                 else "K'-K' pair depth n/a (one core)") + " — "
              + ("DEAD" if t5["dead"] else "alive (no T5-type kill)"))
    lt = ", ".join(f"{t['cell']} {t['verdict']}" for t in node["lane_tags"])
    lv.append(f"LANE (A141 K' lane): {lt or 'not run'}")
    dp = tbl("a141_deep").get(node["id"], [])
    if dp:
        lv.append("CONDITIONAL LANE (A141 T5): " + "; ".join(
            (f"{r.get('corner', '?')} lane_ub {r.get('lane_ub')} M {r.get('M')} "
             f"{r.get('leaves', r.get('n_pieces', '?'))} leaves, {r.get('open', '?')} open"
             + (" KILL" if r.get("kill") else ""))
            if r.get("kind") != "two-crowd" else
            f"{r.get('corner', '?')} two-crowd witness gap {r.get('gap', 0):.4f}"
            for r in dp[:4]))
    else:
        lv.append("CONDITIONAL LANE (A141 T5): not run on this node")
    if node["guard"]:
        g0 = node["guard"][0]
        lv.append(f"GUARD LINE (A144): tightest of {len(node['guard_all'])} lines is "
                  f"{g0['orient']}={g0['off']:.4f} ({g0['tag']}), chord sum {g0['chord_sum']:.4f} "
                  f"vs s0 {S0:.4f}, rhs {g0['rhs']:.4f} — "
                  + ("CONTRADICTION (rhs < 0)" if g0["rhs"] < 0 else "no kill"))
    a144 = tbl("a144").get(node["id"])
    if a144:
        lv.append(f"GUARD LINE (A144 stored offline sweep): max violation "
                  f"{a144['max_viol']:+.4f} on {a144['max_viol_line']['tag']}, "
                  f"{a144['n_lines_violated']} line(s) violated by the stored support")
    if node.get("leafkill"):
        lv.append("KILL LEAF: " + node["leafkill"])
    node["leaves"] = "  |  ".join(lv)
    node["provenance"] = (
        f"A148 v4 page, generated {os.path.basename(__file__)} + gallery148.py + geo148.py. "
        f"Region {node['region'].green.shape[0]}^2 grid x {node['region'].ntilt} tilts in "
        f"{node.get('region_s')} s. Sources: record {node['record']}; K' A132 polycore (certified "
        f"vertices); exact pin/axis cores A135; clip A131; lane A141; guard lines A144; subtree "
        f"cost A142; near-packing A128/A107.")
    return node


# ------------------------------------------------------------------ csv / summary
def csv_row(node, imposs, names, exc, mg):
    reg, disk = node["region"], node["disk"]
    nn = [p for p in node["pockets"] if p["gap"] < 1.0]
    g = node["guard"][0] if node["guard"] else {}
    nfree = sum(1 for n in names if n.startswith("f"))
    return dict(
        file=f"{node['id']}.svg", node=node["id"], camp=node["camp"], cls=node["cls"],
        level=node["level"], family=node["family"], record=node["record"],
        tau=f"{node['tau']:.9f}", budget=node["budget"],
        eta=f"{node['tau'] - node['budget']:+.3e}", minmass=f"{node['minmass']:.3f}",
        converged=node["converged"],
        subtree_cost_s=f"{node['subtree_s']:.0f}",
        subtree_cost_cpuh=f"{node['subtree_s'] / 3600.0:.2f}",
        s_star=f"{node['s_star']:.6f}", s_star_minus_s0=f"{node['s_star'] - S0:+.6f}",
        s_star_minus_shat=f"{node['s_star'] - SHAT:+.6f}",
        realisable_at_s0=("no" if node["s_star"] - S0 > 1e-6
                          else ("yes" if node["is_packing"] else "n/a (raw support)")),
        n_squares_panelN=len(names), n_free_panelN=nfree,
        grid_pitch=f"{reg.pitch:.5f}", grid_tilts=reg.ntilt, region_margin=f"{reg.margin:.5f}",
        feasible_area_green=f"{reg.area_green():.4f}",
        feasible_area_open=f"{reg.area_open():.4f}",
        disk_bound_nmax=disk["n_max"], disk_bound_kills=("YES" if disk["n_max"] < node["budget"]
                                                        else "no"),
        sample_green_hits=node["sample"]["green"]["hits"],
        sample_blocked_hits=node["sample"]["blocked"]["hits"],
        narrowest_pocket=f"{node['pockets'][0]['to']} {node['pockets'][0]['gap']:.4f}",
        n_pockets_lt1=len(nn),
        pockets_lt1="; ".join(f"{p['to']} {p['gap']:.3f}" for p in nn[:6]),
        lane_tags="; ".join(f"{t['cell']}:{t['verdict']}" for t in node["lane_tags"]),
        t5_excursion=f"{node['t5']['excursion']:+.2e}",
        t5_worst_pair=(f"{node['t5']['worst_pair']:+.2e}"
                       if node["t5"]["worst_pair"] is not None else "n/a (one core)"),
        t5_verdict=("DEAD" if node["t5"]["dead"] else "alive"),
        clip=node["clip_note"][:200],
        guard_tightest=(f"{g.get('orient')}={g.get('off', 0):.4f} ({g.get('tag')}) chord sum "
                        f"{g.get('chord_sum', 0):.4f} rhs {g.get('rhs', 0):.4f}" if g else "n/a"),
        guard_within_015=("yes" if g and g.get("rhs", 9) <= 0.15 else "no"),
        n_support=len(node["packing"]), n_impossible=len(imposs),
        w_impossible=f"{sum(r['y'] for r in imposs):.4f}",
        panelN_min_sat=f"{mg:+.2e}", panelN_excursion=f"{exc:+.2e}",
        killed_banner=node.get("banner", ""),
        what_to_look_for=node["look"],
        PI_reading="", PI_shortcut="", PI_load_path="", PI_drain_or_kill="")


def summary(node, imposs, bad, names, exc, mg, W, H):
    reg = node["region"]
    return dict(
        id=node["id"], camp=node["camp"], cls=node["cls"], level=node["level"],
        family=node["family"], record=node["record"], tau=node["tau"], budget=node["budget"],
        minmass=node["minmass"], converged=node["converged"], subtree_s=node["subtree_s"],
        s_star=node["s_star"], is_packing=node["is_packing"],
        grid=dict(n=int(reg.green.shape[0]), pitch=reg.pitch, tilts=reg.ntilt,
                  margin=reg.margin, area_green=reg.area_green(), area_open=reg.area_open()),
        disk=node["disk"], sample=node["sample"],
        pockets=[dict(to=p["to"], gap=p["gap"], kind=p["kind"]) for p in node["pockets"]],
        guard=node["guard"], n_guard_lines=len(node["guard_all"]),
        lane_tags=node["lane_tags"], t5=dict((k, v) for k, v in node["t5"].items()
                                             if k != "pairs"),
        t5_pairs=node["t5"]["pairs"], clip_note=node["clip_note"], clip=node["clip"],
        n_support=len(node["packing"]), n_impossible=len(imposs), impossible=imposs,
        n_outside=bad, panelN_names=names, panelN_min_sat=mg, panelN_excursion=exc,
        look=node["look"], leaves=node["leaves"], banner=node.get("banner", ""),
        width=W, height=H, region_s=node.get("region_s"))
