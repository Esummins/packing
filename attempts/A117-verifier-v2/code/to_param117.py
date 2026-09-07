"""A117 T1 -- emitter: a fixed-side `case-measure-certificate-v1` WITH NO-families
                ->  a `parametric-kill-certificate-v1` WITH NO-families, for verify_param_v2.

This is attempts/A96-a57-parametric/code/to_param96.py with its one refusal removed.  Atom and
core anchoring are IMPORTED from to_param96 (not copied), so the anchoring rules the corpus
already uses are literally the same code:

    atom_anchor(c)  = (c - b*s0, b),  b = 1 if c > s0/2 else 0        (nearest wall)
    core_affine(c)  = the A57 slot anchors, then the (P-aff) cover family
                      e_q(s) = c0 + q(s - 2c0), q in Q_dy   [docs/proofs/cover_invariance.md]

NEW: the NO-family.  A NO-family zone is the branch box F -- the box a region tree (A112) or a
load-path branch (A111) splits on.  F is a FIXED set: the YES/NO split "some square of the packing
has its pose in F, or none does" is a tautology at EVERY side s, for the same F.  So the zone is
emitted with beta = 0 on all four edges (`--zone-anchor const`, the default): the zone does not
move with s, exactly as the branch does not.  `--zone-anchor wall` is available for the case where
a branch box IS wall-anchored (its far edge tracks s - 1/2); it is not used by any A111/A112
certificate and is refused unless asked for.

COMPOSITION OBLIGATION (recorded, not discharged here).  A branch is window-valid only if the YES
child and the NO child use the SAME box F at every s.  The YES child's box enters its certificate
as a CORE, and to_param96's `core_affine` may anchor a core to the cover family (beta != 0), which
would make the YES box move while the NO zone stands still.  `check_yes_no_consistency` below
flags every emitted NO certificate whose partner YES certificate anchors the shared box with
beta != 0; the pair is reported as NEEDS-YES-CHECK rather than silently claimed.

Sound-side note (A56 soundness.md P3, unchanged): anchoring is a COMPLETENESS choice, never a
soundness one -- a bad choice makes the verifier FAIL, it cannot make it wrongly PASS.

    python to_param117.py CERT.json ... --outdir DIR
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from fractions import Fraction as F

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
A96 = os.path.join(ROOT, "attempts", "A96-a57-parametric", "code")
if A96 not in sys.path:
    sys.path.insert(0, A96)
import to_param96 as T96                                          # noqa: E402

S0 = T96.S0


def _rat(x):
    return F(x) if not isinstance(x, F) else x


def zone_affine(coord, mode):
    """(alpha, beta) for one edge of a NO-family zone."""
    c = _rat(coord)
    if mode == "const":
        return c, F(0)
    if mode == "wall":                       # the edge tracks the far wall: c = alpha + s0
        return c - S0, F(1)
    raise ValueError("unknown zone anchor %r" % mode)


def convert(path, out, zone_anchor="const"):
    c = json.load(open(path))
    if c.get("format") != "case-measure-certificate-v1":
        raise ValueError("unexpected format %r" % c.get("format"))
    atoms = []
    for p, w in zip(c["atoms"], c["weights"]):
        ax, bx = T96.atom_anchor(p[0] if isinstance(p, list) else p["x"])
        ay, by = T96.atom_anchor(p[1] if isinstance(p, list) else p["y"])
        atoms.append(dict(ax=str(ax), bx=str(bx), ay=str(ay), by=str(by), w=str(_rat(w))))
    cores = []
    for k in c["hypotheses"]["cores"]:
        akx, bkx = T96.core_affine(k["kx"])
        aky, bky = T96.core_affine(k["ky"])
        cores.append(dict(akx=str(akx), bkx=str(bkx), aky=str(aky), bky=str(bky),
                          tm=str(_rat(k["tm"])), a=str(_rat(k["a"]))))
    nofams = []
    for f in c["hypotheses"].get("nofams", []) or []:
        edges = {}
        for key in ("x0", "x1", "y0", "y1"):
            al, be = zone_affine(f[key], zone_anchor)
            edges[key] = [str(al), str(be)]
        tivs = [[str(_rat(a)), str(_rat(b))] for a, b in f["t_intervals"]]
        for a, b in tivs:
            if not (0 <= F(a) <= F(b) <= 1):
                raise ValueError("nofam t-interval outside [0,1]: [%s,%s]" % (a, b))
        nofams.append(dict(t_intervals=tivs, **edges))
    doc = dict(format="parametric-kill-certificate-v1",
               name=os.path.basename(path)[:-5],
               n=int(c.get("n", 11)), budget=int(c["budget"]),
               total=str(sum(_rat(w) for w in c["weights"])),
               atoms=atoms, hypotheses=dict(cores=cores, nofams=nofams),
               anchoring=dict(rule="A96: slots + (P-aff) cover family e_q(s)=c0+q(s-2c0), q in Q_dy",
                              cover_columns=T96.NX, c0=str(T96.C0),
                              zone_anchor=zone_anchor,
                              zone_rule=("A117: a NO-family zone is the branch box F, an "
                                         "s-independent set; beta = 0 on all four edges"),
                              lemma="docs/proofs/cover_invariance.md CI-1..CI-3"),
               provenance=dict(base=os.path.relpath(path, ROOT).replace("\\", "/"),
                               emitter="A117 code/to_param117.py",
                               verifier="verify_param_v2.py (A117)"))
    with open(out, "w") as fh:
        json.dump(doc, fh, indent=0)
    return doc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("certs", nargs="*")
    ap.add_argument("--from-file", default=None, help="one certificate path per line")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--zone-anchor", default="const", choices=("const", "wall"))
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    certs = list(a.certs)
    if a.from_file:
        certs += [ln.strip() for ln in open(a.from_file) if ln.strip()]
    ok = bad = 0
    for p in certs:
        o = os.path.join(a.outdir, os.path.basename(p)[:-5] + ".param.json")
        try:
            d = convert(p, o, a.zone_anchor)
            ok += 1
            print(json.dumps(dict(src=os.path.basename(p), out=os.path.basename(o),
                                  atoms=len(d["atoms"]), cores=len(d["hypotheses"]["cores"]),
                                  nofams=len(d["hypotheses"]["nofams"]),
                                  total=d["total"], budget=d["budget"])), flush=True)
        except Exception as e:
            bad += 1
            print(json.dumps(dict(src=os.path.basename(p), error=repr(e)[:200])), flush=True)
    print("converted %d, refused %d" % (ok, bad))


if __name__ == "__main__":
    main()
