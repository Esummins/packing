"""A188 T2(b) -- the FROZEN-CHAIN cross-check: A116's selection tree (and, on a DEAD verdict, A133's
t = tan(theta/2) generator + independent checker) on the S01 ROW neighbourhood, per frame.

The row N: the frame's pins + three FREE boxes for the row squares f1, f3, f4 of A107's S01
representative (the horizontal lock y in [1.190, 1.995], notes/s01_identity.json), anchored at s0
as A116 anchors (dilated by s0/s*), symmetric radius r and tilt half-width rho.  The LINE
certificate (s01cert188.py) says the true basin is unbounded along the row and 0.207 across at
ANY tilt; this run measures how far the general-purpose tree (Lemma RELAX's tilt-cell relaxation)
gets on the same object -- its refusals are WALL CAPS, not geometry.

    python tree188.py --cls trump5 --grid "0.1:10,0.2:10,0.2:20,0.3:20,0.4:45" --time-cap 300
    python tree188.py --cls trump5 --emit <id>        # t-emission + checker on a DEAD box set

Writes only under attempts/A188-s01-basin/{results,certs,logs}.  READ-ONLY elsewhere.
"""
from __future__ import annotations

import argparse, gzip, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
A116C = os.path.abspath(os.path.join(HERE, "..", "..", "A116-local-selection-tree", "code"))
sys.path.insert(0, A116C)
import blas1                                # noqa: E402,F401  (MUST precede numpy: one BLAS thread)
sys.path.insert(0, HERE)
import lib188 as L                          # noqa: E402
import a116lib as A                         # noqa: E402

S_STAR = 4.0
ROW = ("f1", "f3", "f4")


def s01_poses():
    d = json.load(open(os.path.join(L.NOTES, "s01_identity.json"), encoding="utf-8"))
    return {f["name"]: (f["x"], f["y"], math.radians(f["theta_deg"])) for f in d["free"]}


def bodies_for(cls, r, rho_deg, anchor_side=A.S0):
    P = s01_poses()
    lam = anchor_side / S_STAR
    rho = math.radians(rho_deg)
    bodies, nv = [], 1
    for n in ROW:
        x, y, t = P[n]
        x, y = x * lam, y * lam
        t = 0.0                                              # the row squares are axis-aligned
        bodies.append(A.Body(n, "free", x0=x - r, x1=x + r, y0=y - r, y1=y + r, t0=t - rho, t1=t + rho,
                             vi=nv, anchor=(x, y, t)))
        nv += 2
    for p in A.CLASS_PINS[cls]:
        ax, ay = A.slot_affine(p)
        bodies.append(A.Body(p, "pin", ax=ax, ay=ay, hh=A.PIN_SLACK, vi=nv,
                             anchor=(A.slot_xy(p, anchor_side)[0], A.slot_xy(p, anchor_side)[1], 0.0)))
        nv += 2
    for b in bodies:
        if b.kind == "free":
            b.ti = nv; nv += 1
    return bodies, nv


def boxlist(bodies):
    out = []
    for b in bodies:
        if b.kind == "free":
            out.append(dict(name=b.name, kind="free", x=[b.x0, b.x1], y=[b.y0, b.y1],
                            theta_deg=[math.degrees(b.t0), math.degrees(b.t1)],
                            anchor=[b.anchor[0], b.anchor[1], math.degrees(b.anchor[2])]))
        else:
            out.append(dict(name=b.name, kind="pin", ax=list(b.ax), ay=list(b.ay), hh=b.hh))
    return out


def run_one(cls, r, rho, time_cap, samples):
    t0 = time.time()
    bodies, nv = bodies_for(cls, r, rho)
    Pe = {b.name: b.anchor for b in bodies}
    ss = A.shadow_selections(bodies, Pe)
    T = A.Tree(bodies, nv, contact_pairs=list(ss), min_cell_deg=0.05, node_cap=2000000,
               time_cap=time_cap, target=A.S0 + 0.9 * (S_STAR - A.S0), tighten_cap=0)
    v = T.run()
    rec = dict(id="S01_%s_A188row_r%.2f_rho%.0f" % (cls, r, rho), tag="S01", cls=cls, r=r, rho_deg=rho,
               L=list(ROW), P=list(A.CLASS_PINS[cls]), tree=v, n_witnesses=len(T.witnesses),
               n_unresolved=len(T.unresolved), witnesses=T.witnesses[:2], boxes=boxlist(bodies),
               seconds_tree=round(time.time() - t0, 1))
    dead = bool(v["dead"]) and not v["capped"]
    if dead and samples:
        rec["sampling"] = A.sample_check(bodies, nv, n_samples=samples, seed=1)
    hits = rec.get("sampling", {}).get("hits", 0)
    rec["dead"] = bool(dead and hits == 0)
    rec["reason"] = ("CERTIFIED" if rec["dead"] else "WITNESS" if T.witnesses else
                     "SAMPLE_HIT" if hits else "WALL_CAP" if v["capped"] else "OPEN")
    rec["seconds"] = round(time.time() - t0, 1)
    return rec


def emit(rec, time_cap):
    """A163's pattern: A119-format meta -> A133 gen_local_t (t-parametrised, exact rationals) ->
    A133 check_local_t (independent checker); BASE re-pointed here, nothing under A133 written."""
    sys.path.insert(0, os.path.join(L.ATT, "A163-s02-other-frames", "code"))
    sys.path.insert(0, os.path.join(L.ATT, "A133-tan-half-emission", "code"))
    import gent163 as G163                   # noqa: E402  (read-only; meta_from_boxes)
    meta = G163.meta_from_boxes(rec["boxes"], rec["id"], rec["cls"],
                                dict(a188_tree_seconds=rec["seconds"], frame=rec["cls"]))
    meta["tag"] = "S01"
    meta["theorem"] = ("Theorem LOCAL (docs/proofs/local_certificate.md sec 3) on the S01 ROW "
                       "neighbourhood (docs/proofs/local_certificate_s01.md sec 4)")
    src = os.path.join(L.CERTS, rec["id"] + ".cert.json.gz")
    with gzip.open(src, "wt", encoding="utf-8") as f:
        json.dump(dict(meta=meta), f)
    import gen_local_t as GEN                # noqa: E402
    GEN.BASE = L.BASE
    GEN.A119CERT = L.CERTS

    class Args:
        pass
    ar = Args()
    ar.min_cell, ar.cap, ar.time_cap, ar.certdir = "1/5000", 900000, time_cap, L.CERTS
    t0 = time.time()
    GEN.run_one(rec["id"], ar)
    p = os.path.join(L.CERTS, rec["id"] + ".tcert.json.gz")
    out = dict(id=rec["id"], generator_seconds=round(time.time() - t0, 1), bytes=os.path.getsize(p))
    import check_local_t as CHK              # noqa: E402
    t1 = time.time()
    with gzip.open(p, "rt", encoding="utf-8") as f:
        cert = json.load(f)
    C_ = CHK.Checker(cert)
    ok = C_.run()
    out.update(checker_ok=bool(ok), checker_seconds=round(time.time() - t1, 1),
               sha256=CHK.sha256_of(p), n_leaves=len(C_.leaves), dead=bool(cert["meta"].get("dead")))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cls", required=True)
    ap.add_argument("--grid", default="0.1:10,0.2:10,0.2:20,0.3:20,0.4:45")
    ap.add_argument("--time-cap", type=float, default=300.0)
    ap.add_argument("--samples", type=int, default=3000)
    ap.add_argument("--emit", default=None)
    a = ap.parse_args()
    out = os.path.join(L.RES, "tree188_%s.jsonl" % a.cls)
    done = set()
    if os.path.exists(out):
        for line in open(out, encoding="utf-8"):
            done.add(json.loads(line)["id"])
    if a.emit:
        recs = [json.loads(x) for x in open(out, encoding="utf-8")]
        rec = [r for r in recs if r["id"] == a.emit and r.get("dead")][0]
        res = emit(rec, a.time_cap)
        with open(os.path.join(L.RES, "tcerts188.jsonl"), "a", encoding="utf-8") as fh:
            fh.write(json.dumps(res) + "\n")
        print(json.dumps(res), flush=True)
        return
    for cell in a.grid.split(","):
        r, rho = cell.split(":")
        r, rho = float(r), float(rho)
        rid = "S01_%s_A188row_r%.2f_rho%.0f" % (a.cls, r, rho)
        if rid in done:
            print("skip", rid, flush=True)
            continue
        rec = run_one(a.cls, r, rho, a.time_cap, a.samples)
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")
        print("%-38s %-10s certified_min=%s tree %.0fs nodes %s" % (
            rid, rec["reason"], rec["tree"].get("certified_min"), rec["seconds_tree"],
            rec["tree"]["stats"].get("nodes")), flush=True)


if __name__ == "__main__":
    main()
