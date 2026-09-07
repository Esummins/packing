"""A119 T2 -- generate lean/PackingCertMathlib/PackingCertMathlib/Local.lean.

The fixed part (definitions, the RELAX algebra, COVER, Theorem LOCAL's composition into a
`ClassKilledAt`-shaped clause) is the template below; the generated part is the CONCRETE leaf
lemmas -- the lowest closed leaves of a certificate, with their relaxed rows written out as
rational-coefficient hypotheses and the kill closed by `linarith` (the Farkas multipliers, all
multiples of 2^-40, are listed in each lemma's docstring).

The rows are rebuilt by `check_local.py` (exact dyadic interval arithmetic) and then ROUNDED
OUTWARD to rationals with denominator 10^15: each emitted coefficient is the rounded one and
the emitted constant is lowered by the total rounding slack over the variable box, so the
emitted row is IMPLIED by the true relaxed row and the Lean lemma is applicable.

Usage: python gen_local_lean.py <cert.json.gz> [--leaves 3]
"""
from __future__ import annotations
import argparse, gzip, json, math, os, sys, time
from fractions import Fraction as Q

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_local as C
from exactiv import SCALE

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "lean", "PackingCertMathlib", "PackingCertMathlib", "Local.lean")
DEN = 10 ** 15


def rnd(q: Q):
    return Q(round(q * DEN), DEN)


def flr(q: Q):
    return Q(math.floor(q * DEN), DEN)


def clg(q: Q):
    return Q(math.ceil(q * DEN), DEN)


def lean_rat(q: Q):
    if q.denominator == 1:
        return "(%d : ℝ)" % q.numerator
    return "((%d : ℝ) / %d)" % (q.numerator, q.denominator)


def vname(v, nv):
    return "s" if v == 0 else "v%d" % v


def emit_leaf(name, cap, meta, idx):
    """one leaf: the rounded rows, the box bounds, and the linarith kill."""
    nv = meta["nv"]
    box = cap["box"]
    rows = cap["rows"]
    y = cap["y"]
    hyps, comments = [], []
    for n, (key, val) in enumerate(sorted(y.items(), key=lambda kv: str(kv[0]))):
        f = rows[key]
        co, slack = {}, Q(0)
        for v, a in f.co.items():
            am = Q(a.lo + a.hi, 2 * SCALE)
            r = rnd(am)
            co[v] = r
            wid = max(abs(Q(a.lo, SCALE) - r), abs(Q(a.hi, SCALE) - r))
            b = box[v]
            slack += wid * max(abs(Q(b.lo, SCALE)), abs(Q(b.hi, SCALE)))
        k = flr(Q(f.k.lo, SCALE) - slack) - Q(1, DEN)
        terms = []
        for v in sorted(co):
            if co[v] == 0:
                continue
            terms.append("%s * %s" % (lean_rat(co[v]), vname(v, nv)))
        if k != 0:
            terms.append(lean_rat(k))
        expr = " + ".join(terms) if terms else "(0 : ℝ)"
        hyps.append("    (h%d : %s ≤ 0)" % (n, expr))
        comments.append("  h%-3d  y = %-22s  row %s" % (n, str(val), "|".join(str(x) for x in key)))
    bnds = []
    for v in range(nv):
        b = box[v]
        bnds.append("    (bl%d : %s ≤ %s) (bh%d : %s ≤ %s)"
                    % (v, lean_rat(flr(Q(b.lo, SCALE))), vname(v, nv),
                       v, vname(v, nv), lean_rat(clg(Q(b.hi, SCALE)))))
    args = " ".join(vname(v, nv) for v in range(nv))
    doc = ("/-- **LEAF %d of `%s`** (Lemma LEAF, `docs/proofs/local_certificate.md` §2).  The\n"
           "relaxed rows of one (tilt cell, selection) leaf, with the tilt cell\n%s\nand the\n"
           "selections %s.  The certified bound of this leaf is %s > s0 = 3.877084; the rational\n"
           "Farkas multipliers (denominator 2^40) that produce it are\n\n%s\n-/"
           % (idx, meta["id"],
              "  " + ", ".join("%s in [%.6f, %.6f] rad" % (k, float(a), float(b))
                               for k, (a, b) in sorted(cap["cells"].items())),
              ", ".join("%s := %s" % (k, v) for k, v in sorted(cap["sel"].items())) or "(none)",
              "%.9f" % float(cap["bound"]), "\n".join(comments)))
    body = ("theorem %s (%s : ℝ)\n%s\n%s :\n    (969271 : ℝ) / 250000 < s := by\n  linarith\n"
            % (name, args, "\n".join(bnds), "\n".join(hyps)))
    return doc + "\n" + body


TEMPLATE_HEAD = r'''/-
# `Local.lean` — Theorem LOCAL as a Lean object (A119 T2, from A116)

The certificate of `docs/proofs/local_certificate.md`: a NEIGHBOURHOOD `N` of a known minimum
`z*`, given by one axis-aligned box per load-bearing square `ℓ ∈ L` and one slack core per class
pin `p ∈ P`, contains no packing of side `≤ s0`.  §8 of that document fixes the Lean shape and
this file follows it:

* **the objects** — `Box`, `Pin`, `LocalHyp` (the hypothesis `N`), `LocalDead` (its conclusion);
* **Lemma SAT** (`sat_selection`) — interior-disjoint unit squares admit one of the eight signed
  separating-axis rows.  Stated here as the file's ONE geometric axiom: `CaseSat.sat_squares`
  gives the closed-square form (four projection overlaps ⇒ the squares MEET), and the passage to
  interiors is the shrink argument of `local_certificate.md` §1 — see the docstring;
* **Lemma COVER** — the finite case split: `cover_bisect` (a tilt interval is the union of its
  two halves), `cover_qsplit` (`le_total` on the q-range), `cover_selection` (the eight
  selections minus the ones excluded by the interval enclosure), all THEOREMS;
* **Lemma RELAX** §3.1 — the affine relaxation over a tilt cell: `axis_decomp` (exact),
  `mccormick_hi` / `mccormick_lo`, `abs_chord`, `chord_of_concave` — all THEOREMS; the two
  trigonometric envelopes `sin_le_sin_abs_le` / `cos_ge_of_abs_le` are proved from Mathlib;
* **Lemma LEAF** — one `linarith` per (cell, leaf) on the relaxed rows.  The generated
  `leaf_*` theorems below are ACTUAL leaves of an ACTUAL certificate
  (`attempts/A119-local-cert-lean/certs/*.cert.json.gz`, re-checked by `check_local.py`), with
  their rows written out as rational-coefficient inequalities and their rational Farkas
  multipliers recorded in the docstring;
* **the composition** — `classKilledAt_of_localDead`: a node whose YES branch is `LocalHyp`
  dies, in the `ClassKilledAt` shape `Composition.lean` consumes.

The file has exactly ONE project axiom, `sat_selection` (Lemma SAT for INTERIORS), and no
`sorry`.  What it does NOT do is derive `LocalDead Ls Ps shat` for a CONCRETE `N` inside Lean:
that step is the recorded finite cover — the bisection tree over the tilt box, the selection case
split per near pair, the impossible selections by interval enclosure, and one `leaf_*` kill per
closed leaf — and it is performed and re-verified, in exact rational arithmetic, by
`attempts/A119-local-cert-lean/code/check_local.py` on the certificate files of
`attempts/A119-local-cert-lean/certs/`.  Status and counts: `notes/lean_status.md`.
-/
import PackingCertMathlib.CaseSat
import PackingCertMathlib.Composition

namespace PackingCert
namespace S11
namespace LocalCert

open Set

noncomputable section

/-! ## 1. The objects -/

/-- One load-bearing square's box: centre in `[cx0, cx1] × [cy0, cy1]`, tilt parameter
`t = tan(θ/2)` in `[t0, t1]`. -/
structure Box where
  cx0 : ℝ
  cx1 : ℝ
  cy0 : ℝ
  cy1 : ℝ
  t0 : ℝ
  t1 : ℝ

/-- A parametrised square lies in a box. -/
def Box.mem (B : Box) (q : PSq) : Prop :=
  q.cx ∈ Icc B.cx0 B.cx1 ∧ q.cy ∈ Icc B.cy0 B.cy1 ∧ q.t ∈ Icc B.t0 B.t1

/-- One class pin: centre `(αx + βx s, αy + βy s) + [−h, h]²`, tilt exactly `0`
(A57's slack cores, `h = δ/√2`, `δ = 10⁻²`). -/
structure Pin where
  ax0 : ℝ
  ax1 : ℝ
  ay0 : ℝ
  ay1 : ℝ
  hh : ℝ

/-- A parametrised square sits in a pin's slack core at side `s`. -/
def Pin.mem (P : Pin) (s : ℝ) (q : PSq) : Prop :=
  |q.cx - (P.ax0 + P.ax1 * s)| ≤ P.hh ∧ |q.cy - (P.ay0 + P.ay1 * s)| ≤ P.hh ∧ q.t = 0

/-- **The local hypothesis `N`** (`local_certificate.md` §1): at side `s`, DISTINCT squares of
`z` occupy every box of `L` and every slack core of `P`.  Nothing is said about the remaining
`11 − |L| − |P|` squares — that is Reduction DROP. -/
def LocalHyp (Ls : List Box) (Ps : List Pin) (s : ℝ) (z : Cfg) : Prop :=
  ∃ wL : Fin Ls.length → Fin 11, ∃ wP : Fin Ps.length → Fin 11,
    Function.Injective wL ∧ Function.Injective wP ∧ (∀ i j, wL i ≠ wP j) ∧
    (∀ i, (Ls.get i).mem (z (wL i))) ∧ (∀ j, (Ps.get j).mem s (z (wP j)))

/-- **`Dead(N, s0)`**: no packing of side `≤ s0` satisfies `N`. -/
def LocalDead (Ls : List Box) (Ps : List Pin) (s0 : ℝ) : Prop :=
  ∀ s : ℝ, ∀ z : Cfg, CfgPacking s z → LocalHyp Ls Ps s z → s0 < s

/-! ## 2. The separating-axis rows and Lemma SAT -/

/-- The owner's axis `a_k(θ)`: `k = false` is `(cos θ, sin θ)`, `k = true` is `(−sin θ, cos θ)`. -/
def axk (q : PSq) (k : Bool) : ℝ × ℝ :=
  if k then (-(sinT q.t), cosT q.t) else (cosT q.t, sinT q.t)

/-- The support width `w(Δ) = |cos Δ| + |sin Δ|` of the OTHER square in the owner's frame,
written with the addition formulas so that it is a function of the two tilt parameters. -/
def wrel (qw qo : PSq) : ℝ :=
  |cosT qw.t * cosT qo.t + sinT qw.t * sinT qo.t| +
    |cosT qw.t * sinT qo.t - sinT qw.t * cosT qo.t|

/-- The signed separating-axis row `g_σ` of the selection `σ = (owner `qw`, axis `k`,
sign `eps`)`: `eps (c_o − c_w)·a_k(θ_w) − 1/2 − w(θ_w − θ_o)/2 ≥ 0` says that the two unit
squares do not overlap along `a_k(θ_w)`. -/
def gsel (qw qo : PSq) (k : Bool) (eps : ℝ) : ℝ :=
  eps * ((qo.cx - qw.cx) * (axk qw k).1 + (qo.cy - qw.cy) * (axk qw k).2)
    - 1 / 2 - wrel qw qo / 2

/-- **Lemma SAT** (`local_certificate.md` §1): two unit squares are interior-disjoint iff some
one of their eight signed selections has `g_σ ≥ 0`.  Only the direction used by Lemma COVER is
stated.

Status: **AXIOM [C]**.  `CaseSat.sat_squares` proves the closed-square contrapositive — if the
four projection overlaps hold (`|d₁| ≤ a + (c+|s|)/2`, `|d₂| ≤ …`, and the two rotated ones with
`a = 1/2`), the squares MEET.  The step from "meet" to "interiors meet" is the shrink argument
of §1: with all eight gaps `< 0` the four overlaps are proper, so both squares may be scaled
about their centres by some `λ < 1` and the scaled picture still satisfies `sat_squares`; a
common point of the scaled squares is an interior point of both originals.  Formalising the
choice of `λ` is the open work. -/
axiom sat_selection (qw qo : PSq)
    (h : Disjoint (interior qw.set) (interior qo.set)) :
    (∃ k : Bool, ∃ eps : ℝ, (eps = 1 ∨ eps = -1) ∧ 0 ≤ gsel qw qo k eps) ∨
    (∃ k : Bool, ∃ eps : ℝ, (eps = 1 ∨ eps = -1) ∧ 0 ≤ gsel qo qw k eps)

/-! ## 3. Lemma COVER — the finite case split -/

/-- Bisecting a tilt cell covers it. -/
theorem cover_bisect {t a m b : ℝ} (h : t ∈ Icc a b) : t ∈ Icc a m ∨ t ∈ Icc m b := by
  rcases le_total t m with h1 | h1
  · exact Or.inl ⟨h.1, h1⟩
  · exact Or.inr ⟨h1, h.2⟩

/-- A q-range split is a genuine case distinction. -/
theorem cover_qsplit (q m : ℝ) : q ≤ m ∨ m ≤ q := le_total q m

/-- The selection case split, with the IMPOSSIBLE selections removed: if the interval enclosure
of a selection is strictly negative on the cell (`hex`), that selection cannot be the one Lemma
SAT provides, so the remaining ones cover. -/
theorem cover_selection {P Q : Prop} (h : P ∨ Q) (hex : ¬ Q) : P := h.resolve_right hex

/-! ## 4. Lemma RELAX — the affine relaxation over a tilt cell (§3.1) -/

/-- The exact decomposition of the owner's axis about the cell midpoint:
`ε d·a(θ* + φ) = p cos φ + q sin φ` with `p = ε d·a(θ*)`, `q = ε d·a(θ* + 90°)`.  This is the
identity that makes the relaxation SECOND order in the cell width. -/
theorem axis_decomp (dx dy tm φ : ℝ) :
    dx * Real.cos (tm + φ) + dy * Real.sin (tm + φ)
      = (dx * Real.cos tm + dy * Real.sin tm) * Real.cos φ
        + (-(dx * Real.sin tm) + dy * Real.cos tm) * Real.sin φ := by
  rw [Real.cos_add, Real.sin_add]; ring

/-- McCormick, upper plane 1: `q φ ≤ q_hi φ − h q + q_hi h` for `q ≤ q_hi`, `−h ≤ φ`. -/
theorem mccormick_hi {q φ qh h : ℝ} (hq : q ≤ qh) (hφ : -h ≤ φ) :
    q * φ ≤ qh * φ - h * q + qh * h := by
  nlinarith [mul_nonneg (sub_nonneg.mpr hq) (by linarith : (0 : ℝ) ≤ φ + h)]

/-- McCormick, upper plane 2: `q φ ≤ q_lo φ + h q − q_lo h` for `q_lo ≤ q`, `φ ≤ h`. -/
theorem mccormick_lo {q φ ql h : ℝ} (hq : ql ≤ q) (hφ : φ ≤ h) :
    q * φ ≤ ql * φ + h * q - ql * h := by
  nlinarith [mul_nonneg (sub_nonneg.mpr hq) (sub_nonneg.mpr hφ)]

/-- The chord of `|q|` over `[q_lo, q_hi]` with `q_lo ≤ 0 ≤ q_hi` (denominators cleared):
`(q_hi − q_lo) |q| ≤ (q_hi + q_lo) q − 2 q_lo q_hi`. -/
theorem abs_chord {q ql qh : ℝ} (h1 : ql ≤ q) (h2 : q ≤ qh) (hl : ql ≤ 0) (hh : 0 ≤ qh) :
    (qh - ql) * |q| ≤ (qh + ql) * q - 2 * ql * qh := by
  rcases abs_cases q with ⟨he, _⟩ | ⟨he, _⟩ <;> rw [he] <;> nlinarith

/-- A concave function dominates any affine function that is below it at BOTH ends of an
interval — the chord bound of `w = |cos| + |sin|` on a cell with no interior kink. -/
theorem chord_of_concave {f : ℝ → ℝ} {a b m c u v : ℝ} (hab : a ≤ b)
    (hcv : ConcaveOn ℝ (Icc a b) f) (ha : m * a + c ≤ f a) (hb : m * b + c ≤ f b)
    (hu : 0 ≤ u) (hv : 0 ≤ v) (huv : u + v = 1) :
    m * (u * a + v * b) + c ≤ f (u * a + v * b) := by
  have h := hcv.2 (left_mem_Icc.mpr hab) (right_mem_Icc.mpr hab) hu hv huv
  simp only [smul_eq_mul] at h
  have e1 := mul_le_mul_of_nonneg_left ha hu
  have e2 := mul_le_mul_of_nonneg_left hb hv
  have hc : u * (m * a + c) + v * (m * b + c) = m * (u * a + v * b) + c * (u + v) := by ring
  rw [huv, mul_one] at hc
  linarith

/-- `|sin φ| ≤ sin h` for `|φ| ≤ h ≤ π/2` — the (A) envelope of Lemma RELAX. -/
theorem abs_sin_le_sin {φ h : ℝ} (hh : h ≤ Real.pi / 2) (hφ : |φ| ≤ h) :
    |Real.sin φ| ≤ Real.sin h := by
  have h0 : 0 ≤ h := le_trans (abs_nonneg φ) hφ
  obtain ⟨h1, h2⟩ := abs_le.mp hφ
  have mono : MonotoneOn Real.sin (Icc (-(Real.pi / 2)) (Real.pi / 2)) :=
    Real.strictMonoOn_sin.monotoneOn
  have mφ : φ ∈ Icc (-(Real.pi / 2)) (Real.pi / 2) := ⟨by linarith, by linarith⟩
  have mh : h ∈ Icc (-(Real.pi / 2)) (Real.pi / 2) := ⟨by linarith, hh⟩
  have mnh : -h ∈ Icc (-(Real.pi / 2)) (Real.pi / 2) := ⟨by linarith, by linarith⟩
  have e1 : Real.sin φ ≤ Real.sin h := mono mφ mh h2
  have e2 : Real.sin (-h) ≤ Real.sin φ := mono mnh mφ h1
  rw [Real.sin_neg] at e2
  exact abs_le.mpr ⟨by linarith, e1⟩

/-- `cos h ≤ cos φ` for `|φ| ≤ h ≤ π` — the correction term of Lemma RELAX (A). -/
theorem cos_ge_of_abs_le {φ h : ℝ} (hh : h ≤ Real.pi) (hφ : |φ| ≤ h) :
    Real.cos h ≤ Real.cos φ := by
  rw [← Real.cos_abs φ]
  exact Real.cos_le_cos_of_nonneg_of_le_pi (abs_nonneg _) hh hφ

/-! ## 5. Lemma LEAF — one `linarith` per (cell, leaf), with the rational Farkas multipliers

The theorems below are generated from a certificate file: the variables are the LP's
(`s`, one `(x, y)` per free body, one `(u, v)` per pin, one tilt `t` per free body), the
hypotheses `h0 …` are that leaf's relaxed rows written `row ≤ 0` with rational coefficients, the
hypotheses `bl* / bh*` are the boxes and slack cores, and the conclusion is the kill
`s0 < s`.  `linarith` closes each one; the Farkas vector that certifies it (all multipliers of
the form `k / 2^40`) is listed in the docstring, row by row.
-/

'''

TEMPLATE_TAIL = r'''
/-! ## 6. Theorem LOCAL and the composition into `ClassKilledAt` -/

/-- **Lemma COVER, one pair** (the step `sat_selection` is for): if every selection with `qw` as
owner is IMPOSSIBLE on the cell (the interval enclosures the certificate records), an
interior-disjoint pair must use one of the selections with `qo` as owner. -/
theorem cover_pair (qw qo : PSq) (h : Disjoint (interior qw.set) (interior qo.set))
    (hexc : ∀ (k : Bool) (eps : ℝ), (eps = 1 ∨ eps = -1) → gsel qw qo k eps < 0) :
    ∃ k : Bool, ∃ eps : ℝ, (eps = 1 ∨ eps = -1) ∧ 0 ≤ gsel qo qw k eps := by
  rcases sat_selection qw qo h with ⟨k, e, he, hg⟩ | h2
  · exact absurd hg (not_le.mpr (hexc k e he))
  · exact h2

/-- `LocalDead` from the leaf kills in contradiction form: if no packing satisfying `N` has side
`≤ s0`, then every one has side `> s0`.  (`LocalDead` is definitionally the second form; this is
the shape the tree produces, one `False` per closed leaf.) -/
theorem localDead_of_contradiction {Ls : List Box} {Ps : List Pin} {s0 : ℝ}
    (h : ∀ s : ℝ, ∀ z : Cfg, CfgPacking s z → LocalHyp Ls Ps s z → s ≤ s0 → False) :
    LocalDead Ls Ps s0 :=
  fun s z hz hN => not_le.mp fun hle => h s z hz hN hle

/-- **Theorem LOCAL, consumer form** (`local_certificate.md` §8, T3(a)): a node of class `i`
whose YES branch is the box hypothesis `N` — the class pins plus one box per `ℓ ∈ L` plus the
tilt cut — dies, in the shape `Composition.lean` consumes. -/
theorem classKilledAt_of_localDead {Ls : List Box} {Ps : List Pin} {i : StratumIdx} {m : ℝ}
    (hD : LocalDead Ls Ps shat)
    (hyp : ∀ z : Cfg, CfgPacking m z → InStratum i m z → LocalHyp Ls Ps m z) :
    ClassKilledAt i m := by
  intro z hz hi
  have h := hD m z hz (hyp z hz hi)
  refine ⟨h.le, fun he => ?_⟩
  rw [he] at h
  exact absurd h (lt_irrefl _)

/-- The YES leaf of A112's region tree: at any side `m ≤ s0` the hypothesis is contradictory. -/
theorem localKill_yes {Ls : List Box} {Ps : List Pin} {s0 m : ℝ}
    (hD : LocalDead Ls Ps s0) (hm : m ≤ s0) (z : Cfg)
    (hz : CfgPacking m z) (hN : LocalHyp Ls Ps m z) : False := by
  have := hD m z hz hN
  linarith

end

end LocalCert
end S11
end PackingCert
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cert")
    ap.add_argument("--leaves", type=int, default=2)
    a = ap.parse_args()
    cert = C.load(a.cert)
    ch = C.Checker(cert)
    ch.capture_max = a.leaves
    t0 = time.time()
    ok = ch.walk(cert["root"], ch.root_cells(), {}, {}, {})
    meta = cert["meta"]
    body = []
    for n, cap in enumerate(ch.capture):
        nm = "leaf_%s_%d" % (meta["id"].replace(".", "_").replace("-", "_"), n)
        body.append(emit_leaf(nm, cap, meta, n))
    txt = TEMPLATE_HEAD + "\n\n".join(body) + TEMPLATE_TAIL
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(txt)
    print("wrote %s (%d bytes, %d leaves from %s, checker ok=%s, %.0fs)"
          % (OUT, len(txt), len(ch.capture), meta["id"], ok, time.time() - t0))


if __name__ == "__main__":
    main()
