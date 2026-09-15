"""A220 -- fold the benchmark certificates into results/bench220.jsonl + results/bench220.md.

One row per (config tag, page): the g1 run's verdict, seconds, node / kill counters, the A220 counters and the WALL
SPLIT BY STAGE (addendum): coarse rounds (the node records' own seconds), no-room (every A189 run at a leaf), the
exact cascade (the `x` records plus the budgeted exact-first rounds that did not kill) and the rest.  Ratios are
taken against the `off` row of the same page (the same code, the A220 flags unset).
    python attempts/A220-exact-first/code/analyze220.py [--quiet]
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
A220 = os.path.abspath(os.path.join(HERE, ".."))
CERTS = os.path.join(A220, "results", "certs")
OUT_J = os.path.join(A220, "results", "bench220.jsonl")
OUT_M = os.path.join(A220, "results", "bench220.md")
ORDER = ["base", "eqbase", "eqoff", "off", "ef", "efs", "nri"]


def stages(run):
    """seconds by stage: coarse rounds / no-room / exact cascade / other."""
    nodes = run.get("nodes") or []
    coarse = exact = 0.0
    ef_runs = ef_kills = ef_to = 0
    for n in nodes:
        sec = float(n.get("seconds") or 0.0)
        if n.get("coarse") is False or n.get("kind") == "exact":
            exact += sec
        else:
            coarse += sec
        ef = n.get("exact_first")
        if ef:
            ef_runs += 1
            ef_to += 1 if ef.get("timeout") else 0
            if ef.get("verdict") == "DEAD":
                ef_kills += 1
            else:
                exact += float(ef.get("seconds") or 0.0)
    nr = sum(float(r.get("seconds") or 0.0) for r in (run.get("noroom_runs") or []))
    tot = float(run.get("seconds") or 0.0)
    return dict(coarse=round(coarse, 1), noroom=round(nr, 1), exact=round(exact, 1),
                other=round(max(0.0, tot - coarse - nr - exact), 1), total=round(tot, 1),
                ef_runs=ef_runs, ef_kills=ef_kills, ef_timeouts=ef_to)


def row_of(tag, nid, path):
    try:
        doc = json.load(open(path, encoding="utf-8"))
    except Exception as e:                                        # noqa: BLE001
        return dict(tag=tag, nid=nid, error=repr(e)[:120])
    run = (doc.get("runs") or {}).get("g1_page") or {}
    if not run:
        return dict(tag=tag, nid=nid, error="no g1 run")
    st = stages(run)
    cfg = run.get("cfg") or {}
    return dict(tag=tag, nid=nid, verdict=run.get("verdict"), seconds=st["total"], n_nodes=run.get("n_nodes"),
                max_depth=run.get("max_depth"), dead_leaves=run.get("dead_leaves"), alive_leaves=run.get("alive_leaves"),
                cc_kills=run.get("cc_kills"), exact_rounds=run.get("exact_rounds"), rsplits=run.get("rsplits"),
                ns_splits=run.get("ns_splits"), pocket_splits=run.get("pocket_splits"), n_inherited=run.get("n_inherited"),
                inherit=(cfg.get("inherit")), wall=run.get("wall"), n_noroom=len(run.get("noroom_runs") or []),
                ef_runs=run.get("ef_runs", st["ef_runs"]), ef_kills=run.get("ef_kills", st["ef_kills"]),
                ef_timeouts=run.get("ef_timeouts", st["ef_timeouts"]), ef_seconds=run.get("ef_seconds"),
                nr_short=run.get("nr_short"), a220=cfg.get("a220"),
                stage=dict(coarse=st["coarse"], noroom=st["noroom"], exact=st["exact"], other=st["other"]),
                node_labels=[n.get("label") for n in (run.get("nodes") or [])],
                node_verdicts=["%s:%s:%s" % (n.get("label"), n.get("verdict"), n.get("clip")) for n in (run.get("nodes") or [])])


def collect():
    rows = []
    if not os.path.isdir(CERTS):
        return rows
    for tag in sorted(os.listdir(CERTS)):
        d = os.path.join(CERTS, tag)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.startswith("coarsetree211_") and f.endswith(".json"):
                rows.append(row_of(tag, f[len("coarsetree211_"):-len(".json")], os.path.join(d, f)))
    rows.sort(key=lambda r: (r["nid"], ORDER.index(r["tag"]) if r["tag"] in ORDER else 99))
    return rows


def pct(a, b):
    return "%d%%" % round(100.0 * a / b) if b else "-"


def table(rows):
    base = {r["nid"]: r for r in rows if r.get("tag") == "off" and not r.get("error")}
    L = ["# A220 benchmark -- exact-first (flag A220_EXACT_FIRST) and the short no-room child cap (A220_NOROOM_INHERIT)",
         "",
         "`off` = the same code with every A220 flag unset (the control); `ef` = exact-first at every role split;",
         "`efs` = exact-first only when the role the split would bisect is positionally small (< 0.25); `nri` = `efs`",
         "+ the short no-room child cap; `eqbase` / `eqoff` = the equivalence pair (pre-A220 code vs this code, flags",
         "off, same page / pad / wall).  All runs: pad g1, one runner, BelowNormal, wall as shown.", "",
         "| page | cfg | inh | verdict | s | ratio | nodes | dead | cc | rsplit | exact | ef run/kill/TO | nr runs | short | coarse s | noroom s | exact s | other s |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r.get("error"):
            L.append("| %s | %s | | ERROR %s | | | | | | | | | | | | | | |" % (r["nid"], r["tag"], r["error"]))
            continue
        b = base.get(r["nid"])
        ratio = "%.2f" % (r["seconds"] / b["seconds"]) if (b and b.get("seconds") and r["tag"] != "off") else ("1.00" if r["tag"] == "off" else "-")
        s = r["stage"]
        L.append("| %s | %s | %s | %s%s | %.0f | %s | %s | %s | %s | %s | %s | %s/%s/%s | %s | %s | %s (%s) | %s (%s) | %s (%s) | %s |" % (
            r["nid"], r["tag"], "y" if r.get("inherit") else "n", r.get("verdict"), " (wall)" if r.get("wall") else "",
            r["seconds"], ratio, r.get("n_nodes"), r.get("dead_leaves"), r.get("cc_kills"), r.get("rsplits"), r.get("exact_rounds"),
            r.get("ef_runs"), r.get("ef_kills"), r.get("ef_timeouts"), r.get("n_noroom"), r.get("nr_short"),
            s["coarse"], pct(s["coarse"], r["seconds"]), s["noroom"], pct(s["noroom"], r["seconds"]),
            s["exact"], pct(s["exact"], r["seconds"]), s["other"]))
    for tag in ("ef", "efs", "nri"):
        rs = [(r, base.get(r["nid"])) for r in rows if r.get("tag") == tag and not r.get("error")]
        rs = [(r, b) for r, b in rs if b and b.get("seconds")]
        if rs:
            g = math.exp(sum(math.log(r["seconds"] / b["seconds"]) for r, b in rs) / len(rs))
            bad = [r["nid"] for r, b in rs if b.get("verdict") == "DEAD" and r.get("verdict") != "DEAD"]
            L += ["", "**%s**: geometric-mean ratio %.3f over %d page(s)%s." % (
                tag, g, len(rs), "; VERDICT REGRESSION on %s" % ", ".join(bad) if bad else "; no verdict regression")]
    eq = {r["tag"]: r for r in rows if r.get("tag") in ("eqbase", "eqoff") and not r.get("error")}
    if len(eq) == 2:
        same = eq["eqbase"]["node_verdicts"] == eq["eqoff"]["node_verdicts"]
        L += ["", "**flag-off equivalence** (%s, pad g1, no inherit): pre-A220 code %s in %.0f s (%d nodes) vs this code %s in %.0f s (%d nodes) -- node list and verdicts %s." % (
            eq["eqbase"]["nid"], eq["eqbase"]["verdict"], eq["eqbase"]["seconds"], eq["eqbase"]["n_nodes"],
            eq["eqoff"]["verdict"], eq["eqoff"]["seconds"], eq["eqoff"]["n_nodes"], "IDENTICAL" if same else "DIFFER")]
        if not same:
            a, b = eq["eqbase"]["node_verdicts"], eq["eqoff"]["node_verdicts"]
            L.append("  first difference: %s" % next((("%s vs %s" % (x, y)) for x, y in zip(a, b) if x != y), "length %d vs %d" % (len(a), len(b))))
    return "\n".join(L) + "\n"


def main():
    rows = collect()
    with open(OUT_J, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    md = table(rows)
    with open(OUT_M, "w", encoding="utf-8") as f:
        f.write(md)
    if "--quiet" not in sys.argv:
        print(md)


if __name__ == "__main__":
    main()
