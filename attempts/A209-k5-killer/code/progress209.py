"""A209 -- results/progress.md: the table (page, pad, stage reached, verdict, seconds) over every node run so far, the
gallery block first; the frontier PRICE (mean / median wall seconds per node over the first 20 frontier nodes) and the
PROJECTION over the remaining census; writes logs/STOP when the projection exceeds 400 CPU-h (the workers then exit).
Run after every node by the worker (and so at least hourly while anything runs)."""
import collections
import json
import os
import statistics
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import load209 as L                                            # noqa: E402

RES = os.path.join(HERE, "..", "results", "k5killer209.jsonl")
OUT = os.path.join(HERE, "..", "results", "progress.md")
STOP = os.path.join(HERE, "..", "logs", "STOP")
CAP_CPUH = 400.0


def main():
    rows = L.jl(RES)
    gal = set(L.gallery_nids())
    per = collections.OrderedDict()                              # nid -> {pad: row}
    for d in rows:
        if d.get("mode") != "page" or not d.get("nid"):
            continue
        per.setdefault(d["nid"], {})[d.get("pad")] = d
    gnodes = [n for n in per if n in gal]
    fnodes = [n for n in per if n not in gal]
    census = L.census()
    remaining = [c for c in census if c["nid"] not in per]
    L2 = ["# A209 progress -- %s" % time.strftime("%Y-%m-%d %H:%M:%S"), "",
          "Chain: A202 stage 0 + A203 CSP -> A204 cascade -> A205 clip tree (Lemma CT, bar-anon, sharp round) + A206 Rule NS (MAX_FRAC 0.5) + A207 basin clip "
          "(k5_16 TR(1,0) r_c 0.03; k5_11 BL(1,1) r_c 0.06) -> A208 no-room with the pocket CN bound at every leaf with >= 9 roles, pocket branching at k = 9.  "
          "Wall 3600 s per pad per page; depth cap 5; node cap 300; every kill [C: library clip trace (+ A189 Lemma 1 / Lemma CN / Lemma BASIN)], no verifier clause.", ""]

    def table(nodes, title):
        L2.append("## %s (%d nodes)" % (title, len(nodes)))
        L2.append("")
        L2.append("| page | pad | stage reached | verdict | seconds |")
        L2.append("|---|---|---|---|---|")
        tot = 0.0
        for n in nodes:
            for pad in ("g1", "zero"):
                d = per[n].get(pad)
                if d is None:
                    continue
                st = "0" if d.get("stage0_kill") or (d.get("n_nodes") in (None, 0) and str(d.get("leaf", "")).startswith("stage 0")) else "2 (tree: %s nodes, depth %s, NS %s, pockets %s)" % (d.get("n_nodes"), d.get("max_depth"), d.get("ns_splits"), d.get("pocket_splits"))
                v = d.get("verdict")
                if v == "DEAD" and pad == "zero":
                    v = "DEAD (s0-only, WINDOW-PENDING)"
                sec = float(d.get("seconds") or 0)
                tot += sec
                L2.append("| %s | %s | %s | %s%s | %.0f |" % (n, pad, st, v, " (wall)" if d.get("wall") else "", sec))
            v = (per[n].get("g1") or {}).get("verdicts") or {}
            if v.get("zero", "").startswith("not run"):
                L2.append("| %s | zero | - | %s | 0 |" % (n, v["zero"]))
        L2.append("")
        L2.append("CPU-h in this block: %.2f" % (tot / 3600))
        L2.append("")
        return tot

    tg = table(gnodes, "The 22 alive k5 gallery pages")
    tf = table(fnodes, "The k5 frontier (A57 census, deepest-first)")
    secs = [sum(float(d.get("seconds") or 0) for d in per[n].values()) for n in fnodes]
    kills_g = sum(1 for n in gnodes if (per[n].get("g1") or {}).get("verdict") == "DEAD")
    kills_f = sum(1 for n in fnodes if (per[n].get("g1") or {}).get("verdict") == "DEAD")
    L2.append("## Price and projection")
    L2.append("")
    L2.append("* gallery: %d / %d pages DEAD at the window pad, %.2f CPU-h" % (kills_g, len(gnodes), tg / 3600))
    if fnodes:
        first = secs[:20]
        mean, med = statistics.mean(first), statistics.median(first)
        proj = mean * len(remaining) / 3600
        L2.append("* frontier: %d nodes run (%d DEAD at the window pad), %.2f CPU-h; the census has %d alive nodes, %d remaining" % (len(fnodes), kills_f, tf / 3600, len(census), len(remaining)))
        L2.append("* PRICE over the first %d frontier nodes: mean %.0f s, median %.0f s per node (both pads); PROJECTION for the remaining %d: %.1f CPU-h (cap %.0f)" % (len(first), mean, med, len(remaining), proj, CAP_CPUH))
        if len(first) >= 20 and proj > CAP_CPUH:
            L2.append("* **STOP: the projection exceeds the cap -- the workers exit after their current node**")
            os.makedirs(os.path.dirname(STOP), exist_ok=True)
            open(STOP, "w").write("projection %.1f CPU-h > %.0f at %s\n" % (proj, CAP_CPUH, time.strftime("%Y-%m-%d %H:%M:%S")))
    else:
        L2.append("* frontier: not started; the census has %d alive nodes (%s)" % (len(census), dict(collections.Counter(c["tree"] for c in census))))
    L2.append("")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(L2) + "\n")
    print("progress: %d gallery, %d frontier nodes; %.1f CPU-h" % (len(gnodes), len(fnodes), (tg + tf) / 3600))


if __name__ == "__main__":
    main()
