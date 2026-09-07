"""A112 T3 -- the verdict: aggregate the four orderings against the old tree's projection.

Reads results/t2_<set>_<ordering>.jsonl and every per-node record under results/rt/, and writes
results/t3.json + notes/t2_table.md.  No solving, no LP: this is arithmetic on what T2 recorded.
"""
from __future__ import annotations

import glob, json, math, os, statistics, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a112lib as L

ORDERS = ["wastage", "stranded", "loadpath", "hybrid"]
SETS = ["s02", "k0"]
# each region set may live in its own run namespace (the k0 face was re-run after a logging bug
# aborted its first pass at the root; the aborted rows are left in place and simply not read)
RUN_BY_SET = {"s02": os.environ.get("A112_RUN_S02", L.RUN),
              "k0": os.environ.get("A112_RUN_K0", L.RUN)}


def _suf(rset):
    r = RUN_BY_SET.get(rset, L.RUN)
    return ("_" + r) if r else ""


def _rt(rset):
    return os.path.join(L.RES, "rt" + _suf(rset))
# Under the PI's protocol (2026-09-06) a kill is a CERTIFIED pass or a free (logic / chain) kill.
# An LP verdict is never a kill, so there is no "deadish" tier any more.
DEAD = ("DEAD-LOGIC", "DEAD-CERT", "DEAD-CLASS", "DEAD-CHAIN-LP")
DEADISH = DEAD


def rows(rset, ordering):
    p = os.path.join(L.RES, "t2%s_%s_%s.jsonl" % (_suf(rset), rset, ordering))
    if not os.path.exists(p):
        return []
    out, seen = [], set()
    for line in open(p, encoding="utf-8"):
        try:
            d = json.loads(line)
        except Exception:
            continue
        # the extended plan carried one region twice (k5_11_interior_Y0041_D02, picked by both the
        # stratified first pass and the survivor extension); keep the first record only
        if d.get("region") in seen:
            continue
        seen.add(d.get("region"))
        out.append(d)
    return out


def node_records(region, ordering, rset="s02"):
    d = os.path.join(_rt(rset), region, ordering)
    if not os.path.isdir(d):
        return []
    out = []
    for p in sorted(glob.glob(os.path.join(d, "*.json"))):
        try:
            out.append(L.jload(p))
        except Exception:
            pass
    return out


def agg(rset, ordering):
    rs = [r for r in rows(rset, ordering) if "error" not in r]
    if not rs:
        return None
    tot = dict(ordering=ordering, rset=rset, regions=len(rs))
    for k in ("nodes", "lps", "logic_kills", "chain_kills", "class_clause", "fires",
              "sampled_pairs", "counterexamples", "certs_pass", "certs_fail"):
        tot[k] = sum(r.get(k) or 0 for r in rs)
    for k in ("lp_wall", "flat900_wall", "cert_wall", "wall"):
        tot[k] = round(sum(r.get(k) or 0.0 for r in rs), 1)
    tot["killed"] = sum(1 for r in rs if r.get("killed"))
    tot["all_leaves_deadish"] = sum(
        1 for r in rs
        if r.get("leaf_status") and all(v in DEADISH for v in r["leaf_status"].values()))
    tot["terminated"] = sum(
        1 for r in rs
        if r.get("leaf_status") and all(v in DEADISH for v in r["leaf_status"].values()))
    tot["open_regions"] = len(rs) - tot["terminated"]
    # what killed the leaves
    kills = dict(logic=0, chain=0, cert=0, cls=0, cap=0, alive=0, other=0)
    for r in rs:
        for v in (r.get("leaf_status") or {}).values():
            if v == "DEAD-LOGIC":
                kills["logic"] += 1
            elif v == "DEAD-CHAIN-LP":
                kills["chain"] += 1
            elif v == "DEAD-CERT":
                kills["cert"] += 1
            elif v == "DEAD-CLASS":
                kills["cls"] += 1
            elif v and v.startswith("CAP"):
                kills["cap"] += 1
            else:
                kills["other"] += 1
    tot["leaf_kills"] = kills
    tot["old_tree"] = dict(
        nodes=round(sum((r.get("old_tree") or {}).get("nodes", 0) for r in rs), 1),
        lps=round(sum((r.get("old_tree") or {}).get("lps", 0) for r in rs), 1),
        wall_s=round(sum((r.get("old_tree") or {}).get("wall_s", 0.0) for r in rs), 1))
    tot["per_region"] = [dict(region=r["region"], nodes=r.get("nodes"), lps=r.get("lps"),
                              lp_wall=r.get("lp_wall"), cert_wall=r.get("cert_wall"),
                              wall=r.get("wall"), killed=r.get("killed"),
                              logic=r.get("logic_kills"),
                              open_leaves=len(r.get("open_leaves") or []),
                              old_tree=r.get("old_tree")) for r in rs]
    return tot


def correlations(rset):
    """PI item: the correlation between the pin-wastage score and the row-mass score, per node."""
    sp_row, sp_str, per = [], [], []
    for ordering in ORDERS:
        for r in rows(rset, ordering):
            for rec in node_records(r.get("region", ""), ordering, rset):
                a = rec.get("wastage_vs_rowmass_spearman")
                b = rec.get("wastage_vs_stranded_spearman")
                if a is not None:
                    sp_row.append(a)
                if b is not None:
                    sp_str.append(b)
                if a is not None:
                    per.append(dict(region=rec.get("region"), ordering=ordering,
                                    key=rec.get("key"), n=rec.get("n_candidates"),
                                    rho_rowmass=round(a, 4),
                                    rho_stranded=(None if b is None else round(b, 4))))
    def sm(v):
        if not v:
            return None
        return dict(n=len(v), mean=round(statistics.fmean(v), 4),
                    median=round(statistics.median(v), 4),
                    min=round(min(v), 4), max=round(max(v), 4),
                    frac_positive=round(sum(1 for x in v if x > 0) / len(v), 3))
    return dict(wastage_vs_rowmass=sm(sp_row), wastage_vs_stranded=sm(sp_str), per_node=per)


def canaries(rset):
    """Trump's grain never killed; every free-kill fire confirmed by dense sampling."""
    viol, fires, sampled, cex, worst = [], 0, 0, 0, -1e18
    for ordering in ORDERS:
        for r in rows(rset, ordering):
            for rec in node_records(r.get("region", ""), ordering, rset):
                if rec.get("trump_realizes") is True and rec.get("status") in DEADISH:
                    viol.append(dict(region=rec.get("region"), ordering=ordering,
                                     key=rec.get("key"), status=rec.get("status")))
                for f in (rec.get("logic") or {}).get("fires", []):
                    fires += 1
                    sm = f.get("sample") or {}
                    sampled += sm.get("n", 0)
                    cex += sm.get("counterexamples", 0)
                    if "worst_sat_gap" in sm:
                        worst = max(worst, sm["worst_sat_gap"])
    return dict(trump_violations=viol, trump_ok=(not viol), fires=fires,
                sampled_pose_pairs=sampled, counterexamples=cex,
                worst_sat_gap=(None if worst < -1e17 else round(worst, 6)),
                dense_sampling_rule_met=bool(sampled >= 10000 and cex == 0))


def head_to_head(rset):
    """Per region, the four orderings side by side: nodes / LPs / LP wall / killed, and which
    ordering wins (fewest nodes to termination, ties broken by LP wall)."""
    try:
        pre = set(L.jload(os.path.join(L.RES, "plan.json")).get("s02_root_trim_dead") or [])
    except Exception:
        pre = set()
    by = {}
    for o in ORDERS:
        for r in rows(rset, o):
            if "error" in r:
                continue
            by.setdefault(r["region"], {})[o] = r
    out, wins = [], {}
    for reg, d in sorted(by.items()):
        rec = dict(region=reg, level=next(iter(d.values())).get("level"),
                   cls=next(iter(d.values())).get("cls"),
                   root_trim_dead=bool(reg in pre))
        cands = []
        for o in ORDERS:
            r = d.get(o)
            if not r:
                continue
            rec[o] = dict(nodes=r.get("nodes"), lps=r.get("lps"), lp_wall=r.get("lp_wall"),
                          killed=r.get("killed"), open=len(r.get("open_leaves") or []),
                          terminated=bool(r.get("leaf_status") and
                                          all(v in DEADISH for v in r["leaf_status"].values())))
            cands.append((0 if rec[o]["terminated"] else 1, rec[o]["nodes"] or 10 ** 6,
                          rec[o]["lp_wall"] or 1e9, o))
        if cands:
            cands.sort()
            best = cands[0]
            tied = [c[3] for c in cands if c[:3] == best[:3]]
            rec["winner"] = best[3]
            rec["tied"] = tied
            # a region all four orderings settle identically says nothing about the ORDER; so
            # does one A96's T5'' trim already kills at the root before any branching happens
            rec["trivial"] = bool(len(tied) == len(cands) or rec["root_trim_dead"])
            if not rec["trivial"]:
                for o in tied:
                    wins[o] = wins.get(o, 0) + 1.0 / len(tied)
        out.append(rec)
    return dict(per_region=out, wins=wins,
                informative=sum(1 for r in out if not r.get("trivial")),
                root_trim_dead=sum(1 for r in out if r.get("root_trim_dead")),
                regions=len(out))


def main():
    out = dict(sets={}, correlations={}, canaries={}, head_to_head={})
    for rset in SETS:
        a = {}
        for o in ORDERS:
            g = agg(rset, o)
            if g:
                a[o] = g
        out["sets"][rset] = a
        out["correlations"][rset] = correlations(rset)
        out["canaries"][rset] = canaries(rset)
        out["head_to_head"][rset] = head_to_head(rset)
    L.jdump(os.path.join(L.RES, "t3%s.json" % L.SUF), out)

    lines = []
    for rset in SETS:
        a = out["sets"].get(rset) or {}
        if not a:
            continue
        lines.append("\n### region set `%s` (%d regions)\n" %
                     (rset, max(g["regions"] for g in a.values())))
        lines.append("| ordering | nodes | LPs | LP wall (protocol) | LP wall (flat 900 s) | "
                     "certify wall | total wall | regions killed | certs P/F | free kills "
                     "(logic+chain) | leaf kills (logic / chain / cert / cap) |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for o in ORDERS:
            g = a.get(o)
            if not g:
                continue
            k = g["leaf_kills"]
            lines.append("| %s | %d | %d | %.0f s | %.0f s | %.0f s | %.0f s | %d/%d | %d/%d | "
                         "%d | %d / %d / %d / %d |"
                         % (o, g["nodes"], g["lps"], g["lp_wall"], g["flat900_wall"],
                            g["cert_wall"], g["wall"], g["killed"], g["regions"],
                            g["certs_pass"], g["certs_fail"],
                            g["logic_kills"] + g["chain_kills"],
                            k["logic"], k["chain"], k["cert"], k["cap"]))
        g0 = next(iter(a.values()))
        ot = g0["old_tree"]
        lines.append("| **old tree (A96 model)** | %.0f | %.0f | %.0f s | %.0f s | — | %.0f s | "
                     "— | — | 0 | — |"
                     % (ot["nodes"], ot["lps"], ot["wall_s"], ot["wall_s"], ot["wall_s"]))
        tot_lp = sum(g["lp_wall"] for g in a.values())
        tot_flat = sum(g["flat900_wall"] for g in a.values())
        if tot_flat > 0:
            lines.append("\nTimeout protocol (PI, 2026-09-06: stage 1 at 240 s, certify anything "
                         "with eta <= -1e-3 at once, escalate only the knife edge to 900 s): "
                         "%.0f s of LP against %.0f s under a flat 900 s cap on the same nodes, "
                         "a factor **%.2f**; per node %.0f s vs %.0f s over %d LPs."
                         % (tot_lp, tot_flat, (tot_flat / tot_lp if tot_lp else 0.0),
                            tot_lp / max(1, sum(g["lps"] for g in a.values())),
                            tot_flat / max(1, sum(g["lps"] for g in a.values())),
                            sum(g["lps"] for g in a.values())))
        c = out["correlations"][rset]["wastage_vs_rowmass"]
        if c:
            lines.append("\nPin wastage vs row mass, Spearman per branching node: n = %d, "
                         "median %.3f, mean %.3f, range [%.3f, %.3f], positive in %.0f%% of nodes."
                         % (c["n"], c["median"], c["mean"], c["min"], c["max"],
                            100 * c["frac_positive"]))
        h = out["head_to_head"][rset]
        lines.append("\nHead to head over %d regions (%d of them informative, i.e. not identical "
                     "for all four orderings): wins %s."
                     % (h["regions"], h["informative"],
                        ", ".join("%s %.1f" % (k, v) for k, v in
                                  sorted(h["wins"].items(), key=lambda kv: -kv[1])) or "none"))
        lines.append("\n| region | L | " + " | ".join("%s nodes/LPs/wall" % o for o in ORDERS) +
                     " | winner |")
        lines.append("|---|---|" + "---|" * (len(ORDERS) + 1))
        for r in h["per_region"]:
            cells = []
            for o in ORDERS:
                v = r.get(o)
                cells.append("—" if not v else "%s / %s / %.0f s%s"
                             % (v["nodes"], v["lps"], v["lp_wall"] or 0.0,
                                "" if v["terminated"] else " (open)"))
            lines.append("| `%s`%s | %s | %s | %s |"
                         % (r["region"], " *(T5″ root kill)*" if r.get("root_trim_dead") else "",
                            r.get("level"), " | ".join(cells),
                            "—" if r.get("trivial") else r.get("winner")))
        cn = out["canaries"][rset]
        lines.append("\nCanaries: Trump's grain killed in %d nodes (must be 0); %d free-kill fires "
                     "checked by %d sampled pose pairs, %d counterexamples, worst SAT gap %s."
                     % (len(cn["trump_violations"]), cn["fires"], cn["sampled_pose_pairs"],
                        cn["counterexamples"], cn["worst_sat_gap"]))
    p = os.path.join(L.BASE, "notes", "t2_table.md")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write("# A112 T2 -- the four orderings, measured\n" + "\n".join(lines) + "\n")
    try:
        print("\n".join(lines))
    except UnicodeEncodeError:            # a cp1252 console; the file itself is utf-8
        sys.stdout.buffer.write(("\n".join(lines)).encode("utf-8", "replace") + b"\n")


if __name__ == "__main__":
    main()
