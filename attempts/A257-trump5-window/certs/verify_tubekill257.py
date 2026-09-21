"""A257 -- the VERIFIER CLAUSE of a TUBE-KILL leaf taken at a WINDOW pad with SLACK pins (Lemma TUBE-KILL,
A256 notes/trump5_closure.md s.3, hypothesis (ii) read as the lemma states it -- see code/trump257.py).

    python verify_tubekill257.py <pilot certificate.json> [...] [--corrupt <gate>] [--no-tube-recheck]

A frozen verifier is never touched and A256's `verify_tubekill256.py` is not edited: this is A257's own file, it
checks only A257's own leaves, and it differs from A256's in exactly one place -- clause (ii).  A256's checks the
tube BOX on every role including the pins; Lemma TUBE-KILL (ii) asks the box on the named FREE roles and the pins
"matched corner by corner", and the proof needs no more (a pinned centre coordinate of P at side m is alpha + beta m
exactly, so its pull-back has w = 0).  With the delta_pin = 1e-2 slack a window statement requires, the pin box is
+-1e-2 > r_c and A256's clause can never pass.  Here:

  (i)   all eleven squares named  -- the leaf's own `n_anon` = 0 and per-role margins for every named role;
  (ii)a free roles               -- dx, dy <= r_c' = r_c - 2(s0 - s-hat) and dt <= r_theta, the radii read from the
                                    CITED certificate, not from the node;
  (ii)b pins                     -- every pin upright, its box centred within 1e-6 of the image pin's corner slot
                                    at s0, half-widths <= the record's delta_pin, |alpha| <= A = 3/2;
  (iii) the tube certificate     -- exists, SLOT ray, trump5's pin set {0,1,2,3,5}, r_s = 0, T >= T'; and
                                    certs/verify_tube.py (frozen, A83's 289-check exact checker) is re-run on it;
  (iv)  Lemma SEAM's (K)         -- T_K(delta_pin) >= T', T_K(d) = ((2/3) d s-hat - (s0 - s-hat))/(1 + (2/3) d),
                                    delta_pin the MINIMUM pin slack of the node's record (A256's tree256 takes the
                                    max, which is the unsound direction; see notes/window257.md s.2).

A TUBE-KILL leaf asserts: no packing satisfying the node exists at any side m < s-hat, and at m = s-hat the only one
is g . z-hat.  It asserts NOTHING about m in (s-hat, s0].
Two certificate shapes are accepted: the full `runs[*].nodes` node records, and -- for a pilot certificate written
before the node records were kept -- the REDUCED record `out.tube_rows` + `out.tube_tries` (same numbers, produced
by the same code path; the reduced case is printed as such and every tube_tries row has n_anon = 0 by construction,
since tube_try257 returns before appending when any square is anonymous).

Corruption gates (each must FAIL every leaf): --corrupt {radii, seam, ray, T, names, pins}.  Exit 0 iff every leaf
passes (and, with --corrupt, iff every leaf fails).
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
TRUMP5_PINS = [0, 1, 2, 3, 5]
SLOT_TOL = Fr(1, 10 ** 6)
A = Fr(3, 2)
_S = {}


def shat():
    if "s" not in _S:
        d = json.load(open(os.path.join(ROOT, "attempts", "A03-upper-reconstruct", "trump11_exact.json"), encoding="utf-8"))
        _S["s"] = Fr(str(d["s"]))
    return _S["s"]


def T_K(dpin):
    d = Fr(str(dpin))
    return (Fr(2, 3) * d * shat() - (S0 - shat())) / (1 + Fr(2, 3) * d)


def leaves(doc):
    """-> [(label, kind, roles {r: (dx, dy, dt_deg)}, pins {p: ok-dict|bool}, seam, radii, reduced)]."""
    out = []
    for _k, d in (doc.get("runs") or {}).items():
        for n in (d.get("nodes") or []):
            if n.get("verdict") not in ("TUBE-KILL", "TRUMP-TUBE"):
                continue
            tb, seam = n.get("tube") or {}, n.get("tube_seam") or {}
            roles = {r: (v.get("dx"), v.get("dy"), v.get("dt_deg")) for r, v in (tb.get("roles") or {}).items()}
            out.append((n.get("label"), n.get("verdict"), roles, tb.get("pins") or {}, seam, tb.get("radii") or {},
                        False, n.get("n_anon")))
    if out:
        return out
    o = doc.get("out") or {}
    tries = {t.get("label"): t for t in (o.get("tube_tries") or [])}
    for r in (o.get("tube_rows") or []):
        t = tries.get(r.get("label")) or {}
        roles = {k: (v[3], v[4], v[5]) for k, v in (t.get("roles") or {}).items()}
        out.append((r.get("label"), r.get("kind"), roles, t.get("pins") or {}, r.get("seam") or t.get("seam") or {},
                    r.get("radii") or {}, True, 0))
    return out


def check(leaf, corrupt, recheck):
    label, kind, roles, pins, seam, radii, reduced, n_anon = leaf
    msgs, ok = [], True
    cert = os.path.join(ROOT, str(radii.get("cert") or ""))
    if corrupt == "names":
        n_anon = 1
    if n_anon not in (0, None) or not roles:
        msgs.append("(i) FAIL: %s anonymous square(s) / no per-role margins" % n_anon)
        ok = False
    if not os.path.exists(cert):
        return False, ["(iii) FAIL: the cited tube certificate is missing: %s" % radii.get("cert")]
    c = json.load(open(cert, encoding="utf-8"))
    rc, rt, rs, T = Fr(c["r_c"]), Fr(c["r_theta"]), Fr(c["r_s"]), Fr(c["T"])
    spec = c.get("spec") or c.get("direction_spec") or {}
    if corrupt == "T":
        T = T / 100
    if corrupt == "ray":
        spec = dict(spec, mode="scale", pins=None)
    Tp = Fr(str(seam.get("T_prime") or 0))
    if rs != 0:
        msgs.append("(iii) FAIL: r_s = %s (Theorem T1's kill needs r_s = 0)" % rs)
        ok = False
    if kind == "TUBE-KILL":
        if spec.get("mode") != "slot" or sorted(spec.get("pins") or []) != TRUMP5_PINS:
            msgs.append("(iii) FAIL: a window TUBE-KILL needs the SLOT ray with trump5's pins %s, got mode=%s pins=%s"
                        % (TRUMP5_PINS, spec.get("mode"), spec.get("pins")))
            ok = False
        if T < Tp:
            msgs.append("(iii) FAIL: T = %s < T' = %s (the slab is deeper than the certified tube)" % (T, Tp))
            ok = False
    rc_eff = rc - 2 * (S0 - shat())
    if corrupt == "radii":
        rc_eff = rc_eff / 100          # SHRINK: A256's gate multiplies by 100, which widens the box and can never
        rt = rt / 100                  # make a passing leaf fail -- a gate that does not bite is not a gate
    # the REDUCED record stores the per-role margins rounded to 7 decimals (5 for the tilt), so the verifier must
    # allow half a unit in the last place there -- and that is exactly why the reduced path is the WEAKER check:
    # it cannot separate "at the wall" from "5e-8 outside it".  A full node record is checked with no tolerance.
    tol_c, tol_t = (Fr(5, 10 ** 8), Fr(5, 10 ** 6) * Fr(31416, 1800000)) if reduced else (Fr(0), Fr(0))
    rc_eff, rt = rc_eff + tol_c, rt + tol_t
    for r, (dx, dy, dt) in sorted(roles.items()):
        fx, fy = Fr(str(dx or 0)), Fr(str(dy or 0))
        ft = Fr(str(dt or 0)) * Fr(31416, 1800000)                 # deg -> rad, rounded UP
        if fx > rc_eff or fy > rc_eff or ft > rt:
            msgs.append("(ii)a FAIL: free role %s outside the tube box (dx %s, dy %s, dt %s rad vs r_c' %s, r_theta %s)"
                        % (r, float(fx), float(fy), float(ft), float(rc_eff), float(rt)))
            ok = False
    if kind == "TUBE-KILL":
        if not pins:
            msgs.append("(ii)b FAIL: no per-pin corner match recorded")
            ok = False
        for p, v in sorted(pins.items()):
            d = v if isinstance(v, dict) else {"ok": bool(v)}
            bad = (corrupt == "pins") or not d.get("ok", False)
            if isinstance(v, dict):
                bad = bad or (not v.get("upright")) or Fr(str(v.get("dc") or 1)) > SLOT_TOL \
                    or max(Fr(str(h)) for h in (v.get("half") or [1, 1])) > Fr(str(v.get("dpin") or 0)) \
                    or Fr(str(v.get("max_abs_alpha") or 9)) > A
            if bad:
                msgs.append("(ii)b FAIL: pin %s is not matched corner by corner: %s" % (p, v))
                ok = False
        dpin = Fr(str(seam.get("delta_pin") or 0))
        if corrupt == "seam":
            dpin = dpin / 1000
        if T_K(dpin) < Tp:
            msgs.append("(iv) FAIL: T_K(delta_pin = %s) = %s < T' = %s -- the record must be re-emitted with a bigger "
                        "pin slack (contraction_tube.md s.4.4 item 1)" % (float(dpin), float(T_K(dpin)), float(Tp)))
            ok = False
    if ok and recheck:
        rc_ = subprocess.call([sys.executable, os.path.join(ROOT, "certs", "verify_tube.py"), cert],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if rc_ != 0:
            msgs.append("(iii) FAIL: certs/verify_tube.py rejected %s (rc %s)" % (radii.get("cert"), rc_))
            ok = False
    return ok, msgs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("certs", nargs="+")
    ap.add_argument("--corrupt", default=None, choices=("radii", "seam", "ray", "T", "names", "pins"))
    ap.add_argument("--no-tube-recheck", dest="recheck", action="store_false")
    a = ap.parse_args()
    n, bad = 0, 0
    for f in a.certs:
        doc = json.load(open(f, encoding="utf-8"))
        for leaf in leaves(doc):
            n += 1
            ok, msgs = check(leaf, a.corrupt, a.recheck)
            print("%s %s %s%s: %s" % (os.path.basename(f), leaf[0], leaf[1], " [reduced record]" if leaf[6] else "",
                                      "PASS" if ok else "FAIL"))
            for m in msgs:
                print("    " + m)
            bad += 0 if ok else 1
    print("== %d tube leaf/leaves, %d failure(s)%s" % (n, bad, (" [gate %s]" % a.corrupt) if a.corrupt else ""))
    if a.corrupt:
        sys.exit(0 if (n == 0 or bad == n) else 1)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
