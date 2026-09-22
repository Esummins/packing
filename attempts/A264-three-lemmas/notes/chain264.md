## 13. The FULL CHAIN for k0 at n = 11 on [3.82, ŝ] (A264, 2026-09-22) — every link tagged

Read top-down; a link tagged [T-computed*] is a certificate whose detached chain has not finished (its index says
how much is done); [C] links are the obligations.  Files in `docs/proofs/` unless noted.

1. **A packing of 11 at side s ∈ [3.82, ŝ] is family-stuck or reduces to the k ≥ 1 classes** [T] — `normal_ring.md`
   §1.2 (Lean `normal_ring_value`); the k ≥ 1 classes are the k1_00 / k5 trees (their own ledgers, not this list).
2. **NORMAL FORM** [T]: among the packings at side s a lexicographic maximiser of (Φ₁, Φ₂, Φ₄, Φ₃) exists with P1
   (touch-normal), P2 (row-normal modulo longer rows), P2′, P3, P4 (RETREAT) — `normal_ring.md` §1 (Lean
   `exists_normalForm`; the compactness step is [T-prose]); P1⁺, the family form — `box_meeters.md` §1.1.
3. **BAND-COUNT / HOLE-ONE** [T]: ≤ 1 square contains O, every other square meets the unit band — `peel.md` §2.1,
   `normal_room.md` §2.1 (Lean `hole_one_tilt`, `band_count` [T-prose]).
4. **MEETERS SPLIT** [T]: a doubly-met corner box has ≤ 1 toucher per wall, none touching both, every further
   meeter floats (SAME-WALL, WEDGED-SEAL, TWO-CORNERS) — `box_meeters.md` §0, §2 (Lean `same_wall_core`,
   `meeters_split` [T-prose]).  Corner types PAIR / THIRD / JAM / FLOAT2 — `no_jam.md` §1.
5. **COUNT + ROOM ⟹ n ≤ 9 for every corner type** [T]: if every unit square disjoint from the minimal box-serving
   structure S_min contains O then n ≤ 9 — `no_jam.md` §2.3 (Lean `jam_count_core`, `no_jam_of_count`); the
   third-meeter type is free by monotonicity.  So NO-JAM(11) = ROOM(JAM ring) ≤ 1, per JAM corner (sectors):
   5a. TL sectors of a JAM corner = **pair3** (row of two + one wall square, 4 parameters) [T-computed*, A262 chain3,
       verifier `verify262`; not started at exit — chain3 waits for search262].
   5b. BL sectors = **pair3 at the BL corner with C's wall drop T_u** [T given STRIP] + **STRIP** [C] (`three_lemmas.md`
       §4.3; [M] 323/323 rings; the 7-parameter `jam` job is the fallback, 15–500 CPU-h, pilot in chain3).
   5c. j = 2 opposite: room 0 [M]; j = 2 adjacent: rings exist, capacity 1 [M] — the same per-corner sectors apply
       (`three_lemmas.md` §4.4); j ≥ 3: none on the window [M].
   5d. Indirect jams (a non-toucher blocker), FLOAT2 corners, a middle toucher above X: [M] pending (`float262`,
       `span262` in chain3) — no room statement yet [C].
   5e. Adversary / search: 399 structured starts, capacity ≤ 1 always, no 11-witness [M].
6. **BOX-MEETERS(11)** [T from 5]: every box has exactly two meeters, wall touchers, eight distinct — `box_meeters.md`
   §5 (Lean `box_meeters_262` from the axiom `jam_count` [C = 5a–5d]).
7. **ROW CLASSIFICATION** [T]: each wall carries a row of two, a row of three or an open pair — `normal_ring.md` §3.1.
8. **WINDOW EXCLUSIONS** (which pinwheels of rows exist below ŝ):
   8a. Rows of three, exactly flat walls, mixed senses at tilts ≥ 0.703° on every wall: A261's LP certificates
       [T-computed*: 11/50 verified at A261's exit; `cert261.jsonl` says which; M1 last].
   8b. The slab (some wall in (0, 0.703°), not all): A263's 492 engine jobs [T-computed*, queued after WE].
   8c. **The all-near-flat cube of every mixed pattern: [T]** — `three_lemmas.md` §3 (Lean `slab_cube_264`).
   8d. Exactly one sense, common tilt, rows of two: this is the normal family D′ / the hybrid ring — not excluded,
       it exists; its room is 10.
   8e. Mixed senses with per-wall tilts exist from s = 3.9298 > ŝ [M, A258] — outside the window.
9. **LOCKS AND OPEN PAIRS** [T]: an open pair survives only HELD by a free square (UNLOCK = P2′; LIFT) —
   `locked_wall.md` §1; unequal tilts survive only as locks — `open_pairs.md` §4.  Non-ADJ walls carry a free square
   in the unserved slot [T, Lean `nonadj_free_meeter`].
10. **ROOM: every free square of the hybrid normal ring contains O**:
    10a. Normal D′ (four rows): A259's PAIR tree [T-computed*: index filling, all ok] + A260's LAYER (PLUG) [T +
         T-computed, verified 0 bad] — `normal_room.md`, `locked_wall.md` §4.
    10b. Hybrid, common tilt, all-ADJ, e ≤ ½: A260's hybA / hybB (81/81) / hybAB [T-computed*: 8/81 at A260's exit].
    10c. Hybrid, independent tilts, all-ADJ: A263's P2 ∧ WE ∧ WS [T] reduction + [T-computed*: P2 40/81 cells at
         A264's exit, three cells (3,4) (3,5) (3,6) reported `ok: false` = OPEN at depth 26 — to be re-examined; WS 3
         cells, WE 1 cell].
    10d. Non-ADJ (wide gap, e up to 1.169): ROOM is [F] as a bare-ring statement; STRUCTURE closes the strip:
         GAP-CELL, BLOCKER-SIDE, STRIP-CHAIN [T] for e ≥ sec φ₁ at common tilt; the case 1 + w − sec ≤ e < sec, the
         wedge case and the count to a fourth free square [C] — `three_lemmas.md` §2.  The non-ADJ certificates
         P2n / WEn / WSn are queued and will mark exactly this region OPEN.
11. **8 + 1 < 11** [T]: eight ring squares + one square containing O — Lean `openPairs_excludes`,
    `normalRoom_count`.  Hence no normal-form family-stuck packing of 11 on the window ⟹ **FAMILY-STUCK-EXIST(11)**
    fails in value form ⟹ with 1: **k0_00 is empty** (Lean `k0_value_of_factors`, `lockedWall_excludes`).
12. **k0_00 via CELLS / K0-FREE** [T]: Lemma CELLS (`ring_swap.md` §1.3, Lean `cells_swap`), K0-FREE = |Π| = 1;
    RAISE(0 → 1) is exactly 11 (`ring_swap.md` §0).
13. **The stretch (ŝ, 4)** [M only] and **uniqueness at ŝ** (the iterated form of VALUE-WLOG, `common_sense.md`
    §2.1 (i): SWAP-RIGIDITY k ≤ 3 [M], k ≥ 4 [C]) are outside this list.

**Still [C] or waiting, exactly:** 5b STRIP (or the `jam` tree); 5d (float262 / indirect jams); 6's Lean axiom
`jam_count`; 8a–8b chains; 10a–10c chains (and the three OPEN P2 cells); 10d the gap closure; the [T-prose] Lean
axioms (`meeters_split`, `band_count`, `normal_form_step`, the three corner lemmas of A264); the stretch.
