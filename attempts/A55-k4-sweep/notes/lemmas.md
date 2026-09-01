# A55 — the k = 4 layer: structure, canaries, arbiters

Everything at s0 = 969271/250000 = 3.877084, in A53's Young-form stratification (A53 L1–L5) with
A54's semantics (S0: τ_LP bounds τ* in NEITHER direction; the sole arbiter of a kill is an exact
rational measure certificate accepted by `verify_case.py`). Budget at k = 4 is 11 − 4 = **7**.
A53 and A54 results are read, never written. A29 untouched.

## K0 [T] — the 14 classes, named

`code/k4_classes.py` reads A53's `results/skeletons_young.json` (census by k: 1,1,3,6,**14**,22,33,
35,30,18 D4 classes) and fixes the A55 names `k4_00 … k4_13` in the file's class order, writing
`results/name_to_slots.json` (the A53-compatible node map) and `results/k4_lattice.json`.
`k4_13 = corners4`, the A14/A16 baseline (checked against A53's own `name_to_slots.json` entry).

## K1 [T] — ALIVENESS PROPAGATES DOWNWARD (the dual of L5's cap)

**Lemma.** Let S ⊆ S' be pin-sets (S' = S ∪ {p}, p an axis-parallel unit slot square disjoint from
S). If τ*(S') ≥ 11 − |S'| — i.e. the residual of S' admits (11 − |S'|) pairwise interior-disjoint
admissible unit squares clear of S' — then τ*(S) ≥ 11 − |S|.

*Proof.* Those 11 − |S'| squares are pairwise disjoint, clear of S' ⊇ S, and none of them meets p
(p ∈ S'); adjoin p itself. The result is 11 − |S'| + 1 = 11 − |S| pairwise interior-disjoint
admissible squares all clear of S, so any measure with μ(Q) ≥ 1 on admissible residual placements
has total ≥ 11 − |S|. ∎

Kills climb (L5), aliveness descends (K1). Contrapositive, the form used here: **a certificate for
S kills every k = 5, 6, … class containing S**, and **a subset of a provably-alive class can never
be certified**.

## K2 [T] — the a priori canary set at k = 4: four classes are UNKILLABLE

trump5 is provably alive (A53 V6 / A54 S4(i); rerun 2026-08-31 under A55: six free squares
admissible, kept by the row filter, min pairwise SAT gap −9.99e-16 = exact touch ⇒ τ*(trump5) ≥ 6).
Exactly four k = 4 classes are sub-skeletons of trump5 up to D4:

    k4_03  BL staircase (2,1) + TL corner          (≅ trump5 minus its TR corner)
    k4_06  BL vertical domino + TL + TR            (≅ trump5 minus the staircase's (1,0) cell)
    k4_08  BL staircase (2,1) + TR corner          (≅ trump5 minus its BR corner)
    k4_11  BL vertical domino + BR + TR            (≅ trump5 minus the staircase's (0,1) cell)

By K1 each has τ* ≥ 7 and **can never carry a certificate**. They are measured (`--no_cert`) and
never certified — the S4 discipline, now with a proof rather than a convention. A PASS on any of
them would refute trump5's feasibility and is treated as a pipeline-corruption alarm.

## K3 [T] — the pivot: k4_05 decides the whole k ≥ 5 tier

After A54 the open classes at k = 5 are exactly {k5_11, trump5, k5_16} (19 of 22 certified;
`code/cap.py` reproduces this from the PASS ledger with 0 discrepancies). Their k = 4 sub-classes:

    trump5 ⊃ {k4_03, k4_06, k4_08, k4_11}          (K2, unkillable)
    k5_11  ⊃ {k4_03, k4_05}
    k5_16  ⊃ {k4_05, k4_06, k4_11, k4_13 = corners4}

So **k4_05 is the unique k = 4 class contained in both open non-Trump k = 5 classes and in
neither trump5**. By L5, a certificate for k4_05 closes k5_11 AND k5_16, leaving trump5 as the
only open class at every k ≥ 5. By K1 the converse is the price: if either k5_11 or k5_16 is
genuinely alive, k4_05 is alive too, so **k4_05 is at least as hard as the harder of A54's two
survivors** (whose margins were 0.35 % short and negative respectively). Likewise
kill(corners4) ⇒ kill(k5_16); corners4's τ ≥ budget makes that route unavailable a priori.

## K4 [M] — the Trump-ghost profile, reproduced and made a score

`code/ghost.py` scores the LP's optimal fractional packing by its zone fingerprint
(`substrat.zones`, cw = 0.6: interior [1.1, 2.777]², four sides, four corners), plus the tilted
(5–85°) share of the interior, and reports
`ghost_score = 1 − ½·L1(normalised profile, normalised trump5 profile) ∈ [0,1]`.
Reproduces A54 S1 exactly on the reference set:

| node | τ | interior (tilted) | side_L | side_B | side_R | side_T | ghost |
|---|---|---|---|---|---|---|---|
| trump5 | 5.97081 | 2.971 (2.827) | 0.506 | 0.000 | 1.000 | 1.000 | 1.000 |
| k5_11 | 5.90512 | 2.917 (2.753) | 0 | 0 | 1.018 | 1.018 | 0.829 |
| k5_13 | 5.67742 | 2.742 (2.564) | 0 | 1.028 | 1.000 | 0 | 0.650 |
| k5_16 | 5.98951 | 2.990 (2.931) | 0 | 1.000 | 1.000 | 1.000 | 0.831 |
| k6_23 | 4.93368 | 2.934 (2.720) | 0 | 0 | 1.000 | 1.000 | 0.833 |
| corners4 | 7.20785 | 3.208 (2.987) | 1.000 | 1.000 | 1.000 | 1.000 | 0.807 |

(trump5's 0.506/0.494 split between side_L and corner_TL is one placement straddling the cw = 0.6
cut, not a structural difference.) The invariant across the whole family, k = 4 to k = 6: an
interior mass of ≈ 3 that is ≈ 93 % tilted, exactly 1.00 per "live" side zone, ≈ 0 in the corners.
**corners4 is the ghost with all four side zones lit** — the k = 4 endpoint of the same object.

## K5 [M] — the tight variety and its COVERAGE NUMBER, with an honest calibration

`code/tightvar.py` maps T_η = {residual placements Q : μ(Q) ≤ 1 + η} on a (cx, cy, θ) grid and
reports the **coverage number** ν(η) = the largest pairwise interior-disjoint subset found inside
T_η (greedy + randomised restarts, exact clearance from the pins at SAT margin 1e-6).
ν(η) ≥ budget would be an integral dual witness (⇒ τ* ≥ budget, unkillable — A54 `alive.py`'s
criterion). **Calibration on trump5, where ν* = 6 is known:** the grid search returns ν = 5
(step 0.03, 1.5°) and `alive.py` on the LP rows also returns 5 (A54 reported 4 with a smaller
pool). So on this machinery **ν undercounts the truth by 1 even on a provably alive node** —
ν = budget − 1 is the alive signature, not a proof, and ν < budget is never evidence of death.
This is GAP-A54-2 restated quantitatively; it is why K1/K2 (combinatorial) and not ν carry the
aliveness verdicts in this report.

## K6 [T] — RESULT: the k = 4 layer is exactly the downward closure of the open k = 5 layer

Sweep outcome: **8 of the 14 classes carry exact certificates** (k4_00, k4_01, k4_02, k4_04,
k4_07, k4_09, k4_10, k4_12; all re-verified independently at depth 60, V4). The 6 survivors are
k4_03, k4_05, k4_06, k4_08, k4_11, k4_13 = corners4. Independently of any LP, the k = 4 classes
contained in an open k = 5 class ({k5_11, trump5, k5_16}) are exactly those same 6. Hence

> **Theorem (measured, V4b).** A k = 4 Young class is certifiably empty **iff** it is contained in
> no open k = 5 class. Equivalently, the certified-empty set at k = 4 is precisely the complement
> of the downward closure (under K1) of {k5_11, trump5, k5_16}.

The ⇐ half is forced by K1 and holds for *any* method, so the guard-LP layer at k = 4 hit the
**theoretical maximum**: nothing killable was left unkilled. Every survivor survives for an
inherited combinatorial reason, not because the LP was too weak — which is the substantive
difference from the k = 5 and k = 6 layers, where survivors were LP-convergence artefacts.

**Consequence for the programme.** The k = 4 tier can no longer be attacked class-by-class with
pin-LPs: further progress *at k = 4* is now **equivalent** to deciding k5_11, k5_16 and trump5.
(One pin-LP target does remain strictly below — k3_00, see K7.) In particular
k4_05 (K3) is a strictly harder target than either A54 straggler, and corners4 is at least as hard
as k5_16. This is the pin-LP route reaching its own boundary, and it localizes the whole remaining
stratification problem onto **three** k = 5 classes.

## K7 — the emptiness map after A55 (the updated L5 cap)

| k | D4 classes | certifiably EMPTY | open |
|---|---|---|---|
| 0 | 1 | 0 | k0_00 |
| 1 | 1 | 0 | k1_00 |
| 2 | 3 | 0 | k2_00, k2_01, k2_02 |
| 3 | 6 | 0 | k3_00 … k3_05 |
| **4** | **14** | **8** | **k4_03, k4_05, k4_06, k4_08, k4_11, k4_13** |
| 5 | 22 | 19 | k5_11, **trump5**, k5_16 |
| 6 | 33 | 33 | — |
| 7 | 35 | 35 | — |
| 8 | 30 | 30 | — |
| 9 | 18 | 18 | — |

Ledger: 60 certified pin-sets (8 at k = 4 [A55], 19 at k = 5 [A53 + A54], 33 at k = 6 [A53 + A54]).
Rebuilt from the PASS files alone by D4-containment (`code/cap.py`); run against the pre-A55
ledger it reproduces A54's closing state with 0 discrepancies (V8).

**Cap statement.** Every stratum whose skeleton contains one of the 60 certified pin-sets is empty.
Concretely: all strata with k ≥ 6 are empty; at k = 5 only k5_11, trump5, k5_16 remain; at k = 4
only the six listed above, and each of those is a sub-skeleton of a surviving k = 5 class. Of the
14 k = 4 classes, 4 (k4_03, k4_06, k4_08, k4_11) are **provably non-empty-able** — they are
sub-skeletons of trump5, so no certificate can ever exist for them (K2).

**Where the route goes next (computed, not assumed).** Of the 11 classes with k ≤ 3, ten sit under
at least one surviving k = 4 class (and under all three open k = 5 classes), so K1 blocks any
certificate for them. **Exactly one does not: k3_00**, the full left-wall column
{(½,½), (½,3/2), (½,5/2)} at budget 8. Every k ≥ 4 class containing it — k4_00, k4_01, k4_02 and
their supersets — is now certifiably empty (all three are A55 kills), yet the *stratum* k3_00
itself (skeleton exactly this triple) is untouched by those kills and is not protected by K1.
So the pin-hypothesis route does **not** terminate at k = 4: k3_00 is the unique remaining
pin-LP target below it. Below that, k2_*, k1_00 and k0_00 are all K1-protected — k0_00 (the empty
skeleton) is the whole problem.

**Scouted (A55, one pass, not a verdict):** `ladder.py --name k3_00 --tag scout`, 2567 s LP,
29395 rows, **τ = 7.666666666679 = 23/3, η = −0.3333 vs budget 8**; certification FAIL after 5
witness-feedback rounds, worst exact holes 1.0324 → 0.9836 → 0.9832 → 0.9571 → 0.9829, cert totals
7.9798 (scale ceiling 8/τ = 1.0435). **This is precisely the profile the eight k = 4 kills showed
at their own first pass** (η ≈ −0.33 to −0.41, worst hole 0.98–0.99, FAIL) before a merged-warm
second/third pass closed them — k4_00 needed three passes and 37k accumulated rows to go from
0.9950 to PASS. k3_00 is therefore a live and promising target at the same effort profile, not a
straggler: `results/k3_00_scout.json`, `certs/k3_00.*` are left as the warm start (GAP-A55-6).

## K8 — gaps

* **GAP-A55-1** — k4_05 and corners4 undecided, and by K6 they cannot be decided at k = 4:
  they are equivalent to deciding k5_11 / k5_16 (GAP-A54-1). Not a separate campaign.
* **GAP-A55-2** — no ALIVE-side verifier still (GAP-A54-2), now quantified: ν undercounts by
  exactly 1 on trump5 (V7), so the six survivors' ν = 5–6 of 7 is consistent with, but does not
  prove, τ* ≥ 7. Only K1/K2 (combinatorial) give real aliveness verdicts.
* **GAP-A55-3** — corners4's residual LP plateaus at τ = 7.200 against A14/A16's 7.000; the
  excess is localized entirely in the interior block (V5) and is a column-generation shortfall,
  not a discrepancy, but it was not driven to 0.
* **GAP-A55-4** — all 8 certificates are at s = s0 only; inherits G-A53-1 (s-parametric transfer),
  which is A56's subject.
* **GAP-A55-6** — **k3_00 (left-wall column of three, budget 8) is open and is the unique
  pin-LP target left below k = 4** (K7). A55 scouted it only; it deserves the A54 ladder in full.
* **GAP-A55-5** — rung 3 (sub-stratification) and rung 4 (wastage) were not run at k = 4. A54 S3's
  a-priori argument for rung 4 applies verbatim (every k = 4 pin is a wall/corner-flush axis-parallel
  unit square, certified dead area exactly 0 vs B0 = 4.0318), so rung 4 is dead here too. Rung 3
  was not needed: the 8 killable classes all fell to rungs 1–2, and the 6 survivors are protected
  by K1, where rung 3 cannot help either (a sub-stratification of an alive node has an alive child).

## K9 — arbiters and discipline used here

Kill = exact rational certificate through `verify_case.py` (interval B&B over (t, cx, cy)).
No verdict is read off τ_LP in either direction (A54 S0). The four K2 classes are never certified.
corners4's certification is refused automatically by `certify.py` (rc = 3) once τ ≥ budget.
Levers carried over from A54 unchanged: merged warm start with row pruning OFF, **column** pruning
only (raises τ, sound for a kill), scale cap lifted to the true ceiling budget/τ, cheap-cert every
round.
