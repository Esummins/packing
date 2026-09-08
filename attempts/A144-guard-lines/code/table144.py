"""A144 -- assemble T2's table: node x (max offline violation, tau before/after, eta, converged,
kill), from results/offline144.jsonl + results/invitro144_s*.jsonl.

    set PYTHONDONTWRITEBYTECODE=1 && python code/table144.py
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
RES = os.path.join(BASE, "results")


def main():
    off = {}
    for ln in open(os.path.join(RES, "offline144.jsonl"), encoding="utf-8"):
        if ln.strip():
            r = json.loads(ln)
            off[r["id"]] = r
    rows = []
    for f in sorted(glob.glob(os.path.join(RES, "invitro144_s*.jsonl"))):
        for ln in open(f, encoding="utf-8"):
            if ln.strip():
                rows.append(json.loads(ln))
    rows = [r for r in rows if "arms" in r]
    rows.sort(key=lambda r: -(r.get("offline_max_viol") or -9e9))
    hdr = ("| node | L | rank | offline viol | tau stored | tau base | tau guard | eta guard | "
           "conv b/g | kill b/g | z>0 | wall s |")
    sep = "|---|---|---|---|---|---|---|---|---|---|---|---|"
    out = [hdr, sep]
    n_kill_base = n_kill_guard = n_new = 0
    for r in rows:
        b, g = r["arms"].get("base", {}), r["arms"].get("guard", {})
        kb, kg = bool(b.get("kills")), bool(g.get("kills"))
        n_kill_base += kb
        n_kill_guard += kg
        n_new += (kg and not kb)
        nz = sum(1 for e in (g.get("z") or []) if e["z"] > 1e-9)
        out.append(
            f"| `{r['id']}` | {r['level']} | {r['rank']} | {r.get('offline_max_viol'):+.6f} | "
            f"{(r['control'].get('tau') or float('nan')):.6f} | "
            f"{(b.get('tau') if b.get('tau') is not None else float('nan')):.6f} | "
            f"{(g.get('tau') if g.get('tau') is not None else float('nan')):.6f} | "
            f"{(g.get('eta') if g.get('eta') is not None else float('nan')):+.6f} | "
            f"{'Y' if b.get('converged') else 'n'}/{'Y' if g.get('converged') else 'n'} | "
            f"{'Y' if kb else 'n'}/{'Y' if kg else 'n'} | {nz}/{len(g.get('z') or [])} | "
            f"{r.get('wall_s')} |")
    summ = dict(n_nodes=len(rows), kills_base=n_kill_base, kills_guard=n_kill_guard,
                kills_new_from_guard=n_new,
                wall_s=round(sum(r.get("wall_s") or 0 for r in rows), 1),
                cpu_h=round(sum(r.get("wall_s") or 0 for r in rows) / 3600.0, 3),
                delta_tau=[dict(id=r["id"], d=r.get("delta_tau")) for r in rows],
                nodes=[dict(id=r["id"], level=r["level"], rank=r["rank"],
                            offline_viol=r.get("offline_max_viol"),
                            tau_stored=r["control"].get("tau"),
                            tau_base=r["arms"].get("base", {}).get("tau"),
                            tau_guard=r["arms"].get("guard", {}).get("tau"),
                            eta_guard=r["arms"].get("guard", {}).get("eta"),
                            conv_base=r["arms"].get("base", {}).get("converged"),
                            conv_guard=r["arms"].get("guard", {}).get("converged"),
                            kill_base=bool(r["arms"].get("base", {}).get("kills")),
                            kill_guard=bool(r["arms"].get("guard", {}).get("kills")),
                            z=[e for e in (r["arms"].get("guard", {}).get("z") or [])
                               if e["z"] > 1e-9],
                            frozen_cert=r["arms"].get("guard", {}).get("frozen_cert"),
                            exact_cores_ok=r["exact_cores"]["ok"],
                            err_base=r["arms"].get("base", {}).get("error"),
                            err_guard=r["arms"].get("guard", {}).get("error"))
                       for r in rows])
    json.dump(summ, open(os.path.join(RES, "table144.json"), "w", encoding="utf-8"), indent=1)
    open(os.path.join(RES, "table144.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("\n".join(out))
    print()
    print(json.dumps({k: v for k, v in summ.items() if k not in ("nodes", "delta_tau")}, indent=1))


if __name__ == "__main__":
    main()
