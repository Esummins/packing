"""A57: which ZONE is worth branching on?

For each A24 zone Z of a stratum, solve
  * the NO child   (budget 11-k)   -- cheap, the zone's admissibility price
  * a sample of YES children (budget 11-k-1) at the t-uniform cover resolution
    (easiest / median / hardest by distance to Trump's ghost)
and record eta = tau - budget for each.  A zone is a viable branch only if BOTH sides can go
negative; the interior zone measured in T3/T4 has NO at eta = -3.0 but YES at eta > 0.
tau is not an arbiter (A54 S0): anything with tau < budget is handed to certify.py.
"""
import argparse, json, math, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
A53 = os.path.abspath(os.path.join(BASE, "..", "A53-simple-strata"))
sys.path.insert(0, HERE)
from caselp import Box, NoFam, Hyp, solve_node
from run_skel import S0F
from substrat import zones, trump_realizes
from tree57 import cover, ghost_placements, ghost_dist
from pinguard import classify
from warm57 import merged_warm

S_RAT = "969271/250000"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--zones", default="corner_TR,corner_TL,corner_BR,corner_BL,side_R,side_T,side_L,side_B")
    ap.add_argument("--w", type=float, default=0.15)
    ap.add_argument("--nth", type=int, default=8)
    ap.add_argument("--cw", type=float, default=0.6)
    ap.add_argument("--samples", type=int, default=3)
    ap.add_argument("--tl", type=float, default=300)
    ap.add_argument("--cert_time", type=float, default=240)
    ap.add_argument("--tag", default="zs")
    a = ap.parse_args()

    slots = [tuple(p) for p in json.load(open(os.path.join(A53, "results", "name_to_slots.json")))[a.name]]
    pins = [Box(x, x, y, y, 0.0, 0.0) for (x, y) in slots]
    budget = 11 - len(slots)
    W, _ = merged_warm(a.name)
    warm = dict(atoms=W["atoms"], rows=[])
    G = ghost_placements()
    outdir = os.path.join(BASE, "results", "zonescan", a.name)
    certdir = os.path.join(BASE, "certs", "zonescan", a.name)
    os.makedirs(outdir, exist_ok=True); os.makedirs(certdir, exist_ok=True)
    recs = []
    summ = os.path.join(BASE, "results", f"zonescan_{a.name}_{a.tag}.jsonl")
    done = set()
    if os.path.exists(summ):
        for line in open(summ):
            try:
                recs.append(json.loads(line)); done.add(recs[-1]["id"])
            except Exception:
                pass

    def run_child(nid, hyp, bud, meta):
        if nid in done:
            return
        npth = os.path.join(outdir, nid + ".json")
        t0 = time.time()
        if os.path.exists(npth):
            res = json.load(open(npth))
        else:
            res = solve_node(S0F, hyp, bud, sym_kind="C1", warm=warm, time_limit=a.tl,
                             max_iter=900, out=None, log=lambda *x: print(*x, flush=True),
                             prune=0, prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002,
                             max_cols_add=400, max_rows_add=2000, fine_slack=0.05, alternate=True)
            json.dump(res, open(npth, "w"))
        r = dict(id=nid, budget=bud, tau=res["tau"], eta=res["tau"] - bud, conv=res["converged"],
                 minmass=res["minmass"], lp_s=round(time.time() - t0, 1), **meta)
        r["trump_realizes"] = trump_realizes(hyp, slots)
        if r["trump_realizes"]:
            r["cert"] = "CANARY (never certified)"
        elif res["tau"] < bud:
            cert = os.path.join(certdir, nid + ".json")
            cmd = [sys.executable, os.path.join(HERE, "certify.py"), npth, "--s_rat", S_RAT,
                   "--rounds", "2", "--jobs", "2", "--depth", "56", "--time_limit", str(a.cert_time),
                   "--out", cert, "--scale", "0", "--scale_cap", "1.40", "--max_w", "64", "--loop_cols"]
            t1 = time.time()
            p = subprocess.run(cmd, capture_output=True, text=True)
            r["cert"] = "PASS" if p.returncode == 0 else f"FAIL(rc={p.returncode})"
            r["cert_s"] = round(time.time() - t1, 1)
            if p.returncode == 0:
                open(cert + ".PASS", "w").write("ok")
            else:
                r["tail"] = [l for l in p.stdout.splitlines() if l.startswith(("  worst", "[round"))][-3:]
        else:
            r["cert"] = "ALIVE-at-LP"
        recs.append(r); done.add(nid)
        print(json.dumps(r), flush=True)
        with open(summ, "a") as f:
            f.write(json.dumps(r) + "\n")

    Z = zones(S0F, a.cw)
    for zn in a.zones.split(","):
        rect = Z[zn]
        run_child(f"{a.name}_{zn}_NO", Hyp(pins, [NoFam(*rect, [(0.0, 90.0)])]), budget,
                  dict(zone=zn, kind="NO", rect=list(rect)))
        boxes, bad, grid = cover(rect, S0F, a.w, a.nth, 0.34)
        if bad:
            print(f"# {zn}: {len(bad)} uncoverable boxes", flush=True)
        if not boxes:
            print(f"# {zn}: cover empty (all vacuous)", flush=True); continue
        srt = sorted(boxes, key=lambda b: -ghost_dist(b, G))
        n = len(srt)
        pick = sorted({0, n // 2, n - 1} | {n // 4, 3 * n // 4})[:max(1, a.samples + 2)]
        print(f"# {zn}: cover {n} boxes, a={float(srt[0].core().a):.4f}, sampling {pick}", flush=True)
        cl = [classify(b, pins, slots)[0] for b in srt]
        print(f"#   pinguard: " + json.dumps({k: cl.count(k) for k in set(cl)}), flush=True)
        okidx = [i for i, st in enumerate(cl) if st == "ok"]
        if not okidx:
            print(f"# {zn}: every box is contradictory or realises a pin -- no sound YES child",
                  flush=True); continue
        nn = len(okidx)
        pick = sorted({okidx[0], okidx[nn // 4], okidx[nn // 2], okidx[3 * nn // 4], okidx[-1]})
        for i in pick:
            b = srt[i]
            run_child(f"{a.name}_{zn}_Y{i:04d}", Hyp(pins + [b], []), budget - 1,
                      dict(zone=zn, kind="YES", box=b.to_json(), a=float(b.core().a),
                           ghost_dist=round(ghost_dist(b, G), 4), cover_n=n, rank=i,
                           pin="ok", n_ok=nn))
    json.dump(recs, open(os.path.join(BASE, "results", f"zonescan_{a.name}_{a.tag}.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
