"""A166 -- assemble `results/subtree166.jsonl` (the one-line-per-cell verdict record the brief asks
for) and `notes/tables.md` from the result files.  No geometry, no LP: it only reads and formats.

    python code/report166.py
"""
import json
import os
import sys
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import cells166 as C                                            # noqa: E402

RES = os.path.join(BASE, "results")
NOTES = os.path.join(BASE, "notes")


def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] \
        if os.path.exists(p) else []


def j(p, d=None):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else d


def main():
    T = j(os.path.join(RES, "trump166.json"), {})
    tc = {r["cell"]: r for r in T.get("cells", [])}
    sq = {(r["cell"], r["pad"]): r for r in j(os.path.join(RES, "squeeze166.json"), [])}
    stg = {}
    for pad in ("wmax", "w0"):
        for r in jl(os.path.join(RES, "subtree166_%s.jsonl" % pad)):
            stg[(r["cell"], pad)] = r
    plan = {r["cell"]: r for r in j(os.path.join(RES, "coverplan166_wmax.json"), [])}
    lp = {}
    for f in sorted(glob.glob(os.path.join(RES, "lp166_*_s*.jsonl"))):
        for r in jl(f):
            lp.setdefault(r.get("cell"), []).append(r)
    # `certified` in the LP records is the status of the certificate as `caselp.make_certificate`
    # emitted it -- with the STOCK cores (notes/certificate_bug.md).  Override it where A166's
    # exact-core patch was verified.
    fix = {}
    for f in sorted(glob.glob(os.path.join(RES, "certfix166_*.json"))):
        d = j(f, {})
        if d.get("node") and any(t.get("result") == "PASS" for t in (d.get("trials") or [])):
            fix[d["node"]] = "PASS (exact cores)"
    for rs in lp.values():
        for r in rs:
            if r.get("node") in fix:
                r["certified_emitted"] = r.get("certified")
                r["certified"] = fix[r["node"]]
    canary = j(os.path.join(RES, "canary166_wmax.json"), {})
    price = j(os.path.join(RES, "price166_wmax.json"), {})

    out = []
    for (meta, bH, _rec) in C.load_eleven():
        n = meta["cell"]
        a = stg.get((n, "wmax"))
        b = stg.get((n, "w0"))
        p = plan.get(n, {})
        rows = lp.get(n, [])
        b8 = [r for r in rows if r.get("kind") == "budget8"]
        b9 = [r for r in rows if r.get("kind") == "degenerate"]

        def sl(rs):
            e = sorted(r["eta"] for r in rs if r.get("eta") is not None)
            if not e:
                return None
            return dict(n=len(e), min=round(e[0], 6), med=round(e[len(e) // 2], 6),
                        max=round(e[-1], 6),
                        converged_kills=sum(1 for r in rs if r.get("kills_converged")),
                        certified=[r.get("certified") for r in rs if r.get("certified")],
                        walls=[r.get("wall_s") for r in rs])
        cm = p.get("H_can_meet_corner")
        nsv = (a or {}).get("n_survivors")
        verdict = "unknown"
        if a is not None:
            if nsv == 0 and cm is False:
                verdict = "DEAD (C leaf, geometry only)"
            elif nsv == 0:
                verdict = ("ALIVE -- budget-8 branch EMPTY, only the budget-9 degenerate branch "
                           "survives")
            else:
                alive8 = [r for r in b8 if not r.get("kills_converged")]
                verdict = ("ALIVE -- %d budget-8 pair cells survive geometry%s"
                           % (nsv, ("; %d/%d sampled LP nodes are converged kills"
                                    % (len(b8) - len(alive8), len(b8))) if b8 else
                              " (LP not sampled)"))
        rec = dict(
            cell=n, level=meta["level"], family=meta["family"],
            record=meta["record"], a115_tau=meta["tau"], a115_budget=meta["budget"],
            nearest_corner=(a or {}).get("corner"),
            d_to_corner=(a or {}).get("dist_to_corner"),
            dists=(a or {}).get("dists"),
            Hbox=bH.to_json(),
            trump=dict(image=tc.get(n, {}).get("trump_interior", {}).get("image"),
                       sq=tc.get(n, {}).get("trump_interior", {}).get("sq"),
                       pose_distance=tc.get(n, {}).get("trump_interior", {}).get("d"),
                       image_nonsimple=tc.get(n, {}).get("image_nonsimple"),
                       image_three_simple=tc.get(n, {}).get("image_three_simple"),
                       nearest_is_nonsimple=tc.get(n, {}).get("nearest_is_nonsimple"),
                       trump_quad=tc.get(n, {}).get("trump_quad")),
            support_quad=tc.get(n, {}).get("support_quad"),
            n_support=tc.get(n, {}).get("n_support"),
            H_can_meet_corner=cm,
            b_meet_kept=p.get("b_meet_kept"),
            cover_complete_at_budget8=p.get("cover_complete_at_b8"),
            stages_wmax=dict(cells=(a or {}).get("cell_stats"), pairs=(a or {}).get("pair_stats"),
                             survivors=nsv, nsub_clip=(a or {}).get("nsub_clip"),
                             mutual_first=(a or {}).get("mutual_first")),
            kept_H_clip=(a or {}).get("kept_H_clip"),
            kept_mutual=(a or {}).get("kept_mutual"),
            stages_w0=dict(cells=(b or {}).get("cell_stats"), pairs=(b or {}).get("pair_stats"),
                           survivors=(b or {}).get("n_survivors")),
            squeeze=dict(bound_wmax=sq.get((n, "wmax"), {}).get("diam_S_star_upper"),
                         bound_w0=sq.get((n, "w0"), {}).get("diam_S_star_upper"),
                         fires_wmax=sq.get((n, "wmax"), {}).get("squeeze_kills"),
                         fires_w0=sq.get((n, "w0"), {}).get("squeeze_kills")),
            lp_budget8=sl(b8), lp_budget9=sl(b9),
            verdict=verdict,
            scope="s0 fixed side; window transfer by dilation (k0_route.md 4.1) -- pending audit",
        )
        out.append(rec)
    with open(os.path.join(RES, "subtree166.jsonl"), "w", encoding="utf-8") as fh:
        for r in out:
            fh.write(json.dumps(r) + "\n")

    # ---------------------------------------------------------------- tables.md
    L = ["# A166 — tables (generated by `code/report166.py`; do not hand-edit)", ""]
    L += ["## 1. The canary", "",
          "`CANARY_PASS = %s`.  Images of Trump realising `l1_153`: %s."
          % (canary.get("CANARY_PASS"), canary.get("images_realising_the_cell")), ""]
    for g in (canary.get("images_realising_the_cell") or []):
        L.append("* `%s` -> %s" % (g, canary["images"][g]["branch"]))
    L += ["", "## 2. Nearest corner, Trump match, and the two branches", "",
          "| cell | lvl | fam | `d(z_H, TR)` | Trump match | pose dist | image non-simple | nearest is | `H` can meet `B_TR^w` | budget-8 cover complete |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(out, key=lambda r: r["d_to_corner"] or 0):
        L.append("| `%s` | %d | %s | %.4f | `%s` sq%s | %.4f | %s | %s | %s | %s |"
                 % (r["cell"], r["level"], r["family"], r["d_to_corner"] or 0,
                    r["trump"]["image"], r["trump"]["sq"], r["trump"]["pose_distance"] or 0,
                    ",".join(r["trump"]["image_nonsimple"] or []),
                    "NON-SIMPLE" if r["trump"]["nearest_is_nonsimple"] else "SIMPLE",
                    "yes" if r["H_can_meet_corner"] else "**no**",
                    "**yes**" if r["cover_complete_at_budget8"] else "no"))
    L += ["", "## 3. The geometric stages at the window pad `w_max`", "",
          "| cell | DEAD_R | DEAD_H2 | DEAD_H1 | DEAD_CLIP | DEGEN | ALIVE cells | pairs alive (A143 chain) | after A166 | squeeze bound |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(out, key=lambda r: r["d_to_corner"] or 0):
        c = r["stages_wmax"]["cells"] or {}
        p = r["stages_wmax"]["pairs"] or {}
        L.append("| `%s` | %s | %s | %s | %s | %s | %s | %s | **%s** | %s |"
                 % (r["cell"], c.get("dead_R"), c.get("dead_H2"), c.get("dead_H1"),
                    c.get("dead_clip"), c.get("degenerate"), c.get("survive"),
                    p.get("raw_alive_a143"), p.get("alive"), r["squeeze"]["bound_wmax"]))
    L += ["", "## 4. The same at pad 0 (the exact unit corner box; s0-only)", "",
          "| cell | ALIVE cells | DEGEN | survivors | squeeze bound | squeeze fires |",
          "|---|---|---|---|---|---|"]
    for r in sorted(out, key=lambda r: r["d_to_corner"] or 0):
        c = r["stages_w0"]["cells"] or {}
        L.append("| `%s` | %s | %s | **%s** | %s | %s |"
                 % (r["cell"], c.get("survive"), c.get("degenerate"),
                    r["stages_w0"]["survivors"], r["squeeze"]["bound_w0"],
                    r["squeeze"]["fires_w0"]))
    L += ["", "## 5. The LP", "",
          "budget 8 = 11 - 3 (`H` + two corner squares), budget 9 = 11 - 2 (the degenerate branch, "
          "`H` itself one of the two meeters).  Cap 240 s, A135 exact cores, `K'` an audit column, "
          "warm start from the cell's own A115 record.", "",
          "| cell | branch | n | eta min / med / max | converged kills | certified | walls (s) |",
          "|---|---|---|---|---|---|---|"]
    for r in sorted(out, key=lambda r: r["d_to_corner"] or 0):
        for k, tag in (("lp_budget8", "budget 8"), ("lp_budget9", "budget 9 (degenerate)")):
            s = r[k]
            if not s:
                continue
            L.append("| `%s` | %s | %d | %.4f / %.4f / %.4f | %d | %s | %s |"
                     % (r["cell"], tag, s["n"], s["min"], s["med"], s["max"],
                        s["converged_kills"], ",".join(map(str, s["certified"])) or "-",
                        ",".join(str(w) for w in s["walls"])))
    L += ["", "## 6. Quadrant census (split at `s0/2`), beside Trump's", "",
          "| cell | n support | support BL/BR/TR/TL | sparsest | matched Trump image | its quad | its non-simple | its three-simple |",
          "|---|---|---|---|---|---|---|---|"]
    for r in sorted(out, key=lambda r: r["d_to_corner"] or 0):
        q = r["support_quad"] or {}
        tq = r["trump"]["trump_quad"] or {}
        mn = min(q.values()) if q else 0
        L.append("| `%s` | %s | %s/%s/%s/%s | %s | `%s` | %s/%s/%s/%s | %s | %s |"
                 % (r["cell"], r["n_support"], q.get("BL"), q.get("BR"), q.get("TR"), q.get("TL"),
                    ",".join(k for k, v in q.items() if v == mn), r["trump"]["image"],
                    tq.get("BL"), tq.get("BR"), tq.get("TR"), tq.get("TL"),
                    ",".join(r["trump"]["image_nonsimple"] or []),
                    ",".join(r["trump"]["image_three_simple"] or [])))
    L += ["", "Trump's own census, per image:", "",
          "| image | BL | BR | TR | TL | non-simple corner | three-simple corner | sparse quadrant |",
          "|---|---|---|---|---|---|---|---|"]
    for g, im in sorted((T.get("images") or {}).items()):
        q = im["quad"]
        mn = min(q.values())
        L.append("| `%s` | %d | %d | %d | %d | %s | %s | %s |"
                 % (g, q["BL"], q["BR"], q["TR"], q["TL"], ",".join(im["nonsimple"]),
                    ",".join(im["three_simple"]), ",".join(k for k, v in q.items() if v == mn)))
    L += ["", "## 6b. Kept fractions of the clips (the coordinator's reinforcement)", "",
          "`kept_union` = area of the bounding box of the union of the clipped rects, over the "
          "original; `nsub = 4` tilt sub-bins. The `K'(H)` clip is applied to every cover box that "
          "survived the reach and `H`-identification stages; the MUTUAL clip is applied per surviving "
          "PAIR, to BOTH members, BEFORE the pair leaf.", "",
          "| cell | K'(H) clip: n boxes / min / Q1 / median | emptied | boxes losing a tilt sub-bin | mutual clip: n / min / median | boxes cut | pairs losing a sub-bin |",
          "|---|---|---|---|---|---|---|---|"]
    for r in sorted(out, key=lambda r: r["d_to_corner"] or 0):
        h = r.get("kept_H_clip") or {}
        m = r.get("kept_mutual") or {}
        L.append("| `%s` | %s / %s / %s / %s | %s | %s | %s / %s / %s | %s | %s |"
                 % (r["cell"], h.get("n"), h.get("min"), h.get("q1"), h.get("median"),
                    h.get("n_emptied"), h.get("n_lost_subbins"),
                    m.get("n"), m.get("min"), m.get("median"), m.get("n_below_1"),
                    m.get("n_lost_subbins")))
    L += ["", "## 7. The price input: the whole remaining open k0_00 pool", ""]
    R = [x for x in (price.get("rows") or []) if "skip" not in x]
    if R:
        from collections import Counter
        cc = Counter(x["corner"] for x in R)
        cm = Counter(x["H_can_meet_corner"] for x in R)
        ds = sorted(x["dist"] for x in R)
        L += ["* pool: %d open k0_00 cells (A115) minus %d A141 `K'`-lane kills = **%d remaining**"
              % (price["n_pool"], price["n_a141_killed"], price["n_remaining"]),
              "* nearest corner: %s" % ", ".join("%s %d" % kv for kv in cc.most_common()),
              "* `H` can meet `B_TR^w`: yes %d, **no %d**" % (cm[True], cm[False]),
              "* `d(z_H, corner)`: min %.4f, Q1 %.4f, median %.4f, Q3 %.4f, max %.4f"
              % (ds[0], ds[len(ds) // 4], ds[len(ds) // 2], ds[3 * len(ds) // 4], ds[-1]),
              "* the crossover: `can_meet = True` for `d` in [%.5f, %.5f], `can_meet = False` for "
              "`d` in [%.5f, %.5f]"
              % (min(x["dist"] for x in R if x["H_can_meet_corner"]),
                 max(x["dist"] for x in R if x["H_can_meet_corner"]),
                 min(x["dist"] for x in R if not x["H_can_meet_corner"]),
                 max(x["dist"] for x in R if not x["H_can_meet_corner"])), ""]
    S = price.get("sample") or []
    if S:
        L += ["| cell | `d` | `H` can meet | ALIVE cells | surviving pairs | s |", "|---|---|---|---|---|---|"]
        for s in sorted(S, key=lambda s: s["dist"]):
            L.append("| `%s` | %.4f | %s | %d | **%d** | %.0f |"
                     % (s["nid"], s["dist"], "yes" if s["H_can_meet_corner"] else "no",
                        s["n_alive_cells"], s["n_survivors"], s["secs"]))
    open(os.path.join(NOTES, "tables.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("wrote results/subtree166.jsonl (%d rows) and notes/tables.md" % len(out))


if __name__ == "__main__":
    main()
