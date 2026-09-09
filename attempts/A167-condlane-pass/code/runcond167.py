"""A167 T2 -- run the CONDITIONAL chord-limited lane over the population (or one named cell).

    python runcond167.py --nid c0_Y0169 --slot "TL(0,0)" --budget 600 --out ../results/y0169.jsonl
    python runcond167.py --pop ../results/pop.json --shard 0/2 --out ../results/pass_s0.jsonl

Every row is appended as it finishes (resumable: a pair already in `--out` is skipped), and a KILL
also writes `certs/cond_<nid>__<slot>.json` with its SHA-256 recorded in the row.
"""
import argparse
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
sys.path.insert(0, HERE)

import condlane2 as C2                       # noqa: E402
import chordlane as CL                       # noqa: E402  READ-ONLY (A161)
import numpy as np                           # noqa: E402


def load_records():
    recs = {r["nid"]: r for r in CL.CP.load_nodes()}
    boxes, _ = CL.CP.load_open_boxes(set(recs))
    for b in boxes:
        if not b.get("covered_by_node"):
            recs.setdefault(b["nid"], b)
    return recs


def slug(slot):
    return slot.replace("(", "").replace(")", "").replace(",", "_")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nid", default="")
    ap.add_argument("--slot", default="")
    ap.add_argument("--pop", default="")
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--budget", type=float, default=60.0, help="seconds per cell")
    ap.add_argument("--cap_s", type=float, default=4000.0, help="wall-clock cap for this shard")
    ap.add_argument("--noff", type=int, default=6)
    ap.add_argument("--nlines", type=int, default=48)
    ap.add_argument("--splitdepth", type=int, default=5)
    ap.add_argument("--predepth", type=int, default=3)
    ap.add_argument("--offs", type=float, default=2.0, help="hard slice per guard offset")
    ap.add_argument("--longs", type=float, default=12.0, help="phase-2 slice on the closest offset")
    ap.add_argument("--maxpieces", type=int, default=48)
    ap.add_argument("--maxopen", type=int, default=2500)
    ap.add_argument("--bandopen", type=int, default=0)
    ap.add_argument("--sample", type=int, default=8000)
    ap.add_argument("--force_off", default="")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--certs", default=os.path.join(BASE, "certs"))
    ap.add_argument("--out", default=os.path.join(BASE, "results", "pass.jsonl"))
    ap.add_argument("--progress", default="")
    a = ap.parse_args()
    prog = a.progress or (a.out.rsplit(".", 1)[0].replace(os.sep + "results" + os.sep,
                                                          os.sep + "progress" + os.sep) + ".json")
    os.makedirs(os.path.dirname(prog), exist_ok=True)
    os.makedirs(a.certs, exist_ok=True)

    if a.pop:
        pop = json.load(open(a.pop, encoding="utf-8"))["pop"]
    else:
        pop = [dict(nid=a.nid, slot=a.slot)]
    k, n = (int(v) for v in a.shard.split("/"))
    pop = [p for idx, p in enumerate(pop) if idx % n == k]
    done = set()
    if os.path.exists(a.out):
        for ln in open(a.out, encoding="utf-8"):
            try:
                done.add((json.loads(ln)["nid"], json.loads(ln)["slot"]))
            except Exception:                                        # noqa: BLE001
                pass
    recs = load_records()
    print("shard %s: %d cells (%d already done)" % (a.shard, len(pop), len(done)), flush=True)

    fh = open(a.out, "a", encoding="utf-8")
    rng = np.random.default_rng(1670 + k)
    t0 = time.time()
    nrun, tally = 0, {}
    for p in pop:
        if (p["nid"], p["slot"]) in done:
            continue
        if time.time() - t0 > a.cap_s:
            print("wall cap reached, stopping", flush=True)
            break
        rec = recs.get(p["nid"])
        row = dict(p)
        if rec is None:
            row["verdict"] = "NO-RECORD"
        else:
            try:
                r, cert = C2.run(rec, p["slot"], rng=rng, budget_s=a.budget, n_off=a.noff,
                                 n_lines=a.nlines, split_depth=a.splitdepth,
                                 pre_depth=a.predepth, off_s=a.offs, long_s=a.longs,
                                 max_pieces=a.maxpieces, max_open=a.maxopen,
                                 band_open=(a.bandopen or None), sample=a.sample,
                                 force_off=(a.force_off or None))
                row.update(r)
                if cert is not None:
                    q = os.path.join(a.certs, "cond_%s__%s.json" % (p["nid"], slug(p["slot"])))
                    blob = json.dumps(cert, sort_keys=True, indent=1).encode("utf-8")
                    open(q, "wb").write(blob)
                    row["cert"] = os.path.relpath(q, ROOT).replace(os.sep, "/")
                    row["sha256"] = hashlib.sha256(blob).hexdigest()
            except Exception as e:                                   # noqa: BLE001
                row["verdict"] = "ERROR"
                row["error"] = repr(e)[:300]
        fh.write(json.dumps(row) + "\n")
        fh.flush()
        tally[row["verdict"]] = tally.get(row["verdict"], 0) + 1
        nrun += 1
        if row["verdict"] in ("KILL", "ERROR"):
            print("  %-30s %-9s %-5s pieces=%s/%s  %ss  %s"
                  % (p["nid"], p["slot"], row["verdict"], row.get("n_done"),
                     row.get("n_pieces"), row.get("elapsed"), row.get("error", "")), flush=True)
        if nrun % 10 == 0:
            el = time.time() - t0
            json.dump(dict(done=nrun, elapsed=round(el, 1), tally=tally),
                      open(prog, "w", encoding="utf-8"))
            print("  %d/%d  %.0f s  %.1f s/cell  %s" % (nrun, len(pop), el, el / nrun, tally),
                  flush=True)
        if a.limit and nrun >= a.limit:
            break
    fh.close()
    json.dump(dict(done=nrun, elapsed=round(time.time() - t0, 1), tally=tally, finished=True),
              open(prog, "w", encoding="utf-8"))
    print("done %d cells, %.0f s, %s" % (nrun, time.time() - t0, tally), flush=True)


if __name__ == "__main__":
    main()
