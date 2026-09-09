"""A177 -- build this attempt's two queues under the WIDEST-CITEABLE-N rule.

    python queues177.py

A136's `queue_a163.json` chose, for each node, the citeable A163 box set with the LARGEST verified
rational margin over `s0`.  Its own §6 finding says that is the wrong rule for the NO side: the
margin says how far the certificate's own tree got, while what the NO side has to kill is the
COMPLEMENT of `N`, so a WIDE `N` is what makes the LP's job small.  Measured on the k5_16 frame,
the largest-margin `h = 1.25deg` link (2.5deg shared-tilt window) left 12 of 12 NO children ALIVE
with `eta = 0` at `tau = 5`, while the 11x-smaller-margin `h = 10deg` link (10deg window) killed 3
of 4 on Y0941.

WIDTH, MADE DECIDABLE.  For a citeable entry, over its FREE bodies, `width = (min tilt width in
degrees, log10 of the product of the box volumes)`, both read off the certificate's own exact
rational bodies through `entry151.a163_entry` -- the same objects the cover will name.  Ties (and
they are exact ties: whole families share a shape) are broken by the largest margin over `s0`, so
this rule refines A136's rather than replacing it.

Two files are written into `results/`:

  * `queue177_h10.json` -- A136's `queue_a163_h10.json` minus `k5_16_interior_Y1110`, whose `NO0`
    is genuinely LP-ALIVE on that leaf (`eta = 0` at `tau = 5`, converged), so the node cannot
    close on it and its slots are better spent elsewhere.  The forced entry IS the widest citeable
    set for those nodes among the CHAIN links; `A163A151B` is wider still and is recorded on every
    row as `wider_alternative` (its own consumer, `k5_16_interior_Y0864`, is in the other queue and
    is the experiment that measures it).
  * `queue177_rest.json` -- the 18 un-run rows of `queue_a163.json`, minus the 6 that the h10 queue
    already carries and minus Y1110, each re-pointed at the widest of ITS OWN citeable sets.

READ-ONLY on A136 and A163: both are read, neither is written.  PYTHONDONTWRITEBYTECODE=1.
"""
from __future__ import annotations

import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A136 = os.path.join(ROOT, "attempts", "A136-a120-resume")
A163R = os.path.join(ROOT, "attempts", "A163-s02-other-frames", "results")
RES = os.path.join(BASE, "results")
os.makedirs(RES, exist_ok=True)

sys.path.insert(0, os.path.join(A136, "code"))
import entry151 as E                                               # noqa: E402


def in_sets(frame):
    """{node id: set of A160-side box-set ids the node's support lies in}, from A163's own
    consumer file (the containment test is A163's, not re-done here)."""
    p = os.path.join(A163R, "consumer163_%s.json" % frame)
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    out = {}
    for e in d["entries"]:
        for r in e["rows"]:
            if r.get("in_sets"):
                out.setdefault(r["nid"], set()).update(r["in_sets"])
    if d.get("y1110", {}).get("in_sets"):
        out.setdefault(d["y1110"]["nid"], set()).update(d["y1110"]["in_sets"])
    return out


def a163_id(label, frame):
    """'024|S02_k5_11_A160chain_...' -> 'S02_<frame>_A163chain_...'; 'S02_k5_11_A151B' ->
    'S02_<frame>_A163A151B'.  A163 re-frames A160's sets one for one and keeps the suffix."""
    s = label.split("|", 1)[-1]
    s = s.replace("S02_k5_11_", "", 1)
    if s.startswith("A160"):
        s = s[len("A160"):]
    return "S02_%s_A163%s" % (frame, s)


def width(entry):
    """(min tilt width in degrees, log10 product of box volumes) over the FREE bodies."""
    dims = [(2 * b["half_extent"][0], 2 * b["half_extent"][1], 2 * b["half_extent"][2])
            for b in entry["boxes"]]
    vol = 1.0
    for d in dims:
        vol *= d[0] * d[1] * d[2]
    return (round(min(d[2] for d in dims), 9),
            round(math.log10(vol) if vol > 0 else -99.0, 6))


def main():
    q = json.load(open(os.path.join(A136, "results", "queue_a163.json"), encoding="utf-8"))
    qh = json.load(open(os.path.join(A136, "results", "queue_a163_h10.json"), encoding="utf-8"))
    h10_ids = [x["id"] for x in qh["ids"]]

    # what already has a terminal record anywhere in A136's record subtrees
    import glob
    have = {}
    for p in glob.glob(os.path.join(A136, "results", "nodes_*", "rec__*.json")):
        try:
            r = json.load(open(p, encoding="utf-8"))
        except Exception:                                          # noqa: BLE001
            continue
        if r.get("id"):
            have.setdefault(r["id"], []).append(r.get("status"))

    IDX = {f: E.a163_index(f) for f in ("k5_16", "trump5")}
    ENT = {}

    def entry(eid, frame):
        if (eid, frame) not in ENT:
            ENT[(eid, frame)] = E.a163_entry(eid, frame)
        return ENT[(eid, frame)]

    ISETS = {f: in_sets(f) for f in ("k5_16", "trump5")}
    rest, table = [], []
    for x in q["ids"]:
        nid, frame = x["id"], x["frame"]
        if nid in h10_ids:
            table.append(dict(id=nid, action="h10 queue", chosen=qh["entry_forced"]))
            continue
        if nid == "k5_16_interior_Y1110":
            table.append(dict(id=nid, action="EXCLUDED: NO0 genuinely LP-ALIVE on the h10 leaf "
                                            "(eta = 0 at tau = 5, converged)"))
            continue
        st = [s for s in have.get(nid, []) if s in ("CLOSED", "OPEN", "SKIP-UNSOUND")]
        if st:
            table.append(dict(id=nid, action="already terminal: %s" % st))
            continue
        cand = []
        for lab in sorted(ISETS[frame].get(nid, ())):
            eid = a163_id(lab, frame)
            if eid not in IDX[frame]:
                continue
            e = entry(eid, frame)
            cand.append((width(e), e["certificate"]["margin_over_s0"], eid))
        if not cand:
            table.append(dict(id=nid, action="NO CITEABLE SET -- dropped"))
            continue
        cand.sort(key=lambda c: (c[0][0], c[0][1], c[1]), reverse=True)
        (mth, lv), marg, best = cand[0]
        rest.append(dict(id=nid, cls=x["cls"], frame=frame, entry=best,
                         margin=marg, min_tilt_deg=mth, log10_volume=lv,
                         was=x["entry"], moved=(best != x["entry"]),
                         candidates=[dict(entry=c[2], min_tilt_deg=c[0][0], log10_volume=c[0][1],
                                          margin=c[1]) for c in cand]))
        table.append(dict(id=nid, action=("MOVED %s -> %s" % (x["entry"], best))
                          if best != x["entry"] else "kept %s (only citeable / already widest)"
                          % best))

    # widest first: the rule's own prediction is that the narrow (h1.25, 2.5deg) leaves prove
    # nothing, so they go last where a cap can cut them without costing a closure.
    rest.sort(key=lambda r: (r["min_tilt_deg"], r["log10_volume"], r["margin"]), reverse=True)
    out = dict(
        name="A177: the 18 un-run rows of A136's queue_a163.json, minus the 6 the h10 queue "
             "carries and minus Y1110, each re-pointed at the WIDEST of its own citeable sets "
             "(min tilt width, then log-volume, margin only as a tie-break)",
        parent="attempts/A136-a120-resume/results/queue_a163.json",
        rule="widest citeable N (A136 notes/frames151.md section 6)",
        ids=rest, decisions=table)
    with open(os.path.join(RES, "queue177_rest.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)

    keep = []
    for x in qh["ids"]:
        if x["id"] == "k5_16_interior_Y1110":
            continue
        e = entry(x["entry"], x["frame"])
        mth, lv = width(e)
        alt = None
        aid = "S02_%s_A163A151B" % x["frame"]
        if aid in IDX[x["frame"]]:
            ae = entry(aid, x["frame"])
            amth, alv = width(ae)
            if (amth, alv) > (mth, lv):
                alt = dict(entry=aid, min_tilt_deg=amth, log10_volume=alv,
                           margin=ae["certificate"]["margin_over_s0"],
                           note="wider still, but its margin over s0 is 4.6e-7; its own consumer "
                                "k5_16_interior_Y0864 is in queue177_rest.json and is the "
                                "experiment that measures whether that width pays")
        keep.append(dict(x, min_tilt_deg=mth, log10_volume=lv, wider_alternative=alt))
    outh = dict(qh)
    outh["name"] = ("A177 re-issue of A136's queue_a163_h10.json: " + qh["name"] +
                    "  Y1110 is DROPPED here -- its NO0 came back genuinely LP-ALIVE on this leaf "
                    "(eta = 0 at tau = 5, converged), so the node cannot close on it.")
    outh["ids"] = keep
    with open(os.path.join(RES, "queue177_h10.json"), "w", encoding="utf-8") as f:
        json.dump(outh, f, indent=1)

    print("queue177_h10.json : %d nodes" % len(keep))
    print("queue177_rest.json: %d nodes (%d moved by the widest-N rule)"
          % (len(rest), sum(1 for r in rest if r["moved"])))
    for r in rest:
        print("   %-26s %-56s min_dth=%5.2f logvol=%7.3f %s"
              % (r["id"], r["entry"], r["min_tilt_deg"], r["log10_volume"],
                 ("MOVED from " + r["was"]) if r["moved"] else ""))
    for t in table:
        if t.get("action", "").startswith(("EXCLUDED", "already", "NO CITEABLE")):
            print("   -- %-26s %s" % (t["id"], t["action"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
