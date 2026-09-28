# A281 -- drafts of the registry row, LOG entry, ledger s.4 note and the k0_knowledge s.14 append (applied at exit)

## k0_knowledge.md s.14 (APPEND)
## 14. APPENDS — A281 (2026-09-28), CORNER COST (`docs/proofs/corner_cost.md`; parts `attempts/A281-corner-cost/notes/`)

- s.1 [T] **Wall ROLES.**  A PAIR corner is class F (one flat + one poker) or T (both tilted); each corner puts one meeter on
  each of its walls, so a wall carries a pair from {Φ (flat), Π (poker), τ (T-meeter)}: six wall types ΦΦ, ΦΠ, ΠΠ, Φτ,
  Πτ, ττ; a corner is T, Ff (flat on its outgoing wall) or Fw.  Exclusive along-wall extents: Φ: 1 + d; Π: min(y_L, y_R)
  ≥ 1 + min(ψ(θ), 1 − cos θ) > 1 (reach y_T ≥ 2); τ: d + min(cos θ, sin θ) (Lemma EXT).  A281 part 1.
- s.2.4 [T] **SIDE per wall type** — ΠΠ dead on W (TWO-POKERS); ΦΠ: s ≥ 3 + d + (1 − sin θ_f)(sec θ_f − 1) (= FLAT-ABOVE
  read from the flat: the flat sits within s − 3 of its corner, never meets the poker's slot; the poker always meets the
  flat's slot); ΦΦ: s ≥ 2 + d + d′; Φτ: s ≥ 1 + d + d′ + w(θ′); Πτ: infimum ≈ 3 (no window bound).  [T-computed] exact
  4-square witnesses of the five live types at 3.82 and ŝ (margins 0.06–0.10; `wall281_pairs.json`).  A281 part 2, 7.
- s.2.4 [T-computed] **A poker's slot is supplied by a T neighbour's wall meeter of EITHER global sense** (frame tilt 18.4°
  opposite sense, margin 0.051; 45.8–46.2° same sense, 0.005–0.012; the row continuation) — **erratum to A248** ("on the
  window every type-F poker's slot is met by an interior square": true only with a type-F wall neighbour; A248's f = 4
  corollary unaffected).  The flat never supplies it (sup 0, the y₀ = y_T limit).  A281 part 3, 7; page (b).
- s.2.2 [T] **The f-table** (15 D4 orbits of corner classes; `count281.py`; Lean `Statements/Open/CornerCost.lean`:
  `allF_is_pinwheel`, `notches_of_noPiPi`, `hasT_or_pinwheel` by `decide`; `realised_has_T`, `no_allF_realised` over the
  bridge axioms `no_PiPi_window` [T-prose] and `notches_le_three` [M]).  SIDE (no ΠΠ wall) kills 3/4 orbits at f = 4, 2/4
  at f = 3, 1/5 at f = 2, none at f ≤ 1; the room count (FAMILY-STUCK dominoes + ninth square + PROJECTION sharing) needs
  h ≤ 2 free squares everywhere and kills NOTHING (A250 in role form); SEPARATE-NOTCHES [M] kills exactly the f = 4
  pinwheel (h_sep = 4 > 3, A248); normal-form locks (ΦΠ, Φτ walls are never rows) need ≤ 2.  Ten orbits survive side +
  count, every one with a T corner except the pinwheel; f = 0 survives with h = 1 = the ribbon poker.  What closes the
  survivors is ROOM on the (hybrid) ring, not any count.  A281 part 6.
- s.2.6 [T-cond] **F3 torque** — the flat has no FORCED wall torque (edge pressure supplies any torque in [−W/2, W/2]); the
  poker (TWO-CONTACT) with only {wall, own flat, a vertical top load} is torque-balanced only if d = sin θ + cos³ θ ≥ 0.98
  (A239 LEVER), which the ΦΠ side bound d < s − 3 ≤ 0.877 forbids: in the all-F pinwheel every LOADED poker has an interior
  contact (or the far floor meeter at R).  With a T neighbour on the poker's edge the lever arm is free: nothing.  T3: LEVER
  is type-F only; the C2 type-T ring has loop gain 1; CHAIN is met by the walls — torque adds nothing to T2.  LOCKED
  (A233) ≠ LOADED: every torque line is conditional on the k ≥ 1 rows AND on load.  A281 part 4, 5.
- s.5.4 [precision] "ONE-SENSE on W certified by A261 + the cube" omits the slab [C]; "LEVER ⟹ s > 4" is for type-F crowds;
  "F costs one interior holder per corner" holds only for the pinwheel (part 8 lists ten errata).
- s.3/s.4 [T-computed]/[M] **8-square outer structures** of the orbits (`wall281_rings.json`, part 7 table 7.2): the all-F
  pinwheel EXISTS on all of W (C4 witness d = 0.662, θ = 14.2°, y_V = 0.948 at ŝ; margins 0.045 / 0.052) — A248's f = 4 kill
  is a HOLDER kill, not a side kill; Ff/Ff/Ff/T exists (0.047 / 0.054); orbits with a ΠΠ wall fail (−0.0003 … −0.0004).

## registry row
| A281-corner-cost | Fable; launch-and-exit, TINY STEPS (one tool call per turn, <= 60 lines per proof piece, each committed), ONE heavy python (BelowNormal + affinity 0xFFFF), PYTHONDONTWRITEBYTECODE=1, explicit-pathspec commits, fetch + plain merge; other campaigns' processes / code / certs never touched (A248 / A249 code imported only) | BRIEF: the two corner classes F / T -- per-wall side costs, holders, torque pinnings (conditional), the f-table | code/ (geom281, wall281, count281, fslots281, pages281, report281), results/ (wall281_pairs.json, wall281_rings.json, count281.json, pages281.json), notes/cost281_part0..8, docs/proofs/corner_cost.md, page docs/residue_map/campaigns/A281-corner-cost/corner_cost.svg, Lean Statements/Open/CornerCost.lean | done | Six wall types; only Pi-Pi dead on W [T]; exact witnesses of the other five at both ends [T-computed]; a poker's slot IS supplied by a T neighbour of either sense (A248 erratum); the all-F pinwheel exists as 8 squares on all of W (A248's f = 4 kill is SEPARATE-NOTCHES [M], a holder kill); the f-table: side kills 6 of 15 orbits, count kills none, [M] kills the pinwheel; every survivor but the pinwheel has a T corner (Lean by decide); torque adds one [T-cond] line (loaded pinwheel pokers need an interior contact) and nothing for T; ROOM, not counting, closes the survivors | attempts/A281-corner-cost |

## LOG entry
## 2026-09-28 - A281 - CORNER COST: the two corner classes F / T as wall roles Phi / Pi / tau; side, holders, torque per class; the f-table (Lean by decide); A248 erratum on the poker's slot
- [T] Six wall types; SIDE kills only Pi-Pi (TWO-POKERS); closed forms: PhiPi s >= 3 + d + (1 - sin th_f)(sec th_f - 1), PhiPhi 2 + d + d', Phi-tau 1 + d + d' + w(th'), Pi-tau infimum ~3.  [T-computed] exact 4-square witnesses of the five live types at 3.82 and s-hat.
- [T-computed] the poker's slot is supplied by a T neighbour's wall meeter of EITHER global sense (erratum to A248's "interior square"; f = 4 unaffected); the flat never (FLAT-ABOVE).  The all-F pinwheel exists as an 8-square outer structure on all of W: A248's f = 4 kill is a holder kill (SEPARATE-NOTCHES [M]).
- [T] f-table over the 15 D4 orbits: side kills 6, the room count kills none (h <= 2), [M] kills the pinwheel; every survivor but the pinwheel has a T corner; f = 0 survives with the ribbon poker (h = 1) -- ROOM closes, not counting.  Lean Statements/Open/CornerCost.lean (3 theorems by decide, 2 bridge axioms, 2 consequences), audit 0 sorry.
- [T-cond] torque: loaded pinwheel pokers need an interior contact (LEVER d >= 0.98 vs d < s - 3); nothing for Pi-tau walls or T rings; LOCKED != LOADED.  Brief errata: part 8 (ten items).
- Files: docs/proofs/corner_cost.md; attempts/A281-corner-cost/{notes/cost281_part0..8, code, results, logs}; page docs/residue_map/campaigns/A281-corner-cost/corner_cost.svg (checks results/pages281.json); k0_knowledge s.14; ledger s.4; registry.

## ledger s.4 note
**[T]/[T-computed]/[M] A281 (2026-09-28) - CORNER COST (`docs/proofs/corner_cost.md`, parts attempts/A281-corner-cost/notes/cost281_part0..8.md).**  The PI's two corner classes as wall roles: a wall is PhiPhi / PhiPi / PiPi / Phi-tau / Pi-tau / tau-tau; only Pi-Pi is dead on the window by side [T]; the other five have exact witnesses at both ends [T-computed]; a poker's slot is supplied by a T neighbour of either sense (A248 erratum) and never by a flat.  f-table: side kills 6 of 15 orbits, the room count none, SEPARATE-NOTCHES [M] the all-F pinwheel (which exists as 8 outer squares on all of W); every survivor but the pinwheel has a T corner (Lean `hasT_or_pinwheel`).  Torque: one [T-cond] line (loaded pinwheel pokers need an interior contact); nothing for T.  Residue unchanged: the survivors are closed by ROOM on the hybrid ring (A259/A260, link 5d), not by any count.
