import PackingCertMathlib.SatInterior

/-!
# The reflected leaf checker of a local certificate — A126 T1

`Local.lean` (A119) emits ONE `theorem … := by linarith` per closed leaf of an A119 certificate
and could only afford three of them.  A real neighbourhood has thousands: `S07 (0.1, 40°)` has
2 302 dead leaves and 27 363 Farkas multipliers.  This file replaces the 2 302 `linarith` calls
by ONE `native_decide` on a Lean FUNCTION over the certificate data, proved sound once:

* `CRow` / `CLeaf` — a leaf of the certificate: its variable box, and the relaxed rows named by
  the Farkas multipliers, each row `Σ_j co_j x_j + k ≤ 0` with its multiplier `y ≥ 0`.  All
  coefficients are rationals; the generator (`attempts/A126-localdead-lean/code/extract126.py`)
  rounds the true rows OUTWARD, so an emitted row is IMPLIED by the true relaxed row and an
  emitted box CONTAINS the true one.
* `checkLeaf` — weak duality, decided exactly: accumulate `e₀ + Σ_r y_r · row_r` (an
  infeasibility ray accumulates `Σ_r y_r · row_r` alone), minimise the accumulated affine form
  over the box coordinatewise, and compare with `s0` (a ray: with `0`).
* `checkLeaf_sound` — a passing leaf whose rows hold at a point of its box has `s0 < x₀`.  No
  axioms beyond the standard three.

What the checker does NOT do is derive the rows from the geometry, nor prove that the recorded
leaves COVER the neighbourhood: those are Lemma RELAX and Lemma COVER, and they are named here
as `LeafHolds` / `CertCover` and consumed by `localDead_of_cert`.  `SatInterior.cover_pair'` and
`Local.cover_bisect` are the two proved ingredients of `CertCover`; what is missing between them
and `CertCover` is a certified rational enclosure of `cos` / `sin` over a rational tilt cell —
see `attempts/A126-localdead-lean/notes/obligations.md`.
-/

namespace PackingCert
namespace S11
namespace LocalCert

open Set

/-! ## 1. Affine forms over the LP variables -/

/-- `evalL co x i = Σ_j co[j] · x (i + j)` — a POSITIONAL coefficient list. -/
def evalL : List ℚ → (Nat → ℝ) → Nat → ℝ
  | [], _, _ => 0
  | a :: t, x, i => (a : ℝ) * x i + evalL t x (i + 1)

/-- Coefficientwise sum, tolerating different lengths. -/
def addL : List ℚ → List ℚ → List ℚ
  | [], v => v
  | u, [] => u
  | a :: u, b :: v => (a + b) :: addL u v

/-- Coefficientwise scaling. -/
def smulL (c : ℚ) : List ℚ → List ℚ
  | [] => []
  | a :: t => c * a :: smulL c t

/-- `x` lies in the box `b` from coordinate `i` on. -/
def InBox : List (ℚ × ℚ) → (Nat → ℝ) → Nat → Prop
  | [], _, _ => True
  | b :: t, x, i => (b.1 : ℝ) ≤ x i ∧ x i ≤ (b.2 : ℝ) ∧ InBox t x (i + 1)

/-- The exact minimum of an affine form's LINEAR part over a box, coordinate by coordinate;
`none` when the box is shorter than the form (then nothing is claimed). -/
def minL : List ℚ → List (ℚ × ℚ) → Option ℚ
  | [], _ => some 0
  | a :: u, b :: t => (minL u t).map (fun r => min (a * b.1) (a * b.2) + r)
  | _ :: _, [] => none

theorem evalL_addL (u v : List ℚ) (x : Nat → ℝ) (i : Nat) :
    evalL (addL u v) x i = evalL u x i + evalL v x i := by
  induction u generalizing v i with
  | nil => simp [addL, evalL]
  | cons a u ih =>
    cases v with
    | nil => simp [addL, evalL]
    | cons b v =>
      simp only [addL, evalL, ih]
      push_cast
      ring

theorem evalL_smulL (c : ℚ) (u : List ℚ) (x : Nat → ℝ) (i : Nat) :
    evalL (smulL c u) x i = (c : ℝ) * evalL u x i := by
  induction u generalizing i with
  | nil => simp [smulL, evalL]
  | cons a u ih =>
    simp only [smulL, evalL, ih]
    push_cast
    ring

theorem evalL_one (x : Nat → ℝ) (i : Nat) : evalL [1] x i = x i := by
  simp [evalL]

/-- The coordinatewise minimum is a genuine lower bound on the box. -/
theorem minL_le : ∀ (u : List ℚ) (b : List (ℚ × ℚ)) (v : ℚ) (x : Nat → ℝ) (i : Nat),
    minL u b = some v → InBox b x i → (v : ℝ) ≤ evalL u x i := by
  intro u
  induction u with
  | nil =>
    intro b v x i h _
    simp only [minL, Option.some.injEq] at h
    simp [evalL, ← h]
  | cons a u ih =>
    intro b v x i h hb
    cases b with
    | nil => simp [minL] at h
    | cons c t =>
      simp only [minL, Option.map_eq_some_iff] at h
      obtain ⟨r, hr, hv⟩ := h
      obtain ⟨hlo, hhi, hrest⟩ := hb
      have hrec := ih t r x (i + 1) hr hrest
      have hterm : ((min (a * c.1) (a * c.2) : ℚ) : ℝ) ≤ (a : ℝ) * x i := by
        rcases le_total 0 a with ha | ha
        · have ha' : (0 : ℝ) ≤ (a : ℝ) := by exact_mod_cast ha
          have h1 : ((a * c.1 : ℚ) : ℝ) ≤ (a : ℝ) * x i := by
            push_cast
            nlinarith [hlo, ha']
          exact le_trans (by exact_mod_cast min_le_left (a * c.1) (a * c.2)) h1
        · have ha' : (a : ℝ) ≤ 0 := by exact_mod_cast ha
          have h1 : ((a * c.2 : ℚ) : ℝ) ≤ (a : ℝ) * x i := by
            push_cast
            nlinarith [hhi, ha']
          exact le_trans (by exact_mod_cast min_le_right (a * c.1) (a * c.2)) h1
      have : ((min (a * c.1) (a * c.2) + r : ℚ) : ℝ) ≤ (a : ℝ) * x i + evalL u x (i + 1) := by
        push_cast
        push_cast at hterm
        linarith
      rw [← hv]
      simpa [evalL] using this

/-! ## 2. Leaves and the weak-duality check -/

/-- One relaxed row of a leaf with its Farkas multiplier: `Σ_j co_j x_j + k ≤ 0`, `y ≥ 0`. -/
structure CRow where
  co : List ℚ
  k : ℚ
  y : ℚ
deriving Inhabited, Repr

/-- One closed leaf: the leaf's variable box (the `s` range, the boxes / slack cores, and the
TILT CELL), and the rows the Farkas vector names.  `infeas` marks an infeasibility RAY —
the rows alone are contradictory on the box, with no `s` column. -/
structure CLeaf where
  infeas : Bool
  box : List (ℚ × ℚ)
  rows : List CRow
deriving Inhabited, Repr

/-- `Σ_r y_r · row_r`, as an affine form. -/
def accum : List CRow → List ℚ × ℚ
  | [] => ([], 0)
  | r :: t => (addL (smulL r.y r.co) (accum t).1, r.y * r.k + (accum t).2)

/-- The accumulated form of a leaf: `e₀ + Σ y_r row_r`, or `Σ y_r row_r` for a ray. -/
def leafForm (L : CLeaf) : List ℚ × ℚ :=
  (if L.infeas then (accum L.rows).1 else addL [1] (accum L.rows).1, (accum L.rows).2)

/-- **The leaf check**: every multiplier is nonnegative, and the accumulated form's exact
minimum over the box exceeds `s0` (a ray: exceeds `0`). -/
def checkLeaf (s0 : ℚ) (L : CLeaf) : Bool :=
  L.rows.all (fun r => 0 ≤ r.y) &&
    (match minL (leafForm L).1 L.box with
     | none => false
     | some v => decide ((if L.infeas then 0 else s0) < v + (leafForm L).2))

/-- The leaf's rows hold, and its box contains, the variable vector `x`. -/
def LeafHolds (L : CLeaf) (x : Nat → ℝ) : Prop :=
  InBox L.box x 0 ∧ ∀ r ∈ L.rows, evalL r.co x 0 + (r.k : ℝ) ≤ 0

theorem accum_le (rows : List CRow) (x : Nat → ℝ)
    (hy : ∀ r ∈ rows, 0 ≤ r.y) (hr : ∀ r ∈ rows, evalL r.co x 0 + (r.k : ℝ) ≤ 0) :
    evalL (accum rows).1 x 0 + (((accum rows).2 : ℚ) : ℝ) ≤ 0 := by
  induction rows with
  | nil => simp [accum, evalL]
  | cons r t ih =>
    have h1 := ih (fun q hq => hy q (List.mem_cons_of_mem _ hq))
      (fun q hq => hr q (List.mem_cons_of_mem _ hq))
    have h2 := hr r (List.mem_cons_self ..)
    have h3 : (0 : ℝ) ≤ (r.y : ℝ) := by exact_mod_cast hy r (List.mem_cons_self ..)
    have h4 : (r.y : ℝ) * (evalL r.co x 0 + (r.k : ℝ)) ≤ 0 := mul_nonpos_of_nonneg_of_nonpos h3 h2
    simp only [accum, evalL_addL, evalL_smulL]
    push_cast
    push_cast at h1 h4
    linarith

/-- **Soundness of the leaf check.**  If the recorded rows hold at a point of the recorded box
and the check passes, the side variable exceeds `s0`. -/
theorem checkLeaf_sound {s0 : ℚ} {L : CLeaf} {x : Nat → ℝ}
    (hL : LeafHolds L x) (h : checkLeaf s0 L = true) : (s0 : ℝ) < x 0 := by
  obtain ⟨hb, hr⟩ := hL
  rw [checkLeaf, Bool.and_eq_true, List.all_eq_true] at h
  obtain ⟨hy, hm⟩ := h
  have hy' : ∀ r ∈ L.rows, 0 ≤ r.y := by
    intro r hrm
    have := hy r hrm
    simpa using this
  have hacc := accum_le L.rows x hy' hr
  revert hm
  cases hmin : minL (leafForm L).1 L.box with
  | none => intro hm; simp [hmin] at hm
  | some v =>
    intro hm
    simp only [hmin, decide_eq_true_eq] at hm
    have hlow : (v : ℝ) ≤ evalL (leafForm L).1 x 0 := minL_le _ _ _ _ _ hmin hb
    by_cases hi : L.infeas
    · exfalso
      have hform : (leafForm L).1 = (accum L.rows).1 := by simp [leafForm, hi]
      rw [hform] at hlow
      simp only [hi, if_true] at hm
      have : ((v + (accum L.rows).2 : ℚ) : ℝ) ≤ 0 := by
        push_cast
        have h2 : ((leafForm L).2 : ℚ) = (accum L.rows).2 := rfl
        linarith
      have hpos : (0 : ℝ) < ((v + (leafForm L).2 : ℚ) : ℝ) := by exact_mod_cast hm
      have h2 : ((leafForm L).2 : ℚ) = (accum L.rows).2 := rfl
      rw [h2] at hpos
      linarith
    · have hform : (leafForm L).1 = addL [1] (accum L.rows).1 := by simp [leafForm, hi]
      rw [hform, evalL_addL, evalL_one] at hlow
      simp only [hi, if_false] at hm
      have hlt : ((s0 : ℚ) : ℝ) < ((v + (leafForm L).2 : ℚ) : ℝ) := by exact_mod_cast hm
      have h2 : ((leafForm L).2 : ℚ) = (accum L.rows).2 := rfl
      rw [h2] at hlt
      push_cast at hlt ⊢
      linarith

/-! ## 3. The decoder

A neighbourhood's certificate has 10⁵ rational coefficients.  Emitting them as nested list
literals costs 10⁵ numeric literals to ELABORATE, which is where a generated file of this size
dies; emitting them as one STRING per leaf costs one token per leaf and moves the decoding into
the same compiled evaluation that runs the check.  A wrong decode cannot make the theorem
unsound: `localDead_of_cert` quantifies the cover obligation over the DECODED leaves, so a
wrong decode makes the obligation harder to discharge, never the conclusion cheaper. -/

private def toI (s : String) : Int := s.toInt?.getD 0

/-- `"<index>:<coefficient>"` tokens into a dense positional coefficient list of length `nv`. -/
def parseCo (nv : Nat) (den : ℚ) (toks : List String) : List ℚ :=
  let sp : List (Nat × ℚ) := toks.filterMap fun t =>
    match t.splitOn ":" with
    | [i, c] => some (i.toNat?.getD 0, (toI c : ℚ) / den)
    | _ => none
  (List.range nv).map fun j => sp.foldl (fun acc p => if p.1 = j then acc + p.2 else acc) 0

/-- `"<k> <y> [<index>:<coefficient>]*"`. -/
def parseRow (nv : Nat) (den : ℚ) (s : String) : CRow :=
  match s.splitOn " " with
  | k :: y :: rest => ⟨parseCo nv den rest, (toI k : ℚ) / den, (toI y : ℚ) / den⟩
  | _ => default

/-- One leaf: `"<infeas>;<lo…>;<hi…>;<row>|<row>|…"`. -/
def parseLeaf (nv : Nat) (den : ℚ) (s : String) : CLeaf :=
  match s.splitOn ";" with
  | [f, lo, hi, rows] =>
      ⟨f == "1",
       ((lo.splitOn " ").map fun t => (toI t : ℚ) / den).zip
         ((hi.splitOn " ").map fun t => (toI t : ℚ) / den),
       (rows.splitOn "|").map (parseRow nv den)⟩
  | _ => default

/-! ## 4. The cover obligation and Theorem LOCAL

`CertCover` is what Lemma COVER + Lemma RELAX deliver and the checker consumes: for every
packing that satisfies the neighbourhood hypothesis there is ONE recorded leaf whose box
contains the configuration's LP variable vector and whose rows hold there.  The variable vector
is existentially quantified with its first coordinate pinned to the side, which is exactly the
freedom the certificate's own body-to-variable numbering uses. -/
def CertCover (leaves : List CLeaf) (Ls : List Box) (Ps : List Pin) (s0 : ℝ) : Prop :=
  ∀ s : ℝ, ∀ z : Cfg, s ≤ s0 → CfgPacking s z → LocalHyp Ls Ps s z →
    ∃ x : Nat → ℝ, x 0 = s ∧ ∃ L ∈ leaves, LeafHolds L x

/-- **Theorem LOCAL from a checked certificate.**  If every recorded leaf passes the reflected
weak-duality check and the recorded leaves cover the neighbourhood, then `N` is dead at `s0`. -/
theorem localDead_of_cert {leaves : List CLeaf} {Ls : List Box} {Ps : List Pin} {s0 : ℚ}
    (hchk : leaves.all (checkLeaf s0) = true)
    (hcov : CertCover leaves Ls Ps (s0 : ℝ)) :
    LocalDead Ls Ps (s0 : ℝ) := by
  intro s z hz hN
  by_contra hle
  push Not at hle
  obtain ⟨x, hx0, L, hLmem, hLh⟩ := hcov s z hle hz hN
  rw [List.all_eq_true] at hchk
  have := checkLeaf_sound hLh (hchk L hLmem)
  rw [hx0] at this
  linarith

end LocalCert
end S11
end PackingCert
