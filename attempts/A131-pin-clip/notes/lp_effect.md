# A131 T3 — does narrowing the box move the LP, or only the columns?

Driver `code/lp131.py` + supervisor `code/run131.ps1`; ledger `results/lp131.jsonl`; node solves
`results/nodes/`; certificates `certs/`; logs `logs/lp131_s{0,1}.log`.

**Protocol.** Ten nodes, each re-solved ONCE on its pin-clipped centre box over its **own tilt
bin** (`nsub = 1`, so the tilt range is untouched and the clip is the only variable), through the
same `solve_node` call and the same warm start `recheck96`/`recheck124` use. Two stages: 240 s LP
cap, certify at once if `η ≤ −1e-3`; otherwise re-solve at 900 s and certify then. Certification is
`certify.py` → `verify_case.py`, i.e. the frozen chain; **a kill is claimed only by a certificate
that passes it**. The control is the node's STORED record — per lemmas.md, a re-emission is not a
reproduction, so nothing here re-emits the control.

**Discipline.** Two processes, BLAS-pinned, BelowNormal (verified at start, not assumed).
`attempts/A57-shadow-trees/PAUSE` was **left in place and untouched** — every `tree57` shard and
both `deepen` producers stayed stopped — and the driver watched its own sentinel
`attempts/A131-pin-clip/PAUSE` via `pausegate.paused(base=...)`, which is A124's scoped-sentinel
mechanism (PAUSED.md v2 §7a). No shard was launched. Total **2.85 CPU-h** against the 6 CPU-h cap;
no wall-cap fired.

## The table

`η = τ − budget`; budget 5 throughout. "control" is the stored record on the ORIGINAL box.

| node | L | kept | control η | control conv / minmass / support | clipped η | conv / minmass / support | cert | wall |
|---|---|---|---|---|---|---|---|---|
| `Y0036_D02` | 2 | 0.287 | +6.2e-12 | F / 0.687 / 5 | **−1.000000** | F / 8e-10 / 4 | **PASS** | 425 s |
| `Y0186_D00_D00` | 3 | 0.092 | +7.8e-13 | F / 0.488 / 8 | **−0.500000** | F / 0.667 / 27 | **PASS** | 471 s |
| `Y0036_D03` | 2 | 0.419 | +7.7e-13 | F / 0.664 / 8 | **−1.000000** | F / 7e-10 / 4 | FAIL(rc=1), 5 holes | 1002 s |
| `Y0996` | 1 | 0.111 | −6.0e-12 | F / 0.429 / 82 | **−0.500000** | F / 0.333 / 16 | FAIL(rc=1) | 849 s |
| `Y0636_D04` | 2 | 0.419 | +2.0e-11 | F / 0.704 / 9 | **−0.500000** | F / 4e-9 / 12 | FAIL(rc=1) | 1295 s |
| `Y0036_D06` | 2 | 0.354 | −2.1e-13 | **T** / 1.000 / 5 | −7.6e-14 | F / 0.500 / 9 | — | 1348 s |
| `Y0036_D07` | 2 | 0.419 | +1.8e-11 | F / 0.676 / **107** | −2.2e-13 | F / 0.600 / **5** | — | 1259 s |
| `Y0674` | 1 | 0.083 | −1.2e-11 | **T** / 1.000 / 5 | −2.5e-13 | **T** / 1.000 / 5 | — | 511 s |
| `Y1128` | 1 | 0.141 | −9.1e-11 | F / 0.333 / **1041** | −5.4e-11 | F / 2e-10 / **5** | — | 1567 s |
| `Y0414_D06` | 2 | 0.392 | 0.0 | **T** / 1.000 / 5 | −2.8e-14 | F / 0.716 / 14 | — | 1534 s |

(All ten are `k5_11` except `Y0674`, which is `k5_16`. All ten were recorded ALIVE except
`Y0036_D06`, which was a FAIL.)

## What it says

**The clip moves the LP on half the sample, and it moves it a long way.** Five of ten go from
`η ≈ 0` (τ pinned at the budget — the definition of ALIVE) to **η = −0.5 or −1.0**, which is not a
numerical shift: τ drops a half or a whole unit of measure. Two of those five carry a certificate
through the frozen verifier inside the 240 s certify cap, so **2 of 10 are outright certified kills
of previously-ALIVE nodes**: `k5_11_interior_Y0036_D02` (level 2, η −1.0, PASS in 11.2 s) and
`k5_11_interior_Y0186_D00_D00` (level 3, η −0.5, PASS in 219 s). Both are among Y0036's own
subtree, which is where the PI's reading started.

**The other three decisive nodes fail certification with real holes, not boundary degeneracy.**
`Y0036_D03`'s report is explicit: 8 witness boxes at depth 56, **5 HOLES** (a placement with exact
mass < 1), 0 tight, 3 undecided — the campaign's ordinary FAIL → resolver path (budget.md §B prices
the resolver at 3–11 s), not a refutation. Running the resolver is a campaign driver and out of
scope here, so the honest count is **2 certified, 3 more with τ ≤ budget − 0.5 pending the
resolver**.

**On the other half the clip moves only the columns — and it moves them dramatically.** The three
nodes whose η stays at 1e-13 show support collapsing: `Y0036_D07` 107 → 5 columns, `Y1128`
1041 → 5, `Y0996` 82 → 16 (that one moved η too). `Y0674` is the cleanest case of "columns only":
the LP **converged** on the clipped box at minmass exactly 1 with 5 support columns, as it did on
the original, at η = −2.5e-13 either way. Those nodes are genuinely alive at this budget, and
shrinking their box by 90 % does not change that. So the answer to the brief's question is
**both, and which one you get is not predicted by how much the clip removes**: the five decisive
nodes keep 0.09–0.42 of their area and the five inert ones keep 0.08–0.42 — the same range.

**A caveat on the count, in the campaign's own favour.** The two-stage protocol certifies only at
`η ≤ −1e-3`. The 900 s re-check's own "kills" are recorded as `τ < budget` at η as small as
−1.4e-14 (PAUSED.md v2 §9), and `recheck96` never runs `certify.py` at all — so its 11-of-23 and
the 27-of-63 now on the ledger are **LP verdicts, not verified certificates**, and are not directly
comparable with the 2 of 10 here. Under the re-check's own criterion all ten of these clipped
solves have τ < budget; under a criterion that means anything, five do; under the frozen verifier,
two. The gate to change if this is deployed is to send knife-edge nodes to the certifier anyway,
as the tree does.

**Cost.** 2.85 CPU-h for ten nodes (mean 1,026 s, range 425–1,567 s), on a box already carrying
five other campaigns, at BelowNormal. Two certified kills for 2.85 CPU-h is 1.4 CPU-h per kill,
against the 900 s re-check's 8.11 CPU-h for 27 LP verdicts (0.30 CPU-h each) — but the re-check's
are not certificates, and the two here are. The comparison that is unambiguous remains T2's: the
132-node backlog costs minutes of geometry and needs no LP at all.
