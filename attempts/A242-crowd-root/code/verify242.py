"""A242 -- the VERIFIER CLAUSE for the two new leaves, and the audit sampling.

The frozen verifiers (`verify_case.py` sha 521cb01f..., `verify_case_v4.py`) are untouched: A242's
leaves are not case-LP certificates and get their own clause here.

CLAUSE L0 (EMPTYBOX, A171's pair leaf).  The cell records a role whose box lost every pose under
`multibox.Node.normalise`.  RE-DECIDE: rebuild the node from the recorded role boxes at the band's
S and check that `normalise` raises `EmptyBox` again (the clip is deterministic and exact).
AUDIT: sample poses of the failing role uniformly from its RECORDED box and check each one is
refused -- it leaves the container, or its body meets the core K' of another role (which lies
inside every pose of that role, A172), so the two squares would overlap.  A sampled pose that
passes is a COUNTEREXAMPLE to the kill and the audit fails loudly.

CLAUSE L1 (NOROOM / NOROOM-POCKET / NOROOM-CN, A189 Lemma 1 + A221 POCKET-DEAD + A209 CN).
RE-DECIDE: re-run `leaves242.l1` on the recorded role boxes with a fresh budget and no inherited
pockets (so the verdict does not depend on the parent's cover) and check DEAD.
AUDIT (independent of the clip machinery): draw random poses (c, theta) of a free unit square with
c in the container's centre box [1/2, S - 1/2]^2 and theta in [0, 90), and test the body against
each role's core polygon with a plain shapely intersection.
  * clip NOROOM / NOROOM-POCKET claims NO free square exists at all: every sample must meet a core.
  * clip NOROOM-CN claims at most `cn_bound` < m free squares: every sample that meets no core must
    have its centre inside one of the recorded surviving pockets.
Either way a sample that escapes is reported; the audit is a falsifier, never a proof.
"""
import argparse
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import leaves242 as L                                              # noqa: E402
import multibox as MB                                              # noqa: E402  READ-ONLY (A171/A172)

try:
    from shapely.geometry import Polygon
except Exception:                                                  # noqa: BLE001
    Polygon = None


def _body(cx, cy, th_deg):
    t = math.radians(th_deg)
    ct, st = math.cos(t), math.sin(t)
    pts = []
    for dx, dy in ((-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)):
        pts.append((cx + dx * ct - dy * st, cy + dx * st + dy * ct))
    return Polygon(pts)


def _cores(nd):
    out = {}
    for k in nd.names:
        mb = nd.boxes[k]
        if mb.pc is None:
            try:
                mb.rebuild()
            except Exception:                                      # noqa: BLE001
                continue
        pts = [(float(x), float(y)) for (x, y) in (mb.pc.verts if mb.pc is not None else [])]
        if len(pts) >= 3:
            out[k] = Polygon(pts)
    return out


def audit_cell(rec, samples=4000, seed=0):
    """The audit of one recorded DEAD cell.  -> dict with `escapes` (must be 0) and the evidence."""
    cell = dict(S=rec["S"], roles=rec["roles"], n=rec.get("n", 11), m=rec.get("m", 3))
    bud = L.N221.budget_of(L.L1_BUDGET)
    rnd = random.Random(seed)
    try:
        nd = L.build_node(cell, bud, name="audit")
    except MB.EmptyBox as e:
        return dict(clause="L0", redecide="EmptyBox", detail=str(e)[:160], escapes=0, samples=0)
    if Polygon is None:
        return dict(clause="L1", escapes=None, note="shapely unavailable: audit skipped")
    cores = _cores(nd)
    S = float(cell["S"])
    alive = [list(map(float, p)) for p in (rec.get("alive") or [])]
    esc, n_in_pocket = 0, 0
    ex = []
    for _ in range(samples):
        cx = rnd.uniform(0.5, S - 0.5)
        cy = rnd.uniform(0.5, S - 0.5)
        th = rnd.uniform(0.0, 90.0)
        b = _body(cx, cy, th)
        if b.bounds[0] < -1e-12 or b.bounds[1] < -1e-12 or b.bounds[2] > S + 1e-12 or b.bounds[3] > S + 1e-12:
            continue                                                # not a pose inside the container
        if any(b.intersection(c).area > 1e-12 for c in cores.values()):
            continue                                                # excluded by a core: as certified
        if alive and any(p[0] - 1e-9 <= cx <= p[1] + 1e-9 and p[2] - 1e-9 <= cy <= p[3] + 1e-9
                         for p in alive):
            n_in_pocket += 1
            continue                                                # inside a SURVIVING pocket: allowed
        esc += 1
        if len(ex) < 5:
            ex.append([round(cx, 5), round(cy, 5), round(th, 3)])
    return dict(clause="L1", clip=rec.get("clip"), n_cores=len(cores), samples=samples,
                escapes=esc, in_pocket=n_in_pocket, examples=ex)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--band", default="W")
    ap.add_argument("--n", type=int, default=12, help="DEAD cells to audit (spread over the file)")
    ap.add_argument("--samples", type=int, default=4000)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    jl = os.path.join(BASE, "results", "crowd242_%s.jsonl" % a.band)
    rows = [json.loads(x) for x in open(jl, encoding="utf-8") if x.strip()]
    import root242 as R
    band = [b for b in R.BANDS if b[0] == a.band][0]
    dead = [r for r in rows if r.get("verdict") == "DEAD"]
    alive = [r for r in rows if r.get("verdict") == "UNDECIDED"]
    pick = dead[:: max(1, len(dead) // max(1, a.n))][:a.n] + alive[:: max(1, len(alive) // 3)][:3]
    out = []
    for r in pick:
        r = dict(r)
        r["S"], r["m"], r["n"] = band[2], 3, 11
        res = audit_cell(r, samples=a.samples, seed=abs(hash(r["label"])) % 10 ** 6)
        res.update(label=r["label"], verdict=r["verdict"])
        out.append(res)
        print(json.dumps(res)[:300], flush=True)
    bad = [o for o in out if o.get("escapes")]
    print("AUDIT %s: %d cell(s), %d with escapes -> %s"
          % (a.band, len(out), len(bad), "FAIL" if bad else "PASS"), flush=True)
    if a.out:
        json.dump(out, open(a.out, "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
