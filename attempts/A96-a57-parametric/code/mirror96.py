"""A96 step 4a: the sigma rewrite, for k5_11's diagonal reflection sigma.

    sigma: (x, y, theta) -> (y, x, 90 - theta),   equivalently  t = tan(theta/2) -> (1-t)/(1+t).

k5_11's slot set is sigma-invariant (A95 T2, checked symbolically in (alpha, beta) at all four
grid sides), so sigma maps the stratum to itself and a certificate for a cover box B rewrites
into a certificate for sigma B.  k5_16's stabiliser is trivial -- no ladder change, no rewrite.

WHY A REWRITE IS SOUND, AND WHAT IS *NOT* ASSUMED.  mu_s = sum_i w_i delta_{p_i(s)} with
p_i(s) = (ax + bx s, ay + by s); a unit square Q with centre c and tilt theta is admissible in
[0,s]^2 iff sigma Q is (the container is sigma-invariant), and mu_s(Q) = (sigma_* mu_s)(sigma Q).
So the certified statement transports verbatim -- PROVIDED the hypotheses transport too, and the
one that does NOT transport for free is the tree's branching obligation

    "every packing square whose (centre, t) lies in B contains the core K_B"

for the mirrored box.  That is a geometry fact about (sigma B, sigma K_B), not a consequence of
the certificate, so it is re-derived here by the SAME C-check A57 uses on native boxes
(pinguard.classify against the pin cores), never assumed.  ccheck_mirror() below does that.

The rewrite itself:
    atoms   (ax, bx, ay, by, w)      ->  (ay, by, ax, bx, w)
    cores   (akx, bkx, aky, bky, tm, a) -> (aky, bky, akx, bkx, (1-tm)/(1+tm), a)
    case-measure certificates: atom (x, y) -> (y, x); core kx <-> ky, tm -> (1-tm)/(1+tm)
Everything is exact rational; weights, budget and total are untouched.

Self-check: sigma is an involution, so mirror(mirror(C)) must equal C field for field.  main()
asserts it on every file it rewrites.
"""
import argparse, json, os
from fractions import Fraction as F


def _rat(x):
    return F(x) if not isinstance(x, F) else x


def mirror_t(tm):
    t = _rat(tm)
    return (1 - t) / (1 + t)


def mirror_param(d):
    """parametric-kill-certificate-v1 -> its sigma image."""
    if d.get("format") != "parametric-kill-certificate-v1":
        raise ValueError(f"unexpected format {d.get('format')!r}")
    out = dict(d)
    out["atoms"] = [dict(ax=a["ay"], bx=a["by"], ay=a["ax"], by=a["bx"], w=a["w"])
                    for a in d["atoms"]]
    out["hypotheses"] = dict(d["hypotheses"])
    out["hypotheses"]["cores"] = [
        dict(akx=k["aky"], bkx=k["bky"], aky=k["akx"], bky=k["bkx"],
             tm=str(mirror_t(k["tm"])), a=k["a"]) for k in d["hypotheses"]["cores"]]
    if d["hypotheses"].get("nofams"):
        raise ValueError("nofams: sigma rewrite of a NO-family is not implemented")
    out["name"] = d.get("name", "") + ".sigma"
    prov = dict(d.get("provenance") or {})
    prov["sigma"] = "A96 code/mirror96.py: (x,y,theta) -> (y,x,90-theta)"
    prov["sigma_preimage"] = d.get("name")
    out["provenance"] = prov
    return out


def mirror_case(d):
    """case-measure-certificate-v1 -> its sigma image (for the fixed-side fallbacks)."""
    if d.get("format") != "case-measure-certificate-v1":
        raise ValueError(f"unexpected format {d.get('format')!r}")
    out = dict(d)
    A = []
    for p in d["atoms"]:
        if isinstance(p, list):
            A.append([p[1], p[0]])
        else:
            q = dict(p); q["x"], q["y"] = p["y"], p["x"]; A.append(q)
    out["atoms"] = A
    out["hypotheses"] = dict(d["hypotheses"])
    out["hypotheses"]["cores"] = [dict(k, kx=k["ky"], ky=k["kx"], tm=str(mirror_t(k["tm"])))
                                  for k in d["hypotheses"]["cores"]]
    if d["hypotheses"].get("nofams"):
        raise ValueError("nofams: sigma rewrite of a NO-family is not implemented")
    prov = dict(d.get("provenance") or {})
    prov["sigma"] = "A96 code/mirror96.py: (x,y,theta) -> (y,x,90-theta)"
    out["provenance"] = prov
    return out


def mirror(d):
    return mirror_param(d) if d.get("format") == "parametric-kill-certificate-v1" else mirror_case(d)


def _canon(d):
    """Comparable form: drop the provenance/name fields the rewrite deliberately annotates."""
    e = {k: v for k, v in d.items() if k not in ("provenance", "name")}
    return json.dumps(e, sort_keys=True)


def ccheck_mirror(box, pins, slots):
    """A57's own C-check (pinguard.classify) applied to the MIRRORED box.

    box is a caselp.Box.  Returns (class, info) exactly as classify does for a native box; the
    caller must require 'ok' before deploying the mirrored certificate, because a 'contradictory'
    mirror is killed by logic (not by the certificate) and a 'parent' mirror is not a leaf.
    """
    import sys
    A57 = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "A57-shadow-trees"))
    if os.path.join(A57, "code") not in sys.path:
        sys.path.insert(0, os.path.join(A57, "code"))
    from caselp import Box
    from pinguard import classify
    mb = Box(box.y0, box.y1, box.x0, box.x1, 90.0 - box.th1, 90.0 - box.th0)
    return classify(mb, pins, slots)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("certs", nargs="+")
    ap.add_argument("--outdir", required=True)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    for p in a.certs:
        d = json.load(open(p))
        m = mirror(d)
        assert _canon(mirror(m)) == _canon(d), f"sigma is not an involution on {p}"
        o = os.path.join(a.outdir, os.path.basename(p).replace(".json", ".sigma.json"))
        json.dump(m, open(o, "w"), indent=0)
        print(json.dumps(dict(src=os.path.basename(p), out=o, involution_ok=True)), flush=True)


if __name__ == "__main__":
    main()
