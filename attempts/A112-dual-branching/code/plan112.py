"""A112 -- the region list for T2.

Region A: the S02-explained STALLED nodes of A57 at levels 2-3 (A107's shadow_nodes.json), all with
          a T5''-trimmed bin (trim57.trim_box actually removes tilt from the node's conditioned bin).
Region B: A113's un-killable k0 level-1 cells, the ones whose LP support is a partial skeleton of a
          near-critical shadow, best matches first (S38 exact, then S07/S13/S01 at Jaccard >= 0.8).

Read-only: every node json is copied into results/nodes/<nid>.src.json before it is opened for a
solve.  Writes results/plan.json.
"""
from __future__ import annotations

import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a112lib as L
import trim57
from caselp import Hyp


def trim_report(hyp):
    pins, bins = L.split_hyp(hyp)
    slots = L.pin_slots(pins)
    tot_excl, tot_sub, emptied = 0, 0, 0
    for b in bins:
        for nb in L.normalise_tilt(b):
            try:
                subs, excl = trim57.trim_box(nb, slots)
            except Exception:
                subs, excl = [nb], []
            tot_excl += len(excl)
            tot_sub += len(subs)
            if not subs:
                emptied += 1
    return dict(bins=len(bins), pins=len(pins), excluded=tot_excl, subs=tot_sub, emptied=emptied)


def plan_s02(n=14, levels=(2, 3), must_include=("k5_11_interior_Y0054_D00",)):
    sn = L.shadow_nodes("S02")
    ex = L.extract_index()
    out = []
    for rec in sn:
        if rec["src"] != "A57" or rec["level"] not in levels:
            continue
        nid = rec["nid"]
        p = L.copy_node(nid, rec["src"])
        if p is None:
            continue
        res = L.jload(p)
        hyp = Hyp.from_json(res["hyp"])
        e = ex.get((rec["src"], nid), {})
        cls = "k5_11" if nid.startswith("k5_11") else ("k5_16" if nid.startswith("k5_16") else "trump5")
        sup = L.support(res)
        out.append(dict(region=nid, src=rec["src"], nid=nid, level=rec["level"], cls=cls,
                        op=e.get("struct_op") or "e", shadow="S02", kind="a57",
                        budget=res["budget"], s=res["s"], tau=res["tau"],
                        converged=bool(res.get("converged")),
                        support=len(sup), sup_mass=round(sum(q["y"] for q in sup), 4),
                        trim=trim_report(hyp), path=p))
    # prefer nodes with a T5''-trimmed bin, then the deeper level, then the richer support
    out.sort(key=lambda o: (0 if o["trim"]["excluded"] else 1, -o["level"], -o["support"], o["nid"]))
    keep, seen = [], set()
    for nid in must_include:
        for o in out:
            if o["nid"] == nid and nid not in seen:
                keep.append(o); seen.add(nid)
    # stratify by (class, level) so the sample is not all one class: round-robin over the strata,
    # each stratum still in its own "trimmed first, deeper first, richer support first" order
    strata = {}
    for o in out:
        if o["nid"] in seen:
            continue
        strata.setdefault((o["cls"], o["level"]), []).append(o)
    order = sorted(strata, key=lambda k: (-len(strata[k]),) if False else (k[0], -k[1]))
    i = 0
    while len(keep) < n and any(strata[k] for k in order):
        k = order[i % len(order)]
        i += 1
        if strata[k]:
            o = strata[k].pop(0)
            keep.append(o); seen.add(o["nid"])
    return keep, out


def plan_k0(n=8):
    rows = [json.loads(l) for l in
            open(os.path.join(L.A113R, "t2_supports.jsonl"), encoding="utf-8")]
    un = [r for r in rows if r.get("unkillable") and r.get("src") == "A38-l1"]
    # the S38/S07-matching ones first, then the rest by Jaccard: A113's criterion is "the support is
    # a 2-6-slot partial skeleton of a near-critical shadow"
    def rank(r):
        sh = r["shadow_hits"]
        pri = 0 if sh["best_shadow"] in ("S38", "S07") else 1
        return (pri, -(sh["best_jaccard"] or 0.0), -len(r["a107_slots"]), r["cid"])
    un.sort(key=rank)
    keep = []
    for r in un[:n]:
        nid = os.path.splitext(os.path.basename(r["path"]))[0]
        p = L.copy_node("k0_" + r["cid"], "A38", path=os.path.join(L.ROOT, r["path"]))
        if p is None:
            continue
        res = L.jload(p)
        sup = L.support(res)
        hyp = Hyp.from_json(res["hyp"])
        keep.append(dict(region="k0_" + r["cid"], src="A38", nid=nid, cid=r["cid"], level=1,
                         cls="k0_00", op="e", shadow=r["shadow_hits"]["best_shadow"], kind="k0",
                         jaccard=r["shadow_hits"]["best_jaccard"], verdict=r["verdict"],
                         budget=res["budget"], s=res["s"], tau=res["tau"],
                         converged=bool(res.get("converged")),
                         support=len(sup), sup_mass=round(sum(q["y"] for q in sup), 4),
                         trim=trim_report(hyp), a113_slot=r.get("slot"), path=p))
    return keep


def main():
    a, alls02 = plan_s02(n=int(sys.argv[1]) if len(sys.argv) > 1 else 14)
    b = plan_k0(n=int(sys.argv[2]) if len(sys.argv) > 2 else 8)
    plan = dict(s02=a, k0=b, s02_pool=len(alls02),
                s02_pool_trimmed=sum(1 for o in alls02 if o["trim"]["excluded"]))
    L.jdump(os.path.join(L.RES, "plan.json"), plan)
    print(json.dumps(dict(s02=[dict(nid=o["nid"], L=o["level"], cls=o["cls"], op=o["op"],
                                    sup=o["support"], trim=o["trim"]["excluded"],
                                    tau=round(o["tau"], 6), conv=o["converged"]) for o in a],
                          k0=[dict(cid=o["cid"], sh=o["shadow"], j=o["jaccard"], sup=o["support"],
                                   tau=round(o["tau"], 6), conv=o["converged"],
                                   trim=o["trim"]["excluded"]) for o in b],
                          pool=plan["s02_pool"], pool_trimmed=plan["s02_pool_trimmed"]), indent=1))


if __name__ == "__main__":
    main()
