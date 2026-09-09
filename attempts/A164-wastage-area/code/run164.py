"""A164 -- run the uncoverable-area leaf over a population of nodes.

  python run164.py --pop k0v4                     the eleven converged-alive k0 cells
  python run164.py --pop a57v4                    the A57/A60 v4 gallery pages
  python run164.py --pop k0v4 --only l1_104 --fig the PI's cell, with the figure

Writes results/u164_<pop>.jsonl (one row per node) and logs/<pop>.log.  READ-ONLY on every
campaign; the only files written live under this attempt.
"""
import argparse
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
for _p in (os.path.join(ATT, "A148-gallery-v4", "code"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np                                                    # noqa: E402
import data148 as D                                                   # noqa: E402
import geo164 as G                                                    # noqa: E402
from caselp import Box                                                # noqa: E402


def boxes_of(node):
    return [Box.from_json(b) if isinstance(b, dict) else b for b in node["boxes"]]


def one(node, lam, pitch, ntilt, nsample, want_extra=True):
    t0 = time.time()
    bx = boxes_of(node)
    obs, names, kinds, _ = G.obstacles_of(node["boxes"])
    npin = sum(1 for k in kinds if k["kind"] == "pin")
    Um, xs, ys, res = G.uncoverable(G.S0, obs, bx, lam=lam, pitch=pitch, ntilt=ntilt,
                                    want_extra=want_extra, n_pins=npin)
    res["id"] = node["id"]
    res["camp"] = node["camp"]
    res["cls"] = node.get("cls")
    res["level"] = node.get("level")
    res["budget"] = node["budget"]
    res["n_boxes"] = len(bx)
    res["n_pins"] = npin
    res["obstacle_names"] = names
    res["record"] = node.get("record")
    res["ratio_B0"] = res["area_U"] / G.B0
    res["kill"] = bool(res["area_U"] > G.B0)
    res["sample"] = G.sample_confirm(G.S0, obs, bx, Um, xs, ys, lam=lam, n=nsample)
    # the UNCONDITIONAL leaf is |U| alone (U is a set, so its area needs no region bookkeeping);
    # Lemma ID's separated-corner row can only add where a corner is unreachable, which is the
    # same event as that corner box lying inside U, so the two never compete.
    res["combined_lb"] = max(res["area_U"], res.get("sep_corner_waste", 0.0))
    res["combined_ratio_B0"] = res["combined_lb"] / G.B0
    res["combined_kill"] = bool(res["combined_lb"] > G.B0)
    res["crowd_kill"] = bool(res.get("crowd", {}).get("kill"))
    res["seconds"] = time.time() - t0
    return res, Um, xs, ys, obs, names, kinds, bx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pop", default="k0v4")
    ap.add_argument("--only", default=None)
    ap.add_argument("--skip", default=None, help="comma list of ids already done")
    ap.add_argument("--lam", type=float, default=1.0)
    ap.add_argument("--window", action="store_true",
                    help="the window-sound variant: cover square at lam_max = s0/3.81794 while "
                         "admissibility stays at side 1")
    ap.add_argument("--pitch", type=float, default=G.PITCH)
    ap.add_argument("--ntilt", type=int, default=G.NTILT)
    ap.add_argument("--nsample", type=int, default=100000)
    ap.add_argument("--fig", action="store_true")
    ap.add_argument("--savemask", action="store_true")
    ap.add_argument("--tag", default="")
    ap.add_argument("--slice", default=None, help="i/k -- take every k-th node starting at i")
    a = ap.parse_args()
    if a.window:
        a.lam = G.LAM_MAX

    pop = D.population(a.pop)
    if a.only:
        keep = set(a.only.split(","))
        pop = [n for n in pop if n["id"] in keep]
    if a.slice:
        i, k = (int(v) for v in a.slice.split("/"))
        pop = pop[i::k]
    if a.skip:
        sk = set(a.skip.split(","))
        pop = [n for n in pop if n["id"] not in sk]

    tag = a.tag or a.pop
    out = os.path.join(BASE, "results", f"u164_{tag}.jsonl")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "a", encoding="utf-8") as fh:
        for i, node in enumerate(pop):
            res, Um, xs, ys, obs, names, kinds, bx = one(
                node, a.lam, a.pitch, a.ntilt, a.nsample)
            fh.write(json.dumps(res) + "\n")
            fh.flush()
            print(f"[{i + 1:3d}/{len(pop)}] {res['id']:32s} |U| {res['area_U']:8.4f} "
                  f"({res['ratio_B0'] * 100:6.2f}% of B0)  comb {res['combined_lb']:8.4f} "
                  f"({res['combined_ratio_B0'] * 100:6.2f}%)  budget {res['budget']}  "
                  f"hits {res['sample']['free']['hits']}  crowdB "
                  + (f"{res['crowd']['area_B']:.3f}" if res.get("crowd", {}).get("applicable")
                     else "n/a") + f"  {res['seconds']:.1f}s"
                  + ("   *** KILL ***" if res["combined_kill"] else "")
                  + ("   *** CROWD-KILL ***" if res["crowd_kill"] else ""), flush=True)
            if a.savemask or a.fig:
                np.savez_compressed(
                    os.path.join(BASE, "results", f"mask_{res['id']}.npz"),
                    U=Um, xs=xs, ys=ys,
                    spec=np.array([json.dumps(dict(
                        id=res["id"], pop=a.pop, s=res["s"], pitch=res["pitch"],
                        ntilt=res["ntilt"], lam=res["lam"], area_U=res["area_U"],
                        boxes=node["boxes"], m1=res["free"]["m1"],
                        half_width=res["free"]["half_width"]))]))
            if a.fig:
                import fig164
                fig164.page(node, res, Um, xs, ys, obs, names, kinds, bx,
                            os.path.join(BASE, "figs", f"{res['id']}_U.svg"))
                json.dump(res, open(os.path.join(BASE, "results", f"u164_{res['id']}.json"),
                                    "w", encoding="utf-8"), indent=1)
    print("wrote", out)


if __name__ == "__main__":
    main()
