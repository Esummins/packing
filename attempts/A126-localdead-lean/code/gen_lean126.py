"""A126 T1 -- emit the Lean data + replay files for one extracted certificate.

    python gen_lean126.py results/<id>.leaves.json

Writes (new files only)

  lean/PackingCertMathlib/PackingCertMathlib/LocalCertS07Data.lean   the leaves, string-encoded
  lean/PackingCertMathlib/PackingCertMathlib/LocalCertS07.lean       the replay + the theorem

The leaves are encoded as ONE STRING PER LEAF rather than as nested list literals: 2 302 leaves
with 27 363 rows and 101 629 nonzero coefficients would be ~10^5 numeric literals to ELABORATE,
which is where a generated Lean file of this size dies.  A string literal costs one token; the
decoding is `LocalCert.parseLeaf`, a Lean function, and it runs inside the same `native_decide`
that runs the check.  A mis-decode cannot make the theorem unsound: the decoded leaves are the
subject of BOTH the check and the cover obligation, so a wrong decode makes the obligation
harder, never the conclusion cheaper.

Chunk grammar (every integer is a numerator over `D = 10^den`):

    <infeas 0|1> ; <lo_0 … lo_{nv-1}> ; <hi_0 … hi_{nv-1}> ; <row> | <row> | …
    row  ::=  <k> <y> [<index>:<coefficient>]*

A round trip (decode the emitted text, re-evaluate the Farkas bound in exact rational
arithmetic, require `> s0`) is run here on every leaf before anything is written.
"""
from __future__ import annotations

import argparse, json, math, os, sys, time
from fractions import Fraction as Q

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
LEAN = os.path.join(ROOT, "lean", "PackingCertMathlib", "PackingCertMathlib")
S0 = Q(969271, 250000)
GROUP = 2000                      # leaf records per emitted list literal


def enc_leaf(lf, nv):
    lo = " ".join(str(v) for v in lf["blo"])
    hi = " ".join(str(v) for v in lf["bhi"])
    rows = "|".join(
        " ".join([str(r["k"]), str(r["y"])] + ["%d:%d" % (i, c) for i, c in r["co"]])
        for r in lf["rows"])
    return "%d;%s;%s;%s" % (1 if lf["infeas"] else 0, lo, hi, rows)


def dec_leaf(s, nv, D):
    """the Lean decoder, in Python -- the round-trip guard."""
    f, lo, hi, rows = s.split(";")
    los = [Q(int(t), D) for t in lo.split(" ")]
    his = [Q(int(t), D) for t in hi.split(" ")]
    out = []
    for rs in rows.split("|"):
        toks = rs.split(" ")
        k, y = Q(int(toks[0]), D), Q(int(toks[1]), D)
        sp = {}
        for t in toks[2:]:
            i, c = t.split(":")
            sp[int(i)] = sp.get(int(i), Q(0)) + Q(int(c), D)
        co = [sp.get(j, Q(0)) for j in range(nv)]
        out.append((co, k, y))
    return (f == "1"), list(zip(los, his)), out


def bound_of(infeas, box, rows, nv):
    acc = {} if infeas else {0: Q(1)}
    kacc = Q(0)
    for (co, k, y) in rows:
        assert y >= 0
        for j in range(nv):
            if co[j]:
                acc[j] = acc.get(j, Q(0)) + y * co[j]
        kacc += y * k
    lb = kacc
    for j, c in acc.items():
        lb += min(c * box[j][0], c * box[j][1])
    return lb


def lean_rat(q: Q):
    if q.denominator == 1:
        return "(%d : ℝ)" % q.numerator
    return "((%d : ℝ) / %d)" % (q.numerator, q.denominator)


def tan_half_in(theta: float, up: bool, den: int = 10 ** 12) -> Q:
    """a rational INNER bound of tan(theta/2): >= it when `up`, <= it otherwise."""
    v = math.tan(theta / 2.0)
    if up:
        return Q(math.ceil(v * den) + 1, den)
    return Q(math.floor(v * den) - 1, den)


def straddles(t0: float, t1: float) -> bool:
    """Does the certificate's tilt cell leave the fundamental domain theta in [0, 90 deg]?

    `Box` carries ONE interval in the Lean parameter `t = tan(theta/2)`, and a packing's poses
    are normalised to `t in [0, 1]` (theta in [0, 90 deg]).  A cell that reaches below 0 (or
    above 90 deg) is the union of TWO t-intervals there, because the square's own 90 deg
    symmetry folds the outside part back to the far end, and a single `Box` can only carry the
    inside part.  The emitted box is then STRICTLY SMALLER than the certificate's cell -- still
    sound (a smaller `N` gives a weaker `LocalDead`), but it must be said out loud.
    """
    return t0 < 0.0 or t1 > math.pi / 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("leaves")
    ap.add_argument("--tag", default="S07")
    a = ap.parse_args()
    t0 = time.time()
    d = json.load(open(a.leaves, encoding="utf-8"))
    nv, den = d["nv"], d["den"]
    D = 10 ** den
    tag = a.tag

    chunks, worst = [], None
    for lf in d["leaves"]:
        s = enc_leaf(lf, nv)
        infeas, box, rows = dec_leaf(s, nv, D)
        lb = bound_of(infeas, box, rows, nv)
        thr = Q(0) if infeas else S0
        if not lb > thr:
            sys.exit("round trip failed: bound %s <= %s" % (float(lb), float(thr)))
        m = lb - thr
        if worst is None or m < worst:
            worst = m
        chunks.append(s)
    print("round trip OK on %d leaves, worst margin %.3e" % (len(chunks), float(worst)))

    # ---- the neighbourhood N: boxes for L, slack cores for P
    bodies = {b["name"]: b for b in d["bodies"]}
    boxes, pins = [], []
    for nm in d["L"]:
        b = bodies[nm]
        boxes.append((Q(b["x0"]), Q(b["x1"]), Q(b["y0"]), Q(b["y1"]),
                      tan_half_in(b["t0"], True), tan_half_in(b["t1"], False), nm,
                      b["t0"], b["t1"]))
    for nm in d["P"]:
        b = bodies[nm]
        pins.append((Q(b["ax"][0]), Q(b["ax"][1]), Q(b["ay"][0]), Q(b["ay"][1]), Q(b["hh"]), nm))

    data_path = os.path.join(LEAN, "LocalCert%sData.lean" % tag)
    with open(data_path, "w", encoding="utf-8") as f:
        f.write(DATA_HEAD % dict(id=d["id"], n=len(chunks),
                                 rows=sum(len(l["rows"]) for l in d["leaves"]),
                                 nv=nv, den=den, tag=tag))
        # Groups of GROUP: ONE list literal of 32 570 elements exceeds the elaborator's
        # recursion depth (`maximum recursion depth has been reached` at the first element),
        # while 2 000 elaborates in well under a second.
        ngroups = (len(chunks) + GROUP - 1) // GROUP
        for gi in range(ngroups):
            part = chunks[gi * GROUP:(gi + 1) * GROUP]
            f.write("private def %sChunks%d : List String := [\n" % (tag.lower(), gi))
            f.write(",\n".join('"%s"' % c for c in part))
            f.write("\n]\n\n")
        f.write("/-- The %d leaf records, in %d groups of at most %d (one list literal of %d\n"
                "elements exceeds the elaborator's recursion depth). -/\n"
                % (len(chunks), ngroups, GROUP, len(chunks)))
        f.write("def %sChunks : List String :=\n  %s\n\n"
                % (tag.lower(),
                   " ++\n  ".join("%sChunks%d" % (tag.lower(), gi) for gi in range(ngroups))))
        f.write(DATA_TAIL % dict(tag=tag, tagl=tag.lower(), nv=nv, D=D))
    print("wrote %s (%.2f MB)" % (data_path, os.path.getsize(data_path) / 1e6))

    boxtxt = ",\n  ".join(
        "⟨%s, %s, %s, %s, %s, %s⟩" % (lean_rat(b[0]), lean_rat(b[1]), lean_rat(b[2]),
                                      lean_rat(b[3]), lean_rat(b[4]), lean_rat(b[5]))
        for b in boxes)
    pintxt = ",\n  ".join(
        "⟨%s, %s, %s, %s, %s⟩" % (lean_rat(p[0]), lean_rat(p[1]), lean_rat(p[2]),
                                  lean_rat(p[3]), lean_rat(p[4]))
        for p in pins)
    boxdoc = "\n".join(
        "  * `%s`: centre in [%.9f, %.9f] × [%.9f, %.9f], tilt θ ∈ [%.6f, %.6f] rad,"
        " i.e. t = tan(θ/2) ∈ [%s, %s] (rounded INWARD)%s"
        % (b[6], float(b[0]), float(b[1]), float(b[2]), float(b[3]), b[7], b[8],
           float(b[4]), float(b[5]),
           "  **this cell leaves θ ∈ [0°, 90°]: the box carries only its inside part**"
           if straddles(b[7], b[8]) else "") for b in boxes)
    nstr = sum(1 for b in boxes if straddles(b[7], b[8]))
    if nstr:
        print("NOTE: %d of %d boxes have a tilt cell outside [0, 90 deg]; the emitted Box is "
              "strictly smaller than the certificate's cell there (sound, weaker)"
              % (nstr, len(boxes)))
    pindoc = "\n".join(
        "  * `%s`: centre (%s + %s·s, %s + %s·s) ± %.12f, tilt 0"
        % (p[5], p[0], p[1], p[2], p[3], float(p[4])) for p in pins)
    chk_path = os.path.join(LEAN, "LocalCert%s.lean" % tag)
    with open(chk_path, "w", encoding="utf-8") as f:
        f.write(CHECK % dict(id=d["id"], tag=tag, tagl=tag.lower(), nleaves=len(chunks),
                             nrows=sum(len(l["rows"]) for l in d["leaves"]),
                             nz=sum(len(r["co"]) for l in d["leaves"] for r in l["rows"]),
                             nbisect=d["counts"]["bisect"], nbranch=d["counts"]["branch"],
                             nimp=d["counts"]["imp"] + d["counts"]["imp_sel"],
                             ninfeas=sum(1 for l in d["leaves"] if l["infeas"]),
                             boxes=boxtxt, pins=pintxt, boxdoc=boxdoc, pindoc=pindoc,
                             nL=len(boxes), nP=len(pins), den=den,
                             s_lo=d["s_lo"], s_hi=d["s_hi"]))
    print("wrote %s   (%.1f s)" % (chk_path, time.time() - t0))


DATA_HEAD = r'''import PackingCertMathlib.LocalCert

/-!
# `%(id)s` — the dead leaves of the certificate, string-encoded (A126 T1)

Auto-generated by `attempts/A126-localdead-lean/code/gen_lean126.py` from
`attempts/A119-local-cert-lean/certs/%(id)s.cert.json.gz`
(extracted and re-verified by `code/extract126.py`).  Do not edit by hand.

%(n)d dead leaves, %(rows)d rows, %(nv)d LP variables, every rational on the denominator
`10^%(den)d`.  One string per leaf; the grammar is

    <infeas 0|1> ; <lo_0 … lo_n> ; <hi_0 … hi_n> ; <row> | <row> | …
    row  ::=  <k> <y> [<index>:<coefficient>]*

decoded by `LocalCert.parseLeaf`.  A leaf's box is the OUTWARD rounding of the certificate's,
its rows are the INWARD (weakened) rounding of the true relaxed rows, and its multipliers are
rounded to the same denominator and clamped at `0` — so a leaf that passes here would pass with
the exact numbers, and the Farkas bound was re-evaluated exactly at generation time.
-/

namespace PackingCert
namespace S11
namespace LocalCert
namespace Data

'''

DATA_TAIL = r'''/-- The %(tag)s neighbourhood's dead leaves, decoded. -/
def %(tagl)sLeaves : List CLeaf := %(tagl)sChunks.map (parseLeaf %(nv)d (%(D)d : ℚ))

end Data
end LocalCert
end S11
end PackingCert
'''

CHECK = r'''import PackingCertMathlib.LocalCert%(tag)sData

/-!
# `LocalDead` for the concrete neighbourhood `%(id)s` — A126 T1

The A119 certificate `%(id)s` (`attempts/A119-local-cert-lean/certs/`), independently re-checked
by `check_local.py`, has

  * %(nbisect)d tilt-cell bisections, %(nbranch)d selection branches, %(nimp)d impossible-selection leaves,
  * %(nleaves)d DEAD leaves (%(ninfeas)d of them infeasibility rays), %(nrows)d Farkas rows,
    %(nz)d nonzero rational coefficients.

`check_%(tagl)s` runs the reflected weak-duality checker of `LocalCert.lean` on ALL %(nleaves)d of
them at once (`native_decide`), replacing %(nleaves)d `linarith` calls.  `localDead_%(tagl)s` is
Theorem LOCAL for this `N`, modulo the single named cover obligation `CertCover` — see §4 of
`LocalCert.lean` and `attempts/A126-localdead-lean/notes/obligations.md`.

## The neighbourhood `N`

`L` (%(nL)d free bodies, one box each — the tilt interval is stated in the Lean parametrisation
`t = tan(θ/2)` and rounded INWARD, so `N` here is CONTAINED in the certificate's `N`):

%(boxdoc)s

`P` (%(nP)d class pins, A57 slack cores, tilt exactly 0):

%(pindoc)s

Every box above is CONTAINED in the certificate's own cell -- the centre bounds are the
certificate's exact dyadic numbers, the tilt bounds are rounded INWARD, and a tilt cell that
leaves the fundamental domain `theta in [0, 90 deg]` keeps only its inside part (`Box` carries
one interval in `t = tan(theta/2)`, while such a cell is the union of two).  A smaller `N` makes
`LocalHyp` harder to satisfy and `LocalDead` a weaker statement, so this direction is the sound
one; the marked boxes are where it is strict.

The certificate's own side window is `[%(s_lo)s, %(s_hi)s]`; the kill threshold is
`s0 = 969271/250000 = 3.877084 ≥ ŝ`.
-/

namespace PackingCert
namespace S11
namespace LocalCert

open Data

/-- The %(nleaves)d recorded dead leaves of `%(id)s` all pass the reflected weak-duality
check.  Evaluated by `native_decide`: the decoding, the accumulation of `e₀ + Σ y_r row_r`, the
coordinatewise minimisation over each leaf's box and the comparison with `s0` are all exact
rational arithmetic. -/
theorem check_%(tagl)s : %(tagl)sLeaves.all (checkLeaf ((969271 : ℚ) / 250000)) = true := by
  native_decide

/-- The boxes of `L`. -/
noncomputable def %(tagl)sBoxes : List Box := [
  %(boxes)s
  ]

/-- The slack cores of `P`. -/
noncomputable def %(tagl)sPins : List Pin := [
  %(pins)s
  ]

/-- **`LocalDead` for `%(id)s`** — Theorem LOCAL for a concrete `N`, from the kernel-checked
certificate plus the cover obligation.  Everything ARITHMETIC in the certificate (every leaf's
Farkas vector, every box minimisation, %(nrows)d rows) is discharged by `check_%(tagl)s`; the
hypothesis `hcov` is Lemma COVER + Lemma RELAX, i.e. "the recorded leaves cover `N` on the
certificate's own window `[191/50, 974271/250000] = [3.82, 3.897084]`".  That window reaches
ABOVE `s0`, so `hcov` is NOT a consequence of the conclusion — see `LocalCert.CertCover`. -/
theorem localDead_%(tagl)s
    (hcov : CertCover %(tagl)sLeaves %(tagl)sBoxes %(tagl)sPins
      ((191 : ℝ) / 50) ((974271 : ℝ) / 250000)) :
    LocalDead %(tagl)sBoxes %(tagl)sPins (((969271 : ℚ) / 250000 : ℚ) : ℝ) :=
  localDead_of_cert (by norm_num) (by push_cast; norm_num) check_%(tagl)s hcov

/-- The same at `ŝ`, the shape `Local.classKilledAt_of_localDead` consumes
(`ŝ ≤ 3877084/1000000 = s0` by `shat_spec`). -/
theorem localDead_%(tagl)s_shat
    (hcov : CertCover %(tagl)sLeaves %(tagl)sBoxes %(tagl)sPins
      ((191 : ℝ) / 50) ((974271 : ℝ) / 250000)) :
    LocalDead %(tagl)sBoxes %(tagl)sPins shat := by
  have h := localDead_%(tagl)s hcov
  intro s z hz hN
  have h1 := h s z hz hN
  have h2 : shat ≤ (((969271 : ℚ) / 250000 : ℚ) : ℝ) := by
    have := shat_spec.2.1.2
    push_cast
    norm_num at this ⊢
    linarith
  linarith

end LocalCert
end S11
end PackingCert
'''


if __name__ == "__main__":
    main()
