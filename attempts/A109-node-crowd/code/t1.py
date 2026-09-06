"""A109 T1 -- the mechanism check on the shadows.

For every alive-at-LP node that A107's gallery explains by S01/S03/S04/S05 (restricted to the
three pinned classes with a slot-crowd table: k5_11, k5_16, trump5), count the DUAL SUPPORT's
incidences with each usable slot box of the node's class:

    I_p(delta) = sum of the dual weights y_Q over support placements Q with slot depth
                 d_p(Q) >= delta      (delta = 0.3, 0.1, 0.05 -- the brief's ladder)
    I_p(0+)    = the same with d_p(Q) > 0, i.e. Q MEETS the open slot box -- the only crowd
                 statement Lemma SLOT-CROWD + SLOT-SLIDE give on A57's G1 slab (a_w = 1).

Lemma SLOT-CROWD says every real packing has >= 2 non-pin meeters at every usable slot, so a dual
support with I_p < 2 at some usable p is a configuration the crowd rows can charge.  The fraction
of explained nodes with min_p I_p < 2 is the UPPER BOUND on what crowd rows can kill.
"""
import json, math, os, sys, time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a109lib as L
import slotfam94 as SF

ROOT = L.ROOT
SHADOWS = ("S01", "S03", "S04", "S05")
DELTAS = [0.3, 0.1, 0.05, 0.0]      # 0.0 == "meets the open box" (d_p > 0)


def main():
    sn = json.load(open(os.path.join(ROOT, "attempts/A107-shadow-gallery/results/shadow_nodes.json")))
    idx = L.node_index()
    out = []
    t0 = time.time()
    seen = set()
    for sid in SHADOWS:
        for rec in sn[sid]:
            nid, src = rec["nid"], rec["src"]
            cls = L.cls_of(nid)
            if cls is None:
                continue
            key = (sid, src, nid)
            if key in seen:
                continue
            seen.add(key)
            p = idx.get((src, nid)) or idx.get(nid)
            if p is None:
                continue
            try:
                res = json.load(open(p))
            except Exception:
                continue
            S = L.support(res)
            hyp = res["hyp"]
            pin_idx, br_idx = L.split_hyp(cls, hyp)
            row = dict(shadow=sid, nid=nid, src=src, shard=rec.get("shard"),
                       level=rec.get("level"), via=rec.get("via"), cls=cls,
                       budget=res["budget"], tau=res["tau"],
                       converged=bool(res.get("converged")), n_support=len(S),
                       n_pin=len(pin_idx), n_branch=len(br_idx))
            for U_tag, cells in (("U4", SF.CLASSES[cls]["slots"]), ("U3", L.FULL_SLOTS[cls])):
                for d in DELTAS:
                    I = []
                    for cell in cells:
                        w = 0.0
                        for (cx, cy, th, y) in S:
                            mu = L.slot_mu(cls, cell, cx, cy, th)
                            if (mu < 1.0 - 1e-12) if d == 0.0 else (mu <= 1.0 - d + 1e-12):
                                w += y
                        I.append(w)
                    row["I_%s_d%g" % (U_tag, d)] = [round(v, 6) for v in I]
                    row["Itot_%s_d%g" % (U_tag, d)] = round(sum(I), 6)
                    row["viol_%s_d%g" % (U_tag, d)] = int(sum(1 for v in I if v < 2.0 - 1e-9))
            out.append(row)
            if len(out) % 100 == 0:
                print("  %d nodes, %.0f s" % (len(out), time.time() - t0), flush=True)
    json.dump(out, open(os.path.join(L.RES, "t1_incidence.json"), "w"))
    # ---- summary
    summ = {}
    for sid in SHADOWS + ("ALL",):
        rows = [r for r in out if sid == "ALL" or r["shadow"] == sid]
        if not rows:
            continue
        e = dict(n=len(rows), by_class=dict(Counter(r["cls"] for r in rows)),
                 by_level=dict(Counter(r["level"] for r in rows)))
        for U_tag in ("U4", "U3"):
            for d in DELTAS:
                k = "viol_%s_d%g" % (U_tag, d)
                nv = sum(1 for r in rows if r[k] > 0)
                e["frac_%s_d%g" % (U_tag, d)] = round(nv / len(rows), 4)
                e["nviol_%s_d%g" % (U_tag, d)] = nv
                e["meanIslots_%s_d%g" % (U_tag, d)] = round(
                    sum(r[k] for r in rows) / len(rows), 3)
                e["meanItot_%s_d%g" % (U_tag, d)] = round(
                    sum(r["Itot_%s_d%g" % (U_tag, d)] for r in rows) / len(rows), 3)
        # which slot is empty/single most often, at the sound threshold
        cnt = Counter()
        for r in rows:
            cells = L.FULL_SLOTS[r["cls"]]
            for c, v in zip(cells, r["I_U3_d0"]):
                if v < 2.0 - 1e-9:
                    cnt[(r["cls"], "%s(%d,%d)" % c)] += 1
        e["empty_or_single_slot_U3_d0"] = {("%s/%s" % k): v for k, v in cnt.most_common()}
        summ[sid] = e
    json.dump(summ, open(os.path.join(L.RES, "t1_summary.json"), "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
