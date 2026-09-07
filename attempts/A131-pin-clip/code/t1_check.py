"""A131 T1 -- confirmation of the pin-clip: sampling + two positive controls.

Reports, per node, drawn -> tested -> hits (lemmas.md "SAMPLED CHECKS" rule).

  * DISCARDED region (original box minus the clipped box, at tilts in the sub-bin): every draw
    must COLLIDE (with some pin core) or leave the container.  A "hit" is a draw that is
    pin-free AND inside the container -- i.e. a counterexample to the clip.  Must be 0.
  * KEPT region (the clipped box x sub-bin): the feasible fraction, reported for information.
    It is NOT required to be 1 (the clip removes only axis-aligned dead slabs; conservatism (c)).

Positive control A: every box the tree killed by "core meets pin core" (T5/T5') must clip to
EMPTY at nsub = 1 -- K_B lies inside every admissible square, so if K_B meets a pin core, every
centre of the box is dead at every tilt.

Positive control B: the LP support columns stored on each solved node
(results/tree/<key>/<id>.json, res["packing"]) are placements the LP believes can appear in a
packing satisfying the node hypothesis; every one of them must be pin-free at its own tilt, and
any whose pose lies inside the node's own conditioned box must lie inside the CLIPPED box.

    python code/t1_check.py [--draws 20000] [--nodes k5_11_interior_Y0036,...]
"""
import argparse, glob, json, math, os, random, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
A57 = os.path.join(ATT, "A57-shadow-trees")
A53 = os.path.join(ATT, "A53-simple-strata")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(A57, "code"))

import pinclip
from caselp import Box

SLOTS = json.load(open(os.path.join(A53, "results", "name_to_slots.json")))


def corpus():
    """A96's 2,222-box corpus: trim96.rows(), re-implemented here so A96 stays read-only."""
    out, seen = [], set()
    for pat in ("tree_k5_1*_interior_G1_s*.jsonl", "tree_k5_1*_interior_G1_D2*.jsonl"):
        for f in sorted(glob.glob(os.path.join(A57, "results", pat))):
            if "_s0.jsonl" in f and "_D2" in f:
                continue
            for ln in open(f):
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    r = json.loads(ln)
                except Exception:
                    continue
                if not r.get("box") or r["id"] in seen:
                    continue
                seen.add(r["id"])
                r["_name"] = "k5_11" if r["id"].startswith("k5_11") else "k5_16"
                r["_level"] = 1 + r["id"].count("_D")
                r["_src"] = os.path.basename(f)
                out.append(r)
    return out


def in_rect(rect, x, y):
    return rect is not None and float(rect[0]) <= x <= float(rect[1]) and \
        float(rect[2]) <= y <= float(rect[3])


def sample_node(box, slots, cl, draws, rng):
    """-> dict(discard_drawn, discard_tested, discard_hits, keep_drawn, keep_tested, keep_feasible)"""
    bins = cl["bins"]
    th0, th1 = box.th0, box.th1
    d_drawn = d_tested = d_hits = 0
    k_drawn = k_tested = k_feas = 0
    tmin, tmax = float(bins[0][0]), float(bins[-1][1])
    for _ in range(draws):
        t = tmin + (tmax - tmin) * rng.random()
        th = math.degrees(2.0 * math.atan(t))
        if th < th0 or th > th1:
            continue
        j = min(len(bins) - 1, max(0, int(len(bins) * (t - tmin) / (tmax - tmin)) if tmax > tmin else 0))
        while j > 0 and t < float(bins[j][0]):
            j -= 1
        while j < len(bins) - 1 and t > float(bins[j][1]):
            j += 1
        rect = bins[j][2]
        x = box.x0 + (box.x1 - box.x0) * rng.random()
        y = box.y0 + (box.y1 - box.y0) * rng.random()
        d_drawn += 1
        if in_rect(rect, x, y):
            continue
        d_tested += 1
        if pinclip.pin_free(x, y, th, slots):
            d_hits += 1
    for _ in range(draws):
        t = tmin + (tmax - tmin) * rng.random()
        th = math.degrees(2.0 * math.atan(t))
        if th < th0 or th > th1:
            continue
        j = min(len(bins) - 1, max(0, int(len(bins) * (t - tmin) / (tmax - tmin)) if tmax > tmin else 0))
        while j > 0 and t < float(bins[j][0]):
            j -= 1
        while j < len(bins) - 1 and t > float(bins[j][1]):
            j += 1
        rect = bins[j][2]
        k_drawn += 1
        if rect is None:
            continue
        x = float(rect[0]) + (float(rect[1]) - float(rect[0])) * rng.random()
        y = float(rect[2]) + (float(rect[3]) - float(rect[2])) * rng.random()
        if not (box.x0 <= x <= box.x1 and box.y0 <= y <= box.y1):
            continue
        k_tested += 1
        if pinclip.pin_free(x, y, th, slots):
            k_feas += 1
    return dict(discard_drawn=d_drawn, discard_tested=d_tested, discard_hits=d_hits,
                keep_drawn=k_drawn, keep_tested=k_tested, keep_feasible=k_feas)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=40000)
    ap.add_argument("--nsub", type=int, default=8)
    ap.add_argument("--sample-nodes", type=int, default=12)
    ap.add_argument("--out", default=os.path.join(BASE, "results", "t1_check.json"))
    a = ap.parse_args()
    rng = random.Random(20260907)
    R = corpus()
    print(f"corpus {len(R)} boxes", flush=True)

    # ---------------- positive control A: every logic kill clips to EMPTY at nsub = 1
    t0 = time.time()
    ctrlA = dict(n=0, empty=0, violations=[])
    for r in R:
        if not str(r.get("cert") or "").startswith("KILL-BY-LOGIC"):
            continue
        ctrlA["n"] += 1
        b = Box.from_json(r["box"])
        cl = pinclip.clip_node(b, SLOTS[r["_name"]], nsub=1)
        if cl["empty"]:
            ctrlA["empty"] += 1
        else:
            ctrlA["violations"].append(dict(id=r["id"], kept=round(cl["kept_union"], 6),
                                            refused=cl["refused"], reason=cl["reason"]))
    ctrlA["clean"] = (ctrlA["empty"] == ctrlA["n"])
    print(f"control A: {ctrlA['empty']}/{ctrlA['n']} logic kills clip to EMPTY at nsub=1 "
          f"({time.time()-t0:.0f}s)", flush=True)

    # ---------------- positive control B: stored LP support columns
    ctrlB = dict(nodes=0, columns=0, n_not_pin_free=0, max_depth=0.0, n_over_eps_core=0,
                 not_pin_free=[], in_box=0, in_box_outside_clip=[], eps_core=2e-3)
    for r in R:
        key = None
        for k in ("_D2_D2_D2", "_D2_D2", "_D2"):
            if r["_src"].endswith(f"G1{k}.jsonl") or r["_src"].endswith(f"G1{k}_s0.jsonl"):
                key = f"{r['_name']}_interior_G1{k}"
                break
        if key is None:
            key = f"{r['_name']}_interior_G1"
        p = os.path.join(A57, "results", "tree", key, r["id"] + ".json")
        if not os.path.exists(p):
            continue
        try:
            res = json.load(open(p))
        except Exception:
            continue
        pk = res.get("packing") or []
        if not pk:
            continue
        ctrlB["nodes"] += 1
        b = Box.from_json(r["box"])
        cl = None
        for col in pk:
            cx, cy, th = col["cx"], col["cy"], col["theta"]
            ctrlB["columns"] += 1
            thn = math.degrees(th) % 90.0        # lpbox stores row tilts in RADIANS
            if not pinclip.pin_free(cx, cy, thn, SLOTS[r["_name"]]):
                ctrlB["n_not_pin_free"] += 1
                dep = pinclip.pin_depth(cx, cy, thn, SLOTS[r["_name"]])
                ctrlB["max_depth"] = max(ctrlB["max_depth"], dep)
                if dep > ctrlB["eps_core"]:
                    ctrlB["n_over_eps_core"] += 1
                if len(ctrlB["not_pin_free"]) < 25:
                    ctrlB["not_pin_free"].append(dict(id=r["id"], col=[cx, cy, th],
                                                      depth=round(dep, 8)))
            if b.contains(cx, cy, thn):
                ctrlB["in_box"] += 1
                if cl is None:
                    cl = pinclip.clip_node(b, SLOTS[r["_name"]], nsub=a.nsub)
                ok = any(float(t0_) <= math.tan(math.radians(thn) / 2) <= float(t1_)
                         and in_rect(rc, cx, cy) for (t0_, t1_, rc) in cl["bins"])
                if not ok and len(ctrlB["in_box_outside_clip"]) < 25:
                    ctrlB["in_box_outside_clip"].append(dict(id=r["id"], col=[cx, cy, th]))
    ctrlB["clean"] = (ctrlB["n_over_eps_core"] == 0) and (not ctrlB["in_box_outside_clip"])
    print(f"control B: {ctrlB['nodes']} solved nodes, {ctrlB['columns']} support columns, "
          f"{ctrlB['n_not_pin_free']} penetrate a pin core (max depth {ctrlB['max_depth']:.3e}, "
          f"{ctrlB['n_over_eps_core']} beyond EPS_CORE=2e-3), {ctrlB['in_box']} inside the node's "
          f"own box, {len(ctrlB['in_box_outside_clip'])} of those outside the clip", flush=True)

    # ---------------- sampled confirmation
    open_rows = [r for r in R if not str(r.get("cert") or "").startswith("KILL-BY-LOGIC")]
    picked = [r for r in open_rows if r["id"] in
              ("k5_11_interior_Y0036", "k5_11_interior_Y0036_D02", "k5_11_interior_Y0036_D03",
               "k5_11_interior_Y0036_D06", "k5_11_interior_Y0036_D07")]
    rest = [r for r in open_rows if r not in picked]
    rng.shuffle(rest)
    picked += rest[:max(0, a.sample_nodes - len(picked))]
    samples = []
    tot = dict(discard_drawn=0, discard_tested=0, discard_hits=0,
               keep_drawn=0, keep_tested=0, keep_feasible=0)
    for r in picked:
        b = Box.from_json(r["box"])
        cl = pinclip.clip_node(b, SLOTS[r["_name"]], nsub=a.nsub)
        sm = sample_node(b, SLOTS[r["_name"]], cl, a.draws, rng)
        for k in tot:
            tot[k] += sm[k]
        samples.append(dict(id=r["id"], level=r["_level"], kept_vol=round(cl["kept_vol"], 6),
                            n_empty=cl["n_empty"], nsub=a.nsub, **sm))
        print(f"  {r['id']:36s} kept={cl['kept_vol']:.4f}  discarded {sm['discard_drawn']} -> "
              f"{sm['discard_tested']} -> {sm['discard_hits']} hits | kept {sm['keep_drawn']} -> "
              f"{sm['keep_tested']} -> {sm['keep_feasible']} feasible", flush=True)

    out = dict(generated="A131 T1", nsub=a.nsub, draws=a.draws,
               control_A=ctrlA, control_B=ctrlB, samples=samples, sample_totals=tot)
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps(dict(control_A={k: v for k, v in ctrlA.items() if k != "violations"},
                          control_B={k: v for k, v in ctrlB.items()
                                     if k not in ("not_pin_free", "in_box_outside_clip")},
                          sample_totals=tot), indent=1))


if __name__ == "__main__":
    main()
