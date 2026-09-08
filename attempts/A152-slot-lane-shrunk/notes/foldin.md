# A152 — the fold-in lines (the exact text of the three appends)

The prerequisite A118-O1 names is **UNMET** (`notes/prereq.md`), so every line below is marked
*conditional on the slack-form extension kill*.  Nothing in A57, A60, A96 or A141 is written by
A152 except the three appends named here; every campaign and prior attempt was read-only.

---

## (a) `attempts/A57-shadow-trees/PAUSED.md` — v3 addendum (append-only)

### Carried forward from v3 — A152's addendum (2026-09-08, append-only)

**A152 (2026-09-08, `slot-lane shrunk`, pure geometry, ~2.8 CPU-h, nothing in A57/A60/A96/A141 written).**
The PI's refinement of A141's slot-lane leaf — *count a square as MEETING the usable slot only if it meets the
cell SHRUNK by the pin tolerance `h = δ/√2 = 7.0711e-3`, because the snap only needs SOME admissible placement
of the extension class's sixth pin* — was stated exactly, tested, and comes out **NEGATIVE on all three
counts**, all of it CONDITIONAL on a prerequisite that does not exist.

1. **The prerequisite is UNMET.** All twelve k6 extension classes (k5_11: k6_18/20/23; k5_16: k6_23/27/28/29/30;
   trump5: k6_07/19/21–24) carry their closed-window kill on a `parametric-kill-certificate-v1` whose six cores are
   uniformly `a = 16383999967232/32768001953125`, `tm = 1/33554432` — a pin POSITION tolerance of **3.08e-8** and a
   tilt tolerance of 3.41e-6°, with **no pin box anywhere in the object** (A96's `pocket96.py` recorded the same
   fact for all 220 k6 cores). They are dead for EXACT-pin class-T packings only. The slack form needs each core
   shrunk to `a = ½ − h = 0.4929289…` (one core for the A60 lane, all six for the A57 lane), the node LP re-solved
   and the whole window re-verified: **1–15 CPU-h for the A60 lane, 2–30 CPU-h for both**, with a real risk that
   k6_20/21/27/29 (τ = 4.60–4.72 against budget 5, three of them unconverged) do not re-solve at δ = 10⁻² at all.
2. **The shrunk-cell step is UNSOUND.** "Every other square misses the shrunk cell ⟹ a free admissible translate
   exists" is true for ONE square (a separating normal `ν` gives the escaping corner `t = −h·sgn ν`) and FALSE from
   four: four pairwise interior-disjoint unit squares entering `C` through its four faces by `h/2` all miss `C_h`,
   yet every `t ∈ [−h,h]²` is blocked by at least two of them, so deleting the one square the leaf may delete does
   not free the slot (machine-checked in exact rationals, `results/t0_counterexample.json`). The corpus realises it:
   **6 cells** (`k5_11_interior_Y0030` TL(1,0), `Y0445` BR(0,1); `k5_16_interior_Y0157`/`Y0428`/`Y0281_D07` BL(1,0),
   `Y0328` TL(1,0)) where the shrunk-cell leaf returns KILL and **no** admissible translate does better than
   NEAR-MISS. The sound form is the TRANSLATED cell at a fixed admissible `t`, certified per node.
3. **The sound form is structurally VACUOUS here, and net negative.** A *completable* slot of a Young down-set has
   both predecessor cells occupied (wall or pin) — checked on all 16 usable (class, slot) pairs — so the admissible
   translate set is always inside `[0, h]²`: the tolerance can only be spent moving the slot square AWAY from its two
   backed sides, i.e. TOWARDS the two open faces where the grazers actually are. Measured over **1 226 of the 1 713
   alive records (71.6 %), 6 170 of 8 694 (node, slot) cells**: 245 certified translated-cell kills on **90 distinct
   cells, ALL 90 of them already A141 kills — ZERO new**; 36 screen-level "upside" candidates, of which the 27 that
   fit the wall were given deep covers and produced **0 kills**. And it COSTS: re-running A141's own kill cells in
   the node's REAL (`δ = 10⁻²` slack) pin regime — which the refinement forces, since the pin obstacle must shrink
   from the full unit square to half-side `½ − h` — **9 of 152 (5.9 %) stop being kills** (8 NEAR-MISS, 1 UNDECIDED);
   the exact-pin control reproduced A141 on 152/152.
4. **One byproduct worth keeping.** In the `δ = 10⁻²` slack family A141's exact snap `t = 0` is INADMISSIBLE at 14
   of the 16 usable slots (a pin displaced by `+h` towards the slot overlaps the exact cell); only the two
   wall-backed corner slots `k5_11 TR(0,0)` and `trump5 TL(0,0)` keep it. So A118-O1 is sharper than "the leaf does
   not prove the slack statement": at 14 of 16 slots the exact snap is not even available there.

90 `polycore_slot_lane_shrunk_v1` certificates (`attempts/A152-slot-lane-shrunk/certs/slotshr_*.json`, SHA-256
manifest `results/cert_manifest.json`), **all 90 PASS the independent checker `code/check152.py`**, which runs
A141's `check141` in full and then rejects any certificate that does not declare itself CONDITIONAL on the
slack-form extension kill. **None of them is a kill today, and none of A57's state changes.** *Every claim in
this addendum that would retire a node is conditional on the slack-form extension kill; the recommendation is
NOT to buy that re-certification for the slot-lane refinement — it should be bought, if at all, to make A141's
existing 244 kills slack-valid (A118 §2 / lemmas.md T23), which is a much better reason.*

---

## (b) `attempts/A60-trump5-campaign/notes/ledger.md` — append

**A152 (2026-09-08, `slot-lane shrunk`).** The PI's tolerance-shrunk refinement of A141's slot-lane leaf, tested
over the alive trump5 population as part of a 71 %-coverage sweep (229 of the 325 trump5 records; the record order
is a deterministic SHA-256 shuffle, so the covered part is a uniform sample). **Result: zero new kills.** The 20
trump5 nodes A152 certifies at an admissible translate — BR(0,1) and TL(0,0) — are all already A141 kills. Three
things specific to A60 are worth recording. (i) A60's pins are EXACT (`deepen.py` builds `Box(x, x, y, y, 0, 0)`),
so the refinement costs A60 nothing on the obstacle side — unlike A57, where the pin core must shrink to
`½ − h = 0.49293` and 5.9 % of A141's kills are lost; and A60's admissible translate set is the full
`{0, h}²` corner set, `t = 0` included. (ii) It nevertheless buys nothing, because every usable slot of trump5 is
backed on its two predecessor faces by a wall or a pin (BL(0,2), BL(1,1), BR(0,1), TR(0,1), TR(1,0) by a pin on at
least one axis; TL(0,0) by two walls), so the tolerance can only move the slot square towards the two OPEN faces,
which is where anything grazing the cell comes from. (iii) Whatever it did buy would be **conditional on a kill of
the extension class with the sixth pin slack**, which does not exist: k6_07/19/21/22/23/24 carry their closed-window
certificates with degenerate pin cores (`a = 16383999967232/32768001953125`, tolerance 3.08e-8). For A60 the
slack re-certification is the cheaper of the two lanes — only ONE core shrinks per class, the other five pins stay
exact — priced at **1–15 CPU-h** for the six classes (`attempts/A152-slot-lane-shrunk/notes/prereq.md`).
**Nothing in A60 was written.**

---

## (c) `docs/residue_ledger.md` §1 — one paragraph

**The slot-lane leaf does not refine (A152, 2026-09-08; conditional on the slack-form extension kill).** The PI's
proposal to count a square as meeting a usable slot only when it meets the cell shrunk by the `δ = 10⁻²` pin
tolerance — so that a grazer does not block the snap — fails in all three places it could bite, and the measurement
is worth banking because it closes a line rather than opening one. The step "every other square misses the shrunk
cell ⟹ some admissible translate is free" is FALSE (four pairwise-disjoint unit squares entering the cell through
its four faces by `h/2` miss the shrunk cell and jointly block every translate; machine-checked, and realised on 6
corpus cells where the shrunk-cell leaf fires and no translate does); the sound form — the leaf at a fixed
admissible translate `C + t` — is structurally vacuous at a *completable* slot, because such a slot has both
predecessor cells occupied by a wall or a pin, so the admissible translates all point away from the backed sides
and towards the open faces where the grazers are; and over 71 % of the alive A57 + A60 population (1 226 of 1 713
records, 6 170 of 8 694 cells) it certifies 90 kill cells, **all 90 already A141's**, while losing 5.9 % of A141's
own kills once the pin obstacles are honestly shrunk to the slack family's `½ − h`. Underneath all of it sits an
unmet prerequisite that A118-O1 already named and that A152 has now measured on the objects: the twelve k6
extension classes are certified dead on the closed window with pin cores of tolerance **3.08e-8** — exact pins —
so no slot-lane kill, A141's or A152's, is valid for the `δ = 10⁻²` slack-pin family until those certificates are
re-solved with `a = ½ − h` and re-verified over the window (one core per class for the A60 lane, all six for A57;
**1–15 / 2–30 CPU-h**, with k6_20/21/27/29 at τ = 4.60–4.72 against budget 5 the ones at risk of not re-solving).
That re-certification is worth pricing on its own account — it is what makes A141's existing 244 kills usable for
T23's broader slack statement — but not for the sake of this refinement.
