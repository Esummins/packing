import PackingCertMathlib.TopLevel
import PackingCertMathlib.CensusSelection

/-!
# The uniqueness clause via the CC-2 chain and Theorem U (A78 T4, depgraph node A.UNIQ)

`docs/proofs/unique_transfer.md` §2–§4, formalised against the census layer now that
`InStratum` is definitional.  `TopLevel.unique_transfer` is discharged by census
exhaustiveness alone (§1); the HONEST route to the uniqueness clause — the one that does
not feed an arbitrary packing to `stratum_kill`'s ∀-packings quantifier at the
K1-protected classes — is the chain + collapse of §2–§4, stated here with its two
remaining obligations as explicit hypotheses:

* **(U-O2, H10-stuck)** `hstuck` — no TELEPORT-STUCK packing at side `ŝ` has skeleton in a
  non-Trump class (`stratum_kill` restricted to stuck packings; this is what the H10
  machinery can prove, `unique_transfer.md` §3);
* **(U-O1, Theorem U)** `hU` — one-square rigidity of ẑ: a packing at `ŝ` that agrees with
  a G-image of ẑ in all but one square IS a G-image of ẑ (A65's 11 re-insertion
  certificates + `docs/proofs/theorem_u.md`, consumed here as an interface — the
  certificate-level discharge is A.THMU).

`unique_via_chain`: under these two hypotheses, and the axioms `trump_residual` + `basin`
(U-O4, the Trump-stratum endpoint), EVERY packing at `ŝ` is a G-image of ẑ.  Proof: strong
induction on `11 − k` (`skeleton_card_le`): a non-stuck packing has a CC-2 teleport move
(`teleport_packing`, `card_lt_teleport` — `k` strictly increases, the move changes ONE
square), so the induction hypothesis gives that the moved packing is Trump, and Theorem U
collapses back; a stuck packing lies in some stratum (`exists_stratum`), which `hstuck`
forces to be Trump's, and `trump_residual` + `basin` finish exactly as in
`s_eleven_unique`.  `s_eleven_unique_of_chain` is the theorem-level clause obtained
WITHOUT `stratum_kill` and WITHOUT `unique_transfer`.

The chain of `unique_transfer.md` §2 is the recursion of this induction; the H1 degenerate
cases are absent by the shape of the statements (A75, `Selection.lean`).
-/

namespace PackingCert
namespace S11

noncomputable section

open Set

/-- `z` is a G-image of ẑ: a container symmetry and a relabelling carry ẑ onto `z`
(the conclusion form of `s_eleven_unique`). -/
def IsTrumpImage (z : Cfg) : Prop :=
  ∃ (f : RP → RP) (e : Equiv.Perm (Fin 11)),
    IsCtrSym shat f ∧ ∀ j, (z (e j)).set = f '' (zhat j).set

/-- **Teleport-stuck** (`unique_transfer.md` §2): no CC-2/CC-2′ move is available — for
every completable slot box inside the container and every non-simple square `i`, some
OTHER square interior-meets the box. -/
def TeleportStuck (s : ℝ) (z : Cfg) : Prop :=
  ∀ a : Slot, Completable s z a → slotBox (slotCentre s a) ⊆ container s →
    ∀ i : Fin 11, NonSimple s z i →
      ∃ j, j ≠ i ∧ ¬Disjoint (interior (slotBox (slotCentre s a))) (interior (z j).set)

/-- The Trump-stratum endpoint: `trump_residual` + `basin` (the last three lines of
`s_eleven_unique`), packaged. -/
theorem isTrumpImage_of_trumpStratum {z : Cfg} (hz : CfgPacking shat z)
    (hstr : InStratum trumpStratum shat z) : IsTrumpImage z := by
  obtain ⟨z'', f2, e2, hsym2, hz'', hbasin, hrel2⟩ :=
    trump_residual shat shat_mem_wnd z hz hstr
  have hzz : z'' = zhat := (basin z'' hbasin).2 hz''
  refine ⟨f2, e2, hsym2, fun j => ?_⟩
  rw [hrel2 j, hzz]

/-- **The uniqueness clause via the chain + collapse** (`unique_transfer.md` §2–§4), with
H10-stuck and Theorem U as explicit hypotheses. -/
theorem unique_via_chain
    (hstuck : ∀ z : Cfg, CfgPacking shat z → TeleportStuck shat z →
      ∀ i : StratumIdx, i ≠ trumpStratum → ¬InStratum i shat z)
    (hU : ∀ z z' : Cfg, CfgPacking shat z → CfgPacking shat z' → IsTrumpImage z' →
      (∃ i : Fin 11, ∀ j, j ≠ i → z j = z' j) → IsTrumpImage z) :
    ∀ z : Cfg, CfgPacking shat z → IsTrumpImage z := by
  have h3 : 3 < shat := (wnd_subset_Ioo shat_mem_wnd).1
  have h4 : shat < 4 := (wnd_subset_Ioo shat_mem_wnd).2
  -- strong induction on the slack `11 − k`
  suffices key : ∀ n : ℕ, ∀ z : Cfg, CfgPacking shat z →
      11 - (skeleton shat z).card ≤ n → IsTrumpImage z from
    fun z hz => key _ z hz le_rfl
  intro n
  induction n with
  | zero =>
    intro z hz hn
    -- `k = 11`: every square is simple, so no non-simple square exists and `z` is stuck
    have hk : (skeleton shat z).card = 11 := by
      have := skeleton_card_le h3 h4 z
      omega
    have hstk : TeleportStuck shat z := by
      intro a ha hbox i hi
      exfalso
      -- an injective assignment of the 11 skeleton slots onto `Fin 11` is surjective,
      -- so `i` occupies a skeleton slot — contradicting non-simplicity
      obtain ⟨f, hinj, hocc⟩ := containsPins_skeleton (z := z) h3 h4
      have hsurj : ∀ k : Fin 11, ∃ a ∈ skeleton shat z, f a = k := by
        have himg : (skeleton shat z).image f = Finset.univ := by
          apply Finset.eq_univ_of_card
          rw [Finset.card_image_of_injOn hinj, hk]
          simp
        intro k
        have hk' : k ∈ (skeleton shat z).image f := by rw [himg]; exact Finset.mem_univ k
        obtain ⟨a, ha, hfa⟩ := Finset.mem_image.mp hk'
        exact ⟨a, ha, hfa⟩
      obtain ⟨b, hb, hfb⟩ := hsurj i
      have := hocc b hb
      rw [hfb] at this
      exact hi b hb this
    obtain ⟨i, hi⟩ := exists_stratum shat_mem_wnd hz
    by_cases hit : i = trumpStratum
    · subst hit
      exact isTrumpImage_of_trumpStratum hz hi
    · exact absurd hi (hstuck z hz hstk i hit)
  | succ n ih =>
    intro z hz hn
    by_cases hstk : TeleportStuck shat z
    · obtain ⟨i, hi⟩ := exists_stratum shat_mem_wnd hz
      by_cases hit : i = trumpStratum
      · subst hit
        exact isTrumpImage_of_trumpStratum hz hi
      · exact absurd hi (hstuck z hz hstk i hit)
    · -- a CC-2 move exists: teleport, recurse, collapse
      simp only [TeleportStuck, not_forall, not_exists, not_and, not_not] at hstk
      obtain ⟨a, ha, hbox, i, hi, hfree⟩ := hstk
      have hfree' : ∀ j, j ≠ i →
          Disjoint (interior (slotBox (slotCentre shat a))) (interior (z j).set) :=
        fun j hj => hfree j hj
      have hz' : CfgPacking shat (teleport z i (slotCentre shat a)) :=
        teleport_packing hz i _ hbox hfree'
      have hlt := card_lt_teleport (s := shat) hi ha
      have hn' : 11 - (skeleton shat (teleport z i (slotCentre shat a))).card ≤ n := by
        have := skeleton_card_le h3 h4 (teleport z i (slotCentre shat a))
        omega
      have hT := ih _ hz' hn'
      exact hU z _ hz hz' hT ⟨i, fun j hj => (teleport_ne z i _ hj).symm⟩

/-- **The uniqueness clause without `stratum_kill` and without `unique_transfer`**:
from H10-stuck + Theorem U (+ `trump_residual`, `basin`, `parametrize`).  This is the
statement `s_eleven_unique` of `TopLevel.lean` with the ∀-packings quantifier of
`stratum_kill` at the K1-protected classes REPLACED by its teleport-stuck restriction —
the non-circular route of `unique_transfer.md`. -/
theorem s_eleven_unique_of_chain
    (hstuck : ∀ z : Cfg, CfgPacking shat z → TeleportStuck shat z →
      ∀ i : StratumIdx, i ≠ trumpStratum → ¬InStratum i shat z)
    (hU : ∀ z z' : Cfg, CfgPacking shat z → CfgPacking shat z' → IsTrumpImage z' →
      (∃ i : Fin 11, ∀ j, j ≠ i → z j = z' j) → IsTrumpImage z) :
    ∀ Q : Fin 11 → Set RP, IsPacking 11 shat Q →
      ∃ (f : RP → RP) (e : Equiv.Perm (Fin 11)),
        IsCtrSym shat f ∧ ∀ i, Q i = f '' (zhat (e i)).set := by
  intro Q hQ
  obtain ⟨z, hzt, hzQ⟩ := parametrize Q hQ
  have hz : CfgPacking shat z := by
    refine ⟨hzt, ?_⟩
    have hfun : (fun i => (z i).set) = Q := funext fun i => (hzQ i).symm
    rw [hfun]
    exact hQ
  obtain ⟨f, e, hsym, hrel⟩ := unique_via_chain hstuck hU z hz
  refine ⟨f, e.symm, hsym, fun j => ?_⟩
  have hk := hrel (e.symm j)
  rw [Equiv.apply_symm_apply] at hk
  rw [hzQ j, hk]

end

end S11
end PackingCert
