"""A99 R2, arbiter leg: run the FROZEN kill chain (tree85.kill -> LP -> certify.py ->
verify_case.py, with A85's eps_geo 0.002/0.004 repair) on the level-1 cells that the R2 LP
screen ranked best under the 3-shallow pattern.

The screen's tau at 300 s is NOT a verdict (minmass is still 0.2-0.5 there); this leg is the only
place in A99 where a KILL may be claimed, and the arbiter is the frozen verifier.

Canary, commit gate, budget assert (11 - #cores == budget) and the images_realizing refusal are
tree85's, untouched.
"""
import argparse, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import blas1  # noqa: F401
from caselp import Box
import tree85 as T
import pilot59 as P
import o3fam
import r2_99

RES = os.path.join(BASE, "results")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", default=None)
    ap.add_argument("--auto-best", type=int, default=0,
                    help="pick the N cells with the lowest screened tau under --pattern")
    ap.add_argument("--pattern", default="sh3")
    ap.add_argument("--delta", type=float, default=0.3)
    ap.add_argument("--lp-time", type=float, default=900.0)
    ap.add_argument("--cert-time", type=float, default=300.0)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--out", default="r2_certify.jsonl")
    a = ap.parse_args()

    T.setup("k0_00")
    warm, used = r2_99.warm_pool()
    P.PILOT_WARM = dict(atoms=list(warm["atoms"]), rows=[])
    P.PILOT_SEEN = {(round(x, 7), round(y, 7)) for (x, y) in warm["atoms"]}
    F, a_val, nfam = r2_99.fams_for(a.delta, True)
    cells = {c["idx"]: c for c in r2_99.l1_cells()}
    sink = T.Sink("a99_r2_certify.jsonl", "a99_r2_certify.log")
    outp = os.path.join(RES, a.out)
    if a.auto_best:
        rows = []
        for fn in ("r2_screen.jsonl", "r2_patterns.jsonl"):
            fp = os.path.join(RES, fn)
            if not os.path.exists(fp):
                continue
            for ln in open(fp):
                try:
                    r = json.loads(ln)
                except Exception:
                    continue
                if r.get("pattern") == a.pattern and r.get("tau") is not None:
                    rows.append(r)
        rows.sort(key=lambda r: r["tau"])
        chosen = [r["idx"] for r in rows[:a.auto_best]]
        print("auto-best %s: %s (tau %s)" % (a.pattern, chosen,
                                             [round(r["tau"], 4) for r in rows[:a.auto_best]]),
              flush=True)
    else:
        chosen = [int(x) for x in a.cells.split(",")]
    for idx in chosen:
        c = cells[idx]
        b = Box.from_json(c["box"])
        nofams = o3fam.nofams_for(r2_99.PATTERNS[a.pattern], F)
        tag = "l1_%03d_%s_d%g" % (idx, a.pattern, a.delta)
        t0 = time.time()
        rec = T.kill(sink, tag, b, [], nofams, 10,
                     dict(group="A99-R2", level="A38-l1", pattern=a.pattern, delta=a.delta,
                          a=None, at=None, kind="YES", depth_j=0,
                          a99_cell=idx, a99_a=a_val, a99_nofams=len(nofams),
                          a38_status=c["a38_status"], a38_tau=c["a38_tau"]),
                     lp_time=a.lp_time, cert_time=a.cert_time, depth=a.depth, jobs=a.jobs)
        out = dict(cell=idx, pattern=a.pattern, delta=a.delta, a=a_val, n_nofams=len(nofams),
                   wall_s=round(time.time() - t0, 1),
                   record=(rec if isinstance(rec, dict) else None))
        with open(outp, "a") as fh:
            fh.write(json.dumps(out) + "\n")
        v = (rec or {}).get("verdict")
        print(f"  cell {idx} {a.pattern} -> {v}  tau={(rec or {}).get('tau')} "
              f"eta={(rec or {}).get('eta')} {out['wall_s']}s", flush=True)
    print("r2_certify done", flush=True)


if __name__ == "__main__":
    main()
