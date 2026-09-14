"""A212 (progress211 adapted) -- results/progress.md: the table (page, stage, verdict DEAD / TRUMP-TUBE / ALIVE, gate hits, tube depth,
kills by rule, seconds) over every node run so far, the gallery block first; the frontier PRICE (mean / median wall seconds
per node over the first 20 frontier nodes) and the PROJECTION over the remaining frontier; writes logs/STOP when the
projection (plus the CPU-h already spent) exceeds CAP_CPUH = 150.  Run after every node by the worker and hourly."""
import collections
import os
import statistics
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import load212 as L                                            # noqa: E402

RES = os.path.join(HERE, "..", "results", "trump5tree212.jsonl")
OUT = os.path.join(HERE, "..", "results", "progress.md")
STOP = os.path.join(HERE, "..", "logs", "STOP")
CAP_CPUH = 150.0


def main():
    rows = L.jl(RES)
    gal = L.gallery_nids()
    per = collections.OrderedDict()
    for d in rows:
        if d.get("mode") == "page" and d.get("nid"):
            per[d["nid"]] = d                                    # the LAST row per node
    gnodes = [n for n in per if n in gal]
    fnodes = [n for n in per if n not in gal]
    front = L.frontier()
    remaining = [c for c in front if c["nid"] not in per]
    L2 = ["# A212 progress -- %s" % time.strftime("%Y-%m-%d %H:%M:%S"), "",
          "The TRUMP5 tree (notes/trump5_tree.md): A211's coarse tree at PAD 0 ONLY (lam = 1, s0-only) + the Trump-containment GATE (a node holding a D4 image of z-hat "
          "is never submitted to a kill rule) + the TUBE LEAF (all 11 named inside the certified tube radii: TRUMP-TUBE, uniqueness, not a kill) + the ALIGNED split.  "
          "Wall %s s per page; depth cap 6; node cap 600; every kill [C: closed-form / library clip trace + the leaf lemma], no verifier clause." % "1800", ""]

    def table(nodes, title):
        L2.append("## %s (%d nodes)" % (title, len(nodes)))
        L2.append("")
        L2.append("| page | stage reached | verdict | root gate | gate hits | tube leaves (depth) | kills by rule | nodes / depth | seconds |")
        L2.append("|---|---|---|---|---|---|---|---|---|")
        tot = 0.0
        for n in nodes:
            d = per[n]
            st = "0" if d.get("stage0_kill") or not d.get("n_nodes") else "2 (tree)"
            sec = float(d.get("seconds") or 0)
            tot += sec
            g = d.get("gate_root") or {}
            L2.append("| %s | %s | %s%s | %s | %s | %s (%s) | %s | %s / %s | %.0f |" % (
                n, st, d.get("verdict"), " (wall)" if d.get("wall") else (" (killed)" if d.get("killed") else ""), ("contains %s" % g.get("g")) if g.get("contains") else "no",
                d.get("gate_hits", 0), d.get("tube_leaves", 0), d.get("tube_depth"), d.get("kills_by_rule") or {}, d.get("n_nodes"), d.get("max_depth"), sec))
        L2.append("")
        L2.append("CPU-h in this block: %.2f" % (tot / 3600))
        L2.append("")
        return tot

    tg = table(gnodes, "The 13 alive trump5 gallery pages")
    tf = table(fnodes, "A60's alive trump5 frontier (deepest first)")
    cnt = collections.Counter(per[n].get("verdict") for n in per)
    L2.append("## Price and projection")
    L2.append("")
    L2.append("* verdicts so far: %s; gallery %d / %d run (%.2f CPU-h); frontier %d run of %d (%d remaining; %.2f CPU-h)" % (
        dict(cnt), len(gnodes), len(gal), tg / 3600, len(fnodes), len(front), len(remaining), tf / 3600))
    spent = (tg + tf) / 3600
    if fnodes:
        first = [float(per[n].get("seconds") or 0) for n in fnodes][:20]
        mean, med = statistics.mean(first), statistics.median(first)
        proj = mean * len(remaining) / 3600
        L2.append("* PRICE over the first %d frontier nodes: mean %.0f s, median %.0f s per node; PROJECTION for the remaining %d: %.1f CPU-h; spent %.1f; cap %.0f" % (
            len(first), mean, med, len(remaining), proj, spent, CAP_CPUH))
        if (len(first) >= 20 and spent + proj > CAP_CPUH) or spent > CAP_CPUH:
            L2.append("* **STOP: spent + projection exceeds the cap -- the workers exit after their current node**")
            os.makedirs(os.path.dirname(STOP), exist_ok=True)
            open(STOP, "w").write("spent %.1f + projection %.1f CPU-h > %.0f at %s\n" % (spent, proj, CAP_CPUH, time.strftime("%Y-%m-%d %H:%M:%S")))
    elif spent > CAP_CPUH:
        os.makedirs(os.path.dirname(STOP), exist_ok=True)
        open(STOP, "w").write("spent %.1f CPU-h > %.0f at %s\n" % (spent, CAP_CPUH, time.strftime("%Y-%m-%d %H:%M:%S")))
    L2.append("")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(L2) + "\n")
    print("progress: %d gallery, %d frontier nodes; %.1f CPU-h; %s" % (len(gnodes), len(fnodes), spent, dict(cnt)))


if __name__ == "__main__":
    main()
