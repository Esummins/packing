"""Collect tau*(s) from results/v2_*.json (+ v1 grid results) and plot. usage: python plot_tau.py"""
import json, glob, math, os
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

rows = []
for f in sorted(glob.glob("results/v2_s*.json")):
    if f.endswith("_state.json"):
        continue
    r = json.load(open(f))
    h = r["history"]
    last = h[-1] if h else {}
    rows.append(dict(file=os.path.basename(f), s=r["s"], tau=r["tau"], conv=r["converged"], rows=r["n_rows"],
                     orbits=r["n_orbits"], minmass=last.get("minmass"), maxcov=last.get("maxcov"), it=len(h),
                     mode="rowonly" if "rowonly" in f else "joint"))
rows.sort(key=lambda r: (r["s"], r["mode"]))
print("| s | mode | tau (LP) | converged | last minmass | last maxcov | rows | orbits | iters | file |")
print("|---|---|---|---|---|---|---|---|---|---|")
for r in rows:
    print(f"| {r['s']:.4f} | {r['mode']} | {r['tau']:.4f} | {r['conv']} | {r['minmass'] if r['minmass'] is None else round(r['minmass'],4)} | "
          f"{r['maxcov'] if r['maxcov'] is None else round(r['maxcov'],4)} | {r['rows']} | {r['orbits']} | {r['it']} | {r['file']} |")
json.dump(rows, open("results/tau_table.json", "w"), indent=1)

fig, ax = plt.subplots(figsize=(8, 5))
J = [r for r in rows if r["mode"] == "joint"]; R = [r for r in rows if r["mode"] == "rowonly"]
ax.plot([r["s"] for r in J], [r["tau"] for r in J], "o-", label="tau* (row+column generation, free atoms)")
if R:
    ax.plot([r["s"] for r in R], [r["tau"] for r in R], "s", label="row-converged (primal feasible; certificate basis)")
ax.axhline(11, color="r", ls="--", lw=1, label="n = 11 threshold"); ax.axhline(10, color="g", ls="--", lw=1, label="n = 10 threshold")
ax.axvline(2 + 2 * math.sqrt(0.8), color="gray", ls=":", label="Stromquist 3.7889")
ax.axvline(3.877084, color="k", ls=":", label="best packing 3.877084")
ax.axvline(3 + 1 / math.sqrt(2), color="green", ls=":", lw=0.8, label="s(10) = 3.7071")
ax.set_xlabel("s"); ax.set_ylabel("tau*(s) = nu*(s)"); ax.grid(alpha=0.3); ax.legend(fontsize=8)
ax.set_title("LP / measure bound: minimal blocking mass tau*(s)")
plt.tight_layout(); plt.savefig("plots/tau_vs_s.png", dpi=120)
print("saved plots/tau_vs_s.png")
