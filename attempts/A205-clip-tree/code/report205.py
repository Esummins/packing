"""A205 report: per (page, pad) the verdict, tree size / depth, seconds, the killing leaves (branch -> clip -> round ->
seconds), the undecided leaves; from results/cliptree205.jsonl + certs.      python report205.py -> results/report205.md"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, ".."))
RES = os.path.join(ATT, "results", "cliptree205.jsonl")


def rows():
    last = {}
    for ln in open(RES, encoding="utf-8"):
        try:
            d = json.loads(ln)
        except Exception:
            continue
        if d.get("pad") in ("g1", "zero"):
            last[(d["nid"], d["pad"])] = d
    return last


def main():
    R = rows()
    L = ["# A205 cliptree205 -- report (from results/cliptree205.jsonl + certs)", ""]
    L.append("| page | pad | verdict | nodes | depth | dead / alive leaves | total s | root s (rounds) | root branch | killing leaves (label slot<-rows: clip r round, s) | undecided |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    tot = 0.0
    for (nid, pad), d in sorted(R.items()):
        rt = d.get("root") or {}
        kills = "; ".join("%s %s<-%s: %s r%s, %ss" % (k.get("label"), k.get("slot") or "root", k.get("rows"), k.get("clip"), k.get("round"), k.get("seconds")) for k in d.get("killing") or []) or "-"
        und = "; ".join("%s (%s)" % (u.get("label"), str(u.get("reason") or "")[:60]) for u in d.get("undecided") or []) or "-"
        L.append("| %s | %s | **%s** | %s | %s | %s / %s | %s%s | %s (%s) | %s over %s | %s | %s |" % (
            nid.replace("_interior", ""), pad, d.get("verdict"), d.get("n_nodes"), d.get("max_depth"), d.get("dead_leaves"), d.get("alive_leaves"),
            d.get("seconds"), " WALL" if d.get("wall") else "", rt.get("seconds"), rt.get("n_rounds"), rt.get("branch_slot"), rt.get("branch_rows"),
            kills.replace("|", "/"), und.replace("|", "/")))
        tot += float(d.get("seconds") or 0)
    pages = {n for n, _ in R}
    dead = {n for (n, p), d in R.items() if d.get("verdict") == "DEAD"}
    L += ["", "- %d (page, pad) runs, %.2f CPU-h; pages %d touched, %d DEAD at some pad (%d at g1), %d ALIVE" % (
        len(R), tot / 3600, len(pages), len(dead), len({n for (n, p), d in R.items() if d.get("verdict") == "DEAD" and p == "g1"}), len(pages - dead))]
    out = "\n".join(L)
    open(os.path.join(ATT, "results", "report205.md"), "w", encoding="utf-8").write(out + "\n")
    print(out)


if __name__ == "__main__":
    main()
