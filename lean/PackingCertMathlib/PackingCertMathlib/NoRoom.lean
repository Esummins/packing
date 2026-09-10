import Mathlib.Tactic
import PackingCertMathlib.Attain

/-!
# The NO-ROOM leaf — Lemma 1 (pocket counting bound) of A189 (A192)

`attempts/A189-noroom/code/noroom189.py` (header, LEMMA 1 [T]): at a node with `k` boxed roles
the remaining `M = n − k` free unit squares have pairwise disjoint interiors, lie in the
container and miss every boxed role's exact core.  A bisection of the free square's
`(centre, tilt)` space certifies every DROPPED piece ("every pose there meets a core"), so every
free pose has its centre in the residue; the residue's centres are covered by finitely many
closed axis-aligned rectangles `P_1..P_r` with non-empty interior (the POCKETS), and the lane
cover returns for each pocket a bound `LANE(P_j)` on the number of pairwise interior-disjoint
free squares whose interiors meet `int P_j`.  Then `M ≤ Σ_j LANE(P_j)`, and the node is DEAD as
soon as the right-hand side is below `M`.

Two facts carry the lemma, both proved here:

* `interior_meets_of_centre_mem` — a unit square whose CENTRE lies in a closed rectangle with
  non-empty interior has its interior meeting the rectangle's interior (the centre is an
  interior point of the square, `mem_interior_iff_uv`, and every neighbourhood of a point of a
  closed rectangle meets its interior: `closure (Ioo a b) = Icc a b`);
* `pocket_bound` — the counting: assign each free square a pocket it meets; the fibres are
  bounded by the lanes (`Finset.card_eq_sum_card_fiberwise`).

`noroom_dead` is the leaf: pockets covering the centres, lanes summing below `M` ⇒ no such
family exists.  What is NOT here: the lane cover's own soundness (`LANE(P) ≥ #meeters`, A141 /
A161's `multibox.Node.lane`, an exact geometric test) and the residue cover (that the dropped
pieces are dead) — both are the certificate's data, stated as hypotheses.  No axiom.
-/

namespace PackingCert
namespace S11
namespace NoRoom

open Set

noncomputable section

/-- A closed axis-aligned rectangle with non-empty interior (a pocket). -/
structure Pocket where
  x0 : ℝ
  x1 : ℝ
  y0 : ℝ
  y1 : ℝ
  hx : x0 < x1
  hy : y0 < y1

/-- The closed rectangle. -/
def Pocket.set (P : Pocket) : Set RP := Icc P.x0 P.x1 ×ˢ Icc P.y0 P.y1

/-- The centre of a parametrised square is an interior point of the square. -/
theorem centre_mem_interior (q : PSq) : (q.cx, q.cy) ∈ interior q.set := by
  rw [mem_interior_iff_uv]
  simp only [sub_self, rdot, zero_mul, add_zero, abs_zero]
  norm_num

/-- A point of a closed rectangle with non-empty interior is in the closure of its interior. -/
theorem mem_closure_interior_pocket (P : Pocket) {p : RP} (hp : p ∈ P.set) :
    p ∈ closure (interior P.set) := by
  unfold Pocket.set at hp ⊢
  rw [interior_prod_eq, interior_Icc, interior_Icc, closure_prod_eq, closure_Ioo P.hx.ne,
    closure_Ioo P.hy.ne]
  exact hp

/-- **Lemma 1, the geometric step.**  A unit square whose centre lies in a pocket has its
interior meeting the pocket's interior. -/
theorem interior_meets_of_centre_mem (P : Pocket) (q : PSq) (hc : (q.cx, q.cy) ∈ P.set) :
    (interior q.set ∩ interior P.set).Nonempty := by
  have h := mem_closure_interior_pocket P hc
  rw [mem_closure_iff] at h
  exact h (interior q.set) isOpen_interior (centre_mem_interior q)

/-- **Lemma 1, the counting.**  `M` pairwise interior-disjoint squares, each meeting (interior
to interior) some pocket `P j`; if any sub-family of pairwise interior-disjoint members meeting
`P j` has at most `lane j` members, then `M ≤ Σ_j lane j`. -/
theorem pocket_bound {M r : ℕ} (q : Fin M → PSq)
    (hdisj : ∀ i j, i ≠ j → Disjoint (interior (q i).set) (interior (q j).set))
    (P : Fin r → Pocket) (lane : Fin r → ℕ)
    (hlane : ∀ j, ∀ G : Finset (Fin M),
      (∀ i ∈ G, ∀ i' ∈ G, i ≠ i' → Disjoint (interior (q i).set) (interior (q i').set)) →
      (∀ i ∈ G, (interior (q i).set ∩ interior (P j).set).Nonempty) → G.card ≤ lane j)
    (hcov : ∀ i, ∃ j, (interior (q i).set ∩ interior (P j).set).Nonempty) :
    M ≤ ∑ j, lane j := by
  classical
  choose f hf using hcov
  have h := Finset.card_eq_sum_card_fiberwise (s := Finset.univ) (t := Finset.univ) (f := f)
    (fun _ _ => Finset.mem_univ _)
  rw [Finset.card_univ, Fintype.card_fin] at h
  rw [h]
  refine Finset.sum_le_sum fun j _ => ?_
  refine hlane j _ (fun i _ i' _ hii => hdisj i i' hii) ?_
  intro i hi
  rw [Finset.mem_filter] at hi
  rw [← hi.2]
  exact hf i

/-- **The NO-ROOM leaf.**  If the centres of the free squares are covered by the pockets and the
lanes sum to less than `M`, no such family of `M` squares exists. -/
theorem noroom_dead {M r : ℕ} (q : Fin M → PSq)
    (hdisj : ∀ i j, i ≠ j → Disjoint (interior (q i).set) (interior (q j).set))
    (P : Fin r → Pocket) (lane : Fin r → ℕ)
    (hlane : ∀ j, ∀ G : Finset (Fin M),
      (∀ i ∈ G, ∀ i' ∈ G, i ≠ i' → Disjoint (interior (q i).set) (interior (q i').set)) →
      (∀ i ∈ G, (interior (q i).set ∩ interior (P j).set).Nonempty) → G.card ≤ lane j)
    (hcent : ∀ i, ∃ j, ((q i).cx, (q i).cy) ∈ (P j).set)
    (hsum : ∑ j, lane j < M) : False := by
  have hcov : ∀ i, ∃ j, (interior (q i).set ∩ interior (P j).set).Nonempty := by
    intro i
    obtain ⟨j, hj⟩ := hcent i
    exact ⟨j, interior_meets_of_centre_mem (P j) (q i) hj⟩
  have := pocket_bound q hdisj P lane hlane hcov
  omega

end

end NoRoom
end S11
end PackingCert
