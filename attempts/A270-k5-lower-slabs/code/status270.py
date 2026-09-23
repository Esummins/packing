"""A270 -- the per-slab STATUS of k5_11 / k5_16 (and trump5), recomputed from disk; READ-ONLY on every campaign.

What a kill covers is decided by its hypothesis (notes/slabs270.md s.1-2, code/pads270.py):
  * an A205/A206/A209/A211 page kill at pad g1 on an A57 record (pins +-1e-2)  -> (3.861637, s0] = G1 (A211 S6 + B')
  * the same at pad 0 (lam = 1)                                                   -> s0 only (WINDOW-PENDING)
  * an A57 G1 LP PASS (cores a = 49/100) / a logic or pin-clip kill at a_pin 49/100 -> m >= 3.851408 with A_S = 3/2: G1
  * an A137 / A149 exact-core LP kill (pin core 1/2 - 0.0070711)                  -> m >= 3.858893 with A_S = 3/2: G1
    (with the census A = 5/2 it would reach only 3.866149: G1 needs A_S = 3/2 -- slot_crowds.md s.0)
  * anything else on the board (A190 guard-line v5, A161 lane, A182 ASSIGN, A136 composition, A198 fastprop, ...)
    -> 'unclassified' here: its slab is whatever its own certificate's side and pin slack give; not cited below.
No kill on disk covers G2, G3 or G4 (every k5 record carries pin slack <= 1e-2; drift at g2 is 0.0117 > 1e-2).

    python status270.py      -> results/slabs270.json + results/slabs270.md"""
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, "..", ".."))
A211 = os.path.join(ROOT, "attempts", "A211-coarse-tree")
sys.path.insert(0, os.path.join(A211, "code"))
sys.path.insert(0, os.path.join(ROOT, "docs", "shadows"))


def jl(p):
    out = []
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8"):
            try:
                out.append(json.loads(ln))
            except Exception:                                   # noqa: BLE001
                pass
    return out


def slab_of(r):
    """the slab a board kill row covers, from its leaf / note / attempt (the classification in the docstring)."""
    t = " ".join(str(r.get(k) or "") for k in ("leaf", "note", "source", "attempt"))
    if re.search(r"s0-only|WINDOW-PENDING|zero pad|\[pad 0|pad 0 \(lam = 1\)", t):
        return "s0"
    if re.search(r"\bg1 pad|the g1 pad|stage1-propagation; g1", t):
        return "G1"
    if re.search(r"window pad|the window pad", t):
        return "G1"                                   # an A57 record (+-1e-2) at the window pad: m >= 3.851408 only
    if re.search(r"case-measure-certificate|PASS --|pin-clip|T5|KILL-BY-LOGIC|tight common-inscribed|logic", t):
        return "G1"
    return "unclassified"


def main():
    import load211 as L
    out = dict(classes={}, gallery=[], a96={}, frontier={})
    trees = L.trees()
    for cls in ("k5_11", "k5_16"):
        c = collections.Counter()
        for key, ids in trees.items():
            if key.startswith(cls):
                for i, (v, r) in ids.items():
                    c[(key, v)] += 1
        out["classes"][cls] = {"%s|%s" % k: n for k, n in sorted(c.items())}
    census = L.census()
    out["census_alive"] = dict(collections.Counter(d["tree"] for d in census))
    # the A211 frontier / gallery page rows, last row per (nid, pad)
    per = collections.defaultdict(dict)
    for d in jl(os.path.join(A211, "results", "coarsetree211.jsonl")):
        if d.get("mode") == "page" and d.get("nid"):
            per[d["nid"]][d.get("pad")] = d
    gal = set(L.gallery_nids())
    for cls in ("k5_11", "k5_16"):
        f = [n for n in per if n not in gal and n.startswith(cls)]
        out["frontier"][cls] = dict(nodes=len(f), g1_dead=sum(1 for n in f if (per[n].get("g1") or {}).get("verdict") == "DEAD"),
                                    zero_dead=sum(1 for n in f if (per[n].get("zero") or {}).get("verdict") == "DEAD"),
                                    other_pads=sorted({p for n in f for p in per[n] if p not in ("g1", "zero")}))
    # the gallery pages: every kill on the board's kill table, classified by slab
    import status_gallery as SG                                   # READ-ONLY: its collectors, no write
    corpus, tags_of = SG.load_a57_corpus()
    table = SG.Table(corpus, tags_of)
    SG.collect(table, corpus)
    for g in SG.load_galleries():
        for p in g["pages"]:
            if p["camp"] != "A57":
                continue
            st, rec, how, direct = SG.decide(table, p)
            kills = table.kills_for("A57", p["tag"], p["node"])
            slabs = sorted({slab_of(k) for k in kills})
            g1 = [k for k in kills if slab_of(k) == "G1"]
            a211 = (per.get(p["node"]) or {}).get("g1") or {}
            out["gallery"].append(dict(page=p["node"], tag=p["tag"], board=st, board_how=how, slabs=slabs,
                                       g1_cited=bool(g1) or a211.get("verdict") == "DEAD",
                                       g1_source=(g1[0]["attempt"] + ": " + str(g1[0]["cert"])) if g1 else (
                                           "A211 g1 page row" if a211.get("verdict") == "DEAD" else None),
                                       board_leaf=(rec or {}).get("leaf", "")[:90] if rec else None))
    # A96's parametric pass: node rows and their certified window fraction
    for f in ("param96.jsonl", "param96_level2.jsonl"):
        for d in jl(os.path.join(ROOT, "attempts", "A96-a57-parametric", "results", f)):
            cls = str(d.get("name") or d.get("cls", ""))[:5]
            cov = d.get("coverage") or {}
            k = "full" if cov.get("certified_frac") == 1.0 else ("partial" if cov else str(d.get("verdict")))
            out["a96"].setdefault(cls, collections.Counter())[k] += 1
    out["a96"] = {k: dict(v) for k, v in out["a96"].items()}
    json.dump(out, open(os.path.join(ATT, "results", "slabs270.json"), "w", encoding="utf-8"), indent=1, default=str)
    md = ["# A270 -- per-slab audit of the k5 board (generated by code/status270.py; read-only on every campaign)", "",
          "census alive (load211.census): %s" % (out["census_alive"] or "0"), "",
          "| class | frontier pages | DEAD at g1 | DEAD at pad 0 (s0 only) | other pads |", "|---|---|---|---|---|"]
    for cls, v in out["frontier"].items():
        md.append("| %s | %d | %d | %d | %s |" % (cls, v["nodes"], v["g1_dead"], v["zero_dead"], v["other_pads"] or "-"))
    md += ["", "A96 parametric rows (node, certified fraction of [3.82, s0]): %s" % out["a96"], "",
           "| gallery page | board | slabs of its kills | G1 cited | G1 source |", "|---|---|---|---|---|"]
    for r in out["gallery"]:
        md.append("| %s | %s | %s | %s | %s |" % (r["page"], r["board"], ", ".join(r["slabs"]) or "-", "yes" if r["g1_cited"] else "**NO**",
                                                (r["g1_source"] or "-")[:110]))
    open(os.path.join(ATT, "results", "slabs270.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
    bad = [r["page"] for r in out["gallery"] if r["board"] == "DEAD" and not r["g1_cited"]]
    print("census alive %s; frontier %s; gallery DEAD without a cited G1 kill: %s" % (out["census_alive"], out["frontier"], bad))


if __name__ == "__main__":
    main()
