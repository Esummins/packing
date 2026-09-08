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
for _p in (os.path.join(ATT, "A57-shadow-trees", "code"),
           os.path.join(ATT, "A132-polygon-core", "code"),
           os.path.join(ATT, "A135-polycore-verifier", "code"),
           os.path.join(A131, "code"), os.path.join(A144, "code"),
           os.path.join(A107, "code"),
           os.path.join(A140, "code"), os.path.join(A142, "code"), HERE):
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
        # t2_a5760 is one row PER NODE with a nested `cells` list, not one row per cell.  The v4
        # draft read it as one row per cell and so found no lane verdict at all on the A57/A60
        # pages; flatten it here.
        v = {}
        for f in sorted(glob.glob(os.path.join(A141, "results", "t2_a5760_s*.jsonl"))):
            for r in _jl(f):
                nid = r.get("nid") or r.get("id")
                for c in (r.get("cells") or []):
                    v.setdefault(nid, []).append(dict(c, slot=c.get("cell"), nid=nid,
                                                      src=r.get("src")))
    elif name == "a157":
        # A157's screen of A141's UNDECIDED slot cells: per (node, slot) a WITNESSED free pose and,
        # where the sample found one, a witnessed DISJOINT PAIR of free meeters.  These are the
        # hairline grazers a lane tag alone hides.
        v = {}
        for f in sorted(glob.glob(os.path.join(ATT, "A157-undecided-slots", "results",
                                               "screen157*.jsonl"))):
            for r in _jl(f):
                v[(r["nid"], r["slot"])] = r
    elif name == "a141_twocrowd":
        v = {}
        for r in (_j(os.path.join(A141, "results", "t5_twocrowd.json"), []) or []):
            v.setdefault((r["cell"], r.get("corner")), r)
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
    elif name == "a145":
        v = {}
        for f in sorted(glob.glob(os.path.join(ATT, "A145-impossible-weight", "results",
                                               "resolves145*.jsonl"))):
            for r in _jl(f):
                v[r["id"]] = r
        for f in sorted(glob.glob(os.path.join(ATT, "A137-night-shift-2", "results",
                                               "emit_lp*.jsonl"))) +                 sorted(glob.glob(os.path.join(ATT, "A137-night-shift-2", "results",
                                              "exact_reemit*.jsonl"))):
            for r in _jl(f):
                if r.get("id"):
                    v[r["id"]] = r
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


def night_kills():
    """Everything that has killed an A57/A60 node SINCE A142 built population142.json.

    A142's own removals (A131 pin-clip, A135 polygon + LP-certified, A124 trim-empty, and the
    descendants of all of those) are already baked into `rank_a57`, so this only has to add what
    landed afterwards.  Read-only: A57's own tree records, A141's two lane-kill files, A137's
    night records if the attempt has produced any, and A144's guard rows with a NEGATIVE rhs.
    Returns {id: reason}."""
    out = {}
    for r in _jl(os.path.join(A141, "results", "polycore_lane_kills.jsonl")):
        out.setdefault(r["nid"], f"A141 K' lane leaf on {r.get('corner')}")
    for f in ("t4_slots.jsonl", "t4_y0460.jsonl"):
        for r in _jl(os.path.join(A141, "results", f)):
            if str(r.get("verdict", "")).startswith("KILL"):
                out.setdefault(r["nid"], f"A141 K' slot lane leaf on {r.get('slot')}")
    for f in sorted(glob.glob(os.path.join(A141, "results", "t2_a5760_s*.jsonl"))):
        for r in _jl(f):
            if str(r.get("verdict", "")).startswith("KILL") and r.get("nid"):
                out.setdefault(r["nid"], f"A141 K' lane leaf on {r.get('corner', r.get('slot'))}")
    for nid, r in tbl("a145").items():
        if str(r.get("result", "")).startswith("PASS"):
            out.setdefault(nid, f"A145/A137 exact-core re-solve certified dead ({r['result']}, "
                                f"tau {r.get('tau')})")
    a137 = os.path.join(ATT, "A137-night-shift-2", "results")
    for f in sorted(glob.glob(os.path.join(a137, "*.jsonl"))):
        for r in _jl(f):
            nid = r.get("id") or r.get("nid")
            v = str(r.get("verdict") or r.get("cert") or "")
            res = str(r.get("result") or "")
            if nid and (v.upper().startswith(("CERTIFIED", "KILL", "DEAD"))
                        or res.startswith("PASS")
                        or r.get("kills_converged") or r.get("emptied8")):
                out.setdefault(nid, f"A137 night: {v or res or 'kill'} "
                                    f"({os.path.basename(f)})")
    # A57's own tree rows: a node whose stored cert has since become a logic kill / PASS
    for f in sorted(glob.glob(os.path.join(ATT, "A57-shadow-trees", "results",
                                           "tree_k5_1*_interior_G1*.jsonl"))):
        for r in _jl(f):
            c = str(r.get("cert") or "")
            if r.get("id") and (c.startswith("KILL-BY-LOGIC") or c.startswith("CERTIFIED")):
                out.setdefault(r["id"], f"A57 tree record: {c[:40]}")
    # CLIP-KILL CERTIFICATES ON DISK.  A142's own A60 clip sweep (clipsweep142.py) wrote its kills
    # as certificates only -- `attempts/A142-a57-review-gallery/certs/a60/<id>.clipkill.json` --
    # with no jsonl result row anywhere, so a kill list built from *.jsonl alone misses them.  The
    # certificate file IS the record; take the id from its name.
    for f in glob.glob(os.path.join(ATT, "*", "certs", "**", "*.clipkill.json"), recursive=True):
        out.setdefault(os.path.basename(f)[:-len(".clipkill.json")],
                       f"pin-clip kill certificate on disk ({os.path.relpath(f, ROOT)})")
    for r in _jl(os.path.join(A144, "results", "offline144.jsonl")):
        for row in (r.get("top_rows") or []):
            if float(row.get("rhs", 1.0)) < 0.0:
                out.setdefault(r["id"], "A144 guard line with rhs < 0 (contradiction)")
    return out


def _a57_population(which):
    """the A57/A60 pages: A142's subtree-cost ranking, refreshed against the night's records."""
    import gallery142 as G142
    pop = tbl("pop142")
    kills = night_kills()
    dead = set(kills)
    out = []
    for key, camp, n in (("rank_a57", "A57", 40), ("rank_a60", "A60", 20)):
        for i, r in enumerate(pop.get(key, [])):
            if len(([x for x in out if x["camp"] == camp])) >= n:
                break
            if r["id"] in dead or any(r["id"].startswith(k + "_D") for k in dead):
                continue
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
                            rank_a142=i + 1, subtree_s=float(r.get("subtree_s") or 0.0),
                            verdict=r.get("verdict"), which=which))
    for camp in ("A57", "A60"):
        k = 0
        for r in out:
            if r["camp"] == camp:
                k += 1
                r["rank"] = k
                r["n_pop"] = sum(1 for x in out if x["camp"] == camp)
    _C["night_kills"] = kills
    return out


# ------------------------------------------------------------------ per-node completion
def _lane_text(r):
    """the tag's second line: the verdict with BOTH lane bounds and M, never just the verdict.

    `lane_ub` alone hides the thing that refutes a reading: `lane_lb` is the number of free
    meeters the SAMPLE actually found, so `lane_lb >= 1` means a witnessed square reaches the
    cell however tight the certified upper bound looks."""
    vd = r.get("verdict") or "n/a"
    bits = []
    if r.get("lane_ub") is not None:
        bits.append(f"ub {r['lane_ub']}")
    if r.get("lane_lb") is not None:
        bits.append(f"lb {r['lane_lb']}")
    if r.get("M") is not None:
        bits.append(f"M {r['M']}" + ("" if r.get("M_exact") else "?"))
    return vd + (" (LANE " + ", ".join(bits) + ")" if bits else "")


def cell_rect(cell, s=S0):
    """the closed unit cell of a slot name, in the CONTAINER frame."""
    c = cell.split("(")[0]
    i, j = (int(v) for v in cell.split("(")[1].rstrip(")").split(","))
    if c == "BL":
        return (i, i + 1.0, j, j + 1.0)
    if c == "BR":
        return (s - (i + 1.0), s - i, j, j + 1.0)
    if c == "TR":
        return (s - (i + 1.0), s - i, s - (j + 1.0), s - j)
    if c == "TL":
        return (i, i + 1.0, s - (j + 1.0), s - j)
    raise ValueError(cell)


def corner_to_container(cell, u, v, th_deg, s=S0):
    """A141 and A157 run the lane test IN THE CELL'S CORNER FRAME (`polylane.centre_window` is
    built from `cell_rect(i, j) = [i, i+1] x [j, j+1]` with the corner at the origin and the axes
    pointing inward), so every pose in their records is a corner-frame pose.  This is the D4 map
    back to the container frame; a reflection negates the tilt, and the tilt is 90-periodic for a
    square.  The cell CENTRES happen to agree with `minimise.slot_centres` in both frames, which
    is why a wrongly-framed pose is the only thing that shows the mistake -- the first draft drew
    c0_Y0076's TL(0,0) witness at y = 0.686 instead of y = 3.191."""
    c = cell.split("(")[0]
    if c == "BL":
        return (u, v, th_deg % 90.0)
    if c == "BR":
        return (s - u, v, (-th_deg) % 90.0)
    if c == "TR":
        return (s - u, s - v, th_deg % 90.0)
    if c == "TL":
        return (u, s - v, (-th_deg) % 90.0)
    return (u, v, th_deg % 90.0)


def _depth_into_cell(pose, cell):
    x0, x1, y0, y1 = cell_rect(cell)
    P = G.sqpoly(pose[0], pose[1], math.radians(pose[2]))
    return -G.sat_gap(P, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


def _witness_poses(node, cell):
    """The WITNESSED free meeters of a cell, as CONTAINER-frame poses to draw: A157's screen (a
    free pose, and a disjoint PAIR where its sample found one) for the A57/A60 slots, A141's
    two-crowd witness (a free square and the conditioned square, disjoint) for the k0 corners.

    A157's poses are corner-frame and are transported; A141's two-crowd poses come from a
    different code path that already works in the container frame and are left alone.  Every
    witness is then CHECKED against the cell it claims to meet, and one that does not meet it is
    kept but marked `meets_cell: false` and not drawn -- a silent reframing error would otherwise
    put a square in the wrong place and look authoritative."""
    out = []
    if node["camp"] == "k0":
        corner = cell.split("(")[0]
        r = tbl("a141_twocrowd").get((node["id"], corner))
        if r:
            if r.get("free"):
                out.append(dict(pose=[float(v) for v in r["free"]], role="free meeter",
                                source="A141 T5 two-crowd", frame="container"))
            if r.get("H"):
                out.append(dict(pose=[float(v) for v in r["H"]], role="conditioned square H",
                                source="A141 T5 two-crowd", frame="container",
                                gap=float(r.get("gap", 0.0))))
    else:
        r = tbl("a157").get((node["id"], cell))
        if r:
            p = r.get("pair")
            if p:
                for nm, k in (("free meeter a", "a"), ("free meeter b", "b")):
                    if p.get(k):
                        out.append(dict(pose=list(corner_to_container(cell, *[float(v)
                                                                              for v in p[k]])),
                                        role=nm, source="A157 screen (disjoint pair)",
                                        frame="corner->container",
                                        gap=float(p.get("gap", 0.0))))
            else:
                w = r.get("witness")
                if w and w.get("free") and w.get("c") is not None:
                    out.append(dict(pose=list(corner_to_container(
                        cell, float(w["c"][0]), float(w["c"][1]), float(w["theta_deg"]))),
                        role="free meeter", source="A157 screen (witness)",
                        frame="corner->container",
                        margin=float(r.get("best_margin") or 0.0)))
    for w in out:
        d = _depth_into_cell(w["pose"], cell)
        w["depth_into_cell"] = float(d)
        # `meets_cell` is a truthful geometric fact, never a licence to draw: a FREE MEETER must
        # meet the cell (if it does not, the pose was mis-framed and the page must not show it),
        # while the conditioned square of a two-crowd pair is the pair's OTHER square and is drawn
        # with its (possibly negative) reach printed, which is the informative part.
        w["meets_cell"] = bool(d > 0.0)
        w["is_free_meeter"] = bool(w["role"].startswith("free"))
        w["draw"] = bool(w["meets_cell"] or not w["is_free_meeter"])
    return out


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
            tags.append(dict(cell=cell, centre=[x, y], verdict=_lane_text(v), source="A141 T2",
                             lane_ub=v.get("lane_ub"), lane_lb=v.get("lane_lb"), M=v.get("M"),
                             witness=_witness_poses(node, cell)))
        if not tags:
            for c, cell in CORNER_CELL.items():
                (x, y) = M.slot_centres([cell], S0)[0]
                tags.append(dict(cell=cell, centre=[x, y], verdict="n/a", source="none",
                                 lane_ub=None, lane_lb=None, M=None,
                                 witness=_witness_poses(node, cell)))
        return tags
    seen = set()
    for src, rows in (("A141 T4 slots", tbl("a141_slots").get(node["id"], [])),
                      ("A141 T2 (A57/A60)", tbl("a141_a5760").get(node["id"], []))):
        for r in rows:
            cell = r.get("slot") or CORNER_CELL.get(r.get("corner") or "", None)
            if not cell or cell in seen:
                continue
            try:
                (x, y) = M.slot_centres([cell], S0)[0]
            except Exception:                                        # noqa: BLE001
                continue
            tags.append(dict(cell=cell, centre=[x, y], verdict=_lane_text(r), source=src,
                             lane_ub=r.get("lane_ub"), lane_lb=r.get("lane_lb"), M=r.get("M"),
                             witness=_witness_poses(node, cell)))
            seen.add(cell)
    if not tags:
        for c, cell in CORNER_CELL.items():
            (x, y) = M.slot_centres([cell], S0)[0]
            tags.append(dict(cell=cell, centre=[x, y], verdict="n/a", source="none",
                             lane_ub=None, lane_lb=None, M=None,
                             witness=_witness_poses(node, cell)))
    # a tag with a WITNESSED meeter is the one that refutes a reading, so it is never dropped
    tags.sort(key=lambda t: (0 if t["witness"] else 1,
                             0 if str(t["verdict"]).startswith(("KILL", "NEAR-MISS")) else 1,
                             t["cell"]))
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
    if node["t5"]["dead"] and not node.get("banner"):
        t5 = node["t5"]
        who = max(t5["pairs"], key=lambda p: p[2]) if t5["pairs"] else None
        if who is not None and who[2] > 0.0:
            node["banner"] = (f"KILLED — T5'''' : the certified cores of {who[0]} and {who[1]} "
                              f"OVERLAP by {who[2]:.6f}, so those two squares can never be "
                              f"interior-disjoint. Dead by geometry, no LP.")
            node["leafkill"] = (f"T5'''' polygon core meets pin core: depth(K'({who[0]}), "
                                f"K'({who[1]})) = {who[2]:.6f} > 0 at every admissible pose")
        else:
            node["banner"] = (f"KILLED — T5'''' : K' leaves the container by "
                              f"{t5['excursion']:.6f}. Dead by geometry, no LP.")
            node["leafkill"] = "T5'''' polygon core not contained in the container"
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
    a145 = tbl("a145").get(node["id"]) if node["camp"] != "k0" else None
    if a145:
        bits.append(f"A145/A137's EXACT-CORE re-solve of this node (a_used exact on "
                    f"{a145.get('frac_exact')} of its cores, cap {a145.get('cap')} s) reached tau "
                    f"{a145.get('tau')} (eta {a145.get('eta')}), converged "
                    f"{a145.get('converged')}, {a145.get('support')} support columns — result "
                    f"{a145.get('result')}"
                    + (f", certificate {a145.get('verifier')}" if a145.get("verifier") else "")
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
    node["headline"] = (f"{node['id']}  —  {node['cls']}, level {node['level']}  ({node['src']})"
                        + (f", rank {node['rank']} of {node.get('n_pop')} by subtree cost"
                           if node.get("rank") else "")
                        + (f", recorded {node['verdict']}" if node.get("verdict") else ""))
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
        look.append(f"CERTIFIED-FREE centre area (green) {reg.area_green():.3f}, plus "
                    f"{reg.area_open() - reg.area_green():.3f} that is UNDECIDED (grey stipple = "
                    f"clearance within the margin, NOT feasible - do not read a stippled strip as "
                    f"free), against {node['budget']} remaining squares x 1 unit of area = "
                    f"{node['budget']}; the disk bound over green+undecided says at most "
                    f"{disk['n_max']} more squares fit")
    nn = [p for p in node["pockets"] if p["gap"] < 1.0]
    if nn:
        look.append(f"{len(nn)} pocket(s) narrower than 1 (nothing fits): "
                    + ", ".join(f"{p['to']} {p['gap']:.3f}" for p in nn[:4]))
    elif node["pockets"]:
        look.append(f"no pocket narrower than 1 (narrowest {node['pockets'][0]['to']} "
                    f"{node['pockets'][0]['gap']:.3f})")
    else:
        look.append("no pocket at all: every measured clearance is a contact below 0.05")
    hot = [t for t in node["lane_tags"]
           if t["verdict"].startswith("KILL") or "NEAR-MISS" in t["verdict"]
           or "LANE<=1" in t["verdict"] or "LANE<=0" in t["verdict"]]
    if hot:
        look.append("lane: " + ", ".join(f"{t['cell']} {t['verdict']}" for t in hot))
    wit = [(t["cell"], w) for t in node["lane_tags"] for w in t.get("witness", [])]
    if wit:
        look.append(f"{len(wit)} WITNESSED free meeter(s) drawn (thin black): "
                    + ", ".join(f"{c} {w['role']} reaches "
                                + (f"{w['depth_into_cell']:+.4f}"
                                   if w.get("depth_into_cell") is not None else "?")
                                + " into the cell" for c, w in wit[:4])
                    + " - a hairline grazer refutes 'nothing reaches this cell'")
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
        f"A148 v4 page, generated {os.path.basename(__file__)} + gallery148.py + geo148.py"
        + (f"; campaign records READ AT {os.environ['A148_STAMP']} (A137 was still running and "
           f"pauses at 07:00, so this page is the night's records AS THEY STOOD at that moment)"
           if os.environ.get("A148_STAMP") else "") + ". "
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
        rank=node.get("rank", ""), rank_a142=node.get("rank_a142", ""),
        verdict=node.get("verdict", ""),
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
        narrowest_pocket=(f"{node['pockets'][0]['to']} {node['pockets'][0]['gap']:.4f}"
                          if node["pockets"] else "none (all clearances are contacts)"),
        n_contacts=(node["pockets"][0].get("n_flush", 0) if node["pockets"] else 0),
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
        n_impossible_also_pin_core=sum(1 for r in imposs if r.get("also_pin_core")),
        w_impossible_also_pin_core=f"{sum(r['y'] for r in imposs if r.get('also_pin_core')):.4f}",
        n_witnessed_meeters=node.get("n_witness_drawn", 0),
        witnessed_meeters="; ".join(
            f"{t['cell']} {w['role']} depth "
            + (f"{w['depth_into_cell']:+.5f}" if w.get("depth_into_cell") is not None else "?")
            + f" @{w['pose'][2]:.2f}deg [{w['source']}]"
            for t in node["lane_tags"] for w in t.get("witness", [])),
        lane_bounds="; ".join(f"{t['cell']}:ub={t.get('lane_ub')},lb={t.get('lane_lb')},"
                              f"M={t.get('M')}" for t in node["lane_tags"]),
        area_undecided=f"{node['region'].area_open() - node['region'].area_green():.4f}",
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
