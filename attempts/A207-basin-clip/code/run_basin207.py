"""A207 driver for the basins.  One process; the frozen verifiers run as ONE subprocess at a time (two processes total).
    python run_basin207.py --ext k6_28 --idx 3 --rc 0.01,0.02,0.03 --tdeg 2.5 [--lp-only] [--lp-time 600] [--cert-time 300]
    python run_basin207.py --cls k5_16 --cell "TR(1,0)" ...      (the (ext, idx) from slotmap207)
Rows: results/basin207.jsonl (slot, class, certificate, r_c, r_t, seconds, verdict); records results/nodes/<tag>.rec.json."""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import basin207 as B                                           # noqa: E402
import slotmap207 as SM                                        # noqa: E402

RES = os.path.join(B.OUT, "results", "basin207.jsonl")


def row(rec, cls=None, cell=None):
    r = dict(slot=cell, cls=cls, ext=rec["ext"], idx=rec["idx"], r_c=rec["r_c"], r_t_deg=round(rec["r_t_deg"], 4), t_r=rec["t_r"], a=rec["a"],
             verdict=rec["verdict"], tau=rec.get("tau"), converged=rec.get("converged"), lp_seconds=rec.get("lp_seconds"), certify=rec.get("certify"),
             certify_seconds=rec.get("certify_seconds"), param=rec.get("param"), param_seconds=rec.get("param_seconds"), param_g1=rec.get("param_g1"),
             window=rec.get("window"), c2=rec.get("c2"), certificate=rec.get("param_cert"), base_cert=(rec.get("cert") or {}).get("path"),
             margin=(rec.get("cert") or {}).get("margin"), seconds=rec.get("seconds"), tag=rec["tag"], when=time.strftime("%Y-%m-%d %H:%M:%S"))
    os.makedirs(os.path.dirname(RES), exist_ok=True)
    with open(RES, "a", encoding="utf-8") as f:
        f.write(json.dumps(r) + "\n")
    return r


def lp_only(ext, idx, rc, tdeg, lp_time, eps_geo):
    from fractions import Fraction as Fr
    B.lpbox.EPS_GEO = eps_geo
    rc, tr = Fr(rc), B.t_of_deg(tdeg)
    hyp, slots, a = B.basin_hyp(ext, idx, rc, tr)
    warm, used, _, _ = B.RM.build_warm(ext)
    t0 = time.time()
    res = B.solve_node(B.S0F, hyp, 11 - len(slots), sym_kind="C1", warm=warm, time_limit=lp_time, max_iter=4000, out=None, log=lambda *x: None, prune=0,
                       prune_cols=0, col_stop_iter=10 ** 6, col_stop_cov=1.002, max_cols_add=1200, max_rows_add=2500, fine_slack=99.0, alternate=True)
    return dict(ext=ext, idx=idx, r_c=float(rc), t_r=str(tr), r_t_deg=B.math.degrees(2 * B.math.atan(float(tr))), a=float(a), tau=res["tau"], converged=res["converged"],
                lp_seconds=round(time.time() - t0, 1), budget=11 - len(slots), verdict="LP-ONLY tau=%.4f" % res["tau"], tag="lp_%s_c%d_rc%s_t%s" % (ext, idx, rc, tr))


if __name__ == "__main__":
    B.belownormal()
    ap = argparse.ArgumentParser()
    ap.add_argument("--ext")
    ap.add_argument("--idx", type=int)
    ap.add_argument("--cls")
    ap.add_argument("--cell")
    ap.add_argument("--rc", required=True, help="comma-separated r_c values (rationals or decimals)")
    ap.add_argument("--tdeg", default="2.5", help="comma-separated tilt radii in degrees")
    ap.add_argument("--lp-only", action="store_true")
    ap.add_argument("--lp-time", type=float, default=600)
    ap.add_argument("--cert-time", type=float, default=300)
    ap.add_argument("--cert-rounds", type=int, default=3)
    ap.add_argument("--eps-geo", type=float, default=0.003)
    ap.add_argument("--depth", type=int, default=48)
    ap.add_argument("--stop-on-fail", action="store_true", help="ascending r_c: stop after the first non-basin")
    a = ap.parse_args()
    cls = cell = None
    if a.cls:
        d = SM.slot_map(a.cls)[a.cell]
        a.ext, a.idx, cls, cell = d["ext"], d["idx"], a.cls, a.cell
    for td in a.tdeg.split(","):
        for rc in a.rc.split(","):
            if a.lp_only:
                rec = lp_only(a.ext, a.idx, rc, td, a.lp_time, a.eps_geo)
                print(json.dumps(rec), flush=True)
                row(rec, cls, cell)
                continue
            rec = B.run(a.ext, a.idx, rc, td, lp_time=a.lp_time, cert_time=a.cert_time, cert_rounds=a.cert_rounds, eps_geo=a.eps_geo, depth=a.depth,
                        log=lambda *x: print(*x, flush=True))
            row(rec, cls, cell)
            if a.stop_on_fail and not rec["verdict"].startswith("BASIN"):
                break
