"""A145 T1(b)/T3 -- the ranking, the distribution, and the two job lists.

`results/impossible_weight.jsonl` (all 448) is the measurement.  This script

  * ranks by the EXACT impossible fraction (the sound one: weight on columns meeting K'(B) or an
    exact pin core, over total dual-support weight), descending;
  * prints the distribution and the top 30;
  * writes `results/jobs145_rank.json`  -- Y0241 first, then the ranking descending (T2's order);
  * writes `results/jobs145_ctrl.json`  -- a STRATIFIED control sample across the whole range.
    Without it the re-solves are all drawn from one tail and "is the fraction a predictor?" cannot
    be answered: a kill rate measured only at frac ~ 0.9 has nothing to be compared against.

    set PYTHONDONTWRITEBYTECODE=1 && python code/rank145.py
"""
import argparse
import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
SRC = os.path.join(BASE, "results", "impossible_weight.jsonl")
FIRST = "k5_11_interior_Y0241"


def load():
    return [json.loads(l) for l in open(SRC, encoding="utf-8") if l.strip()]


def job(r, tag, rank):
    return dict(id=r["id"], box=r["box"], budget=r.get("budget") or 5, tag=tag, rank=rank,
                frac_exact=r.get("frac_exact"), frac_grid=r.get("frac_grid"),
                tau_rec=r.get("tau_rec"), eta_rec=r.get("eta_rec"), verdict=r.get("verdict"),
                level=r.get("level"), cls=r.get("cls"),
                w_imposs_exact=r.get("w_imposs_exact"), w_total=r.get("w_total"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n_rank", type=int, default=18)
    ap.add_argument("--n_ctrl_per_band", type=int, default=3)
    a = ap.parse_args()
    R = [r for r in load() if r.get("status") == "ok"]
    R.sort(key=lambda r: (-(r.get("frac_exact") or 0.0), -(r.get("w_imposs_exact") or 0.0),
                          r["id"]))
    fe = [r["frac_exact"] for r in R]
    fg = [r["frac_grid"] for r in R]
    print(f"{len(R)} nodes measured")
    print(f"frac_exact: mean {statistics.mean(fe):.4f}  median {statistics.median(fe):.4f}  "
          f"min {min(fe):.4f}  max {max(fe):.4f}  zero {sum(1 for f in fe if f == 0)}  "
          f"=1 {sum(1 for f in fe if f >= 0.999)}")
    print(f"frac_grid : mean {statistics.mean(fg):.4f}  median {statistics.median(fg):.4f}")
    print("decile histogram of frac_exact:")
    for k in range(10):
        n = sum(1 for f in fe if (k / 10.0) <= f < ((k + 1) / 10.0 if k < 9 else 1.0001))
        print(f"  [{k/10:.1f},{(k+1)/10:.1f}) {n:4d}  " + "#" * int(n / 3))
    print("\nTOP 30 by exact impossible fraction")
    print(f"{'#':>3} {'node':32s} {'L':>2} {'v':>4} {'sup':>5} {'wtot':>7} {'w_imp':>7} "
          f"{'frac':>6} {'grid':>6} {'H':>4} {'pin':>4} {'tau_rec':>10}")
    for i, r in enumerate(R[:30]):
        print(f"{i+1:3d} {r['id']:32s} {r['level']:2d} "
              f"{('A' if str(r.get('verdict','')).startswith('ALIVE') else 'F'):>4} "
              f"{r['n_support_meas']:5d} {r['w_total']:7.3f} {r['w_imposs_exact']:7.3f} "
              f"{r['frac_exact']:6.3f} {r['frac_grid']:6.3f} "
              f"{r['n_imposs_exact_H']:4d} {r['n_imposs_exact_pin']:4d} "
              f"{(r['tau_rec'] if r['tau_rec'] is not None else float('nan')):10.6f}")

    rankpos = {r["id"]: i + 1 for i, r in enumerate(R)}
    first = [r for r in R if r["id"] == FIRST]
    rest = [r for r in R if r["id"] != FIRST]
    J = [job(r, "rank", rankpos[r["id"]]) for r in (first + rest)][:a.n_rank]
    json.dump(J, open(os.path.join(BASE, "results", "jobs145_rank.json"), "w"), indent=1)
    print(f"\njobs145_rank.json: {len(J)} nodes, first = {J[0]['id']} "
          f"(frac {J[0]['frac_exact']}, ranking position {J[0]['rank']})")

    # --- stratified controls: n per band, taken from the MIDDLE of each band by weight so the
    # sample is not the band's own extreme.  Bands chosen to span the observed range.
    bands = [(0.0, 0.15), (0.15, 0.30), (0.30, 0.45), (0.45, 0.60)]
    C, seen = [], {j["id"] for j in J}
    for lo, hi in bands:
        inb = [r for r in R if lo <= r["frac_exact"] < hi and r["id"] not in seen]
        inb.sort(key=lambda r: abs(r["frac_exact"] - 0.5 * (lo + hi)))
        for r in inb[:a.n_ctrl_per_band]:
            seen.add(r["id"])
            C.append(job(r, f"ctrl[{lo:.2f},{hi:.2f})", rankpos[r["id"]]))
    json.dump(C, open(os.path.join(BASE, "results", "jobs145_ctrl.json"), "w"), indent=1)
    print(f"jobs145_ctrl.json: {len(C)} nodes, fracs "
          + ", ".join(f"{c['frac_exact']:.3f}" for c in C))


if __name__ == "__main__":
    main()
