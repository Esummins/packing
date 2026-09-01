"""A53: assemble the eta_residual table from node results + campaign jsonl + certs."""
import glob, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))

def main():
    rows = []
    for p in sorted(glob.glob(os.path.join(BASE, "results", "nodes", "*.json"))):
        r = json.load(open(p))
        name = r.get("skeleton_name", os.path.basename(p)[:-5])
        cert = "-"
        cp = os.path.join(BASE, "certs_wip", f"{name}.json")
        if os.path.exists(cp + ".PASS"):
            cert = "PASS"
        elif os.path.exists(cp):
            rep = cp.replace(".json", ".json.report.json")
            cert = "attempted"
            try:
                rr = json.load(open(cp + ".report.json"))
                cert = "PASS" if rr.get("verified") else "FAIL"
            except Exception:
                pass
        rows.append(dict(name=name, k=r["k"], budget=r["budget"], tau=r["tau"],
                         eta=r["tau"] - r["budget"], conv=r["converged"],
                         dead_lp=r["tau"] < r["budget"] - 1e-6, cert=cert,
                         slots=r["skeleton_slots"]))
    rows.sort(key=lambda x: (x["k"], x["name"]))
    lines = ["| node | k | budget | tau (LP) | eta_residual | conv | LP<budget | exact cert |",
             "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['name']} | {r['k']} | {r['budget']} | {r['tau']:.6f} | "
                     f"{r['eta']:+.6f} | {'Y' if r['conv'] else 'n'} | "
                     f"{'KILL' if r['dead_lp'] else 'alive'} | {r['cert']} |")
    table = "\n".join(lines)
    open(os.path.join(BASE, "results", "eta_table.md"), "w").write(table + "\n")
    print(table)
    ks = {}
    for r in rows:
        ks.setdefault(r["k"], [0, 0, 0])
        ks[r["k"]][0] += 1
        if r["dead_lp"]:
            ks[r["k"]][1] += 1
        if r["cert"] == "PASS":
            ks[r["k"]][2] += 1
    print("\nby k: {k: [n, lp_kill, cert_pass]}", ks)

if __name__ == "__main__":
    main()
