"""A152 T3 -- the tables: verdict counts, the kill table by class / level / slot, the overlap with
A141's 244 slot-lane kills, the exact-pin baseline cross-check, and the UNSOUNDNESS CANARY (cells
where the PI's shrunk cell would fire but no admissible translate does).

    python t3_fold.py
"""
import collections
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A141R = os.path.join(ROOT, "attempts", "A141-polycore-lane", "results")


def load(pat):
    out = []
    for f in sorted(glob.glob(pat)):
        for ln in open(f, encoding="utf-8"):
            ln = ln.strip()
            if ln:
                out.append(json.loads(ln))
    return out


def main():
    raw = load(os.path.join(BASE, "results", "t2_sweep_s*.jsonl"))
    # the sweep was restarted once with a different record ORDER, so a few (key, slot) pairs were
    # processed twice; keep the LAST row for each.
    dedup = {}
    for r in raw:
        if "error" in r:
            continue
        k = (r["key"], r["slot"])
        prev = dedup.get(k)
        if prev is not None and any(v["verdict"] == "KILL" for v in prev["rows"])                 and not any(v["verdict"] == "KILL" for v in r["rows"]):
            continue          # the later pass ran with an exhausted cover budget; keep the cover
        dedup[k] = r
    rows = list(dedup.values())
    errs = [r for r in load(os.path.join(BASE, "results", "t2_sweep_s*.jsonl"))
            if "error" in r]
    a141 = load(os.path.join(A141R, "t4_slots.jsonl"))
    a141_kills = set((r["nid"], r["slot"]) for r in a141 if r["verdict"] == "KILL")
    a141_nodes = set(r["nid"] for r in a141 if r["verdict"] == "KILL")

    out = dict(cells_swept=len(rows), errors=len(errs),
               records_swept=len(set(r["key"] for r in rows)))

    # --- verdict tallies, per variant kind
    tally = collections.defaultdict(collections.Counter)
    for r in rows:
        for v in r["rows"]:
            tally[v["kind"]][v["verdict"]] += 1
    out["verdicts_by_variant"] = {k: dict(v) for k, v in tally.items()}

    # --- kills
    kills = []          # SOUND form: a translate
    shr_kills = []      # the PI's literal form: the shrunk cell
    for r in rows:
        for v in r["rows"]:
            if v["verdict"] != "KILL":
                continue
            e = dict(key=r["key"], nid=r["nid"], src=r["src"], cls=r["cls"], level=r["level"],
                     slot=r["slot"], t=v["t"], lane_ub=v.get("lane_ub"), M=v.get("M"),
                     cert=v.get("cert"), sample_line=v.get("sample_line"))
            (kills if v["kind"] == "trans" else shr_kills).append(e)
    out["n_kills_translated"] = len(kills)
    out["n_kills_shrunk_diagnostic"] = len(shr_kills)
    out["kill_nodes_translated"] = sorted(set(k["nid"] for k in kills))
    out["by_cls_slot"] = dict(collections.Counter("%s %s" % (k["cls"], k["slot"])
                                                  for k in kills))
    out["by_level"] = dict(collections.Counter(k["level"] for k in kills))
    out["by_src"] = dict(collections.Counter(k["src"] for k in kills))
    out["by_translate"] = dict(collections.Counter(str([round(x, 8) for x in (k["t"] or [])])
                                                   for k in kills))
    out["kill_forms"] = dict(collections.Counter("LANE<=%s,M=%s" % (k["lane_ub"], k["M"])
                                                 for k in kills))

    # --- overlap with A141
    ks = set((k["nid"], k["slot"]) for k in kills)
    out["overlap_with_a141"] = dict(
        a141_cell_kills=len(a141_kills), a152_cell_kills=len(ks),
        both=len(ks & a141_kills), new_in_a152=sorted(ks - a141_kills)[:80],
        n_new_in_a152=len(ks - a141_kills),
        lost_vs_a141=sorted(a141_kills - ks)[:80], n_lost_vs_a141=len(a141_kills - ks),
        a141_nodes=len(a141_nodes),
        a152_nodes=len(set(k["nid"] for k in kills)))

    # --- the exact-pin baseline cross-check (A141's cell + A141's exact pin cores)
    b = collections.Counter()
    for r in rows:
        bl = r["baseline_exact"]
        b["lane_lb>=2" if bl["lane_lb"] >= 2 else
          "lane_lb+M_lb<=1" if bl["lane_lb"] + bl["M_lb"] <= 1 else "near"] += 1
    out["baseline_exact_screen"] = dict(b)

    # --- the unsoundness canary: the shrunk cell fires where no admissible translate does
    canary = []
    for r in rows:
        s = [v for v in r["rows"] if v["kind"] == "shrunk"]
        t = [v for v in r["rows"] if v["kind"] == "trans"]
        if not s:
            continue
        if s[0]["verdict"] == "KILL" and not any(v["verdict"] == "KILL" for v in t):
            canary.append(dict(key=r["key"], slot=r["slot"], cls=r["cls"],
                               n_translates=r["n_translates"],
                               trans_verdicts=[v["verdict"] for v in t]))
    out["unsound_canary_shrunk_fires_no_translate_does"] = dict(n=len(canary),
                                                                examples=canary[:40])

    # --- SCREEN-LEVEL comparison (independent of the cover budget): a cell is a KILL CANDIDATE
    # when the sampler realises no free pose meeting it (lane_lb = 0) and at most one conditioned
    # meeter.  A NEW candidate is one the exact-pin / exact-cell baseline does NOT offer, i.e. a
    # cell the refinement would have to be responsible for; a LOST candidate is the converse.
    cand = collections.Counter()
    new_ex, lost_ex = [], []
    for r in rows:
        bl = r["baseline_exact"]
        base = (bl["lane_lb"] == 0 and bl["M_lb"] <= 1)
        tr = [v for v in r["rows"] if v["kind"] == "trans"]
        sh = [v for v in r["rows"] if v["kind"] == "shrunk"]
        t_c = any(v["lane_lb"] == 0 and v["M_lb"] <= 1 for v in tr)
        s_c = any(v["lane_lb"] == 0 and v["M_lb"] <= 1 for v in sh)
        cand["baseline_exact"] += base
        cand["some_admissible_translate"] += t_c
        cand["shrunk_cell"] += s_c
        cand["translate_and_not_baseline"] += (t_c and not base)
        cand["baseline_and_not_translate"] += (base and not t_c)
        cand["shrunk_and_not_translate"] += (s_c and not t_c)
        if t_c and not base:
            new_ex.append(dict(key=r["key"], slot=r["slot"], cls=r["cls"]))
        if base and not t_c:
            lost_ex.append(dict(key=r["key"], slot=r["slot"], cls=r["cls"]))
    out["screen_candidates"] = dict(cand)
    out["screen_new_examples"] = new_ex[:40]
    out["screen_lost_examples"] = lost_ex[:40]

    # --- how much of the population is reached at all
    out["admissible_translate_counts"] = dict(
        collections.Counter(r["n_translates"] for r in rows))
    p = os.path.join(BASE, "results", "t3_tables.json")
    json.dump(out, open(p, "w", encoding="utf-8"), indent=1)
    json.dump(kills, open(os.path.join(BASE, "results", "a152_kills.json"), "w",
                          encoding="utf-8"), indent=1)
    for k in ("cells_swept", "records_swept", "errors", "n_kills_translated",
              "n_kills_shrunk_diagnostic", "by_cls_slot", "by_level", "by_src",
              "by_translate", "kill_forms", "overlap_with_a141",
              "verdicts_by_variant", "unsound_canary_shrunk_fires_no_translate_does",
              "admissible_translate_counts", "baseline_exact_screen",
              "screen_candidates"):
        v = out[k]
        if isinstance(v, dict) and k == "overlap_with_a141":
            v = {kk: vv for kk, vv in v.items() if not isinstance(vv, list)}
        if isinstance(v, dict) and k == "unsound_canary_shrunk_fires_no_translate_does":
            v = dict(n=v["n"])
        print("%-46s %s" % (k, json.dumps(v)[:400]))
    print("wrote", p)


if __name__ == "__main__":
    main()
