"""A168 resume -- the per-cell summary block (markdown) computed from the tree, the LP records and the
A171 re-verification; printed and written to results/report168_<cell>.md.

    python report168.py --cell l1_104
"""
import argparse
import json
import os
import sys
from collections import Counter, OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cas168 as K                                               # noqa: E402
import cascade168 as CS                                          # noqa: E402


def kind(v):
    if v.startswith("ALIVE"):
        return "ALIVE"
    if v.startswith("PRUNED"):
        return "PRUNED"
    if v.startswith("OPEN"):
        return "OPEN"
    if "ancestor" in v:
        return "DEAD(ancestor)"
    for key, tag in (("R3 lonely", "DEAD(R3 lonely)"), ("R1 ", "DEAD(R1 cells/linf)"),
                     ("coexistence", "DEAD(coexistence)"), ("OVL", "DEAD(OVL)"), ("PAIR", "DEAD(PAIR)"),
                     ("EMPTY after the mutual clip", "DEAD(clip-empty)"), ("chord row", "DEAD(row)"),
                     ("A171", "DEAD(A171 EmptyBox)"), ("LP", "DEAD(LP)")):
        if key in v:
            return tag
    return "DEAD(other)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", default="l1_104")
    a = ap.parse_args()
    T = K.jload(CS.tree_path(a.cell))
    lines = []
    L = lines.append
    L("### %s -- tree summary (computed %s)" % (a.cell, __import__("time").strftime("%Y-%m-%d %H:%M")))
    L("")
    L("| step | ALIVE | DEAD by leaf | PRUNED | OPEN |")
    L("|---|---|---|---|---|")
    by = OrderedDict()
    for p, n in T["nodes"].items():
        st = n.get("step") or "root"
        by.setdefault(st, Counter())[kind(n["verdict"])] += 1
    for st, c in by.items():
        dead = ", ".join("%s %d" % (k[5:-1], v) for k, v in sorted(c.items()) if k.startswith("DEAD"))
        L("| %s | %d | %s | %d | %d |" % (st, c.get("ALIVE", 0), dead or "-", c.get("PRUNED", 0), c.get("OPEN", 0)))
    L("")
    for st, cx in (T.get("coex") or {}).items():
        L("* coexistence cut at %s (second meeter %s): %d first-meeter boxes before, %d after, %d killed"
          % (cx["corner"], cx["second"], cx["n_before"], cx["n_after"], cx["n_killed"]))
    # per-step coexistence status from the nodes themselves
    for st in ("S1", "S3", "S5", "S7"):
        ns = [n for n in T["nodes"].values() if n.get("step") == st and n.get("roles")]
        if not ns:
            continue
        done = [n for n in ns if n.get("coex_done")]
        ok = [n for n in done if n.get("coex", {}).get("ok")]
        alive_untested = [n for n in ns if n["verdict"].startswith("ALIVE") and not n.get("coex_done")]
        L("* %s nodes: %d recorded, coexistence tested %d (coexist %d, killed %d), ALIVE and not yet tested %d"
          % (st, len(ns), len(done), len(ok), len(done) - len(ok), len(alive_untested)))
    if T.get("a169"):
        L("* A169 post-hoc leaves: %s" % T["a169"])
    if T.get("a171"):
        L("* A171 re-verification: %s" % {k: v for k, v in T["a171"].items() if k != "settings"})
    L("* wall-capped nodes: %d" % len(__import__("resume168").wallcapped(a.cell)))
    L("* dead by ancestor (propagated at summary): %s" % T.get("n_dead_by_ancestor"))
    for im in T["canary"]["images"]:
        L("* canary %s: %s" % (im["image"], {k: v for k, v in im.items() if k.endswith("_nodes")}))
    p = os.path.join(K.RES, "lp_%s.jsonl" % a.cell)
    if os.path.exists(p):
        L("")
        L("| LP node | roles | budget | tau | eta | converged | certified | verdict | wall s |")
        L("|---|---|---|---|---|---|---|---|---|")
        for ln in open(p, encoding="utf-8"):
            d = json.loads(ln)
            L("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                d["node"], ",".join(d.get("roles") or []), d.get("budget"),
                ("%.4f" % d["tau"]) if d.get("tau") is not None else "-",
                ("%+.4f" % d["eta"]) if d.get("eta") is not None else "-", d.get("converged"),
                d.get("certified"), d.get("verdict"), d.get("wall_s")))
    # the deepest alive nodes
    alive = [(n.get("level", 0), p) for p, n in T["nodes"].items() if n["verdict"].startswith("ALIVE") and n.get("roles")]
    if alive:
        mx = max(l for l, _ in alive)
        deep = sorted(p for l, p in alive if l == mx)
        L("")
        L("* deepest ALIVE level %d: %d nodes, e.g. %s" % (mx, len(deep), deep[:4]))
    out = os.path.join(K.RES, "report168_%s.md" % a.cell)
    open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
