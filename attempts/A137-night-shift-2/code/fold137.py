"""A137 T1 -- fold the day's certified/logic kills into A57's (and A60's) state.

The tree's own record format for a superseding verdict is
`attempts/A57-shadow-trees/results/superseded_by_tight_core.jsonl` (A96): one row per node,
carrying the PRIOR verdict (retained -- the tree jsonl is never rewritten), what supersedes it,
and a note.  This driver writes the same shape, with two extra fields the backlog needs:
`cert` (the certificate path, so the kill is replayable) and `leaf` (the lemma leaf that owns it).

Sources folded (A144's guard-line results are LP-only, NO certificates -- deliberately NOT folded):
  A131  results/backlog_kills.jsonl            132 pin-clip (T5''') kills, certs under certs/backlog/
  A142  results/exactclip_kills_a57.jsonl       17 exact-pin-core clip kills (A57)
  A142  results/exactclip_kills_a60.jsonl       34 exact-pin-core clip kills (A60)
  A135  results/polycore_kills.jsonl            64 polygon-vs-pin-core logic kills (T5'''') + LP-certified
  A124  results/recheck124.jsonl                TRIM-KILL rows (T5'' empty surviving bin)
  A145  results/resolves145*.jsonl              certified kills (frozen and v3 recorded separately)
  A141  results/polycore_lane_kills.jsonl       lane kills (filtered to A57/A60 classes)

Children of a killed node are dead with it (monotonicity, A124 Sec.4), so every recorded
descendant of a folded kill is folded too, with leaf `inherited`.

Writes: A57/results/superseded_by_backlog_A137.jsonl, A60/results/superseded_by_backlog_A137.jsonl,
and this attempt's results/foldin137.json (the counts).  No tree row is rewritten.
"""
import collections
import glob
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
A57 = os.path.join(ROOT, "A57-shadow-trees")
A60 = os.path.join(ROOT, "A60-trump5-campaign")
STAMP = time.strftime("%Y-%m-%d %H:%M:%S")


def jl(path):
    if not os.path.exists(path):
        return []
    out = []
    for ln in open(path, encoding="utf-8"):
        ln = ln.strip()
        if not ln:
            continue
        try:
            out.append(json.loads(ln))
        except Exception:
            pass
    return out


def corpus(base, pattern, idf="id"):
    """id -> (record, source file).  Last row for an id wins, as board.py does.
    A60's rows call the id `tag` and the verdict `cert` (same shape otherwise)."""
    R, src = {}, {}
    for p in sorted(glob.glob(os.path.join(base, "results", pattern))):
        for r in jl(p):
            if isinstance(r, dict) and idf in r:
                R[r[idf]] = r
                src[r[idf]] = os.path.basename(p)
    return R, src


def corpus_all(base, pattern, idf="id"):
    """id -> [(tag, record)] over EVERY shard file.

    The same child id exists in more than one TREE: `k5_11_interior_Y0041_D02` is a node of the
    L1 tree (eps-fat pins, pin core 1/2 - 2.98e-8) and a different node of the G1 tree (slack
    pins at delta = 1e-2, pin core 1/2 - delta/sqrt2 = 0.492928902).  They are NOT the same
    hypothesis -- G1's is weaker, so its stratum contains L1's -- and a kill proved at one pin
    core only transfers DOWNWARD (a clip computed with a SMALLER pin core is valid for any node
    whose pins contain that core; the reverse is not).  Last-wins would silently attribute a kill
    to the wrong tree, so keep them all."""
    R = collections.defaultdict(list)
    for p in sorted(glob.glob(os.path.join(base, "results", pattern))):
        tag = os.path.basename(p)[5:].rsplit("_s", 1)[0].replace(".jsonl", "")
        for r in jl(p):
            if isinstance(r, dict) and idf in r:
                R[r[idf]].append((tag, os.path.basename(p), r))
    return R


def node_core(rec):
    """the pin core half-side the node's own hypothesis guarantees.

    delta = 1e-2 slack pins  -> 1/2 - delta/sqrt(2) = 0.492928902 (A135 exactcore, certified);
    no `pin_delta` on the record = the library's eps-fat pins -> 1/2 - 2.98e-8."""
    d = rec.get("pin_delta")
    if d is None or d <= 0:
        return 0.5 - 2.9802322387695312e-08
    return 0.5 - d / (2.0 ** 0.5)


def level_of(nid):
    return 1 + nid.count("_D")


def verdict_of(rec):
    c = (rec or {}).get("cert") or (rec or {}).get("verdict") or ""
    if c == "PASS":
        return "PASS"
    if c.startswith("KILL-BY-LOGIC"):
        return "KILL-BY-LOGIC"
    if c.startswith("ALIVE"):
        return "ALIVE"
    if c.startswith("FAIL"):
        return "FAIL"
    if c.startswith("UNSOUND"):
        return "UNSOUND-parent"
    if c.startswith("CANARY"):
        return "CANARY"
    if c.startswith("refused"):
        return "ALIVE"                       # A60's wording for tau >= budget
    return c or "none"


def main():
    A57R, A57src = corpus(A57, "tree_*.jsonl")
    A60R, A60src = corpus(A60, "a60_*.jsonl", idf="tag")
    print(f"A57 corpus rows {len(A57R)}   A60 corpus rows {len(A60R)}")

    # ---------------------------------------------------------------- sources
    kills = {}          # (camp, id) -> dict(leaf, cert, src, detail)
    A_SLACK = 0.492928902                       # 1/2 - 1e-2/sqrt2, A135's certified exact pin core
    A_STOCK = 0.49                              # 1/2 - delta, the deployed clip/trim pin core

    def add(camp, nid, leaf, cert, src, model=None, **extra):
        """`model` = the pin-core half-side the kill's GEOMETRY assumed.  A kill transfers to a
        node whose own guaranteed pin core is at least that big (a smaller obstacle proves less,
        so it stays valid); it does NOT transfer upward."""
        k = (camp, nid)
        if k in kills:
            kills[k]["also"] = kills[k].get("also", []) + [leaf]
            return
        kills[k] = dict(camp=camp, id=nid, leaf=leaf, cert=cert, src=src, model=model, **extra)

    # A131 -- 132 pin-clip kills at the deployed pin core
    a131 = os.path.join(ROOT, "A131-pin-clip")
    for r in jl(os.path.join(a131, "results", "backlog_kills.jsonl")):
        if r.get("kind") == "_header":
            continue
        cert = os.path.join(a131, "certs", "backlog", r["id"] + ".clipkill.json")
        add("A57", r["id"], "T5''' pin-clip (deployed a_pin=49/100)",
            cert if os.path.exists(cert) else None,
            "A131/results/backlog_kills.jsonl", model=A_STOCK, prior=r.get("prior_verdict"))

    # A142 -- exact-pin-core clip kills, A57 and A60
    a142 = os.path.join(ROOT, "A142-a57-review-gallery")
    for camp, f in (("A57", "exactclip_kills_a57.jsonl"), ("A60", "exactclip_kills_a60.jsonl")):
        for r in jl(os.path.join(a142, "results", f)):
            if r.get("kind") == "_header":
                continue
            cert = os.path.join(a142, "certs", camp.lower(), r["id"] + ".clipkill.json")
            add(camp, r["id"], "T5''' pin-clip at the EXACT pin core (a_pin=%s)" % r.get("a_pin"),
                cert if os.path.exists(cert) else None, "A142/results/" + f,
                model=float(__import__("fractions").Fraction(r["a_pin"])) if r.get("a_pin") else None,
                prior=r.get("prior_verdict"))

    # A135 -- polygon-vs-pin-core logic kills and the LP-certified ones
    a135 = os.path.join(ROOT, "A135-polycore-verifier")
    for r in jl(os.path.join(a135, "results", "polycore_kills.jsonl")):
        if r.get("kind") == "_header":
            continue
        nid = r.get("id") or r.get("nid")
        camp = "A60" if str(nid).startswith("c0_") else "A57"
        kind = (r.get("kind") or r.get("leaf") or "").lower()
        if "lp" in kind or r.get("verifier"):
            leaf = "LP kill, exact cores (%s)" % (r.get("verifier") or "frozen verify_case")
        else:
            leaf = "T5'''' polygon core meets pin core (shared witness)"
        add(camp, nid, leaf, r.get("cert") or r.get("cert_path"),
            "A135/results/polycore_kills.jsonl", model=A_SLACK, prior=r.get("prior_verdict"))

    # A124 -- TRIM-KILL rows (T5'' empties the surviving bin)
    a124 = os.path.join(ROOT, "A124-recheck-day")
    for r in jl(os.path.join(a124, "results", "recheck124.jsonl")):
        if r.get("verdict") == "TRIM-KILL":
            add("A57", r["id"], "T5'' trim: surviving tilt bin EMPTY", None,
                "A124/results/recheck124.jsonl", model=A_STOCK,
                prior=r.get("verdict_before"))

    # A145 -- certified kills, frozen and v3 recorded separately
    a145 = os.path.join(ROOT, "A145-impossible-weight")
    for f in ("resolves145.jsonl", "resolves145_rank.jsonl", "resolves145_ctrl.jsonl"):
        for r in jl(os.path.join(a145, "results", f)):
            res = r.get("result") or ""
            if not res.startswith("PASS"):
                continue
            leaf = ("LP kill, exact cores, FROZEN verify_case" if res == "PASS-FROZEN"
                    else "LP kill, exact cores, verify_case_v3 (%s)" % res)
            add("A57", r["id"], leaf, r.get("cert"), "A145/results/" + f, model=A_SLACK,
                prior=r.get("verdict_before"))

    # A141 -- lane kills, only those on A57/A60 nodes
    a141 = os.path.join(ROOT, "A141-polycore-lane")
    for r in jl(os.path.join(a141, "results", "polycore_lane_kills.jsonl")):
        nid = r.get("id") or r.get("nid")
        cls = r.get("cls") or ""
        if cls.startswith("k5_"):
            camp = "A57"
        elif cls.startswith("trump5") or str(nid).startswith("c0_"):
            camp = "A60"
        else:
            continue                                   # k0_00 etc: not this campaign's state
        add(camp, nid, "polycore lane (%s)" % (r.get("leaf") or "lane"),
            (r.get("cert") or {}).get("path"), "A141/results/polycore_lane_kills.jsonl",
            model=None, checker=(r.get("cert") or {}).get("checker"))

    # ---------------------------------------------------------- descendants
    by_camp = {"A57": (A57R, A57src), "A60": (A60R, A60src)}
    inherited = []
    for (camp, nid), k in list(kills.items()):
        R = by_camp[camp][0]
        for oid in R:
            if oid.startswith(nid + "_D") and (camp, oid) not in kills:
                inherited.append((camp, oid, nid))
    for camp, oid, parent in inherited:
        add(camp, oid, "inherited (ancestor %s killed; monotone)" % parent, None,
            "A137 fold-in (monotonicity)")

    # ------------------------------------------------------------- ledgers
    ALLTAGS = {"A57": corpus_all(A57, "tree_*.jsonl"),
               "A60": corpus_all(A60, "a60_*.jsonl", idf="tag")}
    stats = collections.Counter()
    per = collections.defaultdict(collections.Counter)
    out_rows = collections.defaultdict(list)
    unknown, refused = [], []
    for (camp, nid), k in sorted(kills.items()):
        R, src = by_camp[camp]
        rec = R.get(nid)
        if rec is None:
            unknown.append((camp, nid, k["leaf"]))
            stats[camp + "_not_in_corpus"] += 1
            continue
        # ---- which TREES does this kill actually apply to?  A kill computed against a pin core
        # of half-side `model` is valid for a node whose own pins guarantee at least that core.
        tags, tags_refused = [], []
        for (tag, fname, rr) in ALLTAGS[camp].get(nid, []):
            nc = node_core(rr)
            if k.get("model") is None or k["model"] <= nc + 1e-12:
                if tag not in tags:
                    tags.append(tag)
            elif tag not in tags_refused:
                tags_refused.append(tag)
        if tags_refused:
            refused.append((camp, nid, k["leaf"], k.get("model"), tags_refused))
            stats[camp + "_tag_refused"] += 1
        if not tags:
            stats[camp + "_no_applicable_tag"] += 1
            continue
        prior = verdict_of(rec)
        lvl = level_of(nid)
        already = prior in ("PASS", "KILL-BY-LOGIC")
        row = dict(id=nid, level=lvl, cls=nid.split("_interior")[0] if "_interior" in nid else nid.split("_")[0],
                   prior_verdict=prior, prior_cert=rec.get("cert"),
                   superseded_by=k["leaf"], leaf=k["leaf"], cert=k["cert"], source=k["src"],
                   already_dead=already, applies_to_tags=tags,
                   not_applicable_to_tags=tags_refused,
                   pin_core_model=k.get("model"),
                   note=("prior verdict RETAINED; this box is now a KILL in the trees listed in "
                         "applies_to_tags. Not overwritten in the tree jsonl."),
                   folded_by="A137", recorded=STAMP)
        if k.get("also"):
            row["also_killed_by"] = k["also"]
        out_rows[camp].append(row)
        stats[camp + "_folded"] += 1
        if already:
            stats[camp + "_redundant"] += 1
        else:
            stats[camp + "_new_kill"] += 1
            per[camp][("L%d" % lvl, prior)] += 1
            per[camp][("leaf", k["leaf"].split("(")[0].strip())] += 1
    for camp, base in (("A57", A57), ("A60", A60)):
        if not out_rows[camp]:
            continue
        p = os.path.join(base, "results", "superseded_by_backlog_A137.jsonl")
        with open(p, "w", encoding="utf-8") as f:
            for row in out_rows[camp]:
                f.write(json.dumps(row) + "\n")
        print(f"wrote {len(out_rows[camp])} rows -> {p}")

    # ------------------------------------------------- state counts, A57
    board = collections.defaultdict(collections.Counter)
    dead = {nid for (camp, nid) in kills if camp == "A57"}
    for nid, rec in A57R.items():
        key = A57src[nid][5:].rsplit("_s", 1)[0].replace(".jsonl", "")
        v = verdict_of(rec)
        board[key][v] += 1
        board[key]["seen"] += 1
        if v in ("ALIVE", "FAIL") and nid in dead:
            board[key]["newly_dead_" + v] += 1
    summary = dict(when=STAMP, a57_rows=len(A57R), a60_rows=len(A60R),
                   stats=dict(stats), unknown=unknown[:40], n_unknown=len(unknown),
                   tag_refusals=refused,
                   per_camp={c: {str(k): v for k, v in d.items()} for c, d in per.items()},
                   board={k: dict(v) for k, v in board.items()})
    json.dump(summary, open(os.path.join(BASE, "results", "foldin137.json"), "w"), indent=1)
    print(json.dumps({k: dict(v) for k, v in board.items()}, indent=1))
    print(json.dumps(dict(stats), indent=1))
    print("not in corpus:", len(unknown))
    for u in unknown[:20]:
        print("   ", u)


if __name__ == "__main__":
    main()
