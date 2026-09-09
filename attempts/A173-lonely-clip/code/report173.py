"""A173 -- the measurement table and the histogram numbers, from results/measure173_*.jsonl.

Writes results/report173.json and results/table173.md.  Read-only on A168.
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.abspath(os.path.join(HERE, "..", "results"))
BINS = [0.0, 0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.95, 1.0000001]


def load():
    """every measured node, DEDUPED by (cell, step, path): the sweep is resumable and shardable, so
    two processes can in principle both finish the same node; the last record written wins."""
    seen = {}
    for fn in sorted(glob.glob(os.path.join(RES, "measure173_*.jsonl"))):
        for line in open(fn, encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                seen[(r["cell"], r["step"], r["path"])] = r
    return list(seen.values())


def summarise(rows):
    out = dict(n_nodes=len(rows), by_step={}, base_kills=[], lonely_kills=[], errors=[],
               hist_rel_loss={}, table=[])
    for r in rows:
        b, l = r.get("base", {}), r.get("lonely", {})
        key = r["step"]
        st = out["by_step"].setdefault(key, dict(n=0, alive_both=0, base_kill=0, lonely_kill=0,
                                                 err=0, sum_D_before=0.0, sum_D_after=0.0,
                                                 sum_K_before=0.0, sum_K_after=0.0,
                                                 h_moved=0, inv_fail=0, losses=[]))
        st["n"] += 1
        if "error" in b or "error" in l:
            st["err"] += 1
            out["errors"].append(dict(cell=r["cell"], step=key, path=r["path"],
                                      err=(b.get("error") or l.get("error"))))
            continue
        if b.get("kill"):
            st["base_kill"] += 1
            out["base_kills"].append(dict(cell=r["cell"], step=key, path=r["path"],
                                          box=b.get("kill_box"),
                                          reason=(b.get("kill_detail") or {}).get("reason")))
            continue
        if l.get("kill"):
            st["lonely_kill"] += 1
            out["lonely_kills"].append(dict(cell=r["cell"], step=key, path=r["path"],
                                            box=l.get("kill_box"),
                                            D_kept_base=b["kept"]["D"],
                                            reason=(l.get("kill_detail") or {}).get("reason")))
            rel = 1.0
        else:
            st["alive_both"] += 1
            rel = 1.0 - l["kept"]["D"] / b["kept"]["D"] if b["kept"]["D"] > 0 else 0.0
            st["sum_D_before"] += b["kept"]["D"]
            st["sum_D_after"] += l["kept"]["D"]
            st["sum_K_before"] += b["k_area"]["D"]
            st["sum_K_after"] += l["k_area"]["D"]
            if abs(l["kept"]["H"] - b["kept"]["H"]) > 1e-9:
                st["h_moved"] += 1
            if not l.get("invariant", True):
                st["inv_fail"] += 1
        st["losses"].append(rel)
        out["table"].append(dict(
            cell=r["cell"], step=key, path=r["path"],
            D_kept_before=round(b["kept"]["D"], 6),
            D_kept_after=(None if l.get("kill") else round(l["kept"]["D"], 6)),
            rel_loss=round(rel, 6),
            K_D_before=round(b["k_area"]["D"], 6),
            K_D_after=(None if l.get("kill") else round(l["k_area"]["D"], 6)),
            H_kept_before=round(b["kept"]["H"], 6),
            H_kept_after=(None if l.get("kill") else round(l["kept"]["H"], 6)),
            passes_before=b.get("passes"), passes_after=l.get("passes"),
            invariant=(None if l.get("kill") else l.get("invariant")),
            kill=bool(l.get("kill")),
            lonely_removed=(l.get("lonely_removed") or {}).get("D"),
            seconds=[b.get("seconds"), l.get("seconds")]))
    allloss = []
    for k, st in out["by_step"].items():
        L = st.pop("losses")
        allloss += [(k, v) for v in L]
        st["mean_rel_loss"] = round(sum(L) / len(L), 6) if L else 0.0
        st["median_rel_loss"] = round(sorted(L)[len(L) // 2], 6) if L else 0.0
        st["D_kept_total_before"] = round(st.pop("sum_D_before"), 6)
        st["D_kept_total_after"] = round(st.pop("sum_D_after"), 6)
        st["K_D_mean_before"] = round(st.pop("sum_K_before") / max(st["alive_both"], 1), 6)
        st["K_D_mean_after"] = round(st.pop("sum_K_after") / max(st["alive_both"], 1), 6)
    for step in sorted(out["by_step"]):
        h = [0] * (len(BINS) - 1)
        for (k, v) in allloss:
            if k != step:
                continue
            for i in range(len(BINS) - 1):
                if BINS[i] <= v < BINS[i + 1]:
                    h[i] += 1
                    break
        out["hist_rel_loss"][step] = dict(
            edges=[f"{BINS[i]:.2f}-{BINS[i + 1]:.2f}" for i in range(len(BINS) - 1)], counts=h)
    out["table"].sort(key=lambda r: -r["rel_loss"])
    return out


def md(o):
    L = ["# A173 -- the LONELY CLIP on A168's ALIVE nodes (D = first TR meeter, c = 1 + w)", "",
         "`base` = A171/A172 `normalise` (container + mutual clip).  `lonely` = the same with",
         "A173's lonely clip on D at every pass.  Same starting boxes (the A168 roles' piece hulls),",
         "same nsub / refine / max_iter.  KILL = `EmptyBox`: D lost every pose, i.e. the node is dead",
         "by A169 row R3 -- a kill A168's whole-role `lonely_role` test could not see.", ""]
    L.append("| step | nodes | alive both | LONELY KILL | base kill | mean rel. loss of D | "
             "median | mean K'(D) before -> after | H moved |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for step in sorted(o["by_step"]):
        s = o["by_step"][step]
        L.append(f"| {step} | {s['n']} | {s['alive_both']} | {s['lonely_kill']} | "
                 f"{s['base_kill']} | {s['mean_rel_loss']:.4f} | {s['median_rel_loss']:.4f} | "
                 f"{s['K_D_mean_before']:.4f} -> {s['K_D_mean_after']:.4f} | {s['h_moved']} |")
    L += ["", "## relative loss of D's kept fraction (histogram, KILL counted as 1.0)", ""]
    for step, h in o["hist_rel_loss"].items():
        L.append(f"* **{step}**: " + "  ".join(f"{e}: {c}" for e, c in zip(h["edges"], h["counts"])))
    L += ["", "## the nodes, worst first", "",
          "| cell | step | node | D kept before | after | rel. loss | K'(D) before | after | "
          "H kept before | after | passes | inv |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in o["table"]:
        af = "**KILL**" if r["kill"] else f"{r['D_kept_after']:.6f}"
        ka = "-" if r["kill"] else f"{r['K_D_after']:.6f}"
        ha = "-" if r["kill"] else f"{r['H_kept_after']:.6f}"
        L.append(f"| {r['cell']} | {r['step']} | `{r['path']}` | {r['D_kept_before']:.6f} | {af} | "
                 f"{r['rel_loss']:.4f} | {r['K_D_before']:.6f} | {ka} | "
                 f"{r['H_kept_before']:.6f} | {ha} | {r['passes_before']}/{r['passes_after']} | "
                 f"{'ok' if r['invariant'] else ('-' if r['kill'] else 'FAIL')} |")
    if o["base_kills"]:
        L += ["", "## nodes the BASE run already kills (an A172 effect, not A173's)", ""]
        for r in o["base_kills"]:
            L.append(f"* {r['cell']} {r['step']} `{r['path']}` -- box {r['box']} ({r['reason']})")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    rows = load()
    o = summarise(rows)
    json.dump(o, open(os.path.join(RES, "report173.json"), "w", encoding="utf-8"), indent=1)
    text = md(o)
    open(os.path.join(RES, "table173.md"), "w", encoding="utf-8").write(text)
    NOTES = os.path.abspath(os.path.join(HERE, "..", "notes"))
    os.makedirs(NOTES, exist_ok=True)
    open(os.path.join(NOTES, "measure.md"), "w", encoding="utf-8").write(text)
    for step in sorted(o["by_step"]):
        print(step, o["by_step"][step], flush=True)
    print("lonely kills:", len(o["lonely_kills"]), " base kills:", len(o["base_kills"]),
          " errors:", len(o["errors"]))
    print("->", os.path.join(RES, "table173.md"))
    sys.exit(0)
