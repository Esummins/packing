#!/usr/bin/env python
# -*- coding: ascii -*-
"""emit81.py -- A81: assemble the k4_08 beta=1 candidate certificate in the v2.1 form
(pair-certificate-v2 fields + the `urow` block = Lemma U-ROW spec-side data) from a
pairlp_u.py primal, and run the per-run canaries:

  (1) A71 canary_trump: the dilated Trump family is an exact trump5 death witness at these
      parameters (delta slack cores, eps_box widening) -- the machinery cannot cross
      trump5's threshold (results/canary_trump.json);
  (2) U-row canary: each compatible image's dilated free-square poses lie in their own
      zones (all C(7,2) = 21 image pairs are discounted -- the row EXCLUDES exactly the
      pure image family, whose widened-box pair value 21 + 7 = 28 saturates the boosted
      threshold), and the exclusion is consumed ONLY through Lemma U-ROW's exact-stratum
      skeleton mismatch: Trump (skeleton trump5) is outside the k4_08 exact stratum, so
      the row never binds him (results/canary_urow.json).

Zones in the certificate: closed (t, cx, cy) boxes of half-widths (r_t, r_c) about the
EXACT image poses (crowdfam rationals; diag = exact reflection t -> (1-t)/(1+t)); an
upright pose carries BOTH tilt branches ([0, r_t] and [1 - r_t, 1], the mod-pi/2
equivalence of theorem_u.md 3, the second branch conservatively narrow).
"""
import argparse
import json
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(BASE, "..", ".."))
A71 = os.path.join(REPO, "attempts", "A71-pair-emission")
sys.path.insert(0, os.path.join(A71, "code"))

S0 = Fr(969271, 250000)
BOXSPEC = os.path.join(REPO, "attempts", "A65-low-k-closure", "results", "h10_boxspec.json")
CROWDFAM = os.path.join(REPO, "attempts", "A65-low-k-closure", "results", "crowdfam.json")


def frs(x):
    return str(Fr(x))


def canary_trump(log_path, delta, eps_box):
    import emitk408 as ek
    import emitlib as el
    el.BASE = BASE
    ek.el.BASE = BASE
    fh = open(log_path, "a")
    ok = ek.canary_trump(fh, delta=delta, eps_box=eps_box)
    fh.close()
    return ok


def image_poses(name):
    """exact (t, cx, cy) of the 7 free-square poses of image g at s0."""
    fam = json.load(open(CROWDFAM))["classes"]["k4_08"]["family"]
    P = [(Fr(f["t"]), Fr(f["cx"]), Fr(f["cy"])) for f in fam]
    if name == "id":
        return P
    if name == "diag":
        out = []
        for (t, cx, cy) in P:
            tt = (1 - t) / (1 + t) if t > Fr(1, 5) else -t
            out.append((tt, cy, cx))
        return out
    raise ValueError(name)


def zone_boxes(poses, r_t, r_c):
    """per slot j: one or two closed (t,cx,cy) boxes.  A pose with |t| <= r_t is an
    upright: branch A = [0, r_t] (covers t >= 0 and, via t -> -t equivalence at the
    upright, the tiny negative tilts) and branch B = [1 - r_t, 1]."""
    zs = []
    for j, (t, cx, cy) in enumerate(poses):
        cbox = dict(x0=cx - r_c, x1=cx + r_c, y0=cy - r_c, y1=cy + r_c)
        if abs(t) <= r_t:
            zs.append(dict(slot=j, t0=Fr(0), t1=r_t, **cbox))
            zs.append(dict(slot=j, t0=1 - r_t, t1=Fr(1), **cbox))
        else:
            zs.append(dict(slot=j, t0=max(Fr(0), t - r_t), t1=min(Fr(1), t + r_t), **cbox))
    return zs


def sq_geom(t):
    C = (1 - t * t) / (1 + t * t)
    S = 2 * t / (1 + t * t)
    return C, S, abs(C) + abs(S)


def meets_box(t, cx, cy, bx, by, h):
    C, S, w = sq_geom(t)
    dx, dy = cx - bx, cy - by
    return (abs(dx) < h + w / 2 and abs(dy) < h + w / 2
            and abs(dx * C + dy * S) < Fr(1, 2) + h * w and abs(-dx * S + dy * C) < Fr(1, 2) + h * w)


def core_free(t, cx, cy, kx, ky, a):
    C, S, w = sq_geom(t)
    dx, dy = cx - kx, cy - ky
    return (abs(dx) >= a + w / 2 or abs(dy) >= a + w / 2
            or abs(dx * C + dy * S) >= Fr(1, 2) + a * w or abs(-dx * S + dy * C) >= Fr(1, 2) + a * w)


def contained(t, cx, cy):
    _, _, w = sq_geom(t)
    return cx - w / 2 >= 0 and cy - w / 2 >= 0 and cx + w / 2 <= S0 and cy + w / 2 <= S0


def in_zone(t, cx, cy, z):
    return z["x0"] <= cx <= z["x1"] and z["y0"] <= cy <= z["y1"] and z["t0"] <= t <= z["t1"]


def canary_urow(cert, images, zones_by_image, cap, gammas, boxes, cores, fh):
    """exact-rational checks; the row excludes exactly the pure image families."""
    out = dict(rung=cert["urow"]["rung"], cap=cap, images={})
    ok_all = True
    for name in images:
        poses = image_poses(name)
        zs = zones_by_image[name]
        # the exact pose is in the certificate's t-domain: negative upright tilts map to
        # the t -> 1 branch; check membership of the pose's [0,1]-representative
        n_in, slots = 0, set()
        for (t, cx, cy) in poses:
            tr = t if t >= 0 else (1 - abs(t)) / (1 + abs(t))     # theta+pi/2 branch
            hit = [z["slot"] for z in zs if in_zone(tr, cx, cy, z)]
            if hit:
                n_in += 1
                slots |= set(hit)
        cf = all(all(core_free(t, cx, cy, kx, ky, a) for (kx, ky, a) in cores)
                 for (t, cx, cy) in poses)
        ct = all(contained(t, cx, cy) for (t, cx, cy) in poses)
        m2 = 0
        for i in range(len(poses)):
            for j in range(i + 1, len(poses)):
                m2 += sum(1 for (bx, by, h) in boxes
                          if meets_box(*poses[i], bx, by, h) and meets_box(*poses[j], bx, by, h))
        npairs = len(poses) * (len(poses) - 1) // 2
        g = gammas[name]
        rec = dict(n_poses=len(poses), n_in_zone=n_in, distinct_slots=len(slots),
                   all_core_free=cf, all_contained=ct, family_sum_m2_widened=m2,
                   family_pair_value=21 + m2, discounted_family_value=str(21 + m2 - npairs * g),
                   n_discounted_pairs=npairs, cap=cap,
                   row_excludes_pure_family=bool(npairs > cap), gamma=str(g))
        ok = (n_in == len(poses) and len(slots) == len(poses) and cf and ct and npairs > cap)
        rec["ok"] = ok
        ok_all &= ok
        out["images"][name] = rec
        fh.write("CANARY U-row %s: in-zone %d/%d (slots %d) core_free=%s contained=%s "
                 "Sigma m2(widened)=%d -> family value %d; discounted %s; row excludes pure "
                 "family (%d pairs > cap %d): %s\n"
                 % (name, n_in, len(poses), len(slots), cf, ct, m2, 21 + m2,
                    rec["discounted_family_value"], npairs, cap, ok))
    thr = Fr(28) - sum(gammas[n] * cap for n in images)
    out["threshold_discounted"] = str(thr)
    out["W2"] = cert["total"]
    out["P1_ok"] = bool(Fr(cert["total"]) < thr)
    out["verdict"] = (("SAFE: every U-row discounts exactly the pairs of its own image family "
                       "(all poses in-zone, 21 pairs > cap); the family's widened-box value 28 "
                       "saturates the boosted threshold, so the ONLY thing the row removes is "
                       "Trump's image on the exact-k4_08 stratum, consumed through Lemma "
                       "U-ROW's skeleton mismatch (g.zhat has five simple squares); Trump "
                       "(skeleton trump5) is outside the quantifier and is never bound")
                      if ok_all else "CHECK FAILED -- investigate before trusting any emission")
    fh.write(out["verdict"] + "\n")
    return ok_all, out


def build(out_path, seed_path, delta, eps_box, r_t, r_c, fh):
    seed = json.load(open(seed_path))
    spec = json.load(open(BOXSPEC))["classes"]["k4_08"]
    a = Fr(1, 2) - delta
    h = Fr(1, 2) + eps_box
    cores = [(Fr(p[0]), Fr(p[1]), a) for p in spec["pins"]]
    boxes = [(Fr(b["slot"][0]), Fr(b["slot"][1]), h) for b in spec["boxes"]]
    atoms, tot = [], Fr(0)
    for at in seed["atoms"]:
        w = Fr(at["w"])
        if w <= 0:
            continue
        tot += w
        atoms.append({"px": at["px"], "py": at["py"], "qx": at["qx"], "qy": at["qy"], "w": at["w"]})
    u = seed["urow"]
    images = list(u["images"].keys())
    gammas = {n: Fr(u["images"][n]["gamma"]) for n in images}
    cap = int(u["cap"])
    zones_by_image = {n: zone_boxes(image_poses(n), r_t, r_c) for n in images}
    thr = Fr(28) - sum(gammas[n] * cap for n in images)

    def nofloat(x):
        if isinstance(x, float):
            return repr(x)
        if isinstance(x, dict):
            return {k: nofloat(v) for k, v in x.items()}
        if isinstance(x, list):
            return [nofloat(v) for v in x]
        return x
    prov = seed.get("provenance", {})
    cert = {
        "format": "pair-certificate-v2.1",
        "s": frs(S0), "n": 11, "k": 4, "m": 7, "beta": "1",
        "cores": [{"kx": frs(kx), "ky": frs(ky), "a": frs(aa)} for (kx, ky, aa) in cores],
        "boxes": [{"bx": frs(bx), "by": frs(by), "h": frs(hh)} for (bx, by, hh) in boxes],
        "atoms": atoms, "total": frs(tot),
        "urow": {
            "rung": int(u["rung"]), "cap": cap,
            "images": {n: {"gamma": frs(gammas[n]),
                           "zones": [{k: (v if k == "slot" else frs(v)) for k, v in z.items()}
                                     for z in zones_by_image[n]]} for n in images},
            "zone_half_widths": {"r_t": frs(r_t), "r_c": frs(r_c)},
            "threshold_discounted": frs(thr),
            "claim": ("(P2''') mu2{Q,Q'} >= 1 + beta m2(Q,Q') - sum_g gamma_g bz_g(Q,Q') on "
                      "every admissible core-free interior-disjoint pair, bz_g = 1 iff Q, Q' "
                      "lie in zone boxes of g with DISTINCT slots; (P1''') W2 < C(N,2) + "
                      "beta m - sum_g gamma_g cap.  Sound on the EXACT k4_08 stratum only "
                      "(docs/proofs/u_ladder.md Lemma U-ROW, rung %d)" % int(u["rung"])),
        },
        "provenance": {
            "attempt": "A81-slack-verify T1",
            "cls": "k4_08", "seed": seed_path,
            "seed_etas": nofloat(prov.get("etas")),
            "depth_histogram": nofloat(prov.get("depth_histogram")),
            "delta": frs(delta), "eps_box": frs(eps_box),
            "lp_gate": nofloat(u.get("gate_float")),
            "note": ("beta=1 boosted candidate under the rung-%d U-row (both images); slack "
                     "cores half-side 1/2 - delta at the 4 pins; class boxes widened to "
                     "1/2 + eps_box (Lemma P bridge); mixed-depth atoms.  NOT a v2 "
                     "certificate: the urow block needs the versioned v2.1 verifier "
                     "(spec-side data per Lemma U-ROW); the frozen v2 verifiers reject the "
                     "format string." % int(u["rung"])),
            "W2_str": frs(tot),
        },
    }
    with open(out_path, "w") as fo:
        json.dump(cert, fo, indent=1, sort_keys=True)
    print("wrote %s  atoms=%d W2=%s (%.6f) vs discounted threshold %s (%.6f): P1''' %s"
          % (out_path, len(atoms), tot, float(tot), thr, float(thr),
             "OK" if tot < thr else "VIOLATED"))
    ok, rec = canary_urow(cert, images, zones_by_image, cap, gammas, boxes, cores, fh)
    json.dump(rec, open(os.path.join(BASE, "results", "canary_urow.json"), "w"), indent=1)
    return cert, ok


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", required=True)
    ap.add_argument("--delta", default="1/1000")
    ap.add_argument("--eps_box", default="1/833")
    ap.add_argument("--r_t", default="1/10000", help="zone half-width in t")
    ap.add_argument("--r_c", default="1/10000", help="zone half-width in cx, cy")
    ap.add_argument("--skip-canary", action="store_true")
    args = ap.parse_args()
    os.makedirs(os.path.join(BASE, "results"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "logs"), exist_ok=True)
    logp = os.path.join(BASE, "logs", "canary.log")
    if not args.skip_canary:
        ok = canary_trump(logp, Fr(args.delta), Fr(args.eps_box))
        print("canary trump5:", "SAFE" if ok else "FAILED")
        if not ok:
            sys.exit(3)
    fh = open(logp, "a")
    cert, ok2 = build(args.out, args.seed, Fr(args.delta), Fr(args.eps_box), Fr(args.r_t),
                      Fr(args.r_c), fh)
    fh.close()
    print("canary U-row:", "SAFE" if ok2 else "FAILED")
    if not ok2:
        sys.exit(4)
