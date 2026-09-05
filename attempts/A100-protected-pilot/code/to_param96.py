"""A96 emitter: A57 case-measure-certificate-v1 leaf  ->  parametric-kill-certificate-v1.

Derived from attempts/A57-shadow-trees/code/to_param.py.  Two differences, both needed to run the
pass over EVERY A57 node instead of a hand-picked sample of level-1 leaves:

1. core_affine accepts the whole (P-aff) family of cover coordinates, not just the 12 level-1
   column centres.  docs/proofs/cover_invariance.md fixes the family as

       e_q(s) = c0 + q*(s - 2*c0),   q in Q_dy := {0, 1/12, ..., 1} refined dyadically,

   i.e. q with 12*q dyadic and 0 <= q <= 1.  A level-1 column centre is q = (i+1/2)/12; a
   depth-2 child bisects an edge, so its centre is q = (2i+1)/48, and depth d gives 12*q with
   denominator 2^(d+... ).  A57's to_param.py hard-codes q = (i+1/2)/12 and therefore raises on
   every level-2 child.  Widening to Q_dy adds NO soundness assumption: CI-1..CI-3 are proved for
   all of Q_dy, and the reconstruction alpha + beta*s0 == c is still asserted exactly, so a
   coordinate that is not of this form is still rejected rather than silently re-anchored.

2. The caveat string is dropped: cover invariance is proved (docs/proofs/cover_invariance.md,
   2026-09-01), so a PASS is a kill over the window, not a cost measurement.  The per-box
   obligation CI-4 (the logic kills) is NOT discharged here -- those nodes are excluded from the
   parametric pass and keep their per-side C-check, exactly as CI-4 requires.

Everything else (atom "nearest-wall" anchoring, slot anchoring, nofams rejection) is unchanged.
Sound-side note: atom anchoring is a completeness choice, never a soundness one (A56 soundness.md
P3) -- a bad choice makes the verifier FAIL, it cannot make it wrongly PASS.
"""
import argparse, json, os
from fractions import Fraction as F

S0 = F(969271, 250000)
C0 = F(11, 10)
NX = 12
L_SLOTS = (F(1, 2), F(3, 2), F(5, 2))


def _rat(x):
    return F(x) if not isinstance(x, F) else x


def _is_dyadic(q):
    d = q.denominator
    return d & (d - 1) == 0


def core_affine(coord):
    """(alpha, beta) for a core coordinate: slot anchors first, then the (P-aff) cover family."""
    c = _rat(coord)
    for a in L_SLOTS:
        if c == a:
            return a, F(0)
    for a in L_SLOTS:
        if c == S0 - a:
            return -a, F(1)
    beta = (c - C0) / (S0 - 2 * C0)          # = q
    if not (0 <= beta <= 1) or not _is_dyadic(beta * NX):
        raise ValueError(f"core coordinate {c} (~{float(c)}) is neither a slot nor in Q_dy")
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
                   anchoring=dict(rule="A96: slots + (P-aff) cover family e_q(s)=c0+q(s-2c0), q in Q_dy",
                                  cover_columns=NX, c0=str(C0),
                                  lemma="docs/proofs/cover_invariance.md CI-1..CI-3"),
                   provenance=dict(base=path, emitter="A96 code/to_param96.py"))
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
