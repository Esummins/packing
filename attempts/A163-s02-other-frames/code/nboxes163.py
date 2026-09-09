"""A163 T2 -- write the re-framed neighbourhoods in A119/A125's `N_boxes` format, one file per
frame, as a LIST whose hypothesis is a DISJUNCTION, so A136's YES leaf can cite the union.

    results/N_boxes163_k5_16.json     results/N_boxes163_trump5.json

The layout is A119's `results/N_boxes.json` verbatim (same keys, same pin affine form, same `d4_ops`
and `hypothesis` wording), with one entry per CERTIFIED re-framed box set.  Each entry keeps a
`reframe` block naming the A160 object it is the image of, so the two files and A160's own
`N_boxes160.json` are cross-referenced object by object; `tree_verdict` is this attempt's own run in
this attempt's frame (never A160's), and `tcert` names the exact t-certificate when one was emitted.

    python nboxes163.py [--cls k5_16] [--out ...]

READ-ONLY on every campaign and prior attempt.
"""
from __future__ import annotations

import argparse, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib163 as L                 # noqa: E402
import a116lib as A                # noqa: E402

HYP = ("s in [3.82, 3.897084]; for each pin p: a square with tilt 0 and centre in "
       "(alpha_p + beta_p s) + [-%r, %r]^2; for each l in L: a DISTINCT other square with centre in "
       "the box and tilt (mod 90 deg) in the interval; conclusion: no such configuration is a "
       "packing at side <= s0." % (A.PIN_SLACK, A.PIN_SLACK))


def entry(eid, cls, boxes, verdict, extra=None):
    free = [b for b in boxes if b["kind"] == "free"]
    pins = [b for b in boxes if b["kind"] == "pin"]
    e = dict(id=eid, tag=L.TAG, cls=cls,
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


def build(cls):
    tree = os.path.join(L.RES, "tree_%s.jsonl" % cls)
    tc = {}
    p = os.path.join(L.RES, "tcerts163.json")
    if os.path.exists(p):
        for r in json.load(open(p, encoding="utf-8"))["runs"]:
            if r.get("cls") == cls and r.get("key"):
                tc.setdefault(r["key"], r)
    N, refused = [], []
    pins, boxnames, dropped = L.frame(cls)
    for line in open(tree, encoding="utf-8"):
        r = json.loads(line)
        if not r.get("dead"):
            refused.append(dict(id=r["id"], key=r.get("key"), family=r.get("family"),
                                reason=r.get("reason"), witnesses=r.get("n_witnesses"),
                                unresolved=r.get("n_unresolved"), seconds=r.get("seconds"),
                                certified_min=(r.get("tree") or {}).get("certified_min")))
            continue
        eid = (("S02_%s_A163" % cls)
               + r["id"].replace("S02_k5_11_A160", "").replace("S02_k5_11_", ""))
        v = dict(dead=True, certified_min=(r.get("tree") or {}).get("certified_min"),
                 sample_hits=(r.get("sampling") or {}).get("hits"),
                 sample_drawn=(r.get("sampling") or {}).get("drawn"),
                 sample_tested=(r.get("sampling") or {}).get("tested"),
                 trump_inside=(bool((r.get("trump") or {}).get("inside"))
                               if isinstance(r.get("trump"), dict) else None),
                 seconds=r["seconds"], tree="A116 selection tree (a116lib.Tree), frame %s" % cls)
        ex = dict(reframe=dict(a160_id=r["id"], a160_index=r.get("a160_index"),
                               family=r.get("family"), frame=cls,
                               a160_k5_11_verdict=r.get("a160_verdict"),
                               note="same absolute boxes as A160's entry; pins are %s's" % cls))
        for k in ("chain", "slice", "f0_slide"):
            if k in r:
                ex[k] = r[k]
        t = tc.get(r.get("key"))
        if t and t.get("checker_ok"):
            # the shape A136's entry151.CITE_ASYM uses for a citeable YES leaf
            ex["certificate"] = dict(
                id=t["id"], format="local-cert-t-v1",
                file="attempts/A163-s02-other-frames/certs/%s.tcert.json.gz" % t["id"],
                sha256=t.get("sha256"), dead=bool(t.get("dead")), leaves=t.get("n_leaves"),
                status="CHECKED",
                spec="A160's absolute boxes, %s's pin set (A163 re-framing); L = %s, P = %s"
                     % (cls, ",".join(t.get("L") or []), ",".join(t.get("P") or [])),
                boxes="THE CERTIFICATE'S OWN meta.bodies (exact rationals); the entry's float boxes "
                      "are the same box printed in degrees",
                certified_min=t.get("certified_min"),
                checker="attempts/A163-s02-other-frames/results/tcerts163.json "
                        "(A133's check_local_t.py, imported unchanged): %d errors, %s leaves, "
                        "certified minimum %s > s0 = 3.877084"
                        % (t.get("n_errors", 0), t.get("n_leaves"), t.get("certified_min")),
                generator_seconds=t.get("generator_seconds"),
                checker_seconds=t.get("checker_seconds"))
        elif t:
            ex["certificate"] = dict(id=t["id"], status="EMITTED-NOT-CHECKED",
                                     dead=bool(t.get("dead")), sha256=t.get("sha256"),
                                     file="attempts/A163-s02-other-frames/certs/%s.tcert.json.gz"
                                          % t["id"])
        else:
            ex["certificate"] = dict(
                status="PENDING-CERTIFICATE", sha256=None,
                tree_verdict=v,
                caveat="this entry carries only A116's float selection-tree verdict in this frame "
                       "(dead, certified_min, 0 sampling hits).  A136's entry151.py refuses to "
                       "close a node on such an entry (see its A160_NO_CERTIFICATE note); the "
                       "exact object is one gent163.py run away.",
                emit_command="python attempts/A163-s02-other-frames/code/gent163.py --cls %s "
                             "--key '%s' --check" % (cls, r.get("key")))
        N.append(entry(eid, cls, r["boxes"], v, extra=ex))
    return N, refused, (pins, boxnames, dropped)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cls", default=None)
    a = ap.parse_args()
    for cls in ([a.cls] if a.cls else list(L.FRAMES)):
        N, refused, (pins, boxnames, dropped) = build(cls)
        out = dict(generated=time.strftime("%Y-%m-%dT%H:%M:%S"),
                   source="attempts/A163-s02-other-frames/results/tree_%s.jsonl "
                          "(A160's results/N_boxes160.json box sets, re-framed)" % cls,
                   frame=dict(cls=cls, pins=pins, boxes=boxnames, dropped=dropped,
                              pin_slack=A.PIN_SLACK,
                              note="the S02 shadow's seven slot squares contain all three classes' "
                                   "pin sets; f0 and BR(0,0) are the shadow's rattlers (A160 T1) "
                                   "and the wedged no-load slot squares are dropped where the "
                                   "frame does not pin them"),
                   s0=float(A.S0), shat=A.SHAT, s_lo=L.S_LO, s_hi=L.S_HI, pin_slack=A.PIN_SLACK,
                   note="attempts/A119-local-cert-lean/notes/n_boxes.md (DROP/COVER: 'a square in "
                        "each box' + pins => inside N).  A163: this file is a LIST and the "
                        "hypothesis is a DISJUNCTION over entries -- a node of class %s inside ANY "
                        "entry is killed by the YES leaf." % cls,
                   d4_ops={"e": "(x, y, t)", "r90": "(s - y, x, t)", "r180": "(s - x, s - y, t)",
                           "r270": "(y, s - x, t)", "mx": "(s - x, y, -t)", "my": "(x, s - y, -t)",
                           "diag": "(y, x, -t)", "anti": "(s - y, s - x, -t)"},
                   d4_ops_note="apply at s = s0 = 3.877084; A107's struct_op per node, then test "
                               "the boxes; the union is satisfied if any entry is",
                   n_entries=len(N), n_refused=len(refused), refused=refused, N=N)
        p = os.path.join(L.RES, "N_boxes163_%s.json" % cls)
        json.dump(out, open(p, "w", encoding="utf-8"), indent=1)
        print("wrote %s  (%d certified entries, %d refused)" % (p, len(N), len(refused)))


if __name__ == "__main__":
    main()
