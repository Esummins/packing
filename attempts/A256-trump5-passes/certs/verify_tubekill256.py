"""A256 -- the VERIFIER CLAUSE of a TUBE-KILL / TRUMP-TUBE leaf (Lemma TUBE-KILL, notes/trump5_closure.md s.3).

    python verify_tubekill256.py <certificate.json> [<certificate.json> ...] [--corrupt <gate>]

A frozen verifier is never touched: this is A256's own file and it checks only A256's own leaves.  For every node of
every run of the certificate whose verdict is TUBE-KILL or TRUMP-TUBE it re-checks, from the node's recorded
`tube` / `tube_seam` block and NOTHING else:

  (i)   all eleven squares are named            -- `tube.roles` covers the pins and every named role, no anonymous
        square left (`n_anon` = 0 on the node record);
  (ii)  containment                             -- every recorded per-role margin dx, dy <= r_c' = r_c - 2(s0 - s-hat)
        and dt <= r_theta, with r_c, r_theta read from the cited tube certificate itself (not from the node);
  (iii) the tube certificate                    -- the cited certs/tube_*.json exists, is the SLOT ray with trump5's
        pin set {0,1,2,3,5} for a window leaf (the scale ray for a pad-0 TRUMP-TUBE), has r_s = 0, and has
        T >= T' = s-hat - s_bot for the leaf's slab;  certs/verify_tube.py is re-run on it (the 289-check exact
        checker of A83) unless --no-tube-recheck;
  (iv)  Lemma SEAM's (K) condition               -- T_K(delta_pin) >= T', T_K(d) = ((2/3) d s-hat - (s0 - s-hat)) /
        (1 + (2/3) d) with A = 3/2, delta_pin the pin-core slack of the node's own record.

A TRUMP-TUBE leaf (pad 0) is an s0-only LOCALISATION and is checked on (i)-(iii) only; (iv) is a window hypothesis.
A TUBE-KILL leaf asserts: no packing satisfying the node exists at any side m < s-hat, and at m = s-hat the only one
is g . z-hat.  It asserts NOTHING about m in (s-hat, s0].

Corruption gates (each must FAIL): --corrupt {radii, seam, ray, T, names}.
Exit code 0 iff every leaf passes (and every gate fails when --corrupt is given).
"""
import argparse
import json
import os
import subprocess
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
S0 = Fr(969271, 250000)
SHAT = None
TRUMP5_PINS = [0, 1, 2, 3, 5]


def shat():
    global SHAT
    if SHAT is None:
        d = json.load(open(os.path.join(ROOT, "attempts", "A03-upper-reconstruct", "trump11_exact.json"), encoding="utf-8"))
        SHAT = Fr(str(d["s"]))
    return SHAT


def T_K(dpin):
    d = Fr(str(dpin))
    return (Fr(2, 3) * d * shat() - (S0 - shat())) / (1 + Fr(2, 3) * d)


def check_leaf(nid, run, n, corrupt, recheck):
    out, ok = [], True
    kind = n.get("verdict")
    tb = n.get("tube") or {}
    seam = n.get("tube_seam") or {}
    radii = tb.get("radii") or {}
    cert = os.path.join(ROOT, str(radii.get("cert") or ""))
    # (i) every square named
    n_anon = n.get("n_anon")
    if corrupt == "names":
        n_anon = 1
    if n_anon not in (0, None) or not tb.get("roles"):
        out.append("(i) FAIL: %s anonymous square(s) / no per-role margins" % n_anon)
        ok = False
    # (iii) the certificate first: its radii are what (ii) is checked against
    if not os.path.exists(cert):
        return False, ["(iii) FAIL: the cited tube certificate is missing: %s" % radii.get("cert")]
    c = json.load(open(cert, encoding="utf-8"))
    rc, rt, rs, T = Fr(c["r_c"]), Fr(c["r_theta"]), Fr(c["r_s"]), Fr(c["T"])
    spec = c.get("spec") or c.get("direction_spec") or {}
    if corrupt == "T":
        T = T / 100
    if corrupt == "ray":
        spec = dict(spec, mode="scale", pins=None)
    if rs != 0:
        out.append("(iii) FAIL: r_s = %s (Theorem T1's kill needs r_s = 0)" % rs)
        ok = False
    Tp = Fr(str(seam.get("T_prime") or 0))
    if kind == "TUBE-KILL":
        if spec.get("mode") != "slot" or sorted(spec.get("pins") or []) != TRUMP5_PINS:
            out.append("(iii) FAIL: a window TUBE-KILL needs the SLOT ray with trump5's pins %s, got mode=%s pins=%s"
                       % (TRUMP5_PINS, spec.get("mode"), spec.get("pins")))
            ok = False
        if T < Tp:
            out.append("(iii) FAIL: T = %s < T' = %s (the slab is deeper than the certified tube)" % (T, Tp))
            ok = False
    # (ii) containment, against the certificate's own radii
    rc_eff = rc - 2 * (S0 - shat())
    if corrupt == "radii":
        rc_eff = rc_eff * 100
    for r, d in (tb.get("roles") or {}).items():
        dx, dy = Fr(str(d.get("dx") or 0)), Fr(str(d.get("dy") or 0))
        dt = Fr(str(d.get("dt_deg") or d.get("dt") or 0)) * Fr(31416, 1800000)      # deg -> rad, rounded UP
        if dx > rc_eff or dy > rc_eff or dt > rt:
            out.append("(ii) FAIL: role %s outside the tube box (dx %s, dy %s, dt %s rad vs r_c' %s, r_theta %s)"
                       % (r, float(dx), float(dy), float(dt), float(rc_eff), float(rt)))
            ok = False
    # (iv) Lemma SEAM
    if kind == "TUBE-KILL":
        dpin = Fr(str(seam.get("delta_pin") or 0))
        if corrupt == "seam":
            dpin = dpin / 1000
        tk = T_K(dpin)
        if tk < Tp:
            out.append("(iv) FAIL: T_K(delta_pin = %s) = %s < T' = %s -- the record must be re-emitted with a bigger "
                       "pin slack (contraction_tube.md s.4.4 item 1)" % (float(dpin), float(tk), float(Tp)))
            ok = False
    if ok and recheck:
        rc_ = subprocess.call([sys.executable, os.path.join(ROOT, "certs", "verify_tube.py"), cert],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if rc_ != 0:
            out.append("(iii) FAIL: certs/verify_tube.py rejected %s (rc %s)" % (radii.get("cert"), rc_))
            ok = False
    return ok, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("certs", nargs="+")
    ap.add_argument("--corrupt", default=None, choices=("radii", "seam", "ray", "T", "names"))
    ap.add_argument("--no-tube-recheck", dest="recheck", action="store_false")
    a = ap.parse_args()
    n_leaf, n_bad = 0, 0
    for f in a.certs:
        doc = json.load(open(f, encoding="utf-8"))
        for run, d in (doc.get("runs") or {}).items():
            for n in (d.get("nodes") or []):
                if n.get("verdict") not in ("TUBE-KILL", "TRUMP-TUBE"):
                    continue
                n_leaf += 1
                ok, msgs = check_leaf(doc.get("nid"), run, n, a.corrupt, a.recheck)
                print("%s %s %s %s: %s" % (os.path.basename(f), run, n.get("label"), n.get("verdict"),
                                           "PASS" if ok else "FAIL"))
                for m in msgs:
                    print("    " + m)
                n_bad += 0 if ok else 1
    print("== %d tube leaf/leaves, %d failure(s)%s" % (n_leaf, n_bad, (" [gate %s]" % a.corrupt) if a.corrupt else ""))
    if a.corrupt:
        sys.exit(0 if (n_leaf == 0 or n_bad == n_leaf) else 1)     # a gate must make EVERY leaf fail
    sys.exit(1 if n_bad else 0)


if __name__ == "__main__":
    main()
