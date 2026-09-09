"""A160 T3/T4 -- write this attempt's neighbourhoods in A119/A125's `N_boxes` format, as a LIST, so
A136's YES leaf can cite the union.

The format is A119's `results/N_boxes.json` verbatim (same keys, same pin affine form, same
`d4_ops` / `hypothesis` wording), with one entry per certified object:

  * `S02_k5_11_A160chain_k<+/-NN>`  one entry per CERTIFIED LINK of the common-tilt chain -- the
    three tilted boxes centred on the s*(theta_k) configuration dilated by s0/s*(theta_k), the three
    tilt intervals moved together, BR(0,1) at its slot cell;
  * `S02_k5_11_A160f0_*`           the f0-slide entries, when the ladder certified one.

The union's hypothesis is a DISJUNCTION over entries -- a node is killed if it satisfies ANY entry --
which is exactly how a list of YES-leaf boxes is consumed (`attempts/A119-local-cert-lean/notes/
n_boxes.md`, DROP/COVER).  Every per-entry `tree_verdict` is the record of that entry's own run.

    python nboxes160.py [--out results/N_boxes160.json]

READ-ONLY on every campaign and prior attempt.
"""
from __future__ import annotations

import argparse, glob, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib160 as L                 # noqa: E402
import a116lib as A                # noqa: E402

RES = L.RES
HYP = ("s in [3.82, 3.897084]; for each pin p: a square with tilt 0 and centre in "
       "(alpha_p + beta_p s) + [-%r, %r]^2; for each l in L: a DISTINCT other square with centre in "
       "the box and tilt (mod 90 deg) in the interval; conclusion: no such configuration is a "
       "packing at side <= s0." % (A.PIN_SLACK, A.PIN_SLACK))


def entry(eid, boxes, verdict, extra=None):
    free = [b for b in boxes if b["kind"] == "free"]
    pins = [b for b in boxes if b["kind"] == "pin"]
    e = dict(id=eid, tag=L.TAG, cls=L.CLS,
             r=round(max(max(0.5 * (b["x"][1] - b["x"][0]), 0.5 * (b["y"][1] - b["y"][0]))
                         for b in free), 9),
             rho_deg=round(max(0.5 * (b["theta_deg"][1] - b["theta_deg"][0]) for b in free), 6),
             anchor_side=A.S0, window=[L.S_LO, L.S_HI],
             L=[b["name"] for b in free], P=[b["name"] for b in pins],
             boxes=[dict(name=b["name"], cx=b["x"], cy=b["y"], theta_deg=b["theta_deg"],
                         anchor=b["anchor"], tilted=bool(b["name"].startswith("f")),
                         half_extent=[round(0.5 * (b["x"][1] - b["x"][0]), 9),
                                      round(0.5 * (b["y"][1] - b["y"][0]), 9),
                                      round(0.5 * (b["theta_deg"][1] - b["theta_deg"][0]), 6)])
                    for b in free],
             pins=[dict(name=b["name"], alpha=[b["ax"][0], b["ay"][0]],
                        beta=[b["ax"][1], b["ay"][1]], halfwidth=b["hh"]) for b in pins],
             cut=None, hypothesis=HYP, tree_verdict=verdict)
    if extra:
        e.update(extra)
    return e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(RES, "N_boxes160.json"))
    a = ap.parse_args()
    N = []

    for p in sorted(glob.glob(os.path.join(RES, "chain_*.jsonl"))):
        lab = os.path.basename(p)[len("chain_"):-len(".jsonl")]
        for line in open(p, encoding="utf-8"):
            rec = json.loads(line)
            if not rec.get("dead"):
                continue
            off = rec.get("offset_deg", 0.0)
            eid = "S02_k5_11_A160chain_%s_%+06.2f" % (lab, off)
            v = dict(dead=True, certified_min=rec["tree"].get("certified_min"),
                     sample_hits=rec.get("sampling", {}).get("hits"),
                     trump_inside=bool(rec.get("trump", {}).get("inside"))
                     if isinstance(rec.get("trump"), dict) else None,
                     seconds=rec["seconds"])
            N.append(entry(eid, rec["boxes"], v,
                           extra=dict(chain=dict(label=lab, offset_deg=off,
                                                 tilt_deg=rec["tilt_deg"], s_star=rec["s_star"],
                                                 tilt_window=rec["tilt_window"],
                                                 half_deg=rec["half_deg"], r_xy=rec["r_xy"],
                                                 widths=rec.get("widths"),
                                                 f0_in_boxes=rec["use_f0"]))))

    for p in sorted(glob.glob(os.path.join(RES, "slice160*.jsonl"))):
        lab = os.path.basename(p)[len("slice160"):-len(".jsonl")].strip("_") or "a151B"
        for line in open(p, encoding="utf-8"):
            rec = json.loads(line)
            if not rec.get("dead"):
                continue
            eid = "S02_k5_11_A160slice_%s_f2%+05.1f_f3%+05.1f" % (lab, rec["d2"], rec["d3"])
            v = dict(dead=True, certified_min=rec["tree"].get("certified_min"),
                     sample_hits=rec.get("sampling", {}).get("hits"),
                     trump_inside=bool(rec.get("trump", {}).get("inside"))
                     if isinstance(rec.get("trump"), dict) else None,
                     seconds=rec["seconds"])
            N.append(entry(eid, rec["boxes"], v,
                           extra=dict(slice=dict(label=lab, d2=rec["d2"], d3=rec["d3"],
                                                 half_deg=rec["half_deg"],
                                                 f1_tilt=rec.get("f1_tilt"),
                                                 f1_base=rec.get("f1_base")))))

    for p in sorted(glob.glob(os.path.join(RES, "grow_*.jsonl"))):
        job = os.path.basename(p)[len("grow_"):-len(".jsonl")]
        best = None
        for line in open(p, encoding="utf-8"):
            rec = json.loads(line)
            if rec.get("knob") == "FINAL" or not rec.get("dead"):
                continue
            best = rec
        if best is not None and "boxes" not in best:
            best["boxes"] = L.boxlist(best["spec"])
        if best is not None:
            v = dict(dead=True, certified_min=best["tree"].get("certified_min"),
                     sample_hits=best.get("sampling", {}).get("hits"),
                     trump_inside=bool(best.get("trump", {}).get("inside"))
                     if isinstance(best.get("trump"), dict) else None,
                     seconds=best["seconds"])
            N.append(entry("S02_k5_11_A160%s" % job, best["boxes"], v,
                           extra=dict(f0_slide=dict(knob=best.get("knob"),
                                                    value=best.get("value")))))

    out = dict(generated=time.strftime("%Y-%m-%dT%H:%M:%S"),
               source="attempts/A160-s02-f0-slide/results/{chain_*.jsonl,slice160*.jsonl,grow_*.jsonl}",
               s0=float(A.S0), shat=A.SHAT, s_lo=L.S_LO, s_hi=L.S_HI, pin_slack=A.PIN_SLACK,
               note="attempts/A119-local-cert-lean/notes/n_boxes.md (DROP/COVER: 'a square in each "
                    "box' + pins => inside N).  A160: this file is a LIST and the hypothesis is a "
                    "DISJUNCTION over entries -- a node inside ANY entry is killed by the YES leaf.",
               d4_ops={"e": "(x, y, t)", "r90": "(s - y, x, t)", "r180": "(s - x, s - y, t)",
                       "r270": "(y, s - x, t)", "mx": "(s - x, y, -t)", "my": "(x, s - y, -t)",
                       "diag": "(y, x, -t)", "anti": "(s - y, s - x, -t)"},
               d4_ops_note="apply at s = s0 = 3.877084; A107's struct_op per node, then test the "
                           "boxes; the union is satisfied if any entry is",
               n_entries=len(N), N=N)
    json.dump(out, open(a.out, "w", encoding="utf-8"), indent=1)
    print("wrote %s  (%d entries)" % (a.out, len(N)))
    for e in N[:6]:
        print("  %-46s r=%.3f rho=%.3f L=%s" % (e["id"], e["r"], e["rho_deg"], e["L"]))


if __name__ == "__main__":
    main()
