#!/usr/bin/env python3
"""
A42 follow-up -- the ZONE-SIZE lever for conditional occupancy at s0 = 969271/250000.

The r = 0.06 ball chain (chain42.py) measured tau == budget EXACTLY at every k: dead, zero
headroom.  Headroom is bought with EXEMPTED VOLUME, so this probe re-runs the same question with
MEDIUM zones: half-width w = 0.35 (side 0.70, diameter 0.9899 < 1, so Lemma N1's exactly-one
conclusion still applies; pairwise disjoint at the Trump placements, min gap 0.036 for the closest
pair).

Zones are c-only: FULL theta [0,90], no window and no window-complement NoFams.

    zone i core   = Box(clip_rect(c_i, w), 0, 90)      "some square is centred in zone i"
    zone j target = NoFam(clip_rect(c_j, w), [(0,90)]) "zone j is EMPTY"

Node k: cores = first k zones of the conditioning list, target NoFam on the next zone,
budget = 11 - k.  A certified tau < budget refutes the conjunction => zone j must be occupied.

Kill = A39 rule: status "dead(certified)" (exact verify_case PASS at depth 56).

    python zoneprobe42.py --nodes P1
    python zoneprobe42.py --nodes P3 --time_limit 600
    python zoneprobe42.py --show
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import earlycert                                       # noqa: E402
import seam38                                          # noqa: E402
from caselp import Box, NoFam                          # noqa: E402

RES = os.path.abspath(os.path.join(HERE, "..", "results"))
NODEDIR = os.path.join(RES, "zone_nodes")
ZONEJSON = os.path.join(RES, "zoneprobe.json")
LOGDIR = os.path.abspath(os.path.join(HERE, "..", "logs"))

S_RAT = "969271/250000"
NBALL = 11
W_MED = 0.35
FULL_TH = [(0.0, 90.0)]

# zone indices used by the probe (A37 atlas order, D4 element 'e')
Z_TGT1 = 8          # (2.623834, 2.436509)  interior
Z_CORE1 = 6         # (1.959613, 1.688559)  interior
Z_TGT2 = 5          # (1.936475, 3.172475)  clipped in y


# ------------------------------------------------------------------------------- zone geometry
def zones():
    places, _ = seam38.trump_placements("e")
    assert len(places) == NBALL, len(places)
    return places


def rect_of(places, i, w):
    cx, cy, _ = places[i]
    return seam38.clip_rect(cx, cy, w)


def core_of(places, i, w):
    x0, x1, y0, y1 = rect_of(places, i, w)
    return Box(x0, x1, y0, y1, 0.0, 90.0)


def nofam_of(places, i, w):
    x0, x1, y0, y1 = rect_of(places, i, w)
    return NoFam(x0, x1, y0, y1, list(FULL_TH))


def wtag(w):
    return ("w%g" % w).replace(".", "")


# ---------------------------------------------------------------------------------- node specs
def spec(places, tag, core_idx, w_core, tgt_idx, w_tgt, budget, note=""):
    cores = [core_of(places, i, w_core) for i in core_idx]
    nofams = [nofam_of(places, tgt_idx, w_tgt)]
    return dict(tag=tag, kind="zone", cores=cores, nofams=nofams, budget=budget,
                core_idx=list(core_idx), w_core=(w_core if core_idx else None),
                tgt_idx=tgt_idx, w_target=w_tgt, k=len(core_idx), note=note)


def spec_P1(places, w=W_MED):
    return spec(places, "P1_k0_%s" % wtag(w), [], None, Z_TGT1, w, NBALL,
                "k=0 analog of the certified A38 root")


def spec_P2(places, w=W_MED):
    return spec(places, "P2_k1_%s" % wtag(w), [Z_CORE1], w, Z_TGT1, w, NBALL - 1,
                "k=1: core zone 6, target zone 8")


def spec_P3(places, w):
    return spec(places, "P3_k0_%s" % wtag(w), [], None, Z_TGT1, w, NBALL,
                "target-size scan at k=0")


def spec_P4(places, w=W_MED):
    return spec(places, "P4_k2_%s" % wtag(w), [Z_CORE1, Z_TGT1], w, Z_TGT2, w, NBALL - 2,
                "k=2: cores zones 6+8, target zone 5")


def spec_P5(places, w_tgt, w_core=W_MED):
    return spec(places, "P5_k1_%s_t%s" % (wtag(w_core), wtag(w_tgt)), [Z_CORE1], w_core,
                Z_TGT1, w_tgt, NBALL - 1, "mid-chain tightening at medium core scale")


def build(name, places):
    if name == "P1":
        return [spec_P1(places)]
    if name == "P2":
        return [spec_P2(places)]
    if name == "P4":
        return [spec_P4(places)]
    if name.startswith("P3:"):
        return [spec_P3(places, float(name.split(":", 1)[1]))]
    if name.startswith("P5:"):
        return [spec_P5(places, float(name.split(":", 1)[1]))]
    raise SystemExit("unknown node %r" % name)


# ------------------------------------------------------------------------------------- runner
def describe(sp):
    print("  node %-16s budget=%d  k=%d  cores=%s" % (sp["tag"], sp["budget"], sp["k"],
                                                      [repr(c) for c in sp["cores"]]), flush=True)
    print("  core zones %s @ w=%s ; target zone %s @ w=%s"
          % (sp["core_idx"], sp["w_core"], sp["tgt_idx"], sp["w_target"]), flush=True)
    for f in sp["nofams"]:
        print("     %r" % (f,), flush=True)


def row(sp, rec, wall):
    ca = rec.get("cert_attempts") or []
    passed = [a for a in ca if a.get("rc") == 0]
    fa = rec.get("final_attempt") or {}
    if not passed and fa.get("rc") == 0:
        passed = [fa]
    tau = rec.get("tau")
    return dict(
        tag=sp["tag"], kind=sp["kind"], k=sp["k"], note=sp["note"],
        core_idx=sp["core_idx"], w_core=sp["w_core"], tgt_idx=sp["tgt_idx"],
        w_target=sp["w_target"], budget=sp["budget"],
        status=rec.get("status"), status_a27=rec.get("status_a27"),
        tau=tau, slack=(None if tau is None else tau - sp["budget"]),
        converged=rec.get("converged"), minmass=rec.get("minmass"), maxcov=rec.get("maxcov"),
        t_decide=rec.get("t_decide"), wall_s=wall,
        n_cert_attempts=rec.get("n_cert_attempts"),
        cert_scale=(passed[0].get("scale") if passed else None),
        cert_total=(passed[0].get("total") if passed else None),
        cert_verify_s=rec.get("cert_verify_s"),
        n_rows=rec.get("n_rows"), n_orbits=rec.get("n_orbits"),
        rows_fed_back=rec.get("rows_fed_back"), iters=rec.get("iters"),
        cert=rec.get("cert"), node=os.path.join("zone_nodes", sp["tag"] + ".json"),
        when=time.strftime("%Y-%m-%dT%H:%M:%S"))


def append_row(r):
    """checkpoint.  Each node owns its own <tag>.row.json (race-free under concurrent
    processes); zoneprobe.json is then rebuilt as the merge of every row file."""
    os.makedirs(NODEDIR, exist_ok=True)
    own = os.path.join(NODEDIR, r["tag"] + ".row.json")
    json.dump(r, open(own + ".tmp", "w"), indent=1)
    os.replace(own + ".tmp", own)
    tab = []
    for fn in sorted(os.listdir(NODEDIR)):
        if fn.endswith(".row.json"):
            try:
                tab.append(json.load(open(os.path.join(NODEDIR, fn))))
            except Exception:
                pass
    tab.sort(key=lambda t: (t["tag"],))
    tmp = ZONEJSON + ".%d.tmp" % os.getpid()
    json.dump(dict(when=time.strftime("%Y-%m-%dT%H:%M:%S"), s_rat=S_RAT, w_med=W_MED,
                   theta="full [0,90] (c-only zones)",
                   zones=dict(core1=Z_CORE1, tgt1=Z_TGT1, tgt2=Z_TGT2), rows=tab),
              open(tmp, "w"), indent=1)
    os.replace(tmp, ZONEJSON)


def run(sp, time_limit, eps_geo=0.003, jobs=2):
    os.makedirs(NODEDIR, exist_ok=True)
    os.makedirs(LOGDIR, exist_ok=True)
    tag = sp["tag"]
    out = os.path.join(NODEDIR, tag + ".json")
    lg = os.path.join(LOGDIR, tag + ".log")

    def log(*a):
        line = " ".join(str(x) for x in a)
        with open(lg, "a") as f:
            f.write(line + "\n")
        print("   |", line, flush=True)

    print("=" * 78, flush=True)
    describe(sp)
    t0 = time.time()
    try:
        rec = earlycert.solve_node_early(
            S_RAT, sp["cores"], sp["budget"], nofams=sp["nofams"], time_limit=time_limit,
            out=out, log=log, eps_geo=eps_geo, jobs=jobs, tag=tag)
    except MemoryError:
        print("  MemoryError -- retry once serial (jobs=1)", flush=True)
        rec = earlycert.solve_node_early(
            S_RAT, sp["cores"], sp["budget"], nofams=sp["nofams"], time_limit=time_limit,
            out=out, log=log, eps_geo=eps_geo, jobs=1, tag=tag)
    wall = time.time() - t0
    r = row(sp, rec, wall)
    append_row(r)
    print("  -> %-16s status=%-16s tau=%s slack=%s t_dec=%s wall=%.0fs rows=%s orb=%s cert=%s"
          % (tag, r["status"], ("%.5f" % r["tau"]) if r["tau"] is not None else "-",
             ("%+.5f" % r["slack"]) if r["slack"] is not None else "-",
             ("%.1f" % r["t_decide"]) if r["t_decide"] is not None else "-",
             wall, r["n_rows"], r["n_orbits"], r["cert_scale"]), flush=True)
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nodes", default="P1",
                    help="comma list: P1, P2, P4, P3:<w>, P5:<w_target>")
    ap.add_argument("--time_limit", type=float, default=900)
    ap.add_argument("--eps_geo", type=float, default=0.003)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--show", action="store_true")
    a = ap.parse_args()

    places = zones()
    if a.show:
        for i, (cx, cy, th) in enumerate(places):
            print(i, "c=(%.6f, %.6f) th=%.4f" % (cx, cy, th),
                  "rect(w=0.35)=", rect_of(places, i, W_MED))
        for nm in ("P1", "P2", "P4", "P3:0.25", "P3:0.15", "P3:0.1", "P5:0.25", "P5:0.15"):
            for sp in build(nm, places):
                describe(sp)
        return 0

    for nm in [x.strip() for x in a.nodes.split(",") if x.strip()]:
        for sp in build(nm, places):
            try:
                run(sp, a.time_limit, eps_geo=a.eps_geo, jobs=a.jobs)
            except Exception:
                print("  FAILED %s\n%s" % (sp["tag"], traceback.format_exc()[-2000:]), flush=True)
                append_row(dict(tag=sp["tag"], kind=sp["kind"], k=sp["k"], note=sp["note"],
                                core_idx=sp["core_idx"], w_core=sp["w_core"],
                                tgt_idx=sp["tgt_idx"], w_target=sp["w_target"],
                                budget=sp["budget"], status="error", tau=None, slack=None,
                                when=time.strftime("%Y-%m-%dT%H:%M:%S")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
