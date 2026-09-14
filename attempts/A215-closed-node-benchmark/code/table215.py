"""A215 -- build results/benchmark215.md from results/times215.tsv + results/bench215.jsonl."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, "..", ".."))
OLDV = {  # nid -> (campaign, old seconds, old verdict, note)
 "k5_11_interior_Y0308": ("A205", 203.2, "DEAD", "clip tree, root-to-kill"),
 "k5_16_interior_Y0054": ("A205", 312.2, "DEAD", "clip tree, root-to-kill"),
 "k5_16_interior_Y0027": ("A205", 365.2, "DEAD", "clip tree, root-to-kill"),
 "k5_16_interior_Y0565": ("A205", 397.1, "DEAD", "clip tree, root-to-kill"),
 "k5_16_interior_Y0839": ("A205", 526.2, "DEAD", "clip tree, root-to-kill"),
 "k5_16_interior_Y0881": ("A211 pass 1", 879.1, "DEAD", "WITH inherit (2 inherited dead branches)"),
 "k5_16_interior_Y0719": ("A211", 236.6, "DEAD", "WITH inherit (4 inherited dead branches)"),
 "k5_16_interior_Y1110": ("A209", 1765.5, "DEAD", "root-to-kill from the A203 root"),
 "k5_11_interior_Y0036_D07": ("A211f", 106.2, "DEAD", "pad 0; WITH inherit (6 inherited dead); A211e before = 528.9"),
 "k5_11_interior_Y0985": ("A206", 2120.8, "DEAD", "Rule-NS tree on A205's leaves (not root-to-kill)"),
 "k5_11_interior_Y1104": ("A206", 2401.3, "DEAD", "Rule-NS tree on A205's leaves (not root-to-kill)"),
}
rows = {}
res = os.path.join(ATT, "results", "bench215.jsonl")
if os.path.exists(res):
    for line in open(res, encoding="utf-8"):
        try: r = json.loads(line)
        except Exception: continue
        rows[(r.get("nid"), r.get("pad"))] = r
out = []
tim = os.path.join(ATT, "results", "times215.tsv")
for line in open(tim, encoding="utf-8"):
    p = line.rstrip("\n").split("\t")
    if len(p) < 6 or p[0] == "nid": continue
    nid, pad, camp, old, new, rc = p[0], p[1], p[2], float(p[3]), float(p[4]), int(p[5])
    r = rows.get((nid, pad), {})
    out.append(dict(nid=nid, pad=pad, camp=OLDV[nid][0], old=OLDV[nid][1], oldv=OLDV[nid][2], note=OLDV[nid][3],
                    new=new, rowsec=r.get("seconds"), verdict=r.get("verdict", "(no row)"), rc=rc,
                    nodes=r.get("n_nodes"), alive=r.get("alive_leaves"), wall=r.get("wall"),
                    leaf=(r.get("leaf") or "")[:120]))
L = []
L.append("# A215 -- CLOSED-NODE BENCHMARK of the current A211 runner (2026-09-14)\n")
L.append("Each node re-run ROOT-TO-KILL with `attempts/A211-coarse-tree/code/run211.py page <nid> --pads <pad> "
         "--wall 3600 --no-inherit --cert-dir attempts/A215-closed-node-benchmark/certs "
         "--results attempts/A215-closed-node-benchmark/results/bench215.jsonl --no-fig`, every optimisation flag at "
         "its default (A213 integer core, A213b integer clip, A214 C kernel, A211e/f conditional coarse core, A211d/f "
         "memos), ONE process at a time, BelowNormal (A210's fix), BLAS pinned, `PYTHONDONTWRITEBYTECODE=1`.\n")
L.append("`new (s)` is the WALL of the whole process (stage 0 + load + tree), which is what the old campaign seconds "
         "also measured.\n")
L.append("| node | pad | old campaign | old (s) | new (s) | ratio | verdict | agrees? |")
L.append("|---|---|---|---:|---:|---:|---|---|")
rat = []
for r in out:
    ok = (r["verdict"] == r["oldv"])
    ratio = r["old"] / r["new"] if r["new"] > 0 else float("nan")
    if ok: rat.append(ratio)
    L.append("| `%s` | %s | %s | %.1f | %.0f | %s | %s | %s |" % (
        r["nid"], r["pad"], r["camp"], r["old"], r["new"],
        ("%.2fx" % ratio) if r["new"] > 0 else "-", r["verdict"],
        "yes" if ok else "**NO -- REGRESSION**"))
L.append("")
if rat:
    g = math.exp(sum(math.log(x) for x in rat) / len(rat))
    L.append("**Geometric-mean speedup over the %d agreeing nodes: %.2fx**  (spread %.2fx -- %.2fx; "
             "median %.2fx)\n" % (len(rat), g, min(rat), max(rat), sorted(rat)[len(rat)//2]))
bad = [r for r in out if r["verdict"] != r["oldv"]]
if bad:
    L.append("## REGRESSIONS -- nodes that no longer die\n")
    for r in bad:
        L.append("* `%s` pad %s: was **%s** in %s (%.1f s), now **%s** after %.0f s (rc %s, wall-limited=%s, "
                 "%s nodes, %s alive leaves)." % (r["nid"], r["pad"], r["oldv"], r["camp"], r["old"],
                 r["verdict"], r["new"], r["rc"], r["wall"], r["nodes"], r["alive"]))
    L.append("")
else:
    L.append("No regression: every node still dies, with the old verdict.\n")
L.append("## Per-run detail\n")
L.append("| node | pad | nodes | alive leaves | rc | wall-limited | row seconds | leaf |")
L.append("|---|---|---:|---:|---:|---|---:|---|")
for r in out:
    L.append("| `%s` | %s | %s | %s | %s | %s | %s | %s |" % (r["nid"], r["pad"], r["nodes"], r["alive"], r["rc"],
             r["wall"], r["rowsec"], r["leaf"].replace("|", "/")))
L.append("")
L.append("## Caveats on the OLD seconds (quoted exactly from the campaign rows)\n")
for r in out:
    L.append("* `%s` pad %s -- %s, %.1f s, %s: %s" % (r["nid"], r["pad"], r["camp"], r["old"], r["oldv"], r["note"]))
L.append("")
st = os.path.join(ATT, "results", "stagetable215.txt")
if os.path.exists(st):
    L.append("## Stage table (A211f `code/profstage211.py`) for two runs\n")
    L.append("```")
    L.append(open(st, encoding="utf-8").read().rstrip())
    L.append("```")
open(os.path.join(ATT, "results", "benchmark215.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))
