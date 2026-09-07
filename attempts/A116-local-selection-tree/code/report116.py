"""A116 -- tabulate results/t2_*.jsonl into notes/t2_table.md (per (r, rho): near pairs, leaves after the
interval census, tree nodes / closed leaves, verdict, certified minimum, measured minimum, sampling,
Trump canary, wall time; the largest certified (r, rho) per shadow and what limits it)."""
from __future__ import annotations
import glob, json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a116lib as A


def load():
    recs = []
    for p in sorted(glob.glob(os.path.join(A.RES, "t2_*.jsonl"))):
        for line in open(p):
            try:
                recs.append(json.loads(line))
            except Exception:
                pass
    return recs


def verdict(d):
    t = d["tree"]
    if t["dead"]:
        ok = d.get("sampling", {}).get("hits", 1) == 0 and not d["trump"]["inside"]
        return "DEAD" if ok else "DEAD?(check)"
    if d["n_witnesses"]:
        w = d["witnesses"][0]
        return "ALIVE (witness %.6f)" % w["witness_side"]
    if t["capped"]:
        return "CAP"
    return "UNRESOLVED"


def limiter(d):
    """what the lowest closed leaf / the witness realises: the dual support rows of the certified-min leaf."""
    if d["n_witnesses"]:
        w = d["witnesses"][0]
        sels = w["fixed"]
        return "witness: " + ", ".join("%s%s" % (k, v) for k, v in sels.items() if k.split("|")[0].startswith("f") or k.split("|")[1].startswith("f"))
    leaf = d["tree"].get("certified_min_leaf")
    if not leaf or not leaf.get("support"):
        return "-"
    rows = []
    for m, y in leaf["support"]:
        if m[0] == "sel":
            rows.append("%s|%s" % (m[1], m[2]))
        elif m[0] == "wall":
            rows.append("wall:%s/%s" % (m[1], m[2]))
    return " ".join(sorted(set(rows)))


def main():
    recs = load()
    lines = ["# A116 T2 -- the measured radius (results/t2_*.jsonl)", ""]
    groups = {}
    for d in recs:
        key = (d["tag"], d["cls"], d["label"], str(d["cut"]), str(d.get("ceil")), round(d["pin_slack"], 5))
        groups.setdefault(key, []).append(d)
    summary = []
    for key in sorted(groups):
        tag, cls, label, cut, ceil, slack = key
        ds = sorted(groups[key], key=lambda d: (d["rho"], d["r"]))
        lines.append("## %s / %s  label %s  cut %s  ceil %s  pin slack %s  L = %s" % (tag, cls, label, cut, ceil, slack, ds[0]["loadbearing"]))
        lines.append("")
        lines.append("| r | rho | near pairs | leaves (interval) | nodes | closed leaves | branch / bisect / qsplit | verdict | certified min | measured min (SLSQP) | samples / hits | Trump in N | tree s | total s | chain of the lowest leaf / witness |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        best = None
        for d in ds:
            t = d["tree"]; st = t["stats"]
            v = verdict(d)
            cm = t.get("certified_min")
            lm = d.get("local_min", {}) or {}
            samp = d.get("sampling")
            lines.append("| %.3f | %.1f | %d | %d | %d | %d | %d / %d / %d | %s | %s | %s | %s | %s | %.0f | %.0f | %s |" % (
                d["r"], d["rho"], t["n_near"], t["leaves_after_interval"], st["nodes"], t["n_closed"], st["branch"], st["bisect"], st["qsplit"],
                v, ("%.6f" % cm) if cm else "-", ("%.6f" % lm["side"]) if lm else "-",
                ("%d / %d" % (samp["n_samples"], samp["hits"])) if samp else "-", d["trump"]["inside"], d["seconds_tree"], d["seconds"], limiter(d)))
            if v == "DEAD" and (best is None or (d["r"] * d["rho"], d["r"], d["rho"]) > best[0]):
                best = ((d["r"] * d["rho"], d["r"], d["rho"]), d)
        lines.append("")
        if best:
            d = best[1]
            summary.append("%s/%s [%s, cut %s, ceil %s]: largest certified (r, rho) = (%.3f, %.1f deg); certified min %.6f, measured %.6f, %.0f s" % (
                tag, cls, label, cut, ceil, d["r"], d["rho"], d["tree"]["certified_min"] or float("nan"),
                (d.get("local_min") or {}).get("side", float("nan")), d["seconds_tree"]))
    lines.insert(2, "\n".join("* " + s for s in summary) + "\n")
    with open(os.path.join(A.BASE, "notes", "t2_table.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("\n".join(summary))


if __name__ == "__main__":
    main()
