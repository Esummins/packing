# A61 — window stragglers: close G-A56-1

**Role.** Computation postdoc. **Predecessors.** A56 (parametric transfer of the kill library over
W = [3.82, 3.877084]), A57 (merged-warm / checkpoint-folding column machinery), A55/k3_ext
(E3: atoms are the progress variable), A53/A54 (the library and the exact arbiters).

**Target.** The 12 stratum-kill certificates that A56 left valid at s0 only:
k5_02, k5_03, k5_05, k5_10, k5_12, k5_13, k5_14, k5_17, k6_20, k6_21, k6_27, k6_29.
Secondary, bounded: the two A56 PARTIAL rows — k6_23's 8.4e-5 sliver (G-A56-2) and k6_07's
0.050-wide band (G-A56-3).

**Recipe (A56's successor recipe, plus two A61 deltas).**
1. Enrich each stratum's guard LP with the A57 merged-warm / checkpoint-folding column pool
   (extended to A56's and A61's own `_state` checkpoints) to DROP tau0.
2. **Gate** on soundness.md P6(v): `budget - tau0 >= 0.5`. Below the gate, record honestly and
   move on — never burn a certify round (the ~1500 s lesson).
3. eps_geo = 0.003 re-solve, certify, 4D `verify_param` at depth 48 over W, canary C2 with the
   unmodified A53 verifier.
4. **A61 delta 1 (notes/lemmas.md L1): the eps_geo leak.** A56's `resolve_margin.py` set
   `lpbox.EPS_GEO` in its own process but invoked `certify.py` as a subprocess without
   `--eps_geo`, so every `--loop_cols` witness-feedback re-solve ran at the 1e-4 default and
   spent the positional slack the recipe had just bought. Confirmed on A56's own logs: all 7
   "certify PASS, 4D open" rows PASSed at round >= 1 with tau FALLING, which is impossible at
   fixed shrink. A61 passes `--eps_geo <eps> --no_resolve`.
5. **A61 delta 2: the anchoring ladder.** A56 tried only `gap` on these rows; anchoring is
   completeness, never soundness (P3), and a 4D run costs 10-250 s, so A61 walks
   gap -> nearest-wall -> mid-band before recording OPEN.

**Constraints.** <= 2 heavy processes (A57/A60 share the machine), RAM guard 4 GB, checkpointed,
one consolidated waiter, A29 untouched, A53/A54/A55/A56/A57 read-only except the A56 scoreboard
(updated with provenance under the P7 ledger rule, backup kept).

**Deliverable.** Per-stratum outcomes, the final window-coverage count, the updated A56
scoreboard, and the registry row.

**Code.** `code/resolve61.py` (per-stratum pipeline), `code/campaign61.py` (2-wide queue driver,
resumable), `code/sliver61.py` (the two partial rows), `code/update_scoreboard61.py` (P7 ledger
fold-in).
