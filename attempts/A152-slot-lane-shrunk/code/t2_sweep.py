"""A152 T2 -- the population sweep of the shrunk / translated slot-lane leaf.

For every alive A57 (k5_11 / k5_16, node + open box) and A60 (trump5) record and every usable
slot, screen the cell variants (SHRUNK, and every ADMISSIBLE TRANSLATE) and, on the promising
ones, run the full A141 cover to get a certified `LANE_K'` bound and the exact `M`.

Pin regime: the node's OWN family -- A57 / A57box carry the G1 `delta = 1e-2` slack pin boxes, so
their pin obstacles are the K' cores of the m-hulled slot boxes FATTENED by h = delta/sqrt(2);
A60's pins are exact (degenerate boxes), so nothing changes there.  A `exact_cell/exact_pins`
baseline row is also screened, purely as a cross-check against A141's own numbers.

Only variants with `lane_lb == 0` (no free pose meeting the cell was realised) can produce the
`LANE_K' = 0, M <= 1` kill that is the only form this leaf has ever taken, so those get the cover
first; the rest are recorded with their sampled bounds.

    python t2_sweep.py --shard 0/2 --wall 4200

Resumable: `progress/t2_<shard>.json` holds the set of finished record keys.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import lane152 as L152                                   # noqa: E402
import numpy as np                                       # noqa: E402
import emit141 as EM                                     # noqa: E402  READ-ONLY (A141)
import polylane as P                                     # noqa: E402  READ-ONLY (A141)


def variants_for(rec, slot, pin_h, hs):
    conds, meet, (i, j), pin_b = L152.build(rec, slot, pin_h)
    ts = L152.admissible_translates(pin_b, i, j, hs, pin_h)
    vs = [("shrunk", L152.cell_shrunk(i, j, hs), None)]
    for t in ts:
        vs.append(("trans", L152.cell_trans(i, j, t), list(t)))
    return conds, meet, (i, j), ts, vs


def m_lb(sm, meet):
    return sum(1 for e in sm["cond_lb"] if e["can_meet"] and e["j"] in set(meet))


def reckey(rec):
    """A57's tree shards repeat node ids across sides (G1 / L1 / ...), so the identity of a
    record is (src, shard, nid) -- A141 T2's `key` field."""
    return "%s/%s/%s" % (rec["src"], rec.get("shard", "-"), rec["nid"])


def do_cell(rec, slot, hs, rng, sample, maxopen, cover_budget):
    pin_h = L152.node_pin_h(rec)
    out = dict(key=reckey(rec), nid=rec["nid"], shard=rec.get("shard"),
               src=rec["src"], cls=rec["cls"], level=rec["level"], slot=slot,
               pin_h=pin_h, snap_h=hs, rows=[])
    # --- baseline: A141's cell + A141's exact-slot pin cores (cross-check only)
    c0, m0, (i, j), _ = L152.build(rec, slot, 0.0)
    sm0 = L152.screen(L152.cell_exact(i, j), c0, rng, sample)
    out["baseline_exact"] = dict(lane_lb=sm0["lane_lb"], M_lb=m_lb(sm0, m0),
                                 free=sm0.get("free"), meeting=sm0.get("meeting"))
    conds, meet, (i, j), ts, vs = variants_for(rec, slot, pin_h, hs)
    out["n_translates"] = len(ts)
    out["translates"] = [list(t) for t in ts]
    best = None
    for (kind, cell, t) in vs:
        sm = L152.screen(cell, conds, rng, sample)
        M = m_lb(sm, meet)
        row = dict(kind=kind, t=t, cell=[round(v, 9) for v in cell], lane_lb=sm["lane_lb"],
                   M_lb=M, free=sm.get("free"), meeting=sm.get("meeting"),
                   max_pair_gap=sm.get("max_pair_gap"), verdict=None)
        if sm["lane_lb"] == 0 and M <= 1 and cover_budget[0] > 0:
            t0 = time.time()
            res = L152.full(cell, conds, meet, rng, sample, maxopen, keep_cert=True,
                            max_depth=30)
            dt = time.time() - t0
            cover_budget[0] -= dt
            row.update(lane_ub=res["lane_ub"], M=res["M"], verdict=res["verdict"],
                       cover_leaves=res.get("cover_leaves"), cover_open=res.get("cover_open"),
                       cover_s=round(dt, 1))
            if res["verdict"] == "KILL":
                row["sample_line"] = L152.sample_line(conds, cell, rng, 10 * sample)
                row["_res"] = res
                row["_conds"] = conds
                if kind == "trans" and (best is None):
                    best = row
        else:
            row["verdict"] = ("LANE>=2" if sm["lane_lb"] >= 2 else
                              "NEAR-MISS-OR-WORSE" if sm["lane_lb"] + M >= 2 else "SCREEN-ONLY")
        out["rows"].append(row)
    return out, best, (i, j)


def emit(rec, slot, row, ij, hs, outdir):
    res, conds = row.pop("_res"), row.pop("_conds")
    ext = L152.CP.CLASSES[rec["cls"]]["usable"][slot]
    d = EM.cert_dict("polycore_slot_lane_shrunk", rec["nid"], slot, conds,
                     [c.box for c in conds], res,
                     extra=dict(
                         format="polycore_slot_lane_shrunk_v1",
                         key=reckey(rec), node_shard=rec.get("shard"),
                         node_path=rec.get("path"), node_side=rec.get("side"),
                         cell_kind="usable_slot_translated",
                         cls=rec["cls"], src=rec["src"], level=rec["level"],
                         slot_ij=[ij[0], ij[1]],
                         snap_delta=L152.DELTA_G1, snap_h=hs,
                         translate=row["t"], pin_h=row.get("pin_h", L152.node_pin_h(rec)),
                         extension=ext,
                         extension_window="[191/50, 969271/250000] FULL (A56/A61/A114 "
                                          "scoreboard) -- EXACT PINS ONLY",
                         prerequisite="SLACK-FORM extension kill for %s (sixth pin within "
                                      "h = %.7f of the slot); NOT AVAILABLE as of 2026-09-08 "
                                      "-- every A56/A61/A114 window certificate carries "
                                      "a = 16383999967232/32768001953125 (pin tolerance "
                                      "3.08e-8) and tm = 1/33554432" % (ext, hs),
                         conditional=True,
                         n_pins=len(conds) - len([e for e in (res.get("M_detail") or [])]),
                         sample_line=row.get("sample_line")))
    p = os.path.join(outdir, "slotshr_%s__%s__%s.json"
                     % (str(rec.get("shard") or "-").replace("/", "_"), rec["nid"],
                        slot.replace("(", "").replace(")", "").replace(",", "_")))
    return os.path.relpath(p, ROOT), EM.write_cert(p, d)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--wall", type=float, default=4200.0)
    ap.add_argument("--cover_wall", type=float, default=2400.0)
    ap.add_argument("--sample", type=int, default=8000)
    ap.add_argument("--maxopen", type=int, default=500)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    k, n = (int(x) for x in a.shard.split("/"))
    out_p = os.path.join(BASE, "results", "t2_sweep_s%d.jsonl" % k)
    prog_p = os.path.join(BASE, "progress", "t2_sweep_s%d.json" % k)
    certdir = os.path.join(BASE, "certs")
    for d in (os.path.dirname(out_p), os.path.dirname(prog_p), certdir):
        os.makedirs(d, exist_ok=True)
    done = set()
    if os.path.exists(prog_p):
        done = set(json.load(open(prog_p))["done"])

    recs = [r for r in L152.alive_records()]
    # deterministic SHUFFLE, so that a wall-truncated sweep is a uniform sample across all
    # three classes and both campaigns rather than a prefix of the k5_11 shard.
    import hashlib
    recs.sort(key=lambda r: hashlib.sha256(reckey(r).encode()).hexdigest())
    recs = [r for idx, r in enumerate(recs) if idx % n == k]
    if a.limit:
        recs = recs[:a.limit]
    print("shard %d/%d: %d alive records (%d already done)" % (k, n, len(recs), len(done)),
          flush=True)

    fh = open(out_p, "a", encoding="utf-8")
    rng = np.random.default_rng(15200 + k)
    cover_budget = [a.cover_wall]
    t_start = time.time()
    nk = 0
    for idx, rec in enumerate(recs):
        if reckey(rec) in done:
            continue
        if time.time() - t_start > a.wall:
            print("wall budget reached at record %d/%d" % (idx, len(recs)), flush=True)
            break
        for slot in L152.CP.CLASSES[rec["cls"]]["usable"]:
            try:
                row, best, ij = do_cell(rec, slot, L152.H_G1, rng, a.sample, a.maxopen,
                                        cover_budget)
            except Exception as e:                                    # noqa: BLE001
                fh.write(json.dumps(dict(nid=rec["nid"], slot=slot, error=repr(e)[:200])) + "\n")
                continue
            if best is not None:
                cp, sha = emit(rec, slot, best, ij, L152.H_G1, certdir)
                best["cert"], best["sha256"] = cp, sha
                nk += 1
                print("KILL %-34s %-9s t=%s %s" % (rec["nid"], slot, best["t"], cp), flush=True)
            for r in row["rows"]:
                r.pop("_res", None)
                r.pop("_conds", None)
            fh.write(json.dumps(row) + "\n")
            fh.flush()
        done.add(reckey(rec))
        if idx % 25 == 0:
            json.dump(dict(done=sorted(done), cover_left=cover_budget[0]),
                      open(prog_p, "w", encoding="utf-8"))
            print("  %d/%d records, %.0f s, cover budget left %.0f s, %d kills"
                  % (idx, len(recs), time.time() - t_start, cover_budget[0], nk), flush=True)
    json.dump(dict(done=sorted(done), cover_left=cover_budget[0]),
              open(prog_p, "w", encoding="utf-8"))
    fh.close()
    print("done shard %d: %d kills, %.0f s, cover budget left %.0f s"
          % (k, nk, time.time() - t_start, cover_budget[0]), flush=True)


if __name__ == "__main__":
    main()
