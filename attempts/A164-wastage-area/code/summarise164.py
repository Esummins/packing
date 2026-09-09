"""A164 -- the population table and the |U| / (s0^2 - 11) distribution.

    set PYTHONDONTWRITEBYTECODE=1 && python summarise164.py --tags k0v4b,a57v4b
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import geo164 as G                                                    # noqa: E402


def load(tags):
    rows = []
    for t in tags:
        p = os.path.join(BASE, "results", f"u164_{t}.jsonl")
        if not os.path.exists(p):
            continue
        for ln in open(p, encoding="utf-8"):
            ln = ln.strip()
            if ln:
                rows.append(json.loads(ln))
    seen, out = set(), []
    for r in rows:                              # last row per id wins
        pass
    by = {}
    for r in rows:
        by[r["id"]] = r
    return sorted(by.values(), key=lambda r: -r["area_U"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tags", default="k0v4b,a57v4b")
    ap.add_argument("--out", default="summary164")
    a = ap.parse_args()
    rows = load(a.tags.split(","))
    if not rows:
        print("no rows")
        return
    L = []
    L.append(f"A164 -- UNCOVERABLE AREA over {len(rows)} nodes.  Budget B0 = s0^2 - 11 = "
             f"{G.B0:.12f} (the largest wastage budget on the window slab "
             f"[{G.M_WINDOW_LO}, s0]); a node is DEAD when |U| > B0.")
    L.append("")
    L.append(f"{'node':34s} {'camp':5s} {'lvl':>3s} {'box':>3s} {'pin':>3s} {'bud':>3s} "
             f"{'|U|':>9s} {'%B0':>7s} {'U:corners':>10s} {'U:strips':>9s} {'U:interior':>10s} "
             f"{'adm-hits':>8s} {'kill':>5s}")
    for r in rows:
        br = r["by_region"]
        cor = sum(br[f"corner_{c}"]["area_U"] for c in ("BL", "BR", "TR", "TL"))
        st = sum(br[f"strip_{c}"]["area_U"] for c in ("S", "E", "N", "W"))
        L.append(f"{r['id']:34s} {r['camp']:5s} {r.get('level', ''):>3} {r['n_boxes']:>3d} "
                 f"{r['n_pins']:>3d} {r['budget']:>3d} {r['area_U']:>9.5f} "
                 f"{100 * r['ratio_B0']:>6.2f}% {cor:>10.5f} {st:>9.5f} "
                 f"{br['interior']['area_U']:>10.5f} {r['sample']['free']['hits']:>8d} "
                 f"{'YES' if r['combined_kill'] else 'no':>5s}")
    L.append("")
    v = sorted(r["ratio_B0"] for r in rows)
    n = len(v)

    def q(f):
        return v[min(n - 1, int(f * n))]
    L.append(f"DISTRIBUTION of |U| / (s0^2 - 11) over {n} nodes: min {v[0] * 100:.3f}%, "
             f"q1 {q(0.25) * 100:.2f}%, median {q(0.5) * 100:.2f}%, q3 {q(0.75) * 100:.2f}%, "
             f"max {v[-1] * 100:.2f}%; mean {100 * sum(v) / n:.2f}%.  "
             f"Nodes above 50% of the budget: {sum(1 for x in v if x > 0.5)}; above 100% (a "
             f"KILL): {sum(1 for x in v if x > 1.0)}.")
    edges = [0, .01, .05, .10, .15, .20, .25, .30, .50, 1.0, 9e9]
    hist = [sum(1 for x in v if edges[i] <= x < edges[i + 1]) for i in range(len(edges) - 1)]
    L.append("HISTOGRAM (fraction of B0): " + ", ".join(
        f"[{edges[i] * 100:.0f},{min(edges[i + 1], 100) * 100 if edges[i+1] < 9e8 else 100:.0f})% "
        f"{hist[i]}" for i in range(len(hist)) if hist[i]))
    L.append("")
    byc = {}
    for r in rows:
        byc.setdefault((r["camp"], r["n_pins"]), []).append(r["ratio_B0"])
    L.append("BY CAMPAIGN / PIN COUNT (mean and max of |U|/B0):")
    for k in sorted(byc):
        vv = byc[k]
        L.append(f"  {k[0]:5s} {k[1]} pin(s): n = {len(vv):2d}, mean "
                 f"{100 * sum(vv) / len(vv):6.2f}%, max {100 * max(vv):6.2f}%")
    L.append("")
    tot_hits = sum(r["sample"]["free"]["hits"] for r in rows)
    tot_adm = sum(r["sample"]["free"]["admissible"] for r in rows)
    tot_dr = sum(r["sample"]["free"]["drawn"] for r in rows)
    tot_te = sum(r["sample"]["free"].get("tested", r["sample"]["free"]["admissible"])
                 for r in rows)
    L.append(f"SAMPLED CROSS-CHECK over the whole population: {tot_dr} poses drawn, {tot_adm} "
             f"certified admissible by an independent SAT pass, {tot_te} of those carried through "
             f"the containment test, {tot_hits} of them contain a certified-uncoverable cell "
             f"centre.  (Any hit refutes the raster.)")
    cr = [r for r in rows if r.get("crowd", {}).get("applicable")]
    if cr:
        L.append(f"CONDITIONAL CROWD ROW (K0-FREE', applicable on {len(cr)} pin-free nodes): "
                 f"area outside every corner-committed square's reach, max "
                 f"{max(x['crowd']['area_B'] for x in cr):.5f}, needs > n_loose + B0 = "
                 f"{cr[0]['crowd']['n_loose'] + G.B0:.4f} — "
                 + ("KILL" if any(x['crowd']['kill'] for x in cr) else "no kill anywhere"))
    txt = "\n".join(L)
    print(txt)
    open(os.path.join(BASE, "results", a.out + ".txt"), "w", encoding="utf-8").write(txt + "\n")
    import csv
    with open(os.path.join(BASE, "results", a.out + ".csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["node", "camp", "cls", "level", "n_boxes", "n_pins", "budget", "area_U",
                    "ratio_B0", "U_corners", "U_strips", "U_interior", "U_right_wall_strip",
                    "pitch", "ntilt", "lam", "sample_drawn", "sample_admissible", "sample_hits",
                    "crowd_applicable", "crowd_area_B", "kill", "seconds", "record"])
        for r in rows:
            br = r["by_region"]
            w.writerow([r["id"], r["camp"], r.get("cls"), r.get("level"), r["n_boxes"],
                        r["n_pins"], r["budget"], f"{r['area_U']:.6f}", f"{r['ratio_B0']:.6f}",
                        f"{sum(br[f'corner_{c}']['area_U'] for c in ('BL', 'BR', 'TR', 'TL')):.6f}",
                        f"{sum(br[f'strip_{c}']['area_U'] for c in ('S', 'E', 'N', 'W')):.6f}",
                        f"{br['interior']['area_U']:.6f}",
                        f"{r['bands']['right_wall_strip(x>=s-1)']['area_U']:.6f}",
                        f"{r['pitch']:.6f}", r["ntilt"], f"{r['lam']:.6f}",
                        r["sample"]["free"]["drawn"], r["sample"]["free"]["admissible"],
                        r["sample"]["free"]["hits"],
                        r.get("crowd", {}).get("applicable"),
                        r.get("crowd", {}).get("area_B"),
                        "YES" if r["combined_kill"] else "no", f"{r['seconds']:.1f}",
                        r.get("record")])
    print("wrote", os.path.join(BASE, "results", a.out + ".txt/.csv"))


if __name__ == "__main__":
    main()
