"""A160 -- re-emit one of this attempt's boxes through A133's t = tan(theta/2) generator and its
INDEPENDENT rational checker, so the object is in the same frozen format as the YES leaf A136 cites.

A133's `gen_local_t.py` and `check_local_t.py` are IMPORTED UNCHANGED and their module-level `BASE`
(the destination of every write) is re-pointed into this attempt, exactly as A151's `gen_t151.py`
does, so nothing under `attempts/A133-*` or `attempts/A119-*` is written.  The source is an
A119-format meta file written here from a chain link's own box list (`--from-chain`), from a slice
(`--from-slice`), or from a spec file (`--spec`).

    python gent160.py --from-chain results/chain_<label>.jsonl --offset 0.0 --id S02_k5_11_A160chain_p000
    python gent160.py --spec results/spec_F0.json --id S02_k5_11_A160f0
      [--check] [--time-cap 700] [--min-cell 1/5000]

READ-ONLY on every campaign and prior attempt.
"""
from __future__ import annotations

import argparse, gzip, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib160 as L                       # noqa: E402
import a116lib as A                      # noqa: E402

ROOT = L.ROOT
A133C = os.path.join(ROOT, "attempts", "A133-tan-half-emission", "code")
sys.path.insert(0, A133C)
CERTS = L.CERTS


def meta_from_boxes(boxes, eid, note):
    out, nv = [], 1
    free = [b for b in boxes if b["kind"] == "free"]
    pins = [b for b in boxes if b["kind"] == "pin"]
    for b in free:
        out.append(dict(name=b["name"], kind="free", vi=nv, ti=None,
                        x0=b["x"][0], x1=b["x"][1], y0=b["y"][0], y1=b["y"][1],
                        t0=math.radians(b["theta_deg"][0]), t1=math.radians(b["theta_deg"][1]),
                        anchor=[b["anchor"][0], b["anchor"][1], math.radians(b["anchor"][2])]))
        nv += 2
    for b in pins:
        out.append(dict(name=b["name"], kind="pin", vi=nv, ax=list(b["ax"]), ay=list(b["ay"]),
                        hh=b["hh"]))
        nv += 2
    for d in out:
        if d["kind"] == "free":
            d["ti"] = nv
            nv += 1
    return dict(id=eid, tag=L.TAG, cls=L.CLS,
                r=max(max(0.5 * (b["x"][1] - b["x"][0]), 0.5 * (b["y"][1] - b["y"][0]))
                      for b in free),
                rho_deg=max(0.5 * (b["theta_deg"][1] - b["theta_deg"][0]) for b in free),
                asymmetric=True, chain_note=note,
                cut_deg=None, pin_slack=A.PIN_SLACK, anchor_side=A.S0,
                s_lo=L.S_LO, s_hi=L.S_HI, s0=[969271, 250000], kill_margin=1e-08,
                multiplier_denominator="2^40", nv=nv,
                L=[b["name"] for b in free], P=[b["name"] for b in pins],
                generated=time.strftime("%Y-%m-%dT%H:%M:%S"),
                generator="attempts/A160-s02-f0-slide/code/gent160.py (A119 meta layout; the tree "
                          "is rebuilt from scratch by A133's gen_local_t.py in exact rationals)",
                theorem="Theorem LOCAL (docs/proofs/local_certificate.md sec 3), ASYMMETRIC N, "
                        "MOVED ANCHORS (A160's common-tilt chain link)",
                bodies=out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True)
    ap.add_argument("--from-chain", default=None)
    ap.add_argument("--from-slice", default=None)
    ap.add_argument("--offset", type=float, default=0.0)
    ap.add_argument("--slice-d2", type=float, default=0.0)
    ap.add_argument("--slice-d3", type=float, default=0.0)
    ap.add_argument("--spec", default=None)
    ap.add_argument("--min-cell", default="1/5000")
    ap.add_argument("--cap", type=int, default=900000)
    ap.add_argument("--time-cap", type=float, default=700.0)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    os.makedirs(CERTS, exist_ok=True)

    note = None
    if a.from_chain:
        boxes = None
        for line in open(a.from_chain, encoding="utf-8"):
            r = json.loads(line)
            if r.get("dead") and abs(r.get("offset_deg", 1e9) - a.offset) < 1e-9:
                boxes, note = r["boxes"], dict(kind="chain", offset_deg=r["offset_deg"],
                                               tilt_deg=r["tilt_deg"], s_star=r["s_star"],
                                               half_deg=r["half_deg"], r_xy=r["r_xy"])
        if boxes is None:
            raise SystemExit("no certified link at offset %s in %s" % (a.offset, a.from_chain))
    elif a.from_slice:
        boxes = None
        for line in open(a.from_slice, encoding="utf-8"):
            r = json.loads(line)
            if (r.get("dead") and abs(r["d2"] - a.slice_d2) < 1e-9
                    and abs(r["d3"] - a.slice_d3) < 1e-9):
                boxes, note = r["boxes"], dict(kind="slice", d2=r["d2"], d3=r["d3"],
                                               half_deg=r["half_deg"])
        if boxes is None:
            raise SystemExit("no certified slice (%s, %s)" % (a.slice_d2, a.slice_d3))
    else:
        spec = json.load(open(a.spec, encoding="utf-8"))
        boxes, note = L.boxlist(spec), dict(kind="spec", file=os.path.basename(a.spec))

    meta = meta_from_boxes(boxes, a.id, note)
    src = os.path.join(CERTS, a.id + ".cert.json.gz")
    with gzip.open(src, "wt", encoding="utf-8") as f:
        json.dump(dict(meta=meta), f)
    print("wrote source", src)
    for b in meta["bodies"]:
        if b["kind"] == "free":
            print("  %-8s x[%.6f,%.6f] y[%.6f,%.6f] theta[%.4f,%.4f] deg"
                  % (b["name"], b["x0"], b["x1"], b["y0"], b["y1"],
                     math.degrees(b["t0"]), math.degrees(b["t1"])))

    import gen_local_t as GEN               # noqa: E402  (A133, imported read-only)
    GEN.BASE = L.BASE
    GEN.A119CERT = CERTS

    class Args:
        pass
    ar = Args()
    ar.min_cell, ar.cap, ar.time_cap, ar.certdir = a.min_cell, a.cap, a.time_cap, CERTS
    GEN.run_one(a.id, ar)

    if a.check:
        import check_local_t as CHK          # noqa: E402  (A133, imported read-only)
        p = os.path.join(CERTS, a.id + ".tcert.json.gz")
        t0 = time.time()
        with gzip.open(p, "rt", encoding="utf-8") as f:
            cert = json.load(f)
        C_ = CHK.Checker(cert)
        ok = C_.run()
        rec = dict(file=os.path.basename(p), id=cert["meta"]["id"], ok=bool(ok),
                   sha256=CHK.sha256_of(p), seconds=round(time.time() - t0, 1),
                   bytes=os.path.getsize(p), counts=dict(C_.n), n_leaves=len(C_.leaves),
                   certified_min=(None if C_.min_bound is None else str(C_.min_bound)),
                   certified_min_float=(None if C_.min_bound is None else float(C_.min_bound)),
                   s0=float(CHK.S0), n_errors=len(C_.errors), errors=C_.errors[:5],
                   checker="attempts/A133-tan-half-emission/code/check_local_t.py (imported)")
        print("%-40s %s leaves %-6d rows %-7d implied %-7d min %s  %.1f s"
              % (rec["id"], "VALID  " if ok else "INVALID(%d)" % len(C_.errors),
                 len(C_.leaves), C_.n["rows"], C_.n["rows_implied"],
                 ("%.10f" % rec["certified_min_float"]) if C_.min_bound is not None else "-",
                 rec["seconds"]))
        rp = os.path.join(L.RES, "check_local_t160.json")
        prev = json.load(open(rp, encoding="utf-8")).get("runs", []) if os.path.exists(rp) else []
        json.dump(dict(when=time.strftime("%Y-%m-%dT%H:%M:%S"), runs=[rec] + prev),
                  open(rp, "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
