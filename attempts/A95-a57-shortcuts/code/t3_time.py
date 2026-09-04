"""A95 T3: where A57's wall goes, and what is left to run.

Read-only over A57 results/progress/logs.  No numpy, no A57 imports: pure jsonl/json parsing,
so this costs ~30 MB of commit and never touches the running campaign.

Outputs results/t3_time.json:
  * per-node wall split (LP / certify / eps_geo retries / free logic kills) per class,
  * the accounted-vs-elapsed overhead factor per shard (progress json elapsed_s vs the sum of
    the rows' own seconds -- the difference is warm-start build, folding, and process startup),
  * level-2 descent rate per shard and the measured level-2 per-node cost,
  * projected remaining wall for G1 and for sides 4/3/2, with and without the skip list.
"""
import json, glob, os, collections, statistics

A57 = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "A57-shadow-trees"))
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results"))

# tree57 cover per side (measured exactly by A95 t2_reflect.py, and equal to A57's own C-check)
COVER = {"k5_11": {1: (821, 331), 2: (816, 336), 3: (704, 264), 4: (695, 273)},
         "k5_16": {1: (914, 238), 2: (907, 245), 3: (784, 184), 4: (777, 191)}}
CHILDREN = {1: 1153, 2: 1153, 3: 969, 4: 969}      # 12x12x8+1 at sides 1-2, 11x11x8+1 at 3-4
D2_FANOUT = 8                                       # deepen.py --levels 3


def rows(pat):
    """Deduplicated by id, first record wins (A57's s1 shard was re-run over its tail: the
    second copy has lp_seconds = 0 because the node json was reloaded from disk)."""
    out, seen, dups = [], set(), 0
    for f in sorted(glob.glob(os.path.join(A57, "results", pat))):
        for ln in open(f):
            ln = ln.strip()
            if not ln:
                continue
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if r["id"] in seen:
                dups += 1
                continue
            seen.add(r["id"])
            r["_shard"] = os.path.basename(f).rsplit("_", 1)[1].split(".")[0]
            out.append(r)
    return out, dups


def klass(r):
    c = r.get("cert") or ""
    if c.startswith("KILL-BY-LOGIC"):
        return "logic_kill"
    if c == "PASS":
        return "pass_epsgeo" if r.get("eps_geo_used") is not None else "pass_direct"
    if c.startswith("FAIL"):
        return "cert_fail"
    if c.startswith("ALIVE"):
        return "alive_lp"
    if c.startswith("UNSOUND"):
        return "parent_box"
    if c.startswith("CANARY"):
        return "canary"
    return "other"


def eg(r):
    return sum(s.get("seconds", 0.0) for s in (r.get("eps_geo") or []))


def wall(r):
    return (r.get("lp_seconds") or 0.0) + (r.get("cert_seconds") or 0.0) + eg(r)


def analyse(pat, label):
    R, dups = rows(pat)
    by = collections.defaultdict(list)
    for r in R:
        by[klass(r)].append(r)
    rep = {"label": label, "rows": len(R), "duplicate_rows_dropped": dups, "classes": {}}
    tl = tc = te = 0.0
    for k, v in sorted(by.items()):
        lp = sum(r.get("lp_seconds") or 0.0 for r in v)
        ce = sum(r.get("cert_seconds") or 0.0 for r in v)
        e2 = sum(eg(r) for r in v)
        tl += lp; tc += ce; te += e2
        w = [wall(r) for r in v]
        rep["classes"][k] = dict(n=len(v), lp_s=round(lp, 1), cert_s=round(ce, 1),
                                 epsgeo_s=round(e2, 1), wall_s=round(lp + ce + e2, 1),
                                 mean_wall_s=round(statistics.mean(w), 1),
                                 median_wall_s=round(statistics.median(w), 1),
                                 max_wall_s=round(max(w), 1))
    tot = tl + tc + te
    rep["totals"] = dict(lp_s=round(tl, 1), cert_s=round(tc, 1), epsgeo_s=round(te, 1),
                         wall_s=round(tot, 1), lp_frac=round(tl / tot, 4),
                         cert_frac=round(tc / tot, 4), epsgeo_frac=round(te / tot, 4))
    solved = [r for r in R if klass(r) != "logic_kill"]
    rep["per_node"] = dict(
        n_solved=len(solved),
        mean_wall_solved_s=round(statistics.mean([wall(r) for r in solved]), 1),
        median_wall_solved_s=round(statistics.median([wall(r) for r in solved]), 1),
        mean_wall_all_s=round(tot / len(R), 1),
        logic_kill_frac=round(len(by["logic_kill"]) / len(R), 4),
        descent_frac=round((len(by["alive_lp"]) + len(by["cert_fail"])) / len(R), 4),
        mean_certify_only_s=round(statistics.mean(
            [r["cert_seconds"] for r in by["pass_direct"] if r.get("cert_seconds")]), 1))
    sh = collections.defaultdict(collections.Counter)
    wl = collections.defaultdict(float)
    for r in R:
        sh[r["_shard"]][klass(r)] += 1
        wl[r["_shard"]] += wall(r)
    rep["per_shard"] = {}
    key = label.replace("_G1", "_interior_G1")
    for s, c in sorted(sh.items()):
        n = sum(c.values())
        pj = os.path.join(A57, "progress", f"{key}_{s}.json")
        el = json.load(open(pj))["elapsed_s"] if os.path.exists(pj) else None
        rep["per_shard"][s] = dict(
            n=n, **{k: c[k] for k in sorted(c)},
            descent_frac=round((c["alive_lp"] + c["cert_fail"]) / n, 4),
            accounted_s=round(wl[s], 1), progress_elapsed_s=el,
            overhead_factor=(round(el / wl[s], 3) if el and wl[s] else None))
    return rep, R


def level2():
    """Measured level-2 (deepen.py) cost.  Thin: the only D2 rows on disk are the delta = 0
    L1_D2 probes, so this is a bracket, not a rate."""
    out = {}
    for f in glob.glob(os.path.join(A57, "results", "tree_*_L1_D2.jsonl")):
        R = [json.loads(l) for l in open(f) if l.strip()]
        w = [wall(r) for r in R]
        lk = [r for r in R if (r.get("cert") or "").startswith("KILL-BY-LOGIC")]
        out[os.path.basename(f)] = dict(
            rows=len(R), parents=len({r["parent"] for r in R}), logic_kills=len(lk),
            logic_kill_frac=round(len(lk) / len(R), 3),
            mean_wall_s=round(statistics.mean(w), 1),
            mean_wall_solved_s=round(statistics.mean([x for x in w if x > 0]), 1)
            if any(w) else 0.0,
            fanout=D2_FANOUT)
    return out


def main():
    out = {}
    for pat, lab in (("tree_k5_11_interior_G1_s*.jsonl", "k5_11_G1"),
                     ("tree_k5_16_interior_G1_s*.jsonl", "k5_16_G1")):
        out[lab], _ = analyse(pat, lab)
    out["level2_measured"] = level2()

    proj = {}
    d2w = statistics.mean([v["mean_wall_s"] for v in out["level2_measured"].values()]) \
        if out["level2_measured"] else 0.0
    for cls, lab in (("k5_11", "k5_11_G1"), ("k5_16", "k5_16_G1")):
        pn = out[lab]["per_node"]
        mw, lk, df = pn["mean_wall_solved_s"], pn["logic_kill_frac"], pn["descent_frac"]
        ovh = statistics.mean([v["overhead_factor"] for v in out[lab]["per_shard"].values()
                               if v["overhead_factor"]])
        done = out[lab]["rows"]
        p = {"done_at_G1": done, "overhead_factor": round(ovh, 3),
             "mean_wall_solved_s": mw, "logic_kill_frac": lk, "descent_frac": df,
             "level1_by_side": {}, "level2_by_side": {}}
        for side in (1, 2, 3, 4):
            ok, free = COVER[cls][side]
            rem_ok = ok - round(done * (1 - lk)) if side == 1 else ok
            rem_ok = max(rem_ok, 0)
            p["level1_by_side"][side] = dict(
                ok_children=ok, free_logic_kills=free, remaining_ok=rem_ok,
                wall_s=round(rem_ok * mw * ovh, 0),
                wall_days_1proc=round(rem_ok * mw * ovh / 86400, 2))
            resisters = round(ok * df / (1 - lk))
            p["level2_by_side"][side] = dict(
                resisters=resisters, children=resisters * D2_FANOUT,
                wall_s=round(resisters * D2_FANOUT * d2w * ovh, 0),
                wall_days_1proc=round(resisters * D2_FANOUT * d2w * ovh / 86400, 2))
        p["level1_total_remaining_days_1proc"] = round(
            sum(v["wall_s"] for v in p["level1_by_side"].values()) / 86400, 2)
        p["level2_total_days_1proc"] = round(
            sum(v["wall_s"] for v in p["level2_by_side"].values()) / 86400, 2)
        proj[cls] = p
    tot1 = sum(proj[c]["level1_total_remaining_days_1proc"] for c in proj)
    tot2 = sum(proj[c]["level2_total_days_1proc"] for c in proj)
    proj["level2_mean_node_wall_s"] = round(d2w, 1)
    proj["TOTAL_level1_remaining_days_1proc"] = round(tot1, 2)
    proj["TOTAL_level2_days_1proc"] = round(tot2, 2)
    for w in (3, 5):
        proj[f"level1_remaining_wall_days_{w}workers"] = round(tot1 / w, 2)
        proj[f"level1_plus_level2_wall_days_{w}workers"] = round((tot1 + tot2) / w, 2)
    # what the two A95 shortcuts would take off level 1
    proj["shortcut_reflection_sides_2_3_4_children_removed"] = 861     # sigma-symmetric nth=10
    proj["shortcut_reflection_sides_1_2_3_4_children_removed"] = 1177
    out["projection"] = proj
    json.dump(out, open(os.path.join(OUT, "t3_time.json"), "w"), indent=1)
    print(json.dumps(out["projection"], indent=1))


if __name__ == "__main__":
    main()
