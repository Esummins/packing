"""
A57 / A63 route-(a) COST PROBE: case-measure-certificate-v1 leaf -> parametric-kill-certificate-v1,
bypassing make_param's forced core anchoring.

**Soundness-conditional.**  This emitter exists ONLY to measure the 4D verification cost of route
(a).  `make_param.core_anchor()` rejects an A57 leaf because its sixth core (the YES cover box)
sits at an interior centre, not a slot.  Here that core is given the affine centre the A57 cover
actually implies, and the pins keep their slot anchors:

    zone            = [c0, s - c0],  c0 = 11/10          (A57 tree57.zones, cw = 3/5)
    column i of 12  -> centre_x(s) = c0 + (s - 2 c0)(i + 1/2)/12
                     = alpha + beta s,  beta = (i + 1/2)/12,  alpha = c0 (1 - 2 beta)
    verified exactly against the emitted leaf: alpha + beta*s0 reproduces kx, ky as Fractions.

Atoms use make_param's default "nearest-wall" rule (b = 1 iff coord > s0/2), which is a
completeness choice, never a soundness one (A56 soundness.md P3).

**What this does NOT establish.**  That the interior cover REMAINS A COVER of the zone for every
s in the window is the cover-invariance lemma, which is with the theory lead.  Until that exists a
PASS here is a cost measurement, not a kill over the window.
"""
import argparse, json, os, sys
from fractions import Fraction as F

S0 = F(969271, 250000)
C0 = F(11, 10)
NX = 12
L_SLOTS = (F(1, 2), F(3, 2), F(5, 2))


def _rat(x):
    return F(x) if not isinstance(x, F) else x


def core_affine(coord):
    """(alpha, beta) for a core coordinate: slot anchors first, then the A57 column rule."""
    c = _rat(coord)
    for a in L_SLOTS:
        if c == a:
            return a, F(0)
    for a in L_SLOTS:
        if c == S0 - a:
            return -a, F(1)
    # A57 interior cover column: c = C0 + (s - 2 C0) * (i + 1/2)/NX at s = S0
    beta = (c - C0) / (S0 - 2 * C0)
    k2 = beta * NX * 2                       # = 2i + 1, must be an odd integer in [1, 2*NX-1]
    if k2.denominator != 1 or k2 <= 0 or k2 >= 2 * NX or k2 % 2 == 0:
        raise ValueError(f"core coordinate {c} (~{float(c)}) is neither a slot nor a cover column")
    alpha = C0 * (1 - 2 * beta)
    assert alpha + beta * S0 == c, "affine reconstruction must be exact at s0"
    return alpha, beta


def atom_anchor(coord):
    c = _rat(coord)
    b = F(1) if c > S0 / 2 else F(0)
    return c - b * S0, b


def convert(path, out):
    c = json.load(open(path))
    if c.get("format") != "case-measure-certificate-v1":
        raise ValueError(f"unexpected format {c.get('format')!r}")
    if c["hypotheses"].get("nofams"):
        raise ValueError("nofams unsupported by verify_param")
    atoms = []
    for p, w in zip(c["atoms"], c["weights"]):
        ax, bx = atom_anchor(p[0] if isinstance(p, list) else p["x"])
        ay, by = atom_anchor(p[1] if isinstance(p, list) else p["y"])
        atoms.append(dict(ax=str(ax), bx=str(bx), ay=str(ay), by=str(by), w=str(_rat(w))))
    cores = []
    for k in c["hypotheses"]["cores"]:
        akx, bkx = core_affine(k["kx"])
        aky, bky = core_affine(k["ky"])
        cores.append(dict(akx=str(akx), bkx=str(bkx), aky=str(aky), bky=str(bky),
                          tm=str(_rat(k["tm"])), a=str(_rat(k["a"]))))
    out_doc = dict(format="parametric-kill-certificate-v1",
                   name=os.path.basename(path)[:-5],
                   n=int(c.get("n", 11)), budget=int(c["budget"]),
                   total=str(sum(_rat(w) for w in c["weights"])),
                   atoms=atoms, hypotheses=dict(cores=cores, nofams=[]),
                   anchoring=dict(rule="A57 route-(a) cost probe: slots + cover-column affine",
                                  cover_columns=NX, c0=str(C0),
                                  caveat="cover-invariance lemma NOT established; cost probe only"),
                   provenance=dict(base=path, emitter="A57 code/to_param.py"))
    json.dump(out_doc, open(out, "w"), indent=0)
    return out_doc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("certs", nargs="+")
    ap.add_argument("--outdir", default=None)
    a = ap.parse_args()
    od = a.outdir or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "certs", "param")
    os.makedirs(od, exist_ok=True)
    for p in a.certs:
        o = os.path.join(od, os.path.basename(p)[:-5] + ".param.json")
        try:
            d = convert(p, o)
            print(json.dumps(dict(src=os.path.basename(p), out=o, atoms=len(d["atoms"]),
                                  cores=len(d["hypotheses"]["cores"]), total=d["total"],
                                  budget=d["budget"])), flush=True)
        except Exception as e:
            print(json.dumps(dict(src=os.path.basename(p), error=repr(e)[:160])), flush=True)


if __name__ == "__main__":
    main()
