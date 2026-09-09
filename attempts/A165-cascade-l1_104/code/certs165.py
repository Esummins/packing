"""A165 -- emit the attempt's certificates into `certs/` and a SHA-256 manifest.

Three kinds:

  `cascade_row_v1`     a chord-row (C) leaf: the minchord sum on one exact rational wall line
                       exceeds `s0`, so A144 LINE-1 is violated and the case is contradictory.
  `cascade_Mzero_v1`   `M(c) = 0`: A161's full separating-axis test over `H`'s parameter box proves
                       no pose of `H` meets the widened corner box, so every corner meeter is a FREE
                       square (this is what licenses the pair branching at that corner).
  `cascade_cover_v1`   one corner's complete cover: the leaf paths are a complete prefix code over
                       the declared root, every discharged leaf carries its reason (and, for a
                       `witness` leaf, the rational point A132's `vertex_ok` certifies twice).

The case-LP certificates are `case-lp-certificate-v1` files written by A150's `lp150.certify` under
this attempt's `certs/` (the driver redirects `lp150.BASE`); they are checked by the FROZEN
`verify_case.py`, unmodified.

    python code/certs165.py --cell l1_104 --depth 8
"""
import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cas165 as K                                               # noqa: E402
import cascade165 as CS                                          # noqa: E402
import polylane as PL                                            # noqa: E402

CERTS = os.path.join(K.BASE, "certs")


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 16), b""):
            h.update(blk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", default="l1_104")
    ap.add_argument("--depth", type=int, default=8)
    a = ap.parse_args()
    os.makedirs(CERTS, exist_ok=True)
    cov = json.load(open(CS.cover_path(a.cell, a.depth), encoding="utf-8"))
    written = []

    # --- M(c) = 0
    for c in K.CORNERS:
        det = cov["M_exact"][c]
        if not det["misses"]:
            continue
        p = os.path.join(CERTS, "Mzero_%s_%s.json" % (a.cell, c))
        K.jdump(dict(
            leaf="cascade_Mzero_v1",
            claim="no pose of the conditioned square's parameter box has interior meeting the "
                  "interior of the WIDENED corner box, so M(c) = 0 and every meeter of that "
                  "corner is a FREE square",
            s="969271/250000", cell=a.cell, corner=c,
            widened_box=cov["covers"][c]["cell"], pad_w=cov["w"],
            hyp_box=cov["boxes"][0],
            test="A161 chordlane.box_misses_cell_exact: full separating-axis test over the "
                 "parameter box; axis and exact rational margin below",
            separating_axis=det["detail"],
            consumes=["k0_route.md sec 4.1 Lemma K0-WIDEN",
                      "k0_route.md sec 3 Lemma K0-FREE (for what the count is used for)"],
            checker="code/check165.py C6 (independently coded SAT + 5e4 sampled poses)"), p)
        written.append(p)

    # --- the covers
    for c in K.CORNERS:
        d = cov["covers"][c]
        p = os.path.join(CERTS, "cover_%s_%s_d%d.json" % (a.cell, c, a.depth))
        K.jdump(dict(
            leaf="cascade_cover_v1",
            claim="the leaf boxes tile the declared pose root exactly (complete prefix code); "
                  "every DISCHARGED leaf is empty of admissible free corner-meeting poses by the "
                  "reason recorded; the OPEN boxes are therefore a sound over-approximation of the "
                  "poses a free meeter of the widened corner box can take",
            s="969271/250000", cell=a.cell, corner=c, widened_box=d["cell"],
            root=list(PL.centre_window(d["cell"], K.S0)) + [0.0, 90.0],
            root_rule="centre window = the cell grown by sqrt2/2 and clipped to [1/2, s0-1/2]^2 "
                      "(A141 polylane.centre_window), tilt [0, 90) deg",
            split_rule="widest of (x, y, theta/60), deterministic (A141 polylane.split_box)",
            n_leaves=d["n_leaves"], n_open=d["n_open"],
            leaves=d["leaves"], open=d["open"], open_paths=d["open_paths"],
            discharge=["container (every pose leaves [0,s0]^2)",
                       "misses_cell (one cell normal separates over the whole box)",
                       "witness (a rational point in every pose of the box AND of H: the square "
                       "would BE H, A132 vertex_ok twice = Lean checkVertexInPBox)"],
            checker="code/check165.py C2/C3/C4/C9"), p)
        written.append(p)

    # --- the chord-row (C) leaves
    p = os.path.join(CS.RES, "rowprod_%s.json" % CS.tag(a.cell, a.depth))
    if os.path.exists(p):
        rp = json.load(open(p, encoding="utf-8"))
        for i, ct in enumerate(rp.get("certs", [])):
            q = os.path.join(CERTS, "row_%s_%s_%02d.json" % (a.cell, ct["wall"], i))
            K.jdump(dict(
                leaf="cascade_row_v1",
                claim="the certified minimum chords of the case's squares on one axis-parallel "
                      "line already sum to more than s0, contradicting A144 LINE-1 (the chords of "
                      "an interior-disjoint family in [0,s0]^2 on an axis line sum to <= s0): the "
                      "case is a (C) leaf, no LP",
                s="969271/250000", cell=a.cell, wall=ct["wall"], corners=ct["corners"],
                case1=ct["case1"], case2=ct["case2"], boxes=ct["boxes"],
                line=dict(orient=ct["row"]["orient"], off=ct["row"]["off"]),
                minchords=ct["row"]["minchords"], rhs=ct["row"]["rhs"],
                rhs_negative=ct["exact_rhs_negative"],
                distinctness="(R6) s0 - 2(1+w) - sqrt2 = %+.9f > 0, so the two corner crowds are "
                             "disjoint sets of squares; M(c) = 0 puts H outside both"
                             % cov["r6_gap"],
                method="A144 guardline.minchord_box, exact five-point rule, Fractions throughout",
                checker="code/check165.py C7 (minchord re-derived by an independent exact route, "
                        "compared in the HARD direction)"), q)
            written.append(q)

    # --- the manifest
    rows = []
    for f in sorted(os.listdir(CERTS)):
        fp = os.path.join(CERTS, f)
        if os.path.isfile(fp) and f.endswith(".json"):
            rows.append(dict(file=f, bytes=os.path.getsize(fp), sha256=sha(fp)))
    K.jdump(dict(attempt="A165", cell=a.cell, depth=a.depth, n=len(rows), files=rows),
            os.path.join(CS.RES, "cert_manifest_%s.json" % a.cell))
    print("wrote %d certificates + manifest (%d files hashed)" % (len(written), len(rows)),
          flush=True)


if __name__ == "__main__":
    main()
