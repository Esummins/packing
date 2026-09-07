"""A132 T1 -- tables from results/measure132.jsonl (class x level), plus the trim96 comparison."""
import json
import os
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))


def med(v):
    return float(np.median(v)) if len(v) else float("nan")


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, "results", "measure132.jsonl")
    R = [json.loads(l) for l in open(src) if l.strip()]
    R = [r for r in R if "error" not in r]
    print(f"{len(R)} nodes\n")

    hdr = (f"{'class':14s} {'lvl':>3s} {'n':>4s} {'areaK':>7s} {'areaP':>7s} {'P/K':>5s} "
           f"{'sup':>5s} {'sup+':>5s} {'%':>5s} {'w+':>6s} {'w+/tau':>6s} "
           f"{'pool':>7s} {'pool+':>6s} {'%':>5s} {'kill_b':>6s} {'kill_t':>6s} {'T5p':>4s}")
    print(hdr)
    print("-" * len(hdr))
    G = defaultdict(list)
    for r in R:
        G[(r["cls"], r["level"])].append(r)
    tot = defaultdict(float)
    for k in sorted(G):
        rs = G[k]
        n = len(rs)
        sup = sum(x["support"]["n"] for x in rs)
        supp = sum(x["support"]["n_poly_only"] for x in rs)
        wp = sum(x["support"]["w_poly_only"] for x in rs)
        tau = sum(x["support"]["w"] for x in rs)
        pool = sum(x["pool"]["n"] for x in rs)
        poolp = sum(x["pool"]["n_poly_only"] for x in rs)
        kb = sum(1 for x in rs if x.get("kills_brief"))
        kt = sum(1 for x in rs if x.get("kills_tight"))
        t5 = sum(1 for x in rs if x.get("t5poly_dead"))
        print(f"{k[0]:14s} {k[1]:3d} {n:4d} {med([x['area_core'] for x in rs]):7.4f} "
              f"{med([x['area_poly'] for x in rs]):7.4f} {med([x['area_ratio'] for x in rs]):5.3f} "
              f"{sup:5d} {supp:5d} {100.0 * supp / max(sup, 1):5.1f} {wp:6.2f} "
              f"{wp / max(tau, 1e-9):6.3f} {pool:7d} {poolp:6d} {100.0 * poolp / max(pool, 1):5.1f} "
              f"{kb:6d} {kt:6d} {t5:4d}")
        for nm, v in (("n", n), ("sup", sup), ("supp", supp), ("wp", wp), ("tau", tau),
                      ("pool", pool), ("poolp", poolp), ("kb", kb), ("kt", kt), ("t5", t5)):
            tot[nm] += v
    print("-" * len(hdr))
    print(f"{'ALL':14s} {'':3s} {int(tot['n']):4d} {'':7s} {'':7s} "
          f"{med([x['area_ratio'] for x in R]):5.3f} "
          f"{int(tot['sup']):5d} {int(tot['supp']):5d} {100 * tot['supp'] / max(tot['sup'], 1):5.1f} "
          f"{tot['wp']:6.2f} {tot['wp'] / max(tot['tau'], 1e-9):6.3f} "
          f"{int(tot['pool']):7d} {int(tot['poolp']):6d} {100 * tot['poolp'] / max(tot['pool'], 1):5.1f} "
          f"{int(tot['kb']):6d} {int(tot['kt']):6d} {int(tot['t5']):4d}")
    print("\nlegend: sup = dual-support columns, sup+ = those meeting K' but not K(a); w+ = their "
          "weight; pool = rows_all; kill_b = w+ >= tau-(budget-1); kill_t = w+ > tau-budget; "
          "T5p = K'(B) meets a pin K'(P)")

    # ---- nodes with no offending support at all
    zero = [r for r in R if r["support"]["n_poly_only"] == 0]
    print(f"\nnodes with ZERO offending support columns: {len(zero)} / {len(R)}")
    fr = [r["support"]["w_poly_only"] / max(r["support"]["w"], 1e-9) for r in R]
    print(f"offending weight / tau: median {med(fr):.3f}, p90 {float(np.percentile(fr, 90)):.3f}, "
          f"max {max(fr):.3f}")

    # ---- the four L3 nodes the PI checked
    print("\nthe level-3 A57 nodes:")
    for r in sorted([x for x in R if x["camp"] == "A57" and x["level"] == 3], key=lambda x: x["id"]):
        print(f"  {r['id']:30s} P/K {r['area_ratio']:.3f}  support {r['support']['n_poly_only']}"
              f"/{r['support']['n']} w+ {r['support']['w_poly_only']:.3f} of tau "
              f"{r['support']['w']:.3f}  pool {r['pool']['n_poly_only']}/{r['pool']['n']}")

    # ---- T5-polygon kills vs trim96's empties
    t96 = json.load(open(os.path.join(ROOT, "A96-a57-parametric", "results", "trim96.json")))
    empty = {x["id"] for x in t96["rows"] if x.get("surviving") == 0.0}
    touched = {x["id"] for x in t96["rows"] if 0.0 < (x.get("surviving") or 1.0) < 1.0}
    ids = {r["id"] for r in R if r["camp"] == "A57"}
    poly_dead = {r["id"] for r in R if r["camp"] == "A57" and r.get("t5poly_new")}
    print(f"\nT5-polygon: {sum(1 for r in R if r.get('t5poly_dead'))} nodes fire, of which "
          f"{sum(1 for r in R if r.get('t5poly_new'))} are NEW (pinguard says 'ok' today) and "
          f"{sum(1 for r in R if r.get('t5poly_dead') and r.get('pinguard_now') != 'ok')} are "
          f"already killed by the deployed tight-core rule")
    wc = [r for r in R if r.get("t5poly_dead")]
    print(f"  exact rational witness found for {sum(1 for r in wc if r.get('witness_certified'))}"
          f" / {len(wc)} firing nodes")
    print(f"\ntrim96 (2222 boxes): {len(empty)} empties, {len(touched)} trimmed-not-empty")
    print(f"  alive A57 nodes also in trim96's corpus: {len(ids & {x['id'] for x in t96['rows']})}")
    print(f"  alive & trim96-empty (the queued survivors of T5''): {len(ids & empty)}")
    print(f"  T5-polygon kills among the alive: {len(poly_dead)}")
    print(f"    of those also trim96-empty: {len(poly_dead & empty)}")
    print(f"    NEW (not trim96-empty):      {len(poly_dead - empty)}")
    print(f"  trim96-empty but NOT T5-polygon: {len(ids & empty - poly_dead)}")
    if poly_dead:
        print("  ids:", sorted(poly_dead)[:40])
    print("\nlogic-kill accounting, by campaign")
    sup = set()
    sp = os.path.join(ROOT, "A57-shadow-trees", "results", "superseded_by_tight_core.jsonl")
    if os.path.exists(sp):
        sup = {json.loads(l)["id"] for l in open(sp) if l.strip()}
    for camp in ("A57", "A60"):
        S = [r for r in R if r["camp"] == camp]
        t5p = [r for r in S if r.get("t5poly_dead")]
        already = [r for r in S if r.get("pinguard_now") == "contradictory"]
        rec = [r for r in already if r["id"] in sup]
        print(f"  {camp}: {len(S)} alive nodes | deployed T5' (pinguard today) kills "
              f"{len(already)} ({len(rec)} already recorded in superseded_by_tight_core.jsonl, "
              f"{len(already) - len(rec)} NOT recorded) | T5-polygon fires on {len(t5p)}, of which "
              f"{sum(1 for r in t5p if r.get('t5poly_new'))} are new on top of T5'")
    pg = defaultdict(int)
    for r in R:
        pg[r.get("pinguard_now")] += 1
    print("pinguard.classify on the same boxes today:", dict(pg))


if __name__ == "__main__":
    main()
