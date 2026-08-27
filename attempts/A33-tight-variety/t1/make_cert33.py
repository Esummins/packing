"""
Build an exact measure-certificate JSON (format 'measure-certificate-v1') from an A33 field json.

  python make_cert33.py --field results/field_3.877084.json --s 969271/250000 --scale 1.008 \
                        --out certs/cert_3.877084_s1008.json [--n 12] [--jitter 3]

Difference from A07's make_cert.py: here the total mass is ABOVE 11 (we are certifying feasibility
of a guard field at a side where no field of mass < 11 exists), so the certificate's "n" field is
set to a value above the total (default 12) purely to pass verify_measure.py's total < n gate.
The mathematical content used by A33 is the verifier's feasibility statement:
    every closed unit square Q in [0,s]^2 has mu(Q) >= 1.
--jitter k: displace each orbit representative by k units of 1/DP in a deterministic
pseudo-random direction, to break exact atom-on-square-boundary tangencies (Goebel lesson).
"""
import argparse, json, math, hashlib
from fractions import Fraction as F


def d4_images(x, y, s):
    out = []
    for p in [(x, y), (s - x, y), (x, s - y), (s - x, s - y), (y, x), (s - y, x), (y, s - x), (s - y, s - x)]:
        if p not in out:
            out.append(p)
    return out


def build(field, s_rat, scale, DP=10**6, DW=10**6, n=12, jitter=0):
    s = F(s_rat)
    assert abs(float(s) - field["s"]) < 1e-9, f"s mismatch {float(s)} vs {field['s']}"
    atoms, weights, seen = [], [], {}
    n_jittered = n_orbit_mismatch = 0

    def snap(ix, iy):
        x, y = F(ix, DP), F(iy, DP)
        if x < 0: x = F(0)
        if y < 0: y = F(0)
        if 2 * x > s: x = s - x
        if 2 * y > s: y = s - y
        return x, y

    for (rx, ry, w, m) in field["orbits"]:
        if w <= 1e-11:
            continue
        ix0, iy0 = round(rx * DP), round(ry * DP)
        x, y = snap(ix0, iy0)
        imgs = d4_images(x, y, s)
        if len(imgs) != m:
            # rounding broke (or created) a symmetry coincidence; the LP cost of this orbit was
            # m*w, so a changed image count changes the mass. Record it.
            n_orbit_mismatch += 1
        if jitter:
            # jitter must preserve the orbit's stabiliser, else a 4- or 1-point orbit becomes an
            # 8-point one and the total mass jumps.  Accept a jitter only if the image count is
            # unchanged; otherwise keep the unjittered representative.
            h = int(hashlib.sha256(f"{ix0},{iy0}".encode()).hexdigest()[:16], 16)
            dx = (h % (2 * jitter + 1)) - jitter
            dy = ((h >> 8) % (2 * jitter + 1)) - jitter
            if ix0 == iy0:                 # on the diagonal: move along it
                dy = dx
            xj, yj = snap(ix0 + dx, iy0 + dy)
            imj = d4_images(xj, yj, s)
            if len(imj) == len(imgs):
                x, y, imgs = xj, yj, imj
                n_jittered += 1
        wq = F(math.ceil(w * scale * DW), DW)      # round UP
        for p in imgs:
            if p in seen:
                weights[seen[p]] += wq
            else:
                seen[p] = len(atoms)
                atoms.append(p); weights.append(wq)
    total = sum(weights, F(0))
    cert = dict(format="measure-certificate-v1", n=n, s=str(s),
                atoms=[[str(p[0]), str(p[1])] for p in atoms],
                weights=[str(w) for w in weights], total=str(total),
                claim=(f"FEASIBILITY certificate: every closed unit square Q in [0,{s}]^2 satisfies "
                       f"mu(Q) >= 1 for this atomic measure of exact total mass {total} "
                       f"(~{float(total):.9f}).  n={n} is a dummy above the total, present only to "
                       f"pass verify_measure.py's total<n gate; NO lower bound on s(11) is claimed."),
                provenance=dict(attempt="A33-tight-variety/t1", method=(
                    "A07 double cutting-plane LP (row generation over placements, column generation "
                    "over free atoms, HiGHS, D4); orbit representatives rounded to 1/%d%s, weights "
                    "scaled by %.6f and rounded up to 1/%d; LP rows use eps-shrunk squares "
                    "(EPS_GEO=1e-4) for robustness." % (DP, f" and jittered by <= {jitter}/{DP}" if jitter else "", scale, DW)),
                    lp_tau=field.get("tau"), eps_geo=field.get("eps_geo"),
                    oracle_residuals=field.get("oracle_residuals"),
                    scale=scale, jitter=jitter, n_jittered=n_jittered,
                    n_orbit_size_mismatch=n_orbit_mismatch,
                    eta_float=(field.get("tau", 0) - 11)))
    return cert


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--field", required=True)
    ap.add_argument("--s", required=True)
    ap.add_argument("--scale", type=float, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--DP", type=int, default=10**6)
    ap.add_argument("--DW", type=int, default=10**6)
    ap.add_argument("--jitter", type=int, default=0)
    a = ap.parse_args()
    field = json.load(open(a.field))
    cert = build(field, a.s, a.scale, DP=a.DP, DW=a.DW, n=a.n, jitter=a.jitter)
    json.dump(cert, open(a.out, "w"), indent=0)
    t = F(cert["total"])
    print(f"atoms {len(cert['atoms'])} total {cert['total']} = {float(t):.9f} "
          f"eta_cert {float(t) - 11:.9f} (scale {a.scale}, field tau {field.get('tau'):.6f}, "
          f"eta_float {field.get('tau') - 11:.6f}, margin_cost {float(t) - field.get('tau'):.6f})")
