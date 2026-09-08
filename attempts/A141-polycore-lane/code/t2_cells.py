"""A141 T2 -- the K' lane test on all four corners of every open k0 cell.

Corpus: A140's `results/t1_polycore.json` -- the twelve converged-alive cells first, then the 166
other open k0 cells A115 lists.  Per cell: the certified K'(B) of every conditioned box (container-
tightened), the four corner verdicts (LANE_K' upper bound, M, verdict), the ordered pair
contradiction test, and a certificate for every kill.  Resumable: one JSON line per cell.

    python t2_cells.py [--out ../results/t2_cells.jsonl] [--shard k/n] [--limit N]
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
sys.path.insert(0, HERE)

import blas1  # noqa: F401,E402
import numpy as np  # noqa: E402

import polylane as P              # noqa: E402
import emit141 as EM              # noqa: E402
from caselp import Box            # noqa: E402

A140 = os.path.join(ROOT, "attempts", "A140-k0-residue-gallery", "results")
A118 = os.path.join(ROOT, "attempts", "A118-lane-count", "results")
CORNERS = ("BL", "BR", "TR", "TL")


def corpus():
    d = json.load(open(os.path.join(A140, "t1_polycore.json"), encoding="utf-8"))
    rows = []
    for r in d["twelve"]:
        rows.append(dict(r, group="twelve"))
    for r in d["pool"]:
        rows.append(dict(r, group="pool"))
    return rows


def a118_stored():
    """A118's per-corner verdicts, indexed by node id and by A140's lane140 cell name."""
    out = {}
    for f in sorted(__import__("glob").glob(os.path.join(A118, "lane_s*.jsonl"))):
        for ln in open(f, encoding="utf-8"):
            ln = ln.strip()
            if not ln:
                continue
            r = json.loads(ln)
            if r.get("cls") != "k0_00":
                continue
            out[r["nid"]] = {c["cell"]: dict(verdict=c["verdict"], lane_ub=c.get("lane_ub"),
                                             ncond_pot=c.get("ncond_pot"))
                             for c in r.get("cells", [])}
    p = os.path.join(A140, "lane140.json")
    if os.path.exists(p):
        for k, v in json.load(open(p, encoding="utf-8")).items():
            if v.get("a118_stored"):
                out.setdefault(k, v["a118_stored"])
            out.setdefault(k + "@fresh", v.get("fresh", {}))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(BASE, "results", "t2_cells.jsonl"))
    ap.add_argument("--progress", default=os.path.join(BASE, "progress", "t2.json"))
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--sample", type=int, default=20000)
    ap.add_argument("--maxopen", type=int, default=2500)
    a = ap.parse_args()

    rows = corpus()
    k, n = (int(v) for v in a.shard.split("/"))
    if n > 1:
        rows = [r for i, r in enumerate(rows) if i % n == k]
    done = set()
    if os.path.exists(a.out):
        for ln in open(a.out, encoding="utf-8"):
            try:
                done.add(json.loads(ln)["cell"])
            except Exception:
                pass
    stored = a118_stored()
    print("corpus %d cells, %d already done" % (len(rows), len(done)), flush=True)

    fh = open(a.out, "a", encoding="utf-8")
    t00 = time.time()
    nrun = 0
    for r in rows:
        nid = r["cell"]
        if nid in done:
            continue
        t0 = time.time()
        raw = [Box(*b["box"]) for b in r["boxes"]]
        rng = np.random.default_rng(1410 + (abs(hash(nid)) % 100000))
        try:
            conds = P.build_cond(raw)
        except Exception as e:                                  # noqa: BLE001
            fh.write(json.dumps(dict(cell=nid, group=r["group"], error=repr(e)[:200])) + "\n")
            fh.flush()
            continue
        rec = dict(cell=nid, group=r["group"], level=r.get("level"), tau=r.get("tau"),
                   budget=r.get("budget"), converged=r.get("converged"),
                   record=r.get("record"), n_boxes=len(raw),
                   boxes_raw=[P.box_json(b) for b in raw],
                   boxes=[P.box_json(c.box) for c in conds],
                   a118=stored.get(nid) or stored.get(nid.replace("_plain_warm", "")) or {},
                   corners={}, pairs=[], certs={})
        for corner in CORNERS:
            res = P.lane_corner(corner, conds, rng=rng, keep_cert=True,
                                max_open=a.maxopen, sample=a.sample)
            rec["corners"][corner] = {kk: vv for kk, vv in res.items()
                                      if kk not in ("cover_cert", "cover_open_cert", "M_cert")}
            if res["verdict"] == "KILL":
                d = EM.cert_dict("polycore_lane", nid, corner, conds, raw, res)
                p = os.path.join(BASE, "certs", f"{nid}_{corner}.json")
                rec["certs"][corner] = dict(path=os.path.relpath(p, ROOT),
                                            sha256=EM.write_cert(p, d))
        for i in range(len(conds)):
            for j in range(len(conds)):
                if i == j:
                    continue
                pr = P.pair_incompatible(conds[i].box, conds[j].box)
                if pr["ok"]:
                    d = EM.pair_cert_dict(nid, i, j, conds[i].box, conds[j].box, pr)
                    p = os.path.join(BASE, "certs", f"{nid}_pair_{i}{j}.json")
                    rec["pairs"].append(dict(i=i, j=j, incompatible=True,
                                             leaves=pr["n_leaves"],
                                             cert=os.path.relpath(p, ROOT),
                                             sha256=EM.write_cert(p, d)))
        rec["kill"] = bool(rec["certs"]) or bool(rec["pairs"])
        rec["secs"] = round(time.time() - t0, 2)
        fh.write(json.dumps(rec) + "\n")
        fh.flush()
        nrun += 1
        kills = ",".join(sorted(rec["certs"])) or "-"
        print(f"{nid:26s} {rec['n_boxes']}b  " +
              "  ".join(f"{c}:{rec['corners'][c]['verdict']}/{rec['corners'][c]['lane_ub']}"
                        f"+{rec['corners'][c]['M']}" for c in CORNERS)
              + f"  kills={kills} pairs={[(p['i'], p['j']) for p in rec['pairs']]}"
              + f"  {rec['secs']}s", flush=True)
        json.dump(dict(done=nrun, elapsed=round(time.time() - t00, 1)),
                  open(a.progress, "w", encoding="utf-8"))
        if a.limit and nrun >= a.limit:
            break
    fh.close()
    json.dump(dict(done=nrun, elapsed=round(time.time() - t00, 1), finished=True),
              open(a.progress, "w", encoding="utf-8"))
    print("done %d cells in %.0f s" % (nrun, time.time() - t00))


if __name__ == "__main__":
    main()
