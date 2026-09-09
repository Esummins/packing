"""A170 -- the WRAPPER that makes `caselp.make_certificate` carry A135's EXACT cores.

WHY.  `attempts/A57-shadow-trees/code/caselp.py :: make_certificate` ends with

    hyp = Hyp.from_json(res["hyp"])

and `Hyp.__init__` sets `self.cores = [b.core() for b in self.boxes]` -- the STOCK cores -- so the
`cores` field `Hyp.to_json` wrote is silently discarded.  A lane that solves the LP with an
`ExactHyp` (row filter `Hyp.ok_many` against A135's certified EXACT cores) therefore emits a
certificate that exempts a STRICTLY SMALLER core than the LP was entitled to drop rows against, and
every LP-dropped placement in the annulus between the two cores is a guaranteed HOLE.  A166
(`attempts/A166-nearest-corner-subtree/notes/certificate_bug.md`) diagnosed it; the annulus is
1.4 %-15 % of the core half-side on every box of the corner cover.

`caselp.py` is a frozen-adjacent driver and is NOT edited.  Lanes call this wrapper instead of
`caselp.make_certificate` (or post-process an already-written certificate with `carry_exact_cores`).

SOUNDNESS.  A135's `exactcore.exact_a` returns the largest half-side `a` on a rational grid whose
four corners pass A132's EXACT rational vertex test against every pose of the box, i.e. it CERTIFIES
`K(B) subset Q(p)` for every `p in B`.  A square of the packing distinct from the conditioned one is
interior-disjoint from the conditioned square, hence from its core, so exempting placements that meet
the EXACT core is legitimate; the frozen `verify_case.py` validates whatever cores the certificate
carries.  Two guards are enforced here and are the reason this is safe to run over ANY certificate,
including one whose LP used the stock cores:

  * a core is only ever ENLARGED (`a_new = a_exact` only when `a_exact > a_carried`); a certificate
    whose carried core is already at least as large is left byte-identical.  Enlarging a certified
    core can only REMOVE verification obligations, so it can turn FAIL into PASS but never the
    reverse, and the resulting statement is still a theorem.
  * the substitution is refused unless `exact_a` reports `cert_ok` (the vertex test passed) and
    `(kx, ky, tm)` are unchanged, so the core stays the same square, only wider.

    from certwrap170 import make_certificate_exact, carry_exact_cores, run_frozen_verifier
"""
import hashlib
import json
import os
import subprocess
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
for _p in (os.path.join(ATT, "A57-shadow-trees", "code"),
           os.path.join(ATT, "A132-polygon-core", "code"),
           os.path.join(ATT, "A135-polycore-verifier", "code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import caselp                                                  # noqa: E402  READ-ONLY (A57)
from caselp import Box                                         # noqa: E402  READ-ONLY (A57)
import exactcore as EC                                         # noqa: E402  READ-ONLY (A135)

FROZEN = os.path.join(ATT, "A143-corner-first-k0", "code", "verify_case.py")
FROZEN_SHA = "521cb01fe656707cf134864b75227c6051d43a97253749f50ecd1eb37cbef7af"

_CACHE = {}


def frozen_sha(path=FROZEN):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def assert_frozen(path=FROZEN):
    got = frozen_sha(path)
    if got != FROZEN_SHA:
        raise RuntimeError("verify_case.py is NOT the frozen one: %s != %s" % (got, FROZEN_SHA))
    return got


def exact_a_cached(box):
    key = (box.x0, box.x1, box.y0, box.y1, box.th0, box.th1)
    if key not in _CACHE:
        try:
            a, a0, ok = EC.exact_a(box)
        except Exception as ex:                                 # noqa: BLE001
            _CACHE[key] = (None, None, False, repr(ex)[:120])
        else:
            _CACHE[key] = (a, a0, bool(ok), None)
    return _CACHE[key]


def box_from_core_json(cj):
    b = cj.get("box")
    if not b:
        return None
    return Box(**{k: b[k] for k in ("x0", "x1", "y0", "y1", "th0", "th1")})


def carry_exact_cores(cert, cores=None, boxes=None):
    """Substitute A135 exact cores into an emitted certificate, IN PLACE.

    `cores`  -- the live `Hyp.cores` the LP used (preferred: exactly what the row filter saw).
    `boxes`  -- boxes to recompute from, when the live hypothesis is gone.
    neither  -- recompute from the box each core in the certificate carries.

    Returns a report list, one row per core:
        {i, carried, exact, stock, applied, ratio, reason}
    """
    cc = (cert.get("hypotheses", {}) or {}).get("cores") or []
    rep = []
    for i, cj in enumerate(cc):
        car = Fr(cj["a"])
        b = boxes[i] if (boxes is not None and i < len(boxes)) else box_from_core_json(cj)
        if b is None and (cores is None or i >= len(cores)):
            rep.append(dict(i=i, carried=str(car), applied=False, reason="no box"))
            continue
        a_new = a_stock = None
        ok, err = True, None
        kx = ky = tm = None
        if b is not None:
            a_new, a_stock, ok, err = exact_a_cached(b)
            k = b.core()
            if k is not None:
                kx, ky, tm = Fr(k.kx), Fr(k.ky), Fr(k.tm)
        # the cores the LP's row filter actually used win whenever they are LARGER than what the
        # box-recomputed exact core gives (an ExactHyp may install a core certified by a different
        # exact route); a core is never SHRUNK.
        if cores is not None and i < len(cores):
            c = cores[i]
            if a_new is None or Fr(c.a) > a_new:
                a_new = Fr(c.a)
                ok, err = True, None
                kx, ky, tm = Fr(c.kx), Fr(c.ky), Fr(c.tm)
        if a_new is None or not ok:
            rep.append(dict(i=i, carried=str(car), applied=False,
                            reason="exact vertex test failed: %s" % (err or "cert_ok False")))
            continue
        same_square = (kx is None or (Fr(cj["kx"]) == kx and Fr(cj["ky"]) == ky
                                      and Fr(cj["tm"]) == tm))
        if not same_square:
            rep.append(dict(i=i, carried=str(car), exact=str(a_new), applied=False,
                            reason="core centre/tilt differs -- not the same square"))
            continue
        if a_new <= car:
            rep.append(dict(i=i, carried=str(car), exact=str(a_new),
                            stock=(str(a_stock) if a_stock is not None else None),
                            applied=False, ratio=float(a_new) / float(car),
                            reason="carried core already >= exact core"))
            continue
        cj["a"] = str(a_new)
        cj["kx"], cj["ky"], cj["tm"] = str(kx), str(ky), str(tm)
        rep.append(dict(i=i, carried=str(car), exact=str(a_new),
                        stock=(str(a_stock) if a_stock is not None else None),
                        applied=True, ratio=float(a_new) / float(car)))
    if any(r.get("applied") for r in rep):
        cert.setdefault("provenance", {})["a170_exact_cores"] = (
            "cores ENLARGED to A135 exactcore.exact_a (the cores an ExactHyp LP's row filter uses); "
            "caselp.make_certificate reverts to Hyp.from_json's stock b.core() -- see "
            "attempts/A166-nearest-corner-subtree/notes/certificate_bug.md and "
            "attempts/A170-certfix/code/certwrap170.py.  Enlarging a certified core only removes "
            "verification obligations; exact_a certifies K(B) subset Q(p) for every pose p in B.")
    return rep


def make_certificate_exact(res, s_rat, scale=1.03, denom_pos=10 ** 6, denom_w=10 ** 6,
                           hyp=None, boxes=None):
    """`caselp.make_certificate` with the exact cores carried through.

    Pass `hyp` (the LIVE hypothesis the LP was solved with) whenever it is still in hand -- then the
    certificate carries exactly the cores the row filter used.  Otherwise the exact cores are
    recomputed from the boxes.
    """
    cert = caselp.make_certificate(res, s_rat, scale=scale, denom_pos=denom_pos, denom_w=denom_w)
    rep = carry_exact_cores(cert, cores=(list(hyp.cores) if hyp is not None else None), boxes=boxes)
    cert.setdefault("provenance", {})["a170_core_report"] = rep
    return cert


def run_frozen_verifier(cert_path, jobs=1, depth=56, max_w=64, timeout=1800.0, verifier=FROZEN):
    assert_frozen(verifier)
    cmd = [sys.executable, verifier, cert_path, "--jobs", str(jobs), "--depth", str(depth),
           "--max-witnesses", str(max_w), "--report", "--quiet"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, "TIMEOUT after %.0f s" % timeout
    return p.returncode, p.stdout + p.stderr


def verifier_tail(txt):
    return [l for l in (txt or "").splitlines()
            if l.startswith(("PASS", "FAIL", "boxes", "MALFORMED"))]


if __name__ == "__main__":
    print("frozen verify_case.py:", assert_frozen(), "OK")
    print("caselp.make_certificate at", caselp.__file__)
