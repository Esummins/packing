"""A176 -- re-derive A171's demo171 and A172's report172 numbers on node BR139/TRH-25 with the
FIXED library (post 13f23204), writing ONLY under attempts/A176-cascade-fixedlib (A171/A172 are
read-only).  Same ROLES, LINES, settings (nsub=4, refine=3) as the originals; the two original
scripts are imported for their constants, never executed against their own result paths.

    python rederive176.py            -> results/rederive176.json, figs/A168_BR139_TRH-25_{before,after}.svg
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
sys.path.insert(0, os.path.join(ATT, "A171-multibox-invariant", "code"))
sys.path.insert(0, os.path.join(ATT, "A172-multibox-pieces", "code"))
import multibox as MB                                          # noqa: E402
import demo171 as D171                                         # noqa: E402  constants only
import report172 as R172                                       # noqa: E402  constants + snap()

ROLES, LINES, TR_CELL = D171.ROLES, D171.LINES, D171.TR_CELL


def main():
    assert ROLES == R172.ROLES
    t0 = time.time()
    out = dict(source=D171.SRC, roles={k: list(v) for k, v in ROLES.items()}, s=str(MB.S_RAT),
               library=dict(has_uid=hasattr(MB.Obstacle, "uid") or "uid" in getattr(MB.Obstacle, "__slots__", ())))
    os.makedirs(os.path.join(BASE, "figs"), exist_ok=True)
    # ---- demo171 replay
    nd0 = MB.Node(ROLES, name="A168 BR139/TRH-25 as recorded")
    nd0.build_cores()
    r0 = nd0.assert_invariant(raise_on_fail=False)
    out["before"] = dict(ok=r0["ok"], checks={k: v["ok"] for k, v in r0["checks"].items()},
                         failures=r0["failures"], diagnostics=r0["diagnostics"])
    nd0.figure(os.path.join(BASE, "figs", "A168_BR139_TRH-25_before.svg"),
               title="A168 BR139/TRH-25 -- as recorded (unclipped) [A176 post-fix replay]")
    nd = MB.Node(ROLES, name="A168 BR139/TRH-25 normalised")
    t = time.time()
    nd.normalise(nsub=4, refine=3, verbose=False)
    r1 = nd.assert_invariant()
    out["after"] = dict(ok=r1["ok"], checks={k: v["ok"] for k, v in r1["checks"].items()},
                        kept=r1["kept"], sliver_area=r1["sliver_area"], diagnostics=r1["diagnostics"],
                        pieces={k: len(b.pieces) for k, b in nd.boxes.items()},
                        axis_a={k: float(b.core.a) for k, b in nd.boxes.items()},
                        poly_area={k: b.pc.area() for k, b in nd.boxes.items()},
                        stats=nd.stats, seconds=round(time.time() - t, 2))
    nd.figure(os.path.join(BASE, "figs", "A168_BR139_TRH-25_after.svg"),
              title="A168 BR139/TRH-25 -- after normalise (A171 rule, fixed library, A176)")
    out["chord_rows"] = nd.chord_rows(LINES)
    out["misses_cell_TR"] = {k: v["misses"] for k, v in nd.misses_cell(TR_CELL).items()}
    t = time.time()
    lane = nd.lane(TR_CELL, line=None, max_depth=24, max_open=600, deadline=time.time() + 120.0)
    out["lane_TR"] = dict(lane=lane["lane"], leaves=len(lane["leaves"]), open=len(lane["open"]),
                          depth=lane["depth"], reason=lane.get("reason"), seconds=round(time.time() - t, 2))
    print("demo171 replay: kept " + " ".join("%s=%.6f" % kv for kv in r1["kept"].items())
          + " rows " + " ".join("%s beta=%s" % (r["orient"], r["beta"]) for r in out["chord_rows"])
          + " lane=%s" % lane["lane"], flush=True)
    # ---- report172 replay (union / same-pieces / pieces)
    t = time.time()
    ndu = MB.Node(ROLES, name="A168 S2 union-hull K'")
    ndu.normalise(nsub=4, refine=3, kmode="union")
    out["union"] = R172.snap(ndu, time.time() - t)
    t = time.time()
    same, cache = {}, {}
    for k, mb in ndu.boxes.items():
        V, info, boxes = MB.pieces_poly(mb.pieces, cache=cache)
        same[k] = dict(area=float(MB.poly_area_frac(V)), nv=len(V), n_pieces=len(mb.pieces),
                       uncertified=len(MB.certify_verts(V, boxes)), shrink=info["shrink"])
    out["same_pieces"] = dict(K_area={k: v["area"] for k, v in same.items()}, detail=same,
                              seconds=round(time.time() - t, 2))
    t = time.time()
    ndp = MB.Node(ROLES, name="A168 S2 per-piece K'")
    ndp.normalise(nsub=4, refine=3)
    out["pieces"] = R172.snap(ndp, time.time() - t)
    # ---- the lonely clip on the same node (D at TR), the A176 setting
    t = time.time()
    ndl = MB.Node(ROLES, name="A168 S2 per-piece K' + lonely clip")
    ndl.normalise(nsub=4, refine=3, corners={"D": ("TR", MB.C_WIDEN)})
    out["pieces_lonely"] = R172.snap(ndl, time.time() - t)
    out["seconds"] = round(time.time() - t0, 2)
    p = os.path.join(BASE, "results", "rederive176.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, default=str)
    for m in ("union", "pieces", "pieces_lonely"):
        d = out[m]
        print("%-14s kept %s  K_area %s  pieces %s  passes %s inv %s  %.1fs" % (
            m, {k: round(v, 6) for k, v in d["kept"].items()}, {k: round(v, 6) for k, v in d["K_area"].items()},
            d["pieces"], d["passes"], d["invariant"], d["seconds"]), flush=True)
    print("wrote", p, out["seconds"], "s")


if __name__ == "__main__":
    main()
