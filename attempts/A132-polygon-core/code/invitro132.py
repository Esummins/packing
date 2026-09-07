"""A132 T2 -- the IN-VITRO node LP with the column pool pruned by the polygon core K'.

Two arms per node, identical settings and identical warm start (recheck96's node path):

    arm "axis"  the stock hypothesis: a row is dropped only if it penetrates some K(a) by
                more than EPS_CORE = 2e-3 -- what the campaign ran;
    arm "poly"  the same, with K(a) replaced by the CERTIFIED polygon core K'(B) of the same box.

Dropping more rows can only LOWER tau, so a kill in the "poly" arm is not a certificate: the frozen
verifier knows only K(a).  Such a node is recorded as "LP-dead under polygon core, certificate
pending" (T3's v3 is what would close it).  The "axis" arm at the same cap is the control that says
whether a drop is attributable to the polygon core rather than to the re-solve.

NOT a shard launch: nothing is written into any campaign's results, no certificate is emitted, no
tree row is appended.  A57's PAUSE sentinel is reported but not obeyed (this is the A124-sanctioned
pattern of a SEPARATE sentinel for in-vitro work); this driver stops between jobs on its own
sentinel  attempts/A132-polygon-core/PAUSE.

    python code/invitro132.py --jobs results/t2_jobs.json --shard 0 --nshards 2 --cap 240
"""
import argparse
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
A57 = os.path.join(ROOT, "A57-shadow-trees")
A96 = os.path.join(ROOT, "A96-a57-parametric")
A53 = os.path.join(ROOT, "A53-simple-strata")
for p in (os.path.join(A57, "code"), os.path.join(A96, "code"), HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np                                            # noqa: E402
import polycore                                               # noqa: E402
from caselp import Box, Hyp, solve_node, EPS_CORE             # noqa: E402
from warm57 import merged_warm                                # noqa: E402
from pausegate import paused, reason                          # noqa: E402

S_RAT = 969271.0 / 250000.0
DELTA = 1e-2
OWN_PAUSE = os.path.join(BASE, "PAUSE")


class PolyHyp(Hyp):
    """Hyp whose core filter is the certified polygon core K'(B) instead of K(a).

    The ONLY override is the row filter `ok_many`; `cores`, `to_json`, `shell_points` and every
    other member are the base class's, so the record and the warm-start plumbing are unchanged."""

    MAX_V = 16          # a 16-gon is within 5e-4 of the full K' in area (measured) and 2.5x cheaper

    def __init__(self, boxes=(), nofams=(), scope="all"):
        super().__init__(boxes, nofams)
        # scope "all": every box (pins AND the conditioned box) gets its polygon core.
        # scope "box": only the LAST box -- the conditioned one -- does; the pins keep K(a).
        # The attribution test: A96's all-poses row filter was specified for the conditioned box
        # only, so "box" is the comparable arm and "all" is the part A96 never tested.
        self.scope = scope
        self.poly_idx = (set(range(len(self.boxes))) if scope == "all"
                         else {len(self.boxes) - 1})
        self.pcs = [polycore.build(b, max_v=self.MAX_V) if i in self.poly_idx else None
                    for i, b in enumerate(self.boxes)]

    def ok_many(self, C, theta):
        C = np.asarray(C, dtype=float).reshape(-1, 2)
        keep = np.ones(len(C), dtype=bool)
        th_deg = math.degrees(theta) % 90.0
        for f in self.nofams:
            keep &= ~f.inside_many(C, th_deg)
        if not keep.any():
            return keep
        TH = np.full(len(C), float(theta))
        for i, (pc, core) in enumerate(zip(self.pcs, self.cores)):
            if pc is not None:
                keep &= ~polycore.poly_square_meets(pc, C, TH, EPS_CORE)
            else:
                keep &= ~(polycore.core_depth_fast(core, C, TH) > EPS_CORE)
            if not keep.any():
                break
        return keep


def load_jobs(path):
    return json.load(open(path))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", required=True)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--cap", type=float, default=240.0)
    ap.add_argument("--out", default=None)
    ap.add_argument("--budget_s", type=float, default=1e9, help="stop starting jobs past this CPU-s")
    ap.add_argument("--warm_rows", type=int, default=30000,
                    help="cap on merged warm rows; IDENTICAL for both arms, so the arm-vs-arm "
                         "comparison is unaffected.  Lowered from recheck96's 30000 when the box "
                         "is short of physical memory (A57 lemma T19: commit is the binding "
                         "constraint), which also cuts the per-iteration LP solve.")
    ap.add_argument("--fine", action="store_true",
                    help="enable solve_node's FINE row search (n_theta=181, cstep=0.01).  Off by "
                         "default here: with fine_slack=99 it fires on every clean iteration and a "
                         "single fine scan outruns the wall cap by an order of magnitude on a "
                         "contended box, so the cap stops deciding anything.  Off in BOTH arms, so "
                         "the arm-vs-arm comparison is unaffected.")
    a = ap.parse_args()
    out = a.out or os.path.join(BASE, "results",
                                f"invitro132_c{int(a.cap)}_w{a.warm_rows}"
                                f"{'_fine' if a.fine else ''}_s{a.shard}.jsonl")
    # shard by NODE, not by job, so a node's two arms run back to back in the same process and
    # under the same machine load -- the arms are the comparison, so they must not be split.
    allj = load_jobs(a.jobs)
    order = []
    for j in allj:
        if j["id"] not in order:
            order.append(j["id"])
    jobs = [j for j in allj if order.index(j["id"]) % a.nshards == a.shard]
    done = set()
    if os.path.exists(out):
        for ln in open(out):
            try:
                r = json.loads(ln)
                done.add((r["id"], r["arm"], r["cap"]))
            except Exception:
                pass
    slots_all = json.load(open(os.path.join(A53, "results", "name_to_slots.json")))
    hh = DELTA / math.sqrt(2.0)
    print(f"shard {a.shard}: {len(jobs)} jobs at cap {a.cap:.0f} s -> {out}", flush=True)
    print(f"A57 PAUSE sentinel: {paused()} ({reason()!r:.80}) -- reported, not obeyed; "
          f"this driver's own sentinel is {OWN_PAUSE}", flush=True)
    warm = {}
    spent = 0.0
    for j in jobs:
        if os.path.exists(OWN_PAUSE):
            print("A132 pause sentinel set; stopping cleanly", flush=True)
            break
        if spent > a.budget_s:
            print(f"local CPU budget {a.budget_s:.0f} s reached; stopping", flush=True)
            break
        key = (j["id"], j["arm"], a.cap)
        if key in done:
            continue
        nm = "k5_11" if j["id"].startswith("k5_11") else "k5_16"
        sl = [tuple(p) for p in slots_all[nm]]
        pins = [Box(x - hh, x + hh, y - hh, y + hh, 0.0, 0.0) for (x, y) in sl]
        b = Box.from_json(j["box"])
        if nm not in warm:
            warm[nm] = merged_warm(nm, max_rows=a.warm_rows)[0]
        W = warm[nm]
        if j["arm"] == "axis":
            H = Hyp(pins + [b], [])
        else:
            H = PolyHyp(pins + [b], [], scope=("box" if j["arm"] == "polybox" else "all"))
        rec = dict(id=j["id"], arm=j["arm"], cap=a.cap, warm_rows=a.warm_rows,
                   level=j["level"], cls=j["cls"], scope=getattr(H, "scope", "axis"),
                   budget=j["budget"], tau_rec=j.get("tau"), eta_rec=j.get("eta"),
                   minmass_rec=j.get("minmass"))
        t0 = time.time()
        try:
            s = solve_node(S_RAT, H, j["budget"], sym_kind="C1",
                           warm=dict(atoms=list(W["atoms"]), rows=W["rows"]),
                           time_limit=a.cap, max_iter=900, out=None, log=lambda *x: None,
                           prune=0, prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002,
                           max_cols_add=400, max_rows_add=2000, fine_slack=99.0, alternate=True,
                           fine=a.fine)
            tau = s.get("tau")
            ht = s.get("hist_tail") or []
            rec.update(tau=tau, eta=(tau - j["budget"]) if tau is not None else None,
                       converged=s.get("converged"), minmass=s.get("minmass"),
                       maxcov=s.get("maxcov"), n_rows=s.get("n_rows"),
                       n_orbits=s.get("n_orbits"), iters=(ht[-1]["it"] + 1 if ht else None),
                       fine=bool(a.fine),
                       kills=bool(tau is not None and tau < j["budget"] - 1e-6),
                       support=len(s.get("packing") or []))
        except Exception as e:
            rec.update(error=repr(e)[:300])
        rec["wall_s"] = round(time.time() - t0, 1)
        spent += rec["wall_s"]
        with open(out, "a") as fh:
            fh.write(json.dumps(rec) + "\n")
        print(f"{j['id']:30s} {j['arm']:4s} tau {rec.get('tau')} conv={rec.get('converged')} "
              f"kills={rec.get('kills')} {rec['wall_s']}s", flush=True)
    print("invitro132 shard done", flush=True)


if __name__ == "__main__":
    main()
