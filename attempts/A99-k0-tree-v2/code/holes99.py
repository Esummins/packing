"""A99 R1 diagnostic: are the "holes" of A85's FAILed certificates REAL coverage failures?

verify_case.make_witness samples an admissible placement inside an uncovered box and calls the
box a HOLE if that placement's exact mass is < 1 + margin.  It does NOT check whether the
placement itself is exempt (the box was not PROVABLY exempt, but a point inside it can still lie
in a core's SAT region or in a NO-family).  A hole at an exempt placement would be an artefact
and could still close by deeper splitting; a hole at a non-exempt placement is a real defect of
the certificate that no depth and no sub-box restriction can repair.

Exactness: the point test is `core_exempt_frac` / `nofam_exempt` (the frozen predicates) on the
degenerate box [t,t] x [cx,cx] x [cy,cy] -- for a single pose the SAT test is exact and the
"provably exempt over the whole box" caveat is empty.

LP-free, seconds.  Reads the witness files the R1 ladder wrote; writes results/r1_holes.json.
"""
import argparse, glob, json, os, sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
RES = os.path.join(BASE, "results")
WITD = os.path.join(BASE, "certs", "resolve99")
A85C = os.path.join(ROOT, "attempts", "A85-k0-route", "certs", "k0_00")
sys.path.insert(0, HERE)
import verify_case as V


def point_exempt(cores, nofams, t, cx, cy):
    for f in nofams:
        if V.nofam_exempt(f, t, t, cx, cx, cy, cy):
            return "nofam"
    for c in cores:
        if V.core_exempt_frac(c, t, t, cx, cx, cy, cy):
            return "core"
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pattern", default="*.d*.witnesses.json")
    ap.add_argument("--out", default="r1_holes.json")
    a = ap.parse_args()
    out = []
    for wf in sorted(glob.glob(os.path.join(WITD, a.pattern))):
        base = os.path.basename(wf)
        tag, rest = base.split(".d", 1)
        depth = int(rest.split(".")[0])
        cert = os.path.join(A85C, tag + ".json")
        if not os.path.exists(cert):
            continue
        try:
            d, s, n, atoms, weights, total = V.load_certificate(cert, None)
        except Exception as e:
            out.append(dict(tag=tag, depth=depth, error=repr(e)[:160]))
            continue
        cores, nofams = d["_cores"], d["_nofams"]
        W = json.load(open(wf))["witnesses"]
        rows = []
        for w in W:
            if w.get("kind") != "hole":
                continue
            p = w.get("placement")
            if not p:
                continue
            t, cx, cy = F(p["t"]), F(p["cx"]), F(p["cy"])
            ex = point_exempt(cores, nofams, t, cx, cy)
            # is the sampled placement admissible?  (h(theta) <= cx, cy <= s - h)
            c, sn = V.cos_sin_t(t)
            h = (c + sn) / 2
            adm = (h <= cx <= s - h) and (h <= cy <= s - h)
            rows.append(dict(exempt=ex, admissible=bool(adm), mass=w.get("exact_mass"),
                             float_mass=w.get("float_mass"),
                             theta_deg=p.get("theta_deg"), cx=p.get("cx_float"),
                             cy=p.get("cy_float")))
        out.append(dict(tag=tag, depth=depth, n_witness=len(W),
                        n_hole=len(rows),
                        n_hole_exempt=sum(1 for r in rows if r["exempt"]),
                        n_hole_inadmissible=sum(1 for r in rows if not r["admissible"]),
                        n_hole_real=sum(1 for r in rows if not r["exempt"] and r["admissible"]),
                        worst=min((r["float_mass"] for r in rows), default=None),
                        holes=rows[:40]))
        r = out[-1]
        print(f"{tag:44s} d{depth:3d} witnesses={r['n_witness']:4d} holes={r['n_hole']:4d} "
              f"exempt={r['n_hole_exempt']:4d} inadmissible={r['n_hole_inadmissible']:4d} "
              f"REAL={r['n_hole_real']:4d} worst_mass={r['worst']}", flush=True)
    json.dump(out, open(os.path.join(RES, a.out), "w"), indent=1)
    print("holes99 done", flush=True)


if __name__ == "__main__":
    main()
