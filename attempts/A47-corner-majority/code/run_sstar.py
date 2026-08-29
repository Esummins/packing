#!/usr/bin/env python3
"""
A47 leg (a) TASK 2 -- driver: for every rational parameter box (y0, b) produce a measure
certificate (sstar_lp) and verify it exactly (verify_measure_obs).  Checkpointed: a box whose
result file already exists in work/sstar/ is skipped.  Boxes whose LP cannot get below 8 are
subdivided (up to --max-refine levels); a box that still fails is recorded INCONCLUSIVE together
with the reason (never forced).
"""
import argparse
import json
import os
import sys
import time
import traceback
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import sstar_geom as G          # noqa: E402
import sstar_lp                 # noqa: E402
import verify_measure_obs as V  # noqa: E402

WORK = os.path.join(ROOT, "work", "sstar")


def process(box, args, depth_level=0):
    name = G.box_name(box)
    res_path = os.path.join(WORK, name + ".result.json")
    if os.path.exists(res_path) and not args.force:
        with open(res_path) as fh:
            return json.load(fh)
    t0 = time.time()
    rec = {"box": [str(x) for x in box], "box_float": [float(x) for x in box],
           "refine_level": depth_level, "eps": args.eps, "rho": args.rho,
           "scale": args.scale, "delta": str(G.DELTA), "lambda": str(G.LAM), "s_prime": str(G.SP)}
    cert_path = os.path.join(WORK, name + ".cert.json")
    rep_path = os.path.join(WORK, name + ".report.json")
    try:
        P = sstar_lp.Producer(box, na=args.na, eps=float(F(args.eps)), rho=float(F(args.rho)))
        P.add_grid(args.nc0, args.nt0)
        lp_total = P.solve()
        # ---- cutting plane against a fine float scan
        for _ in range(args.rounds):
            viol, worst = P.scan(args.nc1, args.nt1)
            if not viol:
                break
            P.add_placements(viol)
            lp_total = P.solve()
        rec["lp_total"] = lp_total
        rec["lp_rows"] = P.nrows
        # ---- cutting plane against the EXACT verifier (its witnesses are true violations)
        passed = False
        cells_done = set()
        for k in range(args.vrounds):
            atoms, weights, total, _ = P.finalize(scale=F(args.scale), wden=args.wden)
            rec["total"] = str(total)
            rec["total_float"] = float(total)
            rec["n_atoms"] = len(atoms)
            if total >= 8:
                rec["result"] = "LP_OVER"
                rec["time_s"] = time.time() - t0
                with open(res_path, "w") as fh:
                    json.dump(rec, fh, indent=1)
                return rec
            sstar_lp.write_cert(cert_path, box, P.ob, atoms, weights, total,
                                {"lp_total": lp_total, "eps": args.eps, "rho": args.rho,
                                 "scale": args.scale, "na": args.na, "vround": k})
            passed, stats, wits, _, _ = V.run_verify(
                cert_path, depth=args.depth, split=args.split, jobs=args.jobs,
                max_witnesses=args.maxwit, per_box_cap=args.percap)
            rec["verify_boxes"] = stats.get("boxes")
            rec["verify_exempt"] = stats.get("exempt")
            rec["verify_rounds"] = k + 1
            if passed:
                break
            # feed the FAILING BOXES back as ROBUST rows on a fixed lattice: every witness patches
            # its whole 3x3x3 lattice neighbourhood, so the search cannot ping-pong between
            # adjacent unresolved boxes.  Cells already added are never re-added.
            # The lattice is ALIGNED WITH THE VERIFIER'S OWN BOX TREE: centres are bisected inside
            # [1/2, s'-1/2] and t inside [0,1], so cells [A + i*gc, A + (i+1)*gc] with
            # gc = (s'-1)/2^7 and gt = 2^-6 are unions of verifier boxes -- a failing box can never
            # straddle two cells, which is what stalled the plain-inflation feedback.
            A, sp = 0.5, float(G.SP)
            gc, gt = (sp - 1.0) / 128.0, 1.0 / 64.0
            new_cells = set()
            for w in wits:
                bb = w["box"]
                t0f, x0f, y0f = (float(F(bb["t"][0])), float(F(bb["cx"][0])), float(F(bb["cy"][0])))
                i0 = int((x0f - A) / gc + 1e-12)
                j0 = int((y0f - A) / gc + 1e-12)
                k0 = int(t0f / gt + 1e-12)
                for di in (-1, 0, 1):
                    for dj in (-1, 0, 1):
                        for dk in (-1, 0, 1):
                            cell = (i0 + di, j0 + dj, k0 + dk)
                            if cell not in cells_done:
                                new_cells.add(cell)
            cells_done |= new_cells
            bxs = [(max(0.0, k * gt), min(1.0, (k + 1) * gt),
                    max(0.0, A + i * gc), min(sp, A + (i + 1) * gc),
                    max(0.0, A + j * gc), min(sp, A + (j + 1) * gc)) for (i, j, k) in new_cells]
            bxs = [b for b in bxs if b[0] < b[1] and b[2] < b[3] and b[4] < b[5]]
            pl = [(float(F(w["placement"]["t"])), float(F(w["placement"]["cx"])),
                   float(F(w["placement"]["cy"])))
                  for w in wits if w.get("placement")]
            if not bxs:
                rec["note"] = "verifier reported no witness boxes"
                break
            n_added = P.add_box_rows(bxs) + P.add_placements(pl)
            lp_total = P.solve()
            rec["lp_total"] = lp_total
            rec["fed_back"] = rec.get("fed_back", 0) + n_added
            for _ in range(args.postscan):
                viol, worst = P.scan(args.nc1, args.nt1)
                if not viol:
                    break
                P.add_placements(viol)
                lp_total = P.solve()
            rec["lp_total"] = lp_total
        rec["result"] = "PASS" if passed else "VERIFY_FAIL"
        if not passed:
            rec["witness"] = [w.get("placement") for w in wits[:3]]
    except Exception as e:
        rec["result"] = "ERROR"
        rec["error"] = f"{e}"
        rec["traceback"] = traceback.format_exc()[-1500:]
    rec["time_s"] = time.time() - t0
    with open(res_path, "w") as fh:
        json.dump(rec, fh, indent=1)
    return rec


def split_box(box):
    y0, y1, b0, b1 = box
    ym, bm = (y0 + y1) / 2, (b0 + b1) / 2
    return [(y0, ym, b0, bm), (y0, ym, bm, b1), (ym, y1, b0, bm), (ym, y1, bm, b1)]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--y0-step", default="1/8")
    ap.add_argument("--b-step", default="1/4")
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--eps", default="1/128")
    ap.add_argument("--rho", default="1/256")
    ap.add_argument("--scale", default="102/100")
    ap.add_argument("--wden", type=int, default=10000)
    ap.add_argument("--na", type=int, default=61)
    ap.add_argument("--nc0", type=int, default=45)
    ap.add_argument("--nt0", type=int, default=9)
    ap.add_argument("--nc1", type=int, default=97)
    ap.add_argument("--nt1", type=int, default=29)
    ap.add_argument("--rounds", type=int, default=12)
    ap.add_argument("--postscan", type=int, default=1)
    ap.add_argument("--vrounds", type=int, default=18)
    ap.add_argument("--maxwit", type=int, default=200)
    ap.add_argument("--percap", type=int, default=12)
    ap.add_argument("--inflate", type=float, default=4.0)
    ap.add_argument("--min-c", type=float, default=0.025)
    ap.add_argument("--min-t", type=float, default=0.015)
    ap.add_argument("--depth", type=int, default=36)
    ap.add_argument("--split", type=int, default=2)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--max-refine", type=int, default=2)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)

    os.makedirs(WORK, exist_ok=True)
    boxes = G.param_boxes(F(a.y0_step), F(a.b_step))
    boxes = [b for i, b in enumerate(boxes) if i % a.nshards == a.shard]
    print(f"shard {a.shard}/{a.nshards}: {len(boxes)} top-level parameter boxes", flush=True)
    queue = [(b, 0) for b in boxes]
    done = []
    while queue:
        box, lvl = queue.pop(0)
        rec = process(box, a, lvl)
        tag = rec.get("result")
        print(f"[{tag:12s}] lvl{lvl} {G.box_name(box):36s} total={rec.get('total_float')} "
              f"lp={rec.get('lp_total')} vboxes={rec.get('verify_boxes')} "
              f"{rec.get('time_s', 0):.1f}s", flush=True)
        if tag == "PASS":
            done.append(rec)
        elif lvl < a.max_refine:
            print(f"    refining {G.box_name(box)}", flush=True)
            queue = [(sb, lvl + 1) for sb in split_box(box)] + queue
        else:
            rec["result"] = "INCONCLUSIVE"
            done.append(rec)
    out = os.path.join(WORK, f"shard{a.shard}_of{a.nshards}.json")
    with open(out, "w") as fh:
        json.dump(done, fh, indent=1)
    nbad = sum(1 for r in done if r["result"] != "PASS")
    print(f"shard done: {len(done)} leaves, {nbad} not PASS -> {out}", flush=True)
    return 0 if nbad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
