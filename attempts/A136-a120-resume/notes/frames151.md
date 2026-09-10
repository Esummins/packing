# A136 continuation (A151 / A160 / A163) — which certificate a YES leaf may cite, and what each queue could therefore earn

`code/entry151.py` (the entry builders and the citation rules), `code/run151.py` (the driver),
`results/queue_*.json` (the four queues), `results/nodes[_asym|_a160|_a163]/`.
Read-only on A119, A133, A149, A151, A160, A163 and on `lean/`.

## 1. The rule this note exists to state

The YES leaf says: *node ∧ (for every `i`, some square's pose is in `BOX_i`) is dead, because it
implies the hypothesis of a certified neighbourhood `N`.*  `LocalDead` is **antitone in the box
list**, so this is sound only when

> the boxes the cover names are **inside** the boxes the cited certificate is actually about,

and the cited certificate is an object that exists and has been checked.  Two failures of that rule
were found today, one in this attempt's own earlier output and one in an input.

### 1a. The citation correction to A136's own 15 closures

A136's first pass put **A133's t-certificate** in the `hD` slot of every closure while the cover
used **A119's nominal boxes**.  A133's t-form deliberately makes `N` *smaller* than A119's — its
`notes/results.md`: root `t`-cells are "multiples of `2⁻²⁴`, **rounded INWARD** from A119's angle
cells and clipped to `[0, 1]`"; its `notes/method.md`: "a tilt cell that leaves the fundamental
domain is clipped to its inside part at the DEFINITION of `N` … it is smaller than A119's".
Measured against A119's nominal boxes: every tilt bound is inside by `+2.98·10⁻⁶ / −1.77·10⁻⁶`
degrees, and `BR(0,1)`'s `[−10, 10]` (mod 90 the two branches `[[80, 90], [0, 10]]`) is clipped to
the single branch `[0, 9.9999986]` — **a whole 10° branch smaller**.

The closures are **sound**: A119's own angle-space certificate is about exactly the nominal boxes
and was independently re-checked (`check_local.py`, all valid, 1072 s).  Only the citation was
wrong.  `report136.py` now emits A119's certificate (sha `41fa6e5a…`) as load-bearing, with A133's
t-form as a caveated `alternative` valid only for boxes shrunk to its `meta.bodies`.  No LP and no
NO certificate changes.

### 1b. The rule applied to the three new inputs

| input | artefact | verdict |
|---|---|---|
| **A151-B** (asymmetric, `f1` grown to ±0.40/±0.25/±40°) | `S02_k5_11_A151asym_f1.tcert.json.gz`, sha `a0202e53…`, independently checked (`check_local_t151.json`: 0 errors, 38 590 leaves, exact certified minimum 3.8770844581 > `s₀`) | **CITEABLE.**  The cover's boxes are set to the certificate's own `meta.bodies`, so `BOX ⊆ certified-N` holds with **equality** |
| **A160's union** (53 sets) | `attempts/A160-s02-f0-slide/certs/` is **EMPTY**; `N_boxes160.json` carries **no sha256 and no certificate filename** for any entry, and `results/` has no checker output for them.  Each entry carries only an in-run `tree_verdict` — `{dead, certified_min (a FLOAT), sample_hits, seconds}` — from the generator itself | **NOT CITEABLE.**  The coordinator's premise ("each entry carries its own certificate hash") does not hold for this file.  Margins are thin where it matters: the entry two queue-3 nodes need has `certified_min − s₀ = 5.58·10⁻⁷` as a float |
| **A163's re-framings** (52 `k5_16` + 42 `trump5`) | every entry carries a `certificate` block with `format: local-cert-t-v1`, a **file** under `A163/certs/`, a **sha256**, `status: CHECKED`, an **exact rational** `certified_min`, and a `checker` pointing at `tcerts163.json` (A133's `check_local_t.py`) | **CITEABLE**, and verified here independently: 93 runs, `checker_ok` true on all, `n_errors` 0 on all, spot-checked hashes match the files on disk |

**A163's nine exceptions, excluded here rather than cited.**  Eight entries record
`checker_ok: true` but **no `certified_min`** (`chain_BOTH_base_r0.20_h1.25_nof0_−25 … −45`: 7 in
`k5_16`, 1 in `trump5`), so the recorded check establishes no margin over `s₀`; and
`S02_k5_16_A163chain_RXY_probe_−10.00`'s checker run names sha `5d015812…` while the entry and the
file on disk are `20d4ec17…`, i.e. **the run checked a different file**.  `entry151.a163_index`
drops all nine.  43 of 52 `k5_16` and 41 of 42 `trump5` sets remain fully citeable.

## 2. What each queue could therefore earn, and what it did

* **Queue 1 — the 26 owed on the symmetric `N`** (21 never-targeted consumers + 3 NOT-RUN + 2 OPEN),
  A119's nominal boxes, A120's cone-value order.  Real closures.
* **Queue 2 — the 10 new consumers of A151-B**, boxes from A151's checked t-certificate bodies.
  Real closures.
* **Queue 3 — the 6 A160-union consumers** (8 alive, minus 2 A149 had already killed).  Because the
  YES leaf is not citeable, a node here can at best reach **`NO-COMPLETE`**: all four NO children
  certified dead by the frozen `verify_case.py` with `ZONE ⊆ BOX` on the written rationals, the
  expensive half banked, and the YES leaf recorded `PENDING-CERTIFICATE` naming the exact entry.
  `run151.restatus` refuses to write `CLOSED` whenever the cited certificate has no sha256 or is
  `PENDING-CERTIFICATE`, so this cannot be produced by accident.  **A160 already has the tooling to
  convert them** — `code/gent160.py` is "A133's t-generator + the independent rational checker,
  imported unchanged" — so each is minutes of compute from a citeable certificate, exactly as A163
  did for the other two frames.
* **Queue 4 — A163's 22** (19 `k5_16` + 3 `trump5`; 21 + 3 alive consumers minus 2 A149 kills), each
  assigned the citeable set with the **largest verified rational margin** over `s₀` rather than the
  one with the largest float slack.  Prepared and armed; the wall, not the cap, is why it did not
  run — see §3.

## 3. The binding constraint was the box, not the cap

The ceiling is 16 lab python processes.  Other campaigns (A149 ×6, A137 ×3, A156 ×3, A161, plus
children) held the box at **16–19 all evening**, so both of my workers spent long stretches
correctly yielding — the same thing A160 recorded for the same day ("the box itself ran 16-19
throughout … so WALL, not CPU, was binding").

One self-inflicted part of that is worth recording because it cost 72 minutes.  My admission gate
counted **my own** processes against **my own** ceiling, so whichever of my two sanctioned workers
was mid-certification held a `certify136.py` child that locked the other worker out of its next
node.  The gate now excludes this attempt's own processes and applies the ceiling to everyone
else's; the deadlock disappeared immediately (`lab_python`'s docstring records it).

## 4. Loose end, recorded rather than hidden

`entry151.per_box_check`'s **A5** clause — the tight, per-box form of "the node's own A107
configuration lies in the mapped boxes" — reports a negative slack (≈ −0.73) on the asymmetric and
A160 entries even after being rewritten to A151/A160's own rule (the three `f*` boxes, nominal
anchors, best injection).  A151's and A160's own consumer tests report those nodes **inside** with
positive slack, so the two disagree and the disagreement has not been chased down.  It changes
nothing load-bearing: **A5 is a plausibility check, not a soundness condition** — the YES leaf is an
implication about the BOXES and does not mention the node's representative configuration — and
A120's own A1–A7 (including its own A5) pass on every node run here, as does `per_box_check`'s A4
(500/500 draws inside their own box, every box, every node).  The field is kept in the records,
labelled, for whoever reconciles it.

---

# A136 resume, 2026-09-09 (after the 02:20 reboot)

Two findings, both about **which certified `N` a node's YES leaf cites** — the same question §1 is
about, now answered with measurements rather than with the citation rule alone.

## 5. The one NO-COMPLETE node is closed: the missing YES leaf was emitted and checked

`k5_11_interior_Y0274` was the single row of `results/no_complete136.jsonl` — four NO children
certified dead by the frozen `verify_case.py` with `ZONE ⊆ BOX` on the written rationals, and a YES
leaf that pointed at A160 union entry **34**, `S02_k5_11_A160slice_a151B_f2+00.0_f3+40.0`, for
which §1b recorded that **no certificate artefact exists**.  There was no way to cite around it:
A160's own `consumer160.json` puts Y0274 **inside only the SLICES union** (slack +0.12722) and
outside A151-B (−0.58751) and outside the common-tilt chain (−0.93248), so the certificate had to be
made.

`code/yesleaf136.py` makes it, without editing or writing into any other attempt.  It imports
A160's `gent160.py` unchanged (which in turn imports A133's `gen_local_t.py` and `check_local_t.py`
unchanged) and re-points every write target into this attempt — a **dedicated sub-base**
`yesleaf/`, because `gen_local_t` writes its `.tcert` to `<BASE>/certs` while `gent160` looks for it
in `CERTS`; in A160 those two coincide and here they must be made to.  Then:

| step | result |
|---|---|
| source meta rebuilt from A160's own `results/slice160.jsonl` row (`d2 = 0`, `d3 = 40`) | 4 free bodies `f1 f2 f3 BR(0,1)` |
| **bodies asserted float-for-float equal to `N_boxes160.json` entry 34** — the box set the NO side was actually cut against; a certificate for a different box set would not license the citation, so this check is fatal | **ok, 0 discrepancies over 6 bounds × 4 bodies** |
| A133's t-generator rebuilds the tree from scratch in exact rationals | **DEAD**, 20 243 nodes, 8 450 leaves, 0 unresolved, **67.9 s**, 2.90 MB |
| A133's **independent** rational checker on the emitted `.tcert` | **VALID, 0 errors**, 8 450 leaves / 77 604 rows, 21.2 s, sha `1a0c123e6b9bddaa…` |
| exact rational certified minimum vs `s₀ = 969271/250000` | `1117504297361694154655418074219141144140303/288230376151711744000000000000000000000000` ≈ 3.8771218783, **margin +3.788·10⁻⁵**, compared in `Fraction` |

So the entry151 note "each entry is minutes of compute away from being citeable" is now a measured
**89 s** for one entry, and Y0274 is **CLOSED** (25 closures).  The other five nodes of
`queue_a160_8.json` are not helped by this: three are OPEN with genuinely surviving NO children and
two are SKIP-UNSOUND, so **Y0274 was the only A160 node a YES-leaf emission could close**, and there
is no remaining NO-COMPLETE row anywhere in this attempt.

## 6. On A163's k5_16 frame, "largest certified margin over s₀" is the WRONG entry rule

`queue_a163.json` picks, for each node, the citeable box set with the **largest verified rational
margin over s₀**.  On the nine k5_16 nodes whose in-sets contain the `h = 1.25°` common-tilt link at
the pinwheel tilt, that rule picks `chain_BOTH_base_r0.20_h1.25_nof0_+00.00` (margin 8.121·10⁻⁵).
Measured:

| YES leaf | margin over s₀ | NO children run | outcome |
|---|---|---|---|
| `chain…h1.25_nof0_+00.00` | **8.121·10⁻⁵** (largest) | Y0054, Y0183, Y0380 — 12 children | **12 ALIVE.**  The LP converges to `η = 0` at `τ = 5`: the cover proves *nothing* |
| `chain…h10.00_nof0_+00.00` | **7.454·10⁻⁶** (11× smaller) | Y0941 NO0, NO1 | **DEAD-CERT both**, `τ 5 → 4.5`, `η = −0.5`, certificates PASS in 25 s and 74 s |

The margin over `s₀` measures how far the *certificate's own tree* got, and says nothing about how
much of the node's hypothesis the **complement** of `N` still has to carry.  What the NO side needs
is a **wide** `N`: the `h = 10°` link admits a 20°-wide shared-tilt window against the `h = 1.25°`
link's 2.5°, so its complement is a much smaller region and the LP has correspondingly less to kill.
**The right rule is the widest citeable box set, not the deepest-certified one** — and the two are
anti-correlated, because a wider `N` is harder to certify and therefore certifies with less room.
This is the same trade-off A160 recorded between growth directions, seen from the consumer side.

`results/queue_a163_h10.json` forces the `h = 10°` leaf on all nine of those nodes (the two carrying
ALIVE `docs/shadows` pages, `k5_16_interior_Y0054` and `k5_16_interior_Y0380`, first).  It must be
run with **`--out_suffix`**: `noside120` caches at node **and** at NO-child level and both caches are
keyed by node id alone, so re-running an id against a second YES leaf inside the same subtree would
silently return the first leaf's verdicts.  The new flag gives the second run its own
`results/nodes<S>/`, `certs<S>/` and NO-child name suffix and leaves the first run's records intact
next to it; `report136.py` now discovers every `results/nodes_*` subtree by glob rather than by a
hard-coded list, so a node that is OPEN on one leaf and CLOSED on another appears honestly as both.

## 7. This attempt's own certificates carry STOCK cores, and that — not the LP — was holding six nodes

A170 (`results/scan170.json`) classified every certificate in the repo.  Its verdict on this lane:
**122 A136 certificates, `kind: "stock"`, `exact_lane: false`, exact core up to `1.0787x` the
carried one** — because `certify136.py` splices A136's `narrow` into `caselp.make_certificate`,
which is exactly the entry point that `Hyp.from_json`s the hypothesis and drops A135's exact cores.
A170 then re-certified **none of them**: no A136 row appears in any `recert170_*.jsonl`.

That is worth chasing here because of *where* this attempt's survivors sit.  Of **72 ALIVE NO
children**, **56 are LP-alive** — the LP found no kill at all, and no certifier budget touches those
— but **16 are alive only because the certificate did not land** (14 CAP, 2 FAIL) while the LP had
already converged to a margin, `eta` from −0.116 to −0.444.  **Six of the sixteen were the only
alive child of their node.**  Three experiments, cheapest first:

| experiment | what it changes | cost | result |
|---|---|---|---|
| `exactcert136.py` — PATCH the written certificate (A170's `carry_exact_cores`, ENLARGE only), re-run the FROZEN verifier | cores only; no LP, no re-emission | 0–179 s per child | **2 of 16 PASS.**  `Y0441/NO0` CAP → PASS in 10 s, **closing that node**; `Y0691/NO3` CAP → PASS in 48 s |
| the same 6 low-hole failures re-verified at **depth 64** | verifier depth | 5–60 s each | **0 of 6.**  And `Y1147/NO1`'s "0 HOLES at depth 56" became **4 real holes at depth 64** — the holes were there, the depth-56 run just had not found them.  Depth was never the constraint |
| `certify136x.py` — RE-EMIT with the exact cores **inside** the witness-feedback loop (`make_certificate` → `carry_exact_cores` → `narrow`) | every round's certificate, not just the last | 9–900 s per child | **2 more PASS**, incl. the one that mattered |

The patch cannot reach one whole class of failure and the split is clean.  A verdict of *`N` witness
boxes at depth 56, `k` HOLES* is a **coverage** failure: the cover really does leak at a placement
the measure gives less than 1, and a wider core does not add mass, so all of those stayed FAIL.  A
verdict of *`total mass >= budget: certificate proves nothing`* is a **measure** failure — the cover
is fine, the measure the loop built is simply too small — and only more rounds can fix it.  That is
the class re-emission owns:

> `k5_16_interior_Y0941/NO3` had ended its stock-core loop at `total 5.025000 >= budget 5` after the
> full round budget.  With the cores **2.26 % wider** the exact-core loop **PASSed at ROUND 0 in
> 7.1 s**, `total = 2492839/500000 = 4.98568 < 5`.  Y0941 is **CLOSED**, and it carried an ALIVE
> `docs/shadows` page, now `a57v4/killed/`.

`k5_11_interior_Y0691/NO2` went the same way at 558 s over 3 emissions (18 cores enlarged, max
ratio 1.0322), closing Y0691.  Net: **three nodes closed by cores alone, no LP re-solved.**

**The rule to carry.**  *On a stock-core lane, a cert CAP or cert FAIL is not evidence about the
node until it has been re-certified with the cores the LP was entitled to use* — and the two cheap
diagnostics separate the cases before any compute is spent: **holes ⇒ the cover leaks, cores will
not help; `total >= budget` ⇒ the measure is short, cores in the loop are exactly the lever.**  The
four sole survivors that stayed alive (`Y0036_D02/NO2`, `Y0414_D06/NO0`, `Y0978_D07/NO0`,
`Y1147/NO1`) all report real holes under the wider cores, so they are honest survivors of this
cover, not certifier artefacts — which is a stronger statement about them than this attempt could
make yesterday.

One process-discipline note, recorded because it nearly became a false verdict.  Killing the driver
to re-launch it with a tighter per-child wall tore its in-flight children down with it, and the
driver wrote each of them as `FAIL` with `rc = 0xC000013A` after `0.0 s`.  Nothing had been
measured.  Thirteen such rows are quarantined in `results/reemit136_discarded.jsonl`, and
`reemit136.py` now records `KILLED` and re-runs it — the same rule the lab already applies to a CAP:
**a resource event is never a verdict.**

## 8. A177 finishes the owed queues: the closure came from the CAPs, not from the entry rule

A177 (`attempts/A177-a163-queues`) ran the three things this attempt left owed and cheap — the base
worker's last node, the 9 rows of `queue_a163_h10.json` and the 11 remaining rows of
`queue_a163.json` re-pointed at the widest citeable `N` per node — with A170's exact cores carried
**inside** the witness-feedback loop (`certify136x.py`) and the widest-`N` rule of §6 made
computable as `(min tilt width over the free bodies, then log-volume)`.  The result is one closure
and a clean negative, and the two come from opposite findings of this note.

**`k5_11_interior_Y1140_D06` is CLOSED** (`closures136.jsonl` 29 → 30).  This is the node the base
worker recorded `OPEN` with children `[ALIVE, CAP-GATE, CAP-GATE, CAP-GATE]` at 14:54:04: `NO0`'s
certification hit the 2600 s wall and `NO1`–`NO3` were never tested at all because the node
deadline had passed — four verdicts, zero evidence.  Re-run under a fresh `--out_suffix` (both
`noside120` caches are keyed by node id and would otherwise have served the CAP-GATE record
straight back), **all four NO children certify dead under the frozen `verify_case.py`**, `NO0` in
532 s against the 2600 s the stock-core loop had burned.  §7's rule and the resource-event rule
between them were worth a whole node here, and §6's entry rule was not involved: the YES leaf is
A119's ordinary `S02_k5_11_r0.20_rho10`.

**On the k5_16 frame the widest citeable `N` closed nothing, and the survivors are honest.**  All
19 completed a163 rows came back `OPEN` (15) or `SKIP-UNSOUND` (4); the 20th, `Y0973`, is owed on a
certification CAP.  The `h = 10°` link kills three
of four children on `Y0054`, `Y0380` and `Y0422` and none on `Y0183`; the 10× wider `a151B` slice
moves `Y1104` and `Y0854` from zero dead children to one and moves `Y0486`, `Y0570`, `Y0559`,
`Y0985` not at all; the one node that can cite only a 2.5° window (`Y0871`) dies nowhere, exactly as
§6 predicted.  Every one of those ALIVE children is a **converged** LP at η = 0, τ = 5 — not a CAP
and not a cert FAIL — so the barrier on this frame is the **cover**, not the certifier and not the
choice of entry.  §6's `Y0941` (3 of 4 children, closed) is the exception on this frame, not the
pattern, and the queue that was supposed to repeat it did not.

`c0_Y1132`'s `A1_pins_match` refusal was tested rather than assumed: it is refused on its
next-widest citeable set too, so the refusal is a property of the node's pins, not of the entry.

**And the h10 lane's obstruction is one box: `BR(0,1)`, the PIN box.** Six of the eight completed rows are `[DEAD-CERT, DEAD-CERT, DEAD-CERT, ALIVE]` with the survivor always `NO3 = BR(0,1)`; five of the six report a cert FAIL whose own witness-feedback re-solve converges at `tau = 5.000000` exactly (round 0 `4.88…4.91` unconverged, `total 4.98525 < 5`; round 1 converged, `total 5.02500`, 12 cores enlarged up to 1.11×), and the sixth is LP-alive directly.  A `total >= budget` FAIL whose last round CONVERGES at the budget is therefore not the measure failure of §7 at all — no certificate can exist and cores, rounds and depth are provably wasted on it.  Since a certified `N` names only the free bodies, **no entry rule can widen a pin box**: these eight nodes need a re-split of `BR(0,1)` or a geometric kill of it (it is a wall-adjacent pin cell — A161's chord-limited lane shape), and one shared lemma would close all eight.  `A177/notes/queues177.md` §3 carries the tables.
