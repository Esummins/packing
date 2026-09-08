"""A151 -- write an A119-format source certificate (meta only) for an A151 spec, so that A133's
`gen_local_t.py` can re-emit the neighbourhood in t = tan(theta/2) with exact rational enclosures.

    python mk_a119_src.py --spec results/spec_combined.json --id S02_k5_11_A151asym \
                          --certdir certs

`gen_local_t.run_one` reads ONLY `meta` from the source file (the bodies, `nv`, `s_lo`, `s_hi`,
`tag`, `cls`, `r`, `rho_deg`, `L`, `P`) and rebuilds the tree from scratch, so a meta-only file is
a complete input.  The field layout is copied verbatim from A119's
`certs/S02_k5_11_r0.20_rho10.cert.json.gz` (same variable indices, same pin affine form).

READ-ONLY on A119/A133: their files are read, never written.
"""
from __future__ import annotations
import argparse, gzip, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "attempts", "A116-local-selection-tree", "code"))
sys.path.insert(0, HERE)
import a116lib as A     # noqa: E402
import a151grow as G    # noqa: E402

S_LO, S_HI = 3.82, 3.897084


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--id", required=True)
    ap.add_argument("--certdir", default=os.path.join(BASE, "certs"))
    a = ap.parse_args()
    os.makedirs(a.certdir, exist_ok=True)
    spec = G.base_spec()
    spec.update(json.load(open(a.spec, encoding="utf-8")))
    bodies, nv, s_sh, P = G.bodies_for(spec)
    out = []
    for b in bodies:
        if b.kind == "free":
            out.append(dict(name=b.name, kind="free", vi=b.vi, ti=b.ti,
                            x0=b.x0, x1=b.x1, y0=b.y0, y1=b.y1, t0=b.t0, t1=b.t1,
                            anchor=list(b.anchor)))
        else:
            out.append(dict(name=b.name, kind="pin", vi=b.vi,
                            ax=list(b.ax), ay=list(b.ay), hh=b.hh))
    meta = dict(id=a.id, tag=G.TAG, cls=G.CLS,
                r=max(max(s["x"], s["y"]) for s in spec.values()),
                rho_deg=max(s["t"] for s in spec.values()),
                asymmetric=True, spec=spec,
                cut_deg=None, pin_slack=A.PIN_SLACK, anchor_side=A.S0,
                s_lo=S_LO, s_hi=S_HI, s0=[969271, 250000], kill_margin=1e-08,
                multiplier_denominator="2^40", nv=nv,
                L=[b.name for b in bodies if b.kind == "free"],
                P=[b.name for b in bodies if b.kind == "pin"],
                generated=time.strftime("%Y-%m-%dT%H:%M:%S"),
                generator="attempts/A151-pinwheel-basin/code/mk_a119_src.py "
                          "(A119 meta layout; the tree is rebuilt by A133's gen_local_t.py)",
                theorem="Theorem LOCAL (docs/proofs/local_certificate.md sec 3), ASYMMETRIC N",
                bodies=out)
    path = os.path.join(a.certdir, a.id + ".cert.json.gz")
    with gzip.open(path, "wt", encoding="utf-8") as f:
        json.dump(dict(meta=meta), f)
    print("wrote", path)
    for b in out:
        if b["kind"] == "free":
            print("  %-8s x[%.6f,%.6f] y[%.6f,%.6f] theta[%.3f,%.3f] deg"
                  % (b["name"], b["x0"], b["x1"], b["y0"], b["y1"],
                     math.degrees(b["t0"]), math.degrees(b["t1"])))


if __name__ == "__main__":
    main()
