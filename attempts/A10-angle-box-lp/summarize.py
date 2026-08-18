"""Collect results/*.json -> results/summary.json + markdown table + crossing estimates + plot."""
import json, glob, os, math, sys
here = os.path.dirname(os.path.abspath(__file__))
rows = []
for f in sorted(glob.glob(os.path.join(here, "results", "*.json"))):
    if f.endswith("_state.json") or f.endswith("summary.json"):
        continue
    try:
        d = json.load(open(f))
    except Exception:
        continue
    if "tau" not in d:
        continue
    rows.append(dict(name=os.path.basename(f)[:-5], tag=d.get("tag", ""), s=d["s"], tau=d["tau"], sym=d.get("sym"),
                     box=d.get("theta_box"), alpha=d.get("alpha"), conv=d.get("converged"), minmass=d.get("minmass"),
                     maxcov=d.get("maxcov"), time=d.get("time"), n_rows=d.get("n_rows"), n_orbits=d.get("n_orbits"),
                     iters=len(d.get("history", []))))
rows.sort(key=lambda r: (r["tag"], r["s"]))
json.dump(rows, open(os.path.join(here, "results", "summary.json"), "w"), indent=1)

def crossing(pts, level=11.0 - 1e-6):
    """pts: list of (s, tau) sorted; linear interpolation of the first crossing of level"""
    pts = sorted(pts)
    for (s0, t0), (s1, t1) in zip(pts, pts[1:]):
        if t0 < level <= t1:
            return s0 + (level - t0) / (t1 - t0) * (s1 - s0)
    if pts and pts[0][1] >= level:
        return f"<{pts[0][0]}"
    if pts and pts[-1][1] < level:
        return f">{pts[-1][0]}"
    return None

by_tag = {}
for r in rows:
    by_tag.setdefault(r["tag"], []).append(r)
print("| tag | box | sym | s | tau*_B | conv | minmass | maxcov | iters | time s |")
print("|---|---|---|---|---|---|---|---|---|---|")
for tag, rs in by_tag.items():
    for r in rs:
        print(f"| {tag} | {r['box']} | {r['sym']} | {r['s']} | {r['tau']:.4f} | {r['conv']} | {r['minmass']:.4f} | {r['maxcov']:.4f} | {r['iters']} | {r['time']:.0f} |")
print()
print("| tag | crossing s_B (tau=11, lin. interp.) |")
print("|---|---|")
cross = {}
for tag, rs in by_tag.items():
    c = crossing([(r["s"], r["tau"]) for r in rs if r["alpha"] in (None, "")])
    cross[tag] = c
    print(f"| {tag} | {c if isinstance(c, str) or c is None else round(c, 4)} |")
json.dump(cross, open(os.path.join(here, "results", "crossings.json"), "w"), indent=1)

if "--plot" in sys.argv:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 5))
    for tag, rs in by_tag.items():
        if not tag.startswith("trump") and not tag.startswith("san"):
            continue
        rs2 = [r for r in rs if r["alpha"] in (None, "")]
        ax.plot([r["s"] for r in rs2], [r["tau"] for r in rs2], "o-", label=tag)
    ax.axhline(11, color="k", lw=0.8)
    ax.axvline(3.877083590, color="r", lw=0.8, ls="--", label="s* (Trump)")
    ax.set_xlabel("s"); ax.set_ylabel("tau*_B(s)"); ax.legend(fontsize=7); ax.grid(alpha=0.3)
    ax.set_title("orientation-restricted measure LP: Trump box [0,d] u [theta*-d, theta*+d]")
    fig.tight_layout(); fig.savefig(os.path.join(here, "plots", "tau_trump_box.png"), dpi=130)
    print("plot written")
