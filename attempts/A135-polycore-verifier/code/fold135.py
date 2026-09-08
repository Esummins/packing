"""A135 T4 -- the fold-in ledger `results/polycore_kills.jsonl`.

One line per kill, in a shape the A57/A60 owner can fold in at resume:

  * `kind = "T5-poly-logic"` -- A132's 64 T5⁗ firings (37 new over the deployed T5′ tight core).
    Each carries the RATIONAL WITNESS POINT and the two boxes it is certified against, so the
    line is self-contained: the consumer is `PolyCoreT5.shared_point_same_square`
    (`lean/PackingCertMathlib/PackingCertMathlib/PolyCoreT5.lean`), which needs one point and two
    vertex checks and no polygon at all.  Every witness is RE-CERTIFIED here by
    `verify_case_v3.point_in_all_poses` -- an implementation independent of A132's
    `polycore.vertex_ok` -- against BOTH boxes, closed and with a strict margin.
  * `kind = "LP-certified"` -- A135's certified LP kills: the certificate path, the verifier that
    passed it, tau, budget, and whether the frozen verifier suffices.

The A57 rule this ledger is written for: keep the prior verdict, add the new one, as
`superseded_by_tight_core.jsonl` does (PAUSED.md Sec.8, A131's backlog paragraph).  A135 writes
NOTHING into A57/A96/A60 state.
"""
import argparse
import json
import math
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
A132 = os.path.join(ROOT, "A132-polygon-core")
for _p in (os.path.join(ROOT, "A57-shadow-trees", "code"),
           os.path.join(ROOT, "A96-a57-parametric", "code"),
           os.path.join(A132, "code"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from caselp import Box, t_lo, t_hi                                   # noqa: E402
import measure132                                                    # noqa: E402  (read-only)
import verify_case_v3 as v3                                          # noqa: E402

MARGIN = Fr(1, 10 ** 7)          # the strict-interior slack demanded of every witness


def box_rat(b):
    return dict(x0=str(Fr(b.x0)), x1=str(Fr(b.x1)), y0=str(Fr(b.y0)), y1=str(Fr(b.y1)),
                t0=str(t_lo(b.th0)), t1=str(t_hi(b.th1)),
                th0_deg=b.th0, th1_deg=b.th1)


def certify_witness(wx, wy, b):
    """closed containment in every pose, and the same with the box GROWN by MARGIN in x and y --
    which implies the point is at distance >= MARGIN from the boundary of every pose, i.e. in the
    open square (the strict form `core_meet_same_square` consumes)."""
    x0, x1 = Fr(b.x0), Fr(b.x1)
    y0, y1 = Fr(b.y0), Fr(b.y1)
    t0, t1 = t_lo(b.th0), t_hi(b.th1)
    closed = v3.point_in_all_poses(wx, wy, x0, x1, y0, y1, t0, t1)
    strict = v3.point_in_all_poses(wx, wy, x0 - MARGIN, x1 + MARGIN, y0 - MARGIN, y1 + MARGIN,
                                   t0, t1)
    return closed, strict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(BASE, "results", "polycore_kills.jsonl"))
    a = ap.parse_args()
    rows = [json.loads(l) for l in
            open(os.path.join(A132, "results", "measure132.jsonl")) if l.strip()]
    dead = {r["id"]: r for r in rows if r.get("t5poly_dead")}
    print(f"{len(dead)} T5-poly logic kills in A132's measurement "
          f"({sum(1 for r in dead.values() if r.get('t5poly_new'))} new over the deployed T5')",
          flush=True)

    nodes = {}
    for meta, d in measure132.a57_alive() + measure132.a60_alive():
        nodes[meta["id"]] = (meta, d)
    print(f"{len(nodes)} alive node records located", flush=True)

    out, n_ok, n_strict, n_missing = [], 0, 0, 0
    t0 = time.time()
    for nid, r in dead.items():
        if nid not in nodes:
            n_missing += 1
            continue
        meta, d = nodes[nid]
        boxes = [Box.from_json(b) for b in d["hyp"]["boxes"]]
        nb, pins = boxes[-1], boxes[:-1]
        hits = []
        for h in r.get("t5poly_hits") or []:
            wx, wy = Fr(h["witness"][0]), Fr(h["witness"][1])
            pb = pins[h["pin"]]
            cN, sN = certify_witness(wx, wy, nb)
            cP, sP = certify_witness(wx, wy, pb)
            hits.append(dict(pin=h["pin"], witness=[str(wx), str(wy)],
                             pin_box=box_rat(pb),
                             recertified_closed=bool(cN and cP),
                             recertified_strict=bool(sN and sP),
                             margin=str(MARGIN),
                             depth_polypoly=h.get("depth_polypoly"),
                             depth_polycore=h.get("depth_polycore")))
        allc = all(h["recertified_closed"] for h in hits) and bool(hits)
        alls = all(h["recertified_strict"] for h in hits) and bool(hits)
        n_ok += bool(allc)
        n_strict += bool(alls)
        out.append(dict(
            kind="T5-poly-logic", camp=meta["camp"], id=nid, cls=meta["cls"],
            level=meta["level"], budget=meta["budget"],
            prior_verdict=("ALIVE" if meta["camp"] == "A57" else "refused"),
            prior_tau=meta.get("tau"), prior_eta=meta.get("eta"),
            new_over_deployed_T5prime=bool(r.get("t5poly_new")),
            pinguard_now=r.get("pinguard_now"),
            node_box=box_rat(nb), hits=hits,
            recertified_closed=allc, recertified_strict=alls,
            consumer=("PackingCert.S11.shared_point_same_square "
                      "(lean/.../PolyCoreT5.lean) -- one rational point, two vertex checks; "
                      "no polygon, no LP, no certificate"),
            source="attempts/A132-polygon-core/results/measure132.jsonl"))
    print(f"witnesses re-certified: {n_ok}/{len(out)} closed, {n_strict}/{len(out)} strict "
          f"(margin {MARGIN}); {n_missing} nodes without a located record; "
          f"{round(time.time()-t0,1)} s", flush=True)

    # ---------------------------------------------------------------- the certified LP kills
    for f in ("emit135_s0.jsonl", "emit135_s1.jsonl", "emitpoly135.jsonl"):
        p = os.path.join(BASE, "results", f)
        if not os.path.exists(p):
            continue
        for ln in open(p):
            rec = json.loads(ln)
            if rec.get("result") != "PASS":
                continue
            out.append(dict(
                kind="LP-certified", camp="A57", id=rec["id"], scope=rec["scope"],
                budget=rec["budget"], tau=rec["tau"], converged=rec["converged"],
                prior_verdict="ALIVE (tau = budget under the deployed core)",
                cert=os.path.relpath(rec["cert"], ROOT),
                verifier=("frozen verify_case.py sha 521cb01f" if rec["scope"] != "poly"
                          else "verify_case_v3.py (A135) -- polycores clause"),
                frozen_rc=rec.get("frozen_rc"), replay_rc=rec.get("replay_rc"),
                cores=rec.get("a_report"), pin_gate=rec.get("pin_gate"),
                lp_wall_s=rec.get("lp_wall_s"), wall_s=rec.get("wall_s"),
                source="attempts/A135-polycore-verifier/results/" + f))

    # ---------------------------------------------------------------- the sample line
    chk = json.load(open(os.path.join(A132, "results", "check132.json")))
    with open(a.out, "w") as fh:
        fh.write(json.dumps(dict(
            kind="_header", attempt="A135", written=time.strftime("%Y-%m-%dT%H:%M:%S"),
            n_logic=sum(1 for r in out if r["kind"] == "T5-poly-logic"),
            n_logic_new=sum(1 for r in out
                            if r["kind"] == "T5-poly-logic" and r["new_over_deployed_T5prime"]),
            n_lp_certified=sum(1 for r in out if r["kind"] == "LP-certified"),
            recertified_closed=n_ok, recertified_strict=n_strict,
            sample_line=chk.get("D") or chk.get("d") or chk,
            note=("A135 wrote nothing into A57/A96/A60 state; fold in keeping the prior verdict, "
                  "as superseded_by_tight_core.jsonl does."))) + "\n")
        for r in out:
            fh.write(json.dumps(r) + "\n")
    print(f"wrote {len(out)} kill rows + header -> {a.out}")


if __name__ == "__main__":
    main()
