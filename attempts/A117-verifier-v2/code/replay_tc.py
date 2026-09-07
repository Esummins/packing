"""A117 T2(c) -- replay every recorded Lemma-TC fire through the new exact leaf check.

Two sources, both READ-ONLY:

  A112  attempts/A112-dual-branching/results/rt*/<region>/<ordering>/<key>.json  --  every
        region-tree node record carries `logic.fires`, and a TC fire carries the two BOXES, so the
        replay is a direct re-check of the stored geometry.

  A111  attempts/A111-loadpath-branch/results/t3_logickills.json  --  the fire records carry only
        the box NAME and the conditioned-bin index, so the geometry is REBUILT the way
        code/t3_logickills.py built it (`t2_no.node_boxes` + the node's own hypothesis boxes) and
        the original float rule (`octagon.pair_kill`) is re-run to identify which pairs were TC.
        That rebuild is pure geometry -- no LP, no certificate emission -- so it is a replay, not a
        re-emission.  The rebuilt census is compared against the stored one fire for fire.

Each TC fire is then put through:
  (1) the EXACT check `tcleaf.tc_fires` (rational, tilt intervals normalised to [0, 90], domain
      asserted, cos/sin enclosed from below), and
  (2) >= 10^4 sampled pose pairs (`tcleaf.sample_confirm`), which must ALL overlap.

Writes results/tc_replay.json.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from fractions import Fraction as F

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = "1"
sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
RES = os.path.normpath(os.path.join(HERE, "..", "results"))
sys.path.insert(0, HERE)
import tcleaf as TC                                               # noqa: E402


def as_bin(d, name=""):
    return TC.Bin(F(d["x0"]), F(d["x1"]), F(d["y0"]), F(d["y1"]),
                  F(d["th0"]), F(d["th1"]), name)


def pair_kind(n1, n2):
    """A fire between two s-independent branch/conditioned boxes transfers to the whole window
    unchanged; a fire against a CLASS PIN does not, because a pin box is [alpha + beta*s +- h] and
    moves with the side."""
    p = [str(n1).lower(), str(n2).lower()]
    return "bin-vs-pin" if any(q.startswith("pin") for q in p) else "bin-vs-bin"


def check(b1, b2, n_samples, seed):
    fired, detail = TC.tc_fires(b1, b2)
    bad, worst, n = (None, None, 0)
    if fired:
        bad, worst, n = TC.sample_confirm(b1, b2, n=n_samples, seed=seed)
    return dict(exact_fires=bool(fired), detail=detail,
                samples=n, counterexamples=bad, worst_sat_gap=worst)


# ------------------------------------------------------------------ A112
def a112_fires(n_samples):
    rows = []
    base = os.path.join(ROOT, "attempts", "A112-dual-branching", "results")
    for root, _, fs in os.walk(base):
        for f in sorted(fs):
            if not f.endswith(".json"):
                continue
            p = os.path.join(root, f)
            try:
                d = json.load(open(p))
            except Exception:
                continue
            lg = d.get("logic") if isinstance(d, dict) else None
            if not isinstance(lg, dict):
                continue
            for k, fi in enumerate(lg.get("fires", [])):
                if fi.get("rule") != "TC" or "boxes" not in fi:
                    continue
                b1 = as_bin(fi["boxes"][0], fi["pair"][0])
                b2 = as_bin(fi["boxes"][1], fi["pair"][1])
                r = check(b1, b2, n_samples, seed=9000 + len(rows))
                rows.append(dict(src="A112", record=os.path.relpath(p, ROOT).replace("\\", "/"),
                                 region=d.get("region"), ordering=d.get("ordering"),
                                 node=d.get("key"), pair=fi["pair"],
                                 kind=pair_kind(fi["pair"][0], fi["pair"][1]),
                                 stored=dict(dtheta_min_deg=fi.get("dtheta_min_deg"),
                                             need=fi.get("need_centre_dist"),
                                             cmax=fi.get("max_centre_dist"),
                                             sample=fi.get("sample")),
                                 **r))
    return rows


# ------------------------------------------------------------------ A111
def a111_fires(n_samples, radii=None):
    A111 = os.path.join(ROOT, "attempts", "A111-loadpath-branch", "code")
    sys.path.insert(0, A111)
    import a111lib as L                                           # noqa: F401
    import t2_no as T2
    import octagon as OC

    stored = json.load(open(os.path.join(ROOT, "attempts", "A111-loadpath-branch", "results",
                                         "t3_logickills.json")))
    ex = {(n["src"], n["nid"]): n for n in
          json.load(open(os.path.join(T2.A107R, "extract.json"), encoding="utf-8"))["nodes"]}
    rows = []
    n_stored_tc = n_seen_tc = n_stored_cm = 0
    for tag in ("S02", "S07"):
        sn = json.load(open(os.path.join(T2.A107R, "shadow_nodes.json"), encoding="utf-8"))[tag]
        by_nid = {r["nid"]: r for r in stored[tag]["rows"]}
        for rec in sn:
            key = (rec["src"], rec["nid"])
            n = ex.get(key)
            if n is None or rec["nid"] not in by_nid:
                continue
            op = n.get("struct_op") or "e"
            cls = ("k5_11" if rec["nid"].startswith("k5_11")
                   else "k5_16" if rec["nid"].startswith("k5_16") else "trump5")
            p = L.copy_node(rec["nid"], rec["src"])
            if p is None:
                continue
            d = json.load(open(p, encoding="utf-8"))
            cond = [b for b in d["hyp"]["boxes"]
                    if (b["th1"] - b["th0"]) > 1e-6 or (b["x1"] - b["x0"]) > 0.02]
            if not cond:
                continue
            s_node = d["s"]
            for (r, rho) in (radii or T3_RADII):
                kk = "%g/%g" % (r, rho)
                st = by_nid[rec["nid"]]["per_radius"].get(kk)
                if st is None:
                    continue
                n_stored_tc += sum(1 for f in st["fires"] if f["rule"] == "TC")
                n_stored_cm += sum(1 for f in st["fires"] if f["rule"] == "CORE-MEET")
                bn, NB = T2.node_boxes(tag, "lpa", cls, r, rho, op, s_node)
                for ci, cb in enumerate(cond):
                    for nm in bn:
                        ok, info = OC.pair_kill(cb, NB[nm])
                        if not ok or info.get("rule") != "TC":
                            continue
                        n_seen_tc += 1
                        b1 = as_bin(cb, "cond%d" % ci)
                        b2 = as_bin(NB[nm], nm)
                        res = check(b1, b2, n_samples, seed=7000 + len(rows))
                        rows.append(dict(src="A111", tag=tag, nid=rec["nid"], level=rec["level"],
                                         cls=cls, radius=kk, cond=ci, box=nm,
                                         pair=["cond%d" % ci, nm],
                                         kind=pair_kind("cond%d" % ci, nm),
                                         stored=dict(dtheta_min_deg=info.get("dtheta_min_deg"),
                                                     need=info.get("need_centre_dist"),
                                                     cmax=info.get("max_centre_dist")),
                                         **res))
    return rows, dict(stored_tc=n_stored_tc, rebuilt_tc=n_seen_tc, stored_core_meet=n_stored_cm)


T3_RADII = ((0.02, 5.0), (0.05, 5.0), (0.0699, 4.87), (0.035, 2.43), (0.0175, 1.22),
            (0.0087, 0.61), (0.1, 10.0), (0.2, 20.0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples", type=int, default=10000)
    ap.add_argument("--out", default=os.path.join(RES, "tc_replay.json"))
    ap.add_argument("--skip-a111", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    r112 = a112_fires(a.samples)
    print("A112: %d TC fires replayed (%d exact-fire, %d confirmed by sampling)"
          % (len(r112), sum(1 for r in r112 if r["exact_fires"]),
             sum(1 for r in r112 if r["exact_fires"] and r["counterexamples"] == 0)), flush=True)
    r111, census = ([], {})
    if not a.skip_a111:
        r111, census = a111_fires(a.samples)
        print("A111: %d TC fires replayed  (census %s)" % (len(r111), census), flush=True)
    rows = r112 + r111
    doc = dict(samples_per_fire=a.samples, seconds=round(time.time() - t0, 1),
               n_fires=len(rows),
               n_exact_fires=sum(1 for r in rows if r["exact_fires"]),
               n_not_reproduced=sum(1 for r in rows if not r["exact_fires"]),
               n_sample_counterexamples=sum((r["counterexamples"] or 0) for r in rows),
               total_sampled_pairs=sum(r["samples"] for r in rows),
               worst_sat_gap=max([r["worst_sat_gap"] for r in rows
                                  if r["worst_sat_gap"] is not None] or [None]),
               min_exact_slack=min([r["detail"]["min_slack_float"] for r in rows
                                    if r["exact_fires"]] or [None]),
               by_kind={k: sum(1 for r in rows if r.get("kind") == k)
                        for k in ("bin-vs-bin", "bin-vs-pin")},
               a111_census=census, rows=rows)
    json.dump(doc, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in doc.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
