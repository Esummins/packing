"""A140 T1 addendum -- the IN-VITRO k0 node LP with the column pool pruned by the polygon core K'.

A132's invitro132.py for the k0_00 class: there are NO pins, so every hypothesis box is a
CONDITIONED square and `scope` is vacuous -- all boxes get their certified polygon core K'(B).
The control arm is not re-run: A115's own stored record IS the axis arm AT CONVERGENCE
(converged = True, tau = budget exactly, minmass 1.000), a stronger control than a fresh 240 s
axis solve, so this driver runs ONE LP per cell (the brief's clause).

Dropping more rows can only LOWER tau, so a kill here is NOT a certificate: the frozen verifier
knows only the axis core K(a).  A kill is recorded as "LP-dead under polygon core, certificate
pending".  T1's `w_exact_only` column says how much of the dropped weight the A135 EXACT AXIS CORE
alone removes -- that part IS inside the frozen certificate schema (a square at the box's own tilt).

NOT a shard launch: nothing is written into any campaign's results, no certificate is emitted, no
tree row is appended.  Own sentinel: attempts/A140-k0-residue-gallery/PAUSE.

    python code/invitro140.py --shard 0 --nshards 2 --cap 240
"""
import argparse
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
for p in (os.path.join(ROOT, "attempts", "A57-shadow-trees", "code"),
          os.path.join(ROOT, "attempts", "A132-polygon-core", "code"),
          HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np                                             # noqa: E402
import polycore                                                # noqa: E402
from caselp import Box, Hyp, solve_node, EPS_CORE              # noqa: E402
import cells140 as C140                                        # noqa: E402

S_RAT = 969271.0 / 250000.0
OWN_PAUSE = os.path.join(BASE, "PAUSE")


class PolyHyp(Hyp):
    """Hyp whose row filter is the certified polygon core K'(B) of every conditioned box."""

    MAX_V = 16          # A132: a 16-gon is within 5e-4 of the full K' in area and 2.5x cheaper

    def __init__(self, boxes=(), nofams=()):
        super().__init__(boxes, nofams)
        self.scope = "all"
        self.pcs = [polycore.build(b, max_v=self.MAX_V) for b in self.boxes]

    def ok_many(self, C, theta):
        C = np.asarray(C, dtype=float).reshape(-1, 2)
        keep = np.ones(len(C), dtype=bool)
        th_deg = math.degrees(theta) % 90.0
        for f in self.nofams:
            keep &= ~f.inside_many(C, th_deg)
        if not keep.any():
            return keep
        TH = np.full(len(C), float(theta))
        for pc in self.pcs:
            keep &= ~polycore.poly_square_meets(pc, C, TH, EPS_CORE)
            if not keep.any():
                break
        return keep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--cap", type=float, default=240.0)
    ap.add_argument("--warm_rows", type=int, default=14000)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or os.path.join(BASE, "results", f"invitro140_s{a.shard}.jsonl")
    names = [c[0] for c in C140.CELLS]
    mine = [n for i, n in enumerate(names) if i % a.nshards == a.shard]
    done = set()
    if os.path.exists(out):
        for ln in open(out, encoding="utf-8"):
            try:
                done.add(json.loads(ln)["cell"])
            except Exception:                                   # noqa: BLE001
                pass
    print(f"shard {a.shard}: {len(mine)} cells at cap {a.cap:.0f} s -> {out}", flush=True)
    for cell in mine:
        if cell in done:
            continue
        if os.path.exists(OWN_PAUSE):
            print("A140 pause sentinel set; stopping cleanly", flush=True)
            break
        meta, d = C140.load_cell(cell)
        boxes = [Box.from_json(b) for b in d["hyp"]["boxes"]]
        budget = int(d["budget"])
        atoms = [(float(p[0]), float(p[1])) for p in (d.get("atoms_all") or [])]
        rows = [(float(r[0]), float(r[1]), float(r[2]))
                for r in (d.get("rows_all") or [])][:a.warm_rows]
        H = PolyHyp(boxes, [])
        rec = dict(cell=cell, arm="poly", cap=a.cap, level=meta["level"], budget=budget,
                   tau_rec=d.get("tau"), converged_rec=d.get("converged"),
                   minmass_rec=d.get("minmass"), warm_rows=len(rows), warm_atoms=len(atoms),
                   n_boxes=len(boxes))
        t0 = time.time()
        try:
            s = solve_node(float(d.get("s") or S_RAT), H, budget, sym_kind=d.get("sym") or "C1",
                           warm=dict(atoms=atoms, rows=rows), time_limit=a.cap, max_iter=900,
                           out=None, log=lambda *x: None, prune=0, prune_cols=3,
                           col_stop_iter=10 ** 6, col_stop_cov=1.002, max_cols_add=400,
                           max_rows_add=2000, fine_slack=99.0, alternate=True, fine=False)
            tau = s.get("tau")
            rec.update(tau=tau, eta=(tau - budget) if tau is not None else None,
                       converged=s.get("converged"), minmass=s.get("minmass"),
                       maxcov=s.get("maxcov"), n_rows=s.get("n_rows"),
                       support=len(s.get("packing") or []),
                       kills=bool(tau is not None and tau < budget - 1e-6),
                       kills_converged=bool(s.get("converged") and tau is not None
                                            and tau < budget - 1e-6))
        except Exception as e:                                  # noqa: BLE001
            rec.update(error=repr(e)[:300])
        rec["wall_s"] = round(time.time() - t0, 1)
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")
        print(f"{cell:28s} tau {rec.get('tau')} conv={rec.get('converged')} "
              f"kills={rec.get('kills')} {rec['wall_s']}s", flush=True)
    print("invitro140 shard done", flush=True)


if __name__ == "__main__":
    main()
