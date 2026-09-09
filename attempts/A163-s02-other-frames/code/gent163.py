"""A163 T1(b) -- re-emit a re-framed box set through A133's t = tan(theta/2) generator and its
INDEPENDENT rational checker, so the object is in the same frozen format as the YES leaf A136 cites.

A133's `gen_local_t.py` and `check_local_t.py` are IMPORTED UNCHANGED and their module-level `BASE`
(the destination of every write) is re-pointed into this attempt, exactly as A151's `gen_t151.py` and
A160's `gent160.py` do, so nothing under `attempts/A133-*`, `A151-*`, `A160-*` is written.  The
source is an A119-format meta file written here from one record of this attempt's own tree run --
i.e. from A160's absolute boxes with k5_16's or trump5's pins.

    python gent163.py --cls k5_16 --key "000|S02_k5_11_A160chain_..." [--check] [--time-cap 700]
    python gent163.py --cls k5_16 --pick central --check          # the central box set of the frame

READ-ONLY on every campaign and prior attempt.
"""
from __future__ import annotations

import argparse, gzip, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib163 as L                       # noqa: E402
import a116lib as A                      # noqa: E402

A133C = os.path.join(L.ROOT, "attempts", "A133-tan-half-emission", "code")
sys.path.insert(0, A133C)


def new_id(cls, key):
    """S02_<cls>_A163<the A160 object's own name>."""
    src = key.split("|", 1)[1] if "|" in key else key
    return ("S02_%s_A163" % cls) + src.replace("S02_k5_11_A160", "").replace("S02_k5_11_", "")


def meta_from_boxes(boxes, eid, cls, note):
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
    return dict(id=eid, tag=L.TAG, cls=cls,
                r=max(max(0.5 * (b["x"][1] - b["x"][0]), 0.5 * (b["y"][1] - b["y"][0]))
                      for b in free),
                rho_deg=max(0.5 * (b["theta_deg"][1] - b["theta_deg"][0]) for b in free),
                asymmetric=True, reframe_note=note,
                cut_deg=None, pin_slack=A.PIN_SLACK, anchor_side=A.S0,
                s_lo=L.S_LO, s_hi=L.S_HI, s0=[969271, 250000], kill_margin=1e-08,
                multiplier_denominator="2^40", nv=nv,
                L=[b["name"] for b in free], P=[b["name"] for b in pins],
                generated=time.strftime("%Y-%m-%dT%H:%M:%S"),
                generator="attempts/A163-s02-other-frames/code/gent163.py (A119 meta layout; the "
                          "tree is rebuilt from scratch by A133's gen_local_t.py in exact rationals)",
                theorem="Theorem LOCAL (docs/proofs/local_certificate.md sec 3), ASYMMETRIC N, "
                        "A160's absolute boxes in %s's frame (A163)" % cls,
                bodies=out)


def pick(records, how):
    if how == "central":
        for r in records:
            if r["id"].endswith("h1.25_nof0_+00.00"):
                return r
    if how == "widest":
        return max(records, key=lambda r: (r.get("tree") or {}).get("rows", 0) or r["seconds"])
    if how == "cheapest":
        return min(records, key=lambda r: r["seconds"])
    raise SystemExit("unknown --pick %s" % how)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cls", required=True)
    ap.add_argument("--tree", default=None)
    ap.add_argument("--key", default=None)
    ap.add_argument("--pick", default=None)
    ap.add_argument("--min-cell", default="1/5000")
    ap.add_argument("--cap", type=int, default=900000)
    ap.add_argument("--time-cap", type=float, default=700.0)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--keep", action="store_true", help="keep the .tcert.json.gz (default: keep)")
    a = ap.parse_args()
    tree = a.tree or os.path.join(L.RES, "tree_%s.jsonl" % a.cls)
    recs = [json.loads(x) for x in open(tree, encoding="utf-8")]
    recs = [r for r in recs if r.get("dead")]
    if a.key:
        rec = [r for r in recs if r.get("key") == a.key or r["id"] == a.key]
        if not rec:
            raise SystemExit("no certified record %s in %s" % (a.key, tree))
        rec = rec[0]
    else:
        rec = pick(recs, a.pick or "central")
    eid = new_id(a.cls, rec.get("key", rec["id"]))
    note = dict(a160_id=rec["id"], a160_index=rec.get("a160_index"), family=rec.get("family"),
                a116_tree_seconds=rec["seconds"], frame=a.cls,
                a160_frame_verdict=rec.get("a160_verdict"))
    meta = meta_from_boxes(rec["boxes"], eid, a.cls, note)
    src = os.path.join(L.CERTS, eid + ".cert.json.gz")
    with gzip.open(src, "wt", encoding="utf-8") as f:
        json.dump(dict(meta=meta), f)
    print("source %s\n  L %s\n  P %s" % (src, meta["L"], meta["P"]), flush=True)

    import gen_local_t as GEN               # noqa: E402  (A133, imported read-only)
    GEN.BASE = L.BASE
    GEN.A119CERT = L.CERTS

    class Args:
        pass
    ar = Args()
    ar.min_cell, ar.cap, ar.time_cap, ar.certdir = a.min_cell, a.cap, a.time_cap, L.CERTS
    t0 = time.time()
    GEN.run_one(eid, ar)
    gen_s = time.time() - t0

    p = os.path.join(L.CERTS, eid + ".tcert.json.gz")
    with gzip.open(p, "rt", encoding="utf-8") as f:
        tmeta = json.load(f)["meta"]
    rec_out = dict(id=eid, cls=a.cls, source_id=rec["id"], key=rec.get("key"),
                   family=rec.get("family"), dead=bool(tmeta.get("dead")),
                   generator_seconds=round(gen_s, 1), bytes=os.path.getsize(p),
                   L=tmeta["L"], P=tmeta["P"], min_cell_t=tmeta.get("min_cell_t"))
    if a.check:
        import check_local_t as CHK          # noqa: E402  (A133, imported read-only)
        t1 = time.time()
        with gzip.open(p, "rt", encoding="utf-8") as f:
            cert = json.load(f)
        C_ = CHK.Checker(cert)
        ok = C_.run()
        rec_out.update(checker_ok=bool(ok), checker_seconds=round(time.time() - t1, 1),
                       sha256=CHK.sha256_of(p), n_leaves=len(C_.leaves), counts=dict(C_.n),
                       certified_min=(None if C_.min_bound is None else str(C_.min_bound)),
                       certified_min_float=(None if C_.min_bound is None
                                            else float(C_.min_bound)),
                       n_errors=len(C_.errors), errors=C_.errors[:5],
                       checker="attempts/A133-tan-half-emission/code/check_local_t.py (imported)")
        print("%-52s %s leaves %-6d min %s  %.1f s"
              % (eid, "VALID  " if ok else "INVALID(%d)" % len(C_.errors), len(C_.leaves),
                 ("%.10f" % rec_out["certified_min_float"]) if C_.min_bound is not None else "-",
                 rec_out["checker_seconds"]), flush=True)
    rp = os.path.join(L.RES, "tcerts163.json")
    prev = json.load(open(rp, encoding="utf-8")).get("runs", []) if os.path.exists(rp) else []
    json.dump(dict(when=time.strftime("%Y-%m-%dT%H:%M:%S"), runs=[rec_out] + prev),
              open(rp, "w", encoding="utf-8"), indent=1)
    print("recorded", rp, flush=True)


if __name__ == "__main__":
    main()
