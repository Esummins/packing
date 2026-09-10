# Packing repository review — 10 September 2026

Snapshot: [`e672154ab96d2c5a1410d5fa477f1b8f61ccf654`](https://github.com/Esummins/packing/commit/e672154ab96d2c5a1410d5fa477f1b8f61ccf654), committed 07:22:02 UTC. This review covers the four writeup documents, the current budget and status records, selected proof specifications, current Lean interfaces and replay logs, CI configuration/results, and the newest verifier code. It is a documentary and targeted correctness audit, not a fresh build of the entire Lean corpus or independent verification of every archived certificate. No remote repository changes were made.

## Decision

The project is worth presenting to Anthropic soon as an ongoing human–AI research collaboration with certified mathematical results and a substantial formal verification infrastructure. Tonight's package should not claim that a complete optimality-and-uniqueness proof is ready except for a purchasable amount of compute.

The immediate work is a small, prioritized release pass: fix a reproduced verifier soundness bug; reconcile the headline status; distinguish the actual frontier from the gallery; publish a current dependency and budget table; and make the visual workflow visible. A new theory breakthrough or a 400-CPU-hour projection is not a prerequisite to an honest initial conversation.

## 1. Release-blocking correctness findings

### P0 — v5 accepts an unjustifiably small right-hand side

[guardlines_v5.py](https://github.com/Esummins/packing/blob/e672154ab96d2c5a1410d5fa477f1b8f61ccf654/attempts/A190-guardline-clause/code/guardlines_v5.py), `rederive`, lines 189–192 computes `rhs_star`, rejects a declared RHS GREATER than it, and then uses `min(rhs, rhs_star)`. The proved inequality bounds the counted chord sum by `rhs_star`; it does not bound it by an arbitrary smaller declaration.

I reproduced an actual false PASS using the unmodified verifier with its frozen dependency hashes satisfied: no atoms, no cores, no windows, four horizontal lines with density 3, and declared RHS 0. The verifier reports that ONE unit square cannot fit inside side 3.877084. It finishes in about 0.1 seconds, with 416 boxes and 240 line-only covers. Obviously a single unit square fits.

This is a soundness bug, not a floating-point or performance issue. Simplest correction: always use the recomputed `rhs_star`; if the declared field remains a consistency check, require exact equality. A different smaller RHS needs an additional independently checked proof. Update the proof specification and the existing test T3: it currently tests and enshrines the wrong inequality direction.

**Scope:** I loaded all three committed A190 kill certificates, `k5_11_interior_Y0147`, `c0_Y0952`, and `c0_Y0959`. Each has one active line and its declared RHS equals its recomputed RHS. This particular bug therefore does not by itself refute those three results. Nevertheless v5's general PASS-implies-exclusion claim is false. Correct the checker, add the adversarial regression below, and replay these certificates before counting v5 as a trusted release component. The earlier 3.82 bound does not use v5.

### P0/P1 — LINE-1's stated hypothesis is false

[guardline_clause.md §1](https://github.com/Esummins/packing/blob/e672154ab96d2c5a1410d5fa477f1b8f61ccf654/docs/proofs/guardline_clause.md) claims that closed squares with pairwise disjoint interiors have total closed-chord length at most the container side along every axis-parallel line.

Counterexample: the four unit squares in the ordinary 2-by-2 tiling of `[0,2]^2`. On the line `y=1`, each has a closed chord of length 1, so the sum is 4, greater than 2. A square boundary can contain an entire chord; the proof's assertion that the boundary meets the line only at chord endpoints is false.

Theorem G's actual node hypothesis later assumes pairwise disjoint CLOSED squares, which is strong enough. Repair the lemma and proposed Lean statement to that scope, then explicitly cite the dilation/transfer that makes it applicable to the search. If the intended theorem must allow touching squares, use an appropriate interior-chord or generic-line formulation and reprove the bound and checker interface. Do not silently apply the closed-chord claim at a flush stack or equality endpoint.

This is the same general distinction needed in the summary's “two squares sharing a point are the same square”: it requires the strict closed-disjoint family used by the certificate bridge.

## 2. What the writeups should say

### Defensible present state

- There is an unconditional certified lower bound `s(11) ≥ 3.82`, with an end-to-end Lean bridge; the documented safe upper bound is `s(11) ≤ 3.877084`.
- The census and much of the checker/geometry infrastructure are formalized. There are 52/52 full-window certificate rows in the designated window scoreboard. That is substantial progress, but it is not closure of every non-k0 class.
- A139's committed build logs support successful concrete S07 and S02 local-certificate replays: 571 s and 6,707 s respectively. This is real progress beyond a generic local-checker soundness theorem.
- The complete optimality and uniqueness theorem remains conditional. `TopLevel.lean` still names `stratum_kill`, `trump_residual`, and `a22_exact_structure`. The newer composition route refines the outstanding obligations; it does not supply all per-class instances.
- A57's two window trees, protected cases, Trump residual work, k0, and tree-cover/certificate-integration obligations remain. The newest v4/v5 clauses add prose proofs and implementations, with formal work still outstanding.

Sources: [mathematics §0 and §8](https://github.com/Esummins/packing/blob/e672154ab96d2c5a1410d5fa477f1b8f61ccf654/writeup/02_mathematics.md), [TopLevel](https://github.com/Esummins/packing/blob/e672154ab96d2c5a1410d5fa477f1b8f61ccf654/lean/PackingCertMathlib/PackingCertMathlib/TopLevel.lean), [A139 build log](https://github.com/Esummins/packing/blob/e672154ab96d2c5a1410d5fa477f1b8f61ccf654/attempts/A139-r4-replay/logs/build_both.log), [Lean theorem inventory](https://github.com/Esummins/packing/blob/e672154ab96d2c5a1410d5fa477f1b8f61ccf654/lean/README.md).

### Required corrections by document

| Document | Correction before external circulation |
|---|---|
| [01_summary.md](https://github.com/Esummins/packing/blob/e672154ab96d2c5a1410d5fa477f1b8f61ccf654/writeup/01_summary.md) | Replace “every class but one is closed” with the explicit unfinished-family list. “52/52 window rows” must retain its denominator and scope. |
| Summary and related-work R21 | Replace “the residue is eleven cells” with “eleven converged-alive diagnostic cells”; include the separate exhaustive work frontier and unresolved certificate candidates. |
| Summary | Replace “no k0 cell has yet been killed” with “no whole target gallery cell has been closed by the new cascade.” A115 already records 22 root-cell kills; A141 records additional conditional lane kills. |
| Summary | Define k0 as no simple corner-slot square. The two-meeter reduction depends on K0-O1 and its geometric transfer; it is not the definition of k0, and “both tilted” needs justification. |
| Summary and timeline §7 | Remove the claim that one successful k0 cell would establish that all remaining work is “just compute.” It is a useful pilot, not a termination or global cost theorem. |
| Mathematics §8.2 | Refresh the open-obligation list through A191, including boxed windows and guard lines. Mark obsolete obligations as such: A139 re-emitted certificates to avoid needing the sharper exact w-range implementation for its two concrete replays. |
| Mathematics and timeline | Identify the actual two concrete LocalDead subjects as S07 and S02. Avoid conflating feasible stationary configurations, proved local minima, and neighborhood exclusion certificates. |
| Timeline §7 | Cite a concrete theorem for the upper endpoint 3.877083590022814. The theorem inventory separately documents 3.877084 and a tight certificate at 3.877083591023; do not attach extra digits to “both ends Lean” without the corresponding theorem. |
| Timeline and budget | Replace stale 406–423 work-owing summaries with the explicitly defined current frontier; A149's later id-by-id table counts 2,052 owing nodes on side 1 plus 4,683 children on sides 2–4. These populations must not be silently interchanged. |
| All writeups | Make tag meanings uniform. The writeup uses [C] for certified; attempt notes often use [C] for open. [P] should not quietly mean both pending computation and missing proof. |
| Root README | Add a clearly dated “start here” link to the external brief and current status. Keep historical logs accessible behind it. |

The eleven-cell qualification is not speculative. [A115's current handoff](https://github.com/Esummins/packing/blob/e672154ab96d2c5a1410d5fa477f1b8f61ccf654/attempts/A115-k0-corner-rows/notes/t6_report.md) separates the converged-alive list from unfinished candidates. Its A170 addendum describes 128 kill-candidate records in a 166-open-record pool, with zero recovered by that recertification pass. The [gallery status](https://github.com/Esummins/packing/blob/e672154ab96d2c5a1410d5fa477f1b8f61ccf654/docs/shadows/STATUS.md) itself has sample-dependent counts. It is a review interface, not a substitute for an exhaustive covering manifest.

### Scientific and narrative accuracy

The strongest presentation is the documented interaction: observation → conjecture → exact test or counterexample → reusable rule → measured effect. The pin-clip case, the hull-versus-piece core correction, and a human conjecture refuted by a certified grazer are strong examples.

Avoid counterfactual claims about what either party “could not do alone.” The record establishes what happened in this collaboration and which suggestions preceded which results; it is not a controlled AI-alone comparison. The related-work chapter's explicit disclaimer is appropriately narrower than several claims in the summary and timeline.

Do not describe the agents as having “built the Lean kernel.” They built formalizations/checkers using Lean. Distinguish kernel `decide` from `native_decide`: the latter's compiler/evaluation trust is explicitly acknowledged by the repo's axiom audits.

The paper title `s(11)=ŝ` needs “toward” or an equally conspicuous target-status qualifier on an external cover. The detailed chapter does distinguish the target internally, but a title is often read alone.

## 3. Compute review

The current [budget table](https://github.com/Esummins/packing/blob/e672154ab96d2c5a1410d5fa477f1b8f61ccf654/docs/budget.md) contains arithmetic and scope drift:

| Scenario | Sum of displayed components | Displayed total |
|---|---:|---:|
| Hypothetical theorem route: A57 1,800 + protected 3,800 + k0 0 | 5,600 CPU-h | 6,100 CPU-h |
| Tree route using displayed k0 12,000 | 17,600 CPU-h | 19,500 CPU-h |
| Tree route using the same row's post-A141 k0 9,400–10,900 | 15,000–16,500 CPU-h | No reconciled total |
| Sum of displayed component low/high ranges | 11,050–28,350 CPU-h | 12,550–31,050 CPU-h |

These sums are not new estimates. They show why the existing totals need regeneration or an explicit overhead row.

More substantially:

1. **Theorem-route k0 = 0 is conditional on obtaining a theorem.** It is not a purchasable alternative to the tree route.
2. **A57's model has real measurements but an assumed tail.** Its recursion ends with `E_5=0`; observing no deeper descent in a sample does not prove the remaining tree has that depth. Quote it as an empirical forecast.
3. **Protected-tier extrapolation is weak where no closing mechanism is measured.** Mathematics §8.2 explicitly says corners4/k4_05 lack a priced route and identifies a resister branch. This prevents treating the aggregate as a completion guarantee.
4. **k0's old tree estimate does not price the new cascade.** [A191](https://github.com/Esummins/packing/blob/e672154ab96d2c5a1410d5fa477f1b8f61ccf654/attempts/A191-combined-cascade/BRIEF.md) is READY, NOT LAUNCHED and still asks for an additional row argument to be written. Its complete target-cell closure cost is unmeasured.
5. **Geometric pruning can cost substantial time.** [A184](https://github.com/Esummins/packing/blob/e672154ab96d2c5a1410d5fa477f1b8f61ccf654/attempts/A184-cascade-knobs/notes/knobs.md) measures mean S3 cost 41.7 s coarse versus 263.9 s fine, for just one extra verdict change among 64 cases. This supports the coarse-first choice; it does not establish the whole search price.
6. **LP candidates, verified leaves, closed subtrees, and retired gallery pages are different units.** Do not count unconverged v4 “LP-dead” records as certificates, or add overlapping savings from multiple attempts.
7. **Lean replay is excluded from the headline budget.** A complete proof package must separately budget replay, cover generation/checking, retries, artifact storage, and the engineering/formal work that compute cannot buy automatically.

For a fresh budget, every unresolved branch should have: an immutable identity and parent; the exact hypothesis/window; verifier version; current result class; next permitted operation; measured time/memory; and the remaining covering obligation. Deduplicate by tree plus node identity, not page name.

### Does single-digit-thousands make sense?

It is a plausible envelope for the *modeled search workload*, but the repo does not establish that it buys theorem completion.

Use a measured effective dollar cost per desktop-equivalent worker-hour, not a cloud vCPU count as if it were a desktop physical core. Include RAM and actual parallel throughput; the recent runners impose a 6,144 MB commit gate per LP. Cloud CPU and memory billing are distinct, and disk/network are additional costs ([Google's pricing documentation](https://cloud.google.com/products/compute/pricing)).

Sensitivity examples, **assumptions rather than provider quotes**:

| Search workload | At $0.10 per equivalent worker-hour | At $0.20 |
|---|---:|---:|
| 15,000–16,500 hours | $1,500–$1,650 | $3,000–$3,300 |
| Published high scenario, 31,050 hours | $3,105 | $6,210 |

Replay, retries, storage, and headroom are extra. These numbers explain why there is no need to force a speculative 400-hour target before outreach. They do not validate the workload forecast.

A practical proposal is a **$300–$500 capped calibration pilot**, followed by a revised allocation within a total ceiling such as **$7,500**. The pilot should use the corrected verifier and include ordinary A57 work, a protected hard case, k0 work, and at least one complete representative certificate replay. Report throughput, memory, exact closed work, remaining fan-out, and all timeouts. Release the larger allocation only against the refreshed manifest and cost model. Do not make success of a single selected k0 cell the sole gate.

## 4. Lean work to prioritize

| Priority | Deliverable | Why it matters |
|---|---|---|
| First | Sound v5 RHS handling; precise LINE-1 statement and transfer | Stops false certificates and an invalid proposed theorem from entering the critical path. |
| First | Concrete tree-file → cover/ClosedTree checking on one complete example | A proved generic tree-composition theorem does not verify that an emitted search tree covers its parent. This is essential to trustworthy large-scale search. |
| Next, if using new leaves | v3 polygon exemption, v4 window soundness, v5 chord/measure and distinctness bridges | Existing frozen-v1 Lean proofs do not automatically certify these extensions. |
| Parallel formal task | `a22_exact_structure` witness lemmas | Separates the exact octic identification/interface debt from computational exclusion. |
| Before claiming completion | All required per-class instances, K0-O1 dependencies, equality/uniqueness landings, and concrete corpus replay | These discharge the actual global theorem, rather than just its composition statement. |
| Can be deferred for outreach | S33/S38 formal replay and additional optional leaves not consumed by the selected route | Valuable follow-up, but not necessary to present the already established results honestly. |

Latest inspected CI was successful at commit `696998795340615f657391c779619c75b32d3863` ([run](https://github.com/Esummins/packing/actions/runs/34384301118)). The reviewed head is later and has no run, consistent with the workflow's path filters. The default build and manual slow/corpus targets have different scopes. A green badge must name what was actually built and must not be described as verification of every certificate or the global theorem.

## 5. Related-work accuracy and presentability

The related-work chapter should be shortened for the initial package. It is approximately 5,450 words and devotes substantial space to competitor claims, disputed attribution, and classifying other people's contributions. These are peripheral to the strongest evidence here and unnecessarily enlarge the fact-checking burden.

One concrete factual correction from primary-source checking: R10 dates arXiv:2601.22401v3 to 24 August and gives a different result breakdown. The [arXiv v3 record](https://arxiv.org/abs/2601.22401v3) dates it to **5 February 2026**, describing **five seemingly novel autonomous solutions and eight literature identifications**. Cite the exact version actually used. The chapter also lists Lean as a standard trust anchor across R10 despite its own row describing informal expert verification.

Replace “no comparable project found” novelty arguments with a direct contribution statement: this repository documents sustained visual guidance by an engineer, exact falsification of suggestions in both directions, and the resulting proof/search artifacts. A survey's inability to find another example does not establish priority.

For context, Anthropic's [FLT account](https://www.anthropic.com/research/formalizing-fermats-last-theorem) provides a verified primary comparator for formalization and orchestration. Three or four closely relevant primary references are sufficient for the initial brief.

### The visual story currently is not actually displayed

The mathematics chapter is about 17,700 words and the timeline about 15,600. Both contain figure filenames in code spans, but neither embeds those figures as Markdown images or HTML images. The figures are present in `writeup/figures/`; the main claimed interface is therefore hidden from a reader of the documents.

Embed three well-captioned before/after figures directly in the external brief. State for each: the original reading, the mathematical change or refutation, exact measured effect, and remaining limitation. Keep full logs and the long timeline as appendices. Fix “three documents” versus the four listed in `writeup/README.md`, replace code-span source paths with clickable links, and avoid giant tables containing whole paragraphs.

## 6. Minimum package for Anthropic

**For an initial technical conversation, five items suffice:**

1. **A two-page brief.** Problem, established bound, incomplete target, why the human–AI workflow is interesting, three figures, and a specific request. Lead with the work's observable contribution, not a claim of being uniquely non-professional.
2. **One canonical status sheet pinned to a commit.** Columns: result; proved in prose; exact checker; concrete Lean theorem/replay; open dependency. Put unfinished families visibly on it.
3. **A small reproducibility bundle.** One command for the certified headline result or a clearly timed target, one representative local/tree artifact, expected outputs, pinned tools, checker hashes, and an axiom report. Include the new adversarial v5 regression.
4. **A one-page capped compute plan.** Reconciled components, representative pilot, hardware normalization, memory, replay allowance, stop conditions, and total dollar ceiling. Label estimated closure/termination as estimated.
5. **A dated workflow case study.** Three episodes with traceable human suggestion, agent response, checker/counterexample, and measured outcome; distinguish literal transcript quotations from later paraphrases.

You do not need to polish every historical attempt, formalize every optional lemma, prove the complete target, or hit 400 CPU-hours before making contact. You do need to fix or explicitly quarantine v5, remove the contradictory headline claims, and make the remaining work legible.

For a stronger claim that **only raw compute remains**, the bar is higher: a sound fixed certificate chain, all non-computational proof/transfer obligations discharged or separately committed, an exhaustive outstanding-work manifest, independently checked tree composition, and a workload estimate calibrated on representative complete branches. Tonight's repo is not yet at that point.

The most credible request is for technical review of the existing certified results and workflow, plus discussion of a capped completion campaign. If seeking API credits, state them separately from raw CPU expenditure; A191 explicitly mentions waiting for API credits.

## Appendix — exact false-PASS regression

From a checkout of the reviewed commit, save the following as `repro_v5_false_kill.json`:

```json
{
  "format": "test",
  "n": 1,
  "s": "969271/250000",
  "budget": 1,
  "atoms": [],
  "weights": [],
  "hypotheses": {
    "cores": [],
    "nofams": [],
    "guardlines": [
      {"orient": "h", "off": "1/2", "z": "3", "rhs": "0"},
      {"orient": "h", "off": "27/20", "z": "3", "rhs": "0"},
      {"orient": "h", "off": "11/5", "z": "3", "rhs": "0"},
      {"orient": "h", "off": "61/20", "z": "3", "rhs": "0"}
    ]
  }
}
```

Run:

```sh
python attempts/A190-guardline-clause/code/verify_case_v5.py repro_v5_false_kill.json --replay --depth 40 --quiet
```

Observed: exit 0; total 0 < budget 1; PASS; “no packing of 1 unit squares” in side 969271/250000. Each recomputed RHS is 969271/250000, but the effective RHS is 0. The test is entirely exact, with the float prepass disabled.

Control: replace every `rhs` with `"969271/250000"`. Observed: exit 2; total mass 46.525008 ≥ budget 1, so no exclusion certificate.

Suggested correction in `rederive`:

```python
L.rhs_star = s - sum((c for _, c in terms), ZERO)
if L.rhs != L.rhs_star:
    raise ValueError("declared rhs differs from independently derived rhs")
L.rhs_eff = L.rhs_star
```

This fixes the demonstrated direction bug. It is not a substitute for the separate chord-boundary correction, the existing corpus replay, or the required formal bridge.

